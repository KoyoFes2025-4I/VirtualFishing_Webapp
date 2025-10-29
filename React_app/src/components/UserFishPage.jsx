import { useState, useEffect } from "react";

// ある1人のユーザーが釣れた魚を表示するページ
function UserFishPage({ user }) {
    const [creatorMap, setCreatorMap] = useState({}); // 魚名から製作者名のマッピング

    // 対象ユーザーが存在するか確認
    if (!user) {
        return (
            <div className="container ranking-container text-center">
                <p>データを読み込み中...</p>
            </div>
        );
    }

    // 魚名に対応する製作者名を取得する関数
    const fetchCreatorName = async (fish) => {
        try {
            // FlaskのAPIサーバへGETリクエストを送ってレスポンスを取得
            const response = await fetch(`http://localhost:5000/GetCreatorName?fishName=${encodeURIComponent(fish)}`, {
                method: "GET",
            });

            const data = await response.json(); // JSONレスポンスを受け取る

            if (data.success) {
                return data.creator; // creatorを取得して返す
            } else {
                console.error("取得失敗:", data.error);
                return null;
            }
        } catch (err) {
            console.error("通信エラー:", err);
            return null;
        }
    }

    // ユーザーが更新されたら、そのユーザーが釣った全ての魚に対して製作者を取得
    useEffect(() => {
        if (!user?.fishes) return;

        const loadCreators = async () => {
            const newMap = {};
            for (const fish of user.fishes) {
                const creator = await fetchCreatorName(fish.fish);
                newMap[fish.fish] = creator;
            }
            setCreatorMap(newMap);
        };

        loadCreators();
    }, [user]);

    return (
        <>
            <div className="userfish-background"></div>
            <div className="container ranking-container">
                <div className="card shadow-sm ranking-card">
                    <div className="card-body text-center">
                        <h3 className="card-title mb-3">
                            🎣 {user.username} さんが釣り上げた魚
                        </h3>
                        <p className="text-muted">スコア：{user.score}</p>
                        <ul className="list-group list-group-flush">
                            {user.fishes.map((fish, i) => (
                                <li key={i} className="list-group-item">
                                    {fish.fish}
                                    {creatorMap[fish.fish]
                                        ? `（${creatorMap[fish.fish]}）`
                                        : "（取得中...）"}
                                    × {fish.quantity}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </>
    );
}

export default UserFishPage;