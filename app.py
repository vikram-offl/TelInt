import asyncio
import json
import os
from flask import Flask, render_template, request, jsonify, Response
from main import process_channels
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
DATASET_PATH = "OSINT_Datasets/online_telegram_channels.csv"


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    loop.close()
    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    def generate():
        try:
            result = run_async(process_channels(DATASET_PATH, keyword, API_ID, API_HASH))

            if 'error' in result:
                yield f"data: {json.dumps(result)}\n\n"
            else:
                for item in result['results']:
                    yield f"data: {json.dumps(item)}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.run(debug=True, port=8080, threaded=True)