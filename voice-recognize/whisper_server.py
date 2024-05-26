import os
import subprocess
import threading
import time

import whisper
from flask import Flask, jsonify, redirect, request

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"m4a", "mp3", "wav"}
WHISPER_MODEL_NAME = "small"  # tiny, base, small, medium
WHISPER_DEVICE = "cpu"  # cpu, cuda

args = {
    "shell": True,
    "capture_output": True,
    "text": True
}

print("loading whisper model", WHISPER_MODEL_NAME, WHISPER_DEVICE)
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__, static_url_path="/")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

lock = threading.Lock()


def is_allowed_file(filename):
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return redirect("/index.html")


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    time_sta = time.perf_counter()
    print("start transcribe " + str(time_sta))
    file = request.files["file"]
    if file and is_allowed_file(file.filename):
        extension = file.filename.rsplit(".", 1)[1].lower()
        filename = str(int(time.time())) + "." + extension
        print(filename)
        saved_filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        print(saved_filename)
        file.save(saved_filename)
        lock.acquire()
        try:
            # シェルコマンドを実行し、その出力を取得
            command = f"whisper {saved_filename} --language ja"
            result = subprocess.run(command, **args)
            if result.returncode != 0:
                raise Exception(f"Whisper command failed: {result.stderr}")

            output = result.stdout
            elapsed_time = time.perf_counter() - time_sta
            print("time=" + str(elapsed_time))
            print(output)
            basename = filename.split(".")[0]
            remove_files_with_base_name(basename)
            os.remove(saved_filename)
            return jsonify(output), 200
        except Exception as e:
            print("Error:", str(e))
            return jsonify({"error": "Transcription error"}), 500
        finally:
            lock.release()
    else:
        print("Invalid file format")
        return jsonify({"error": "Invalid file format"}), 400


# ファイルを削除する関数
def remove_files_with_base_name(base_name):
    extensions_to_remove = [".txt", ".srt", ".tsv", ".vtt", ".json"]
    for extension in extensions_to_remove:
        file_path = base_name + extension
        os.remove(file_path)


# Flaskのみで動作するビルトインサーバーを起動する
if __name__ == "__main__":
    PORT = 5000
    app.run(
        threaded=True,
        debug=True,
        port=PORT,
        host="0.0.0.0",
    )
