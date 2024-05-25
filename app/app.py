# coding:utf-8
from flask import Flask, request

app = Flask(__name__)
app.config.from_json("development.json", True)

@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/test", methods=["GET"])
def test():
    return "Test OK!", 404

