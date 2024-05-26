import os

import openai
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# .envファイルの内容を読み込見込む
load_dotenv()

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.environ["OPENAI_ACCESS_TOKEN"]
openai.api_key = TOKEN
app = Flask(__name__, static_url_path="/")


@app.route("/api/respond_text", methods=["POST"])
def respond_text():
    print("start respond_text")
    request_data = request.get_json()
    if request_data is None:
        return jsonify({"error": "No JSON data received"}), 400
    print(request_data)
    translator = Translator(from_lang="ja", to_lang="en")
    result = translator.translate(request_data["text"])
    print("en" + result)
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "英語で返答してください。"},
            {"role": "user", "content": result},
        ],
    )
    print(res["choices"][0]["message"]["content"])

    # 英語→日本語の翻訳
    translator = Translator(from_lang="en", to_lang="ja")
    respond_data_text = translator.translate(res["choices"][0]["message"]["content"])
    print("ja" + respond_data_text)

    # レスポンスデータを作成
    response_data = {"text": respond_data_text}

    # レスポンスデータをJSON形式で返す
    return jsonify(response_data), 200


# Flaskのみで動作するビルトインサーバーを起動する※ローカルで動かす時用
if __name__ == "__main__":
    PORT = 5001
    app.run(
        threaded=True,
        debug=True,
        port=PORT,
        host="0.0.0.0",
    )
