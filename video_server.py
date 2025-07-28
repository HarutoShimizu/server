from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# Windows上のフォルダを仮のNASとして使う（適宜変更）
NAS_VIDEO_PATH = 'C:/Users/haru10/Videos'  # ← 自分のPCの動画フォルダに書き換えてください

app = Flask(__name__)
CORS(app)

@app.route('/search')
def search_files():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query not specified"}), 400

    found_files = []
    for root, dirs, files in os.walk(NAS_VIDEO_PATH):
        for file in files:
            if query.lower() in file.lower() and file.endswith(('.mp4', '.mov')):
                relative_path = os.path.relpath(os.path.join(root, file), NAS_VIDEO_PATH)
                found_files.append({
                    "name": file,
                    "path": relative_path
                })
    return jsonify(found_files)

@app.route('/video/<path:filepath>')
def stream_video(filepath):
    return send_from_directory(NAS_VIDEO_PATH, filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
