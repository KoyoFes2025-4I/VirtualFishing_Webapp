from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)  # 他アプリからのこのAPIサーバへのリクエストを全て許可

# ユーザー登録 : React => Flask => MySQL
# ユーザー登録をUnity側へ反映 : MySQL => Flask => Unity
# ゲーム終了後のユーザー情報登録 : Unity => Flask => MySQL
# リアルタイムのランキング表示 : MySQL => Flask => React
# PNG画像（写真）を貼付テクスチャ用にUnityへ送る : Flutter => Flask => Unity

@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask!"})

# "http://localhost:5000" でFlaskサーバが立ち上がる
if __name__ == "__main__":
    app.run(port=5000, debug=True)