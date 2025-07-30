import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS  # Flutter Web対応のために必要
from werkzeug.utils import safe_join
from waitress import serve

app = Flask(name)
CORS(app)

# 🔧 動画を保存しているルートディレクトリをここで指定
VIDEO_DIR = 'C:/Users/siras/Videos'  # ← 自分の環境に合わせて変更

# 🔍 /search?q=キーワード → 一致する動画ファイルを一覧で返す
@app.route('/search')
def search_files():
    query = request.args.get('q', '').lower()
    results = []

    for root, dirs, files in os.walk(VIDEO_DIR):
        for file in files:
            if query in file.lower() and file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                relative_path = os.path.relpath(os.path.join(root, file), VIDEO_DIR)
                relative_path = relative_path.replace("\\", "/")
                results.append({
                    'name': file,
                    'path': relative_path
                })
    return jsonify(results or [{"message": "No files found"}])

# 🎥 /video/動画のパス → ファイルを直接配信
@app.route('/video/<path:video_path>')
def stream_video(video_path):
    import os
    full_path = os.path.join(VIDEO_DIR, video_path)
    print("探しているパス:", full_path)

    if not os.path.exists(full_path):
        return f"ファイルが見つかりません: {full_path}", 404

    return send_from_directory(VIDEO_DIR, video_path)

# 📁 /list?path=サブフォルダ → フォルダ構造を返す（任意）
@app.route('/list')
def list_files():
    relative_path = request.args.get('path', '')
    if '..' in relative_path.split(os.path.sep):
        return jsonify({"error": "Invalid path"}), 400

    current_dir = os.path.join(VIDEO_DIR, relative_path)
    if not os.path.isdir(current_dir):
        return jsonify({"error": "Directory not found"}), 404

    items = []
    for item_name in os.listdir(current_dir):
        full_path = os.path.join(current_dir, item_name)
        item_relative_path = os.path.join(relative_path, item_name)
        if os.path.isdir(full_path):
            items.append({"name": item_name, "path": item_relative_path, "type": "directory"})
        elif item_name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            items.append({"name": item_name, "path": item_relative_path, "type": "file"})

    return jsonify(items)

# 🔧 アプリの起動設定
if name == 'main':
    serve(app, host='0.0.0.0', port=5000)