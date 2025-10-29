from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, func
from collections import Counter

app = Flask(__name__)
CORS(app)  # 他アプリからのこのAPIサーバへのリクエストを全て許可

# ユーザー登録 : React => Flask => MySQL
# ユーザー情報をUnity側からロード : MySQL => Flask => Unity
# 任意のユーザーのロード済みの状態をリセットする : Unity => Flask => MySQL
# ゲーム終了後のユーザー情報登録 : Unity => Flask => MySQL
# Unity側で新規テクスチャを登録した際に名前と製作者をfishlistsへ保存 : Unity => Flask => MySQL
# リアルタイムのランキング表示（スコア、釣った魚、製作者） : MySQL => Flask => React
# 現在の来場者数表示用アプリでusersの総カラム数を取得する MySQL => Flask => Unity

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:3710@localhost/virtualfishing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# usersテーブルのモデル
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True) # user_id
    username = db.Column(db.String(80), nullable=False, unique=True) # username
    loaded = db.Column(db.Integer, nullable=False) # loaded
    
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
    fish_creator = db.Column(db.String(100), nullable=False, unique=True) # fish_creator

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
        # 現状loaded = 0 の未ロードのユーザーをすべて取得
        new_users = User.query.filter_by(loaded=0).all()

        # new_usersの要素を全て取得してリストにする
        usernames = [user.username for user in new_users]

        # 該当ユーザーのloadedを1（ロード済み）に更新させる
        if new_users:
            for user in new_users:
                user.loaded = 1
            db.session.commit()

        # 成功したらJSONでそのリストをレスポンスする
        return jsonify({"usernames": usernames})
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗
    
# Unity側から呼んでGETで指定したユーザーのloadedを0（未ロード）に戻す
# 2回目以降来た人のユーザー名をロードする用
@app.route("/RestoreLoaded", methods=['GET'])
def restore_user():
    try:
        # GETパラメータからusernameを取得
        username = request.args.get('username')
        if not username:
            return jsonify(success=False, error="username parameter is required"), 400
        
        # 対象ユーザーを取得
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify(success=False, error=f"User '{username}' not found"), 404
        
        # loadedを0（未ロード）に戻す
        user.loaded = 0
        db.session.commit()

        return jsonify(success=True, message=f"User '{username}' restored")
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗

# ゲーム終了時にスコアなどのデータをデータベースに記録する
# どのユーザーが、得点がいくつで、どの魚を釣ったのか（匹数の情報含む）の各々のデータをJSONで受け取る
# 何回目のプレイか（play_number）は、API側で自動でそのユーザーが何回目のプレイかを処理する
@app.route("/RecordResult", methods=['POST'])
def record_result():
    data = request.get_json()  # JSONを取得

    # 必須フィールドの有無をチェック
    required_fields = ["name", "point", "fishedThingNames"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify(success=False, error=f"Missing fields: {missing}"), 400

    # JSONの値を取り出す
    user_name = data["name"] # どのユーザーが
    score = data["point"] # 得点がいくつで
    fish_data = data["fishedThingNames"] # 釣れた魚のリスト（魚の重複あり）
    
    try:
        # Fishlistsテーブルからfish_name → fish_idの辞書リストを作っておく
        fish_dict = {f.fish_name: f.fish_id for f in Fishlists.query.all()}

        # fish_dataから各魚の出現回数をCounterでMapとしてまとめる
        fish_counter = Counter(fish_data)

        # quantity > 0 の魚だけに絞って登録用リストを作成
        # (fish_id, quantity)の組のリストができる（quantity = 0 を除く）
        played_fishes_to_add = [
            (fish_dict[fish_name], quantity)
            for fish_name, quantity in fish_counter.items()
            if fish_name in fish_dict and quantity > 0
        ]

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
        for fish_name, quantity in played_fishes_to_add:
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
# さらにそれらのユーザーが実際に釣った魚の情報もレスポンスする
@app.route("/GetRanking", methods=['POST'])
def get_ranking():
    try:
        # スコアの値が高い順に上から5つ、それぞれどのplay_idで何回目のプレイで何点取ったかをPlaysから読み取る
        # (play_id, username, score) のタプルをtop_five_playsに受け取る
        top_five_plays = (
            db.session.query(Play.play_id, User.username, Play.score)
            .join(User, Play.user_id == User.user_id)
            .order_by(Play.score.desc()) # scoreの大きい順に並び変え
            .limit(5) # 上位5名を見る
            .all()
        )

        ranking_data = []

        # top_five_playsの各要素について、そのplay_idを使い何の魚を何匹釣ったかのリストをPlayed_fishesから読み取る
        for play_id, username, score in top_five_plays:
            fished_fishes = (
                db.session.query(Fishlists.fish_name, Played_fishes.quantity)
                .join(Played_fishes, Played_fishes.fish_id == Fishlists.fish_id)
                .filter(Played_fishes.play_id == play_id, Played_fishes.quantity > 0)
                .all()
            )

        # [(魚名, 数量)] → [{"fish": 魚名, "quantity": 数量}] に変える
        fish_list = [{"fish": row[0], "quantity": row[1]} for row in fished_fishes]

        # スコア上位5名が、誰が何点取って何の魚を何匹とったのかのリストを作る
        ranking_data.append({
            "username": username,
            "score": score,
            "fishes": fish_list
        })

        # JSONでranking_dataをレスポンスする
        return jsonify({"ranking": ranking_data}), 200
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗

# Unity側から呼んで現在の総来場者数を取得する
@app.route("/GetTurnouts", methods=['GET'])
def get_turnouts():
    try:
        # usersテーブルの総カラム数（登録されているユーザー数）を取得する
        total_users = db.session.query(User).count()

        return jsonify({"turnouts": total_users})
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗

# Unity側から呼んでオブジェクト名と製作者名をfishlistsへ追加する
@app.route("/SetFishObjects", methods=['POST'])
def set_fish_objects():
    data = request.get_json()  # JSONを取得

    # 必須フィールドの有無をチェック
    required_fields = ["fishName", "fishCreator"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify(success=False, error=f"Missing fields: {missing}"), 400

    # JSONの値を取り出す
    fishName = data["fishName"] # オブジェクト名
    fishCreator = data["fishCreator"] # 製作者名

    try:
        # Fishlistsテーブルに新しいレコードを追加する
        new_fishData = Fishlists(
            fish_name = fishName,
            fish_creator = fishCreator
        )
        db.session.add(new_fishData)
        db.session.commit()

        return jsonify(success=True), 201 # 成功
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500 # 失敗

# "http://localhost:5000" でFlaskサーバが立ち上がる
if __name__ == "__main__":
    app.run(port=5000, debug=True)