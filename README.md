# データベース設計書

## テーブル一覧

users: 各ユーザーの情報を記録（ユーザーIDとユーザー名を記録）  
plays: プレイ履歴（全体でのプレイ履歴をユーザーと紐づけて順に記録）  
played_fishes: 釣れた魚の記録管理（各プレイでどの魚をいくつ釣ったかを順に記録）  
fishlists: 存在する魚の固定リスト（各オブジェクトの名前、製作者、テクスチャ名を記録）  

・ユーザーは複数回ゲームをプレイすることを想定  
・各プレイごとに総得点と釣った魚を記録  

## テーブル詳細

### users テーブル

| user_id | INT | PK, AUTO_INCREMENT | ユーザーID  
| username | VARCHAR(50) | NOT NULL, UNIQUE | ユーザー名  
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | ユーザー登録時の日時 

・user_id が主キー  
・user_id は AUTO_INCREMENT で自動で連番が振られていく  

### plays テーブル

| play_id | INT | PK, AUTO_INCREMENT | プレイID（全プレイでユニーク）  
| user_id | INT | NOT NULL, FK → users(user_id) | どのユーザーのプレイか  
| play_number | INT | NOT NULL, UNIQUE(user_id, play_number) | そのユーザーのn回目のプレイ  
| score | INT | NOT NULL | プレイのスコア  
| played_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | プレイ日時  

・play_id が主キー  
・play_id は users(user_id) を参照する外部キー  
・play_id は AUTO_INCREMENT で自動で連番が振られていく  

### played_fishes テーブル

| play_fish_id | INT | PK, AUTO_INCREMENT | プレイアイテムID  
| play_id | INT | NOT NULL, FK → plays(play_id) | どのプレイか  
| fish_id | INT | NOT NULL, FK → fishlists(fish_id) | どの魚か  
| quantity | INT | DEFAULT 1 | 釣れた匹数  

・play_fish_id が主キー  
・play_fish_id は AUTO_INCREMENT で自動で連番が振られていく  
・play_id は plays(play_id) を参照する外部キー  
・fish_id は fishlists(fish_id) を参照する外部キー  
・UNIQUE(play_id, item_id) で同じプレイ内の重複を防止  

### fishlists テーブル

| fish_id | INT | PK, AUTO_INCREMENT | オブジェクトID  
| fish_name | VARCHAR(100) | NOT NULL, UNIQUE | オブジェクト名  
| fish_creater | VARCHAR(100) | NOT NULL, UNIQUE | 製作者名  
| fish_texture_name | VARCHAR(100) | NOT NULL, UNIQUE | テクスチャ名  

・fish_id が主キー  
・fish_id は AUTO_INCREMENT で自動で連番が振られていく  

```
mysql -u root -p virtualfishing < virtualfishing.sql // データベースの復元
```

## ゲーム終了時のUnityからのスコアなど記録処理の動作例

usersテーブルとfishlistsテーブルは以下のようになっているとする  

### users テーブル（ユーザー登録可能）

| user_id | name  |
|:-------:|:-----:|
| 1       | Alice |
| 2       | Bob   |

### fishlists テーブル（固定リスト）

| fish_id | fish_name |
|:-------:|:---------:|
| 1       | tuna      |
| 2       | salmon    |
| 3       | carp      |
| 4       | shark     |

1回目のPOSTで送るJSON  
→Aliceが2回目のプレイで1500点獲得、["salmon", "tuna", "tuna", "salmon"]の魚を釣った  
```
{
  "name": "Alice",
  "play_number": 2,
  "score": 1500,
  "fish": ["salmon", "tuna", "tuna", "salmon"]
}
```

実行後のデータベース  

### plays テーブル

| play_id | user_id | play_number | score |
|:-------:|:-------:|:-----------:|------:|
| 1       | 1       | 2           | 1500  |

### played_fishes テーブル

| play_fish_id | play_id | fish_id | quantity |
|:------------:|:-------:|:-------:|---------:|
| 1            | 1       | 1       | 2        |
| 2            | 1       | 2       | 2        |
| 3            | 1       | 3       | 0        |
| 4            | 1       | 4       | 0        |

2回目のPOSTで送るJSON  
→Bobが1回目のプレイで2000点獲得、["salmon", "tuna", "carp", "salmon"]の魚を釣った
```
{ 
  "name": "Bob", 
  "play_number": 1, 
  "score": 2000, 
  "fish": ["salmon", "tuna", "carp", "salmon"] 
}
```

実行後のデータベース

### plays テーブル

| play_id | user_id | play_number | score |
|:-------:|:-------:|:-----------:|------:|
| 1       | 1       | 2           | 1500  |
| 2       | 2       | 1           | 2000  |

### played_fishes テーブル

| play_fish_id | play_id | fish_id | quantity |
|:------------:|:-------:|:-------:|---------:|
| 1            | 1       | 1       | 2        |
| 2            | 1       | 2       | 2        |
| 3            | 1       | 3       | 0        |
| 4            | 1       | 4       | 0        |
| 5            | 2       | 1       | 1        |
| 6            | 2       | 2       | 2        |
| 7            | 2       | 3       | 1        |
| 8            | 2       | 4       | 0        |
