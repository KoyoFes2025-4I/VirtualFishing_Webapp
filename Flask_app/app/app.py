from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, func

app = Flask(__name__)
CORS(app)  # 他アプリからのこのAPIサーバへのリクエストを全て許可

# ユーザー登録 : React => Flask => MySQL
# ユーザー登録をUnity側へ反映 : MySQL => Flask => Unity
# ゲーム終了後のユーザー情報登録 : Unity => Flask => MySQL
# リアルタイムのランキング表示 : MySQL => Flask => React
# PNG画像をスキャンして貼付テクスチャ用にUnityへ送る : Scanner => PC(Flask) => Unity

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:3710@localhost/virtualfishing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# usersテーブルのモデル
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True) # user_id
    username = db.Column(db.String(80), nullable=False, unique=True) # username
    
# playsテーブルのモデル
class Play(db.Model):
    __tablename__ = 'plays'

    play_id = db.Column(db.Integer, primary_key=True) # play_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False) # user_id
    play_number = db.Column(db.Integer, nullable=False) # play_number
    score = db.Column(db.Integer, nullable=False) # score

    # 複合ユニーク制約（user_idとplay_numberの組み合わせが重複無し）
    __table_args__ = (
        UniqueConstraint('user_id', 'play_number', name='uix_user_play'),
    )

# played_fishesテーブルのモデル
class Played_fishes(db.Model):
    __tablename__ = 'played_fishes'

    play_fish_id = db.Column(db.Integer, primary_key=True) # play_fish_id
    play_id = db.Column(db.Integer, db.ForeignKey('plays.play_id'), nullable=False) # play_id
    fish_id = db.Column(db.Integer, db.ForeignKey('fishlists.fish_id'), nullable=False) # fish_id
    quantity = db.Column(db.Integer, default=1) # quantity

# fishlistsテーブルのモデル
class Fishlists(db.Model):
    __tablename__ = 'fishlists'

    fish_id = db.Column(db.Integer, primary_key=True) # fish_id
    fish_name = db.Column(db.String(100), nullable=False, unique=True) # fish_name

# 新規ユーザーをusersテーブルに追加する
# 'name'の値をJSONで受け取る
@app.route("/Add", methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify(success=False, error="No 'name' field in JSON"), 400

    user_name = data['name'] # nameの値を受け取る

    try:
        new_user = User(username=user_name) # usersのusernameに登録
        db.session.add(new_user)
        db.session.commit()
        return jsonify(success=True) # 成功
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)) # 失敗
    
# Unity側から呼んで現在登録されている全てのユーザーをロードする
@app.route("/LoadUsers", methods=['GET'])
def load_user():
    try:
        # usersテーブルの全usernameを取得してリストにする
        usernames = [user.username for user in User.query.all()]

        # 成功したらJSONでそのリストをレスポンスする
        return jsonify({"usernames": usernames})
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗
    
# ゲーム終了時にスコアなどのデータをデータベースに記録する
# どのユーザーが、得点がいくつで、どの魚を釣ったのか（匹数の情報含む）の各々のデータをJSONで受け取る
# 何回目のプレイか（play_number）は、API側で自動でそのユーザーが何回目のプレイかを処理する
@app.route("/RecordResult", methods=['POST'])
def Record_result():
    data = request.get_json()  # JSONを取得

    # 必須フィールドの有無をチェック
    required_fields = ["name", "point", "fishedThingNames"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify(success=False, error=f"Missing fields: {missing}"), 400

    # JSONの値を取り出す
    user_name = data["name"] # どのユーザーが
    score = data["point"] # 得点がいくつで
    fish_data = data["fishedThingNames"] # 釣れた魚のリスト

    fishnames = [] # 全ての魚オブジェクトの名前のリスト
    fish_occurrences = [] # 各魚のそのプレイでの出現回数のリスト（fishnamesと順序同じ）
    
    try:
        # Fishlistsテーブルからfish_name → fish_idの辞書リストを作っておく
        fish_dict = {f.fish_name: f.fish_id for f in Fishlists.query.all()}

        # # fishlistsテーブルの全fish_nameを取得してfishnamesに入れる
        fishnames = list(fish_dict.keys())

        # fish_dataの中に各魚が何回出現していたのかをfish_occurrencesにリスト化（0匹も含む）
        fish_occurrences = [fish_data.count(fish) for fish in fishnames]

        # ユーザーIDを取得（user_nameに対応するidを取得）
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return jsonify(success=False, error="User not found"), 404
        
        # そのユーザーが何回目のプレイであるのかをデータベースを参照して計算する
        # 現時点での一番大きいplay_numberを探してきてその+1の値とする
        max_play_number = db.session.query(func.max(Play.play_number))\
            .filter_by(user_id=user.user_id).scalar()
        play_number = (max_play_number or 0) + 1
        
        # 新しいplaysのレコードを作成
        new_play = Play(
            user_id=user.user_id, # user_idをセット
            play_number=play_number, # play_numberをセット
            score=score # scoreをセット
        )
        db.session.add(new_play)
        db.session.commit() # 自動セットされるplay_idを取得するために一度commit

        play_id = new_play.play_id # play_idを取得（AUTO_INCREMENT）

        # fishnamesリストとfish_occurrencesをまとめてplayed_fishesに登録
        for fish_name, quantity in zip(fishnames, fish_occurrences):
            played_fish = Played_fishes(
                play_id=play_id, # play_idを連携させる
                fish_id=fish_dict[fish_name], # 魚の名前をidに変換して保存
                quantity=quantity # 何匹とれたか（0匹でも0と表示）
            )
            db.session.add(played_fish)

        db.session.commit()

        return jsonify(success=True), 201 # 成功

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500 # 失敗
    
# React側から呼んでユーザー名とスコアの1位～5位をリストで取得する
@app.route("/GetRanking", methods=['POST'])
def get_ranking():
    try:
        # (username, score) のタプルとしてtop_five_playsに結果を受け取る
        top_five_plays = (
            db.session.query(User.username, Play.score) # usersのnameとplaysのscoreを取り出す
            .join(User, Play.user_id == User.user_id) # PlayとUserを結合
            .order_by(Play.score.desc()) # scoreの大きい順に並び変え
            .limit(5) # 上位5名を見る
            .all()
        )

        # それぞれユーザー名とスコアのリストに分ける（順序同じ）
        usernames = [row[0] for row in top_five_plays]
        ranked_score = [row[1] for row in top_five_plays]

        # 成功したらJSONで2つのリストをJSONでレスポンスする
        return jsonify({"ranked_score": ranked_score, "usernames": usernames})
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗

# "http://localhost:5000" でFlaskサーバが立ち上がる
if __name__ == "__main__":
    app.run(port=5000, debug=True)