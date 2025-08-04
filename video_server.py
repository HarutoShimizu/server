import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS  # Flutter Web対応のために必要
from werkzeug.utils import safe_join
from waitress import serve

app = Flask(__name__)
CORS(app)

# 🔧 動画を保存しているルートディレクトリをここで指定
# 複数のNAS共有フォルダをまとめて定義
VIDEO_DIRS = [
    r'\\192.168.0.51\1Fcam1\1Fkyouyoubu1\Schedule',
    r'\\192.168.0.51\1Fcam2\1Fkyouyoubu2\Schedule',
    r'\\192.168.0.51\1Fcam3\1Fkyouyoubu3\Schedule',
    r'\\192.168.0.51\2Fcam1\2Fkyouyoubu1\Schedule',
    r'\\192.168.0.51\2Fcam2\2Fkyouyoubu2\Schedule',
    r'\\192.168.0.51\2Fcam3\2Fkyouyoubu3\Schedule',
    r'\\192.168.0.51\2Fcam4\2Fkyouyoubu4\Schedule',
    r'\\192.168.0.51\2Fcam5\201\Schedule',
    r'\\192.168.0.52\2Fcam6\202\Schedule',
    r'\\192.168.0.52\2Fcam7\203\Schedule',
    r'\\192.168.0.52\2Fcam8\204\Schedule',
    r'\\192.168.0.52\2Fcam9\205\Schedule',
    r'\\192.168.0.52\2Fcam10\206\Schedule',
    r'\\192.168.0.52\2Fcam11\207\Schedule',
    r'\\192.168.0.52\2Fcam12\208\Schedule',
    r'\\192.168.0.53\2Fcam13\209\Schedule',
    r'\\192.168.0.53\2Fcam14\210\Schedule',
    r'\\192.168.0.53\2Fcam15\211\Schedule',
    r'\\192.168.0.53\2Fcam16\212\Schedule',
    r'\\192.168.0.53\2Fcam17\213\Schedule',
    r'\\192.168.0.53\3Fcam1\3Fkyouyoubu1\Schedule',
    r'\\192.168.0.53\3Fcam2\3Fkyouyoubu2\Schedule',
    r'\\192.168.0.53\3Fcam3\3Fkyouyoubu3\Schedule',
    r'\\192.168.0.54\3Fcam4\3Fkyouyoubu4\Schedule',
    r'\\192.168.0.54\3Fcam5\301\Schedule',
    r'\\192.168.0.54\3Fcam6\302\Schedule',
    r'\\192.168.0.54\3Fcam7\303\Schedule',
    r'\\192.168.0.54\3Fcam8\304\Schedule',
    r'\\192.168.0.54\3Fcam9\305\Schedule',
    r'\\192.168.0.54\3Fcam10\306\Schedule',
    r'\\192.168.0.54\3Fcam11\307\Schedule',
    r'\\192.168.0.55\3Fcam12\308\Schedule',
    r'\\192.168.0.55\3Fcam13\309\Schedule',
    r'\\192.168.0.55\3Fcam14\310\Schedule',
    r'\\192.168.0.55\3Fcam15\311\Schedule',
    r'\\192.168.0.55\3Fcam16\312\Schedule',
    r'\\192.168.0.55\3Fcam17\313Schedule',
    r'\\192.168.0.55\3Fcam18\314\Schedule',
    r'\\192.168.0.55\3Fcam19\315\Schedule',
    r'\\192.168.0.56\3Fcam20\316\Schedule',
    r'\\192.168.0.56\4Fcam1\4Fkyouyoubu1\Schedule',
    r'\\192.168.0.56\4Fcam2\4Fkyouyoubu2\Schedule',
    r'\\192.168.0.56\4Fcam3\4Fkyouyoubu3\Schedule',
    r'\\192.168.0.56\4Fcam4\401\Schedule',
    r'\\192.168.0.56\4Fcam5\402Schedule',
    r'\\192.168.0.56\4Fcam6\403\Schedule',
    r'\\192.168.0.57\4Fcam7\404\Schedule',
    r'\\192.168.0.57\4Fcam8\405\Schedule',
    r'\\192.168.0.57\4Fcam9\406Schedule',
    r'\\192.168.0.57\4Fcam10\407Schedule',
    r'\\192.168.0.57\4Fcam11\408\Schedule',
    r'\\192.168.0.57\4Fcam12\409\Schedule',
    r'\\192.168.0.57\4Fcam13\410\Schedule',

    r"C:\fall-detection-video",

]

# 🔍 /search?q=キーワード → 一致する動画ファイルを一覧で返す
@app.route('/search')
def search_files():
    query = request.args.get('q', '').lower()
    results = []

    for base_dir in VIDEO_DIRS:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if query in file.lower() and file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    relative_path = os.path.relpath(os.path.join(root, file), base_dir)
                    relative_path = relative_path.replace("\\", "/")
                    results.append({
                        'name': file,
                        'path': relative_path,
                        'base': base_dir,  # ← これを動画再生時に使う
                    })
    return jsonify(results or [{"message": "No files found"}])


# 🎥 /video/動画のパス → ファイルを直接配信
@app.route('/video/<path:video_path>')
def stream_video(video_path):
    base = request.args.get('base')  # base をクエリで受け取る
    if not base or base not in VIDEO_DIRS:
        return jsonify({"error": "Invalid base path"}), 400

    full_path = os.path.join(base, video_path)
    print("探しているパス:", full_path)

    if not os.path.exists(full_path):
        return f"ファイルが見つかりません: {full_path}", 404

    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    return send_from_directory(directory, filename)

# 📁 /list?path=サブフォルダ → フォルダ構造を返す（任意）
@app.route('/list')
def list_files():
    base = request.args.get('base')
    relative_path = request.args.get('path', '')

    if not base or base not in VIDEO_DIRS:
        return jsonify({"error": "Invalid base path"}), 400
    if '..' in relative_path.split(os.path.sep):
        return jsonify({"error": "Invalid path"}), 400

    current_dir = os.path.join(base, relative_path)
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
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
