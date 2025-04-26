







import pandas as pd
import asyncio
from telethon import TelegramClient, errors

async def search_in_channel(client, channel_link, keyword):
    try:
        print(f"Searching in: {channel_link} for keyword: {keyword}")
        channel = await client.get_entity(channel_link)
        messages = await client.get_messages(channel, search=keyword, limit=100)

        results = []
        for msg in messages:
            if msg.text and keyword.lower() in msg.text.lower():
                date = msg.date.strftime('%Y-%m-%d %H:%M:%S') if msg.date else 'Unknown date'
                results.append({
                    "channel": channel_link,
                    "message": msg.text,
                    "date": date,
                    "url": f"https://t.me/c/{channel.id}/{msg.id}"
                })

        return results
    except errors.FloodWaitError as e:
        print(f"FloodWaitError: Waiting {e.seconds} seconds.")
        await asyncio.sleep(e.seconds)
        return []
    except Exception as e:
        print(f"Error accessing {channel_link}: {e}")
        return []


async def process_channels(dataset_path, keyword, api_id, api_hash):
    try:
        df = pd.read_csv(dataset_path)
        if 'channel' not in df.columns:
            return {"error": "Dataset must contain a 'channel' column."}

        channel_links = df['channel'].dropna().unique().tolist()
        if not channel_links:
            return {"error": "No valid Telegram links found in dataset."}

        async with TelegramClient('session_name', api_id, api_hash) as client:
            tasks = [search_in_channel(client, link, keyword) for link in channel_links]
            results = await asyncio.gather(*tasks)

        return {"results": [item for sublist in results for item in sublist]}
    except Exception as e:
        return {"error": f"Error processing dataset: {e}"}