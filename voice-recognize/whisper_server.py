import os
import time
from flask import Flask, request, redirect, jsonify
import whisper
import threading
import openai
import subprocess
import traceback

# .envファイルの内容を読み込見込む
#load_dotenv()

# 自分のBotのアクセストークンに置き換えてください
#TOKEN = os.environ['OPENAI_ACCESS_TOKEN']
#openai.api_key = TOKEN
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'wav'}
WHISPER_MODEL_NAME = 'small'  # tiny, base, small, medium
WHISPER_DEVICE = 'cpu'  # cpu, cuda

print('loading whisper model', WHISPER_MODEL_NAME, WHISPER_DEVICE)
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__, static_url_path='/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

lock = threading.Lock()

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect('/index.html')

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    time_sta = time.perf_counter()
    print('start transcribe ' + str(time_sta))  # カッコが閉じていない
    file = request.files['file']
    if file and is_allowed_file(file.filename):
        filename = str(int(time.time())) + '.' + file.filename.rsplit('.', 1)[1].lower()
        print(filename)
        saved_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(saved_filename)
        file.save(saved_filename)
        lock.acquire()
        try:
            print('a')
            # シェルコマンドを実行し、その出力を取得
            command = f"whisper {saved_filename} --language ja"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Whisper command failed: {result.stderr}")
            
            output = result.stdout
            elapsed_time = time.perf_counter() - time_sta  # タイポ修正
            print('time=' + str(elapsed_time))
            print(output)
            basename=filename.split('.')[0]
            remove_files_with_base_name(basename)
            os.remove(saved_filename)
            return jsonify(output), 200
        except Exception as e:
            print('Error:', str(e))
            return jsonify({'error': 'Transcription error'}), 500
        finally:
            lock.release()
    else:
        print('Invalid file format')
        return jsonify({'error': 'Invalid file format'}), 400

@app.route('/api/respond_text', methods=['POST'])
def respond_text():
    print('start respond_text')
    # POSTリクエストからJSONデータを取得
    request_data = request.get_json()
    if request_data is None:
        return jsonify({'error': 'No JSON data received'}), 400

    # レスポンスデータを作成
    response_data = {'text': 'うまくいってます'}

    # レスポンスデータをJSON形式で返す
    return jsonify(response_data), 200


# ファイルを削除する関数
def remove_files_with_base_name(base_name):
    extensions_to_remove = ['.txt', '.srt', '.tsv', '.vtt', '.json']
    for extension in extensions_to_remove:
            file_path=base_name+extension
            os.remove(file_path)

# 削除したいファイル名と拡張子のリスト

# Flaskのみで動作するビルトインサーバーを起動する※ローカルで動かす時用
if __name__ == '__main__':
    PORT = 5000
    app.run(
        threaded=True,
        debug=True,
        port=PORT,
        host='0.0.0.0',
    )