from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

app = Flask(__name__)
CORS(app)  # 他アプリからのこのAPIサーバへのリクエストを全て許可

# ユーザー登録 : React => Flask => MySQL
# ユーザー登録をUnity側へ反映 : MySQL => Flask => Unity
# ゲーム終了後のユーザー情報登録 : Unity => Flask => MySQL
# リアルタイムのランキング表示 : MySQL => Flask => React
# PNG画像（写真）を貼付テクスチャ用にUnityへ送る : Flutter => Flask => Unity

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# usersテーブルのモデル
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True) # user_id
    name = db.Column(db.String(80), nullable=False, unique=True) # username
    
# playsテーブルのモデル
class Play(db.Model):
    __tablename__ = 'plays'

    id = db.Column(db.Integer, primary_key=True) # play_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # user_id
    play_number = db.Column(db.Integer, nullable=False) # play_number
    score = db.Column(db.Integer, nullable=False) # score

    # 複合ユニーク制約（user_idとplay_numberの組み合わせが重複無し）
    __table_args__ = (
        UniqueConstraint('user_id', 'play_number', name='uix_user_play'),
    )

# played_fishesテーブルのモデル
class Played_fishes(db.Model):
    __tablename__ = 'played_fishes'

    id = db.Column(db.Integer, primary_key=True) # play_fish_id
    play_id = db.Column(db.Integer, db.ForeignKey('plays.id'), nullable=False) # play_id
    fish_id = db.Column(db.Integer, db.ForeignKey('fishlists.id'), nullable=False) # fish_id
    quantity = db.Column(db.Integer, default=1) # quantity

# fishlistsテーブルのモデル
class Fishlists(db.Model):
    __tablename__ = 'fishlists'

    id = db.Column(db.Integer, primary_key=True) # fish_id

# 新規ユーザーをusersテーブルに追加する
# 'name'の値をJSONで受け取る（POSTメソッド）
@app.route("/Add", methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify(success=False, error="No 'name' field in JSON"), 400

    user_name = data['name'] # nameの値を受け取る

    try:
        new_user = User(name=user_name) # usersのusernameに登録
        db.session.add(new_user)
        db.session.commit()
        return jsonify(success=True) # 成功
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)) # 失敗
    
# Unity側から呼んで現在登録されている全てのユーザーをロードする
@app.route("/LoadUsers", methods=['POST'])
def load_user():
    try:
        # usersテーブルの全usernameを取得してリストにする
        usernames = [user.name for user in User.query.all()]

        # 成功したらJSONでそのリストをレスポンスする
        return jsonify({"usernames": usernames})
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗

# "http://localhost:5000" でFlaskサーバが立ち上がる
if __name__ == "__main__":
    app.run(port=5000, debug=True)