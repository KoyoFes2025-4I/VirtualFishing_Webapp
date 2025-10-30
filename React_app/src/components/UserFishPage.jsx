import { useState, useEffect } from "react";

import '../styles/UserFishPage.css'

// ある1人のユーザーが釣れた魚を表示するページ
function UserFishPage({ user }) {
    const [creatorMap, setCreatorMap] = useState({}); // 魚名から製作者名のマッピング

    // ユーザーが存在するときだけ製作者情報を取得
    useEffect(() => {
        if (!user?.fishes) return; // ユーザーが存在しない

        const fetchCreators = async () => {
            const newMap = {};
            await Promise.all(user.fishes.map(async (fish) => {
                const fishName = typeof fish === "string" ? fish : fish.fish;
                try {
                    // FlaskのAPIサーバへGETリクエストを送ってレスポンスを取得
                    const response = await fetch(`http://localhost:5000/GetCreatorName?fishName=${encodeURIComponent(fish.fish)}`);
                    const data = await response.json();
                    newMap[fishName] = data.creator || null;
                } catch (err) {
                    newMap[fishName] = null;
                }
            }));
            setCreatorMap(newMap);
        };
        fetchCreators();
    }, [user]);

    // ユーザーがnullの場合の表示を切り替える
    if (!user) {
        return (
            <div className="container ranking-container text-center">
                <p>データを読み込み中...</p>
            </div>
        );
    }

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
                                    <span className="fish-name">{fish.fish}</span>
                                    {creatorMap[fish.fish] ? (
                                        <span className="creator">（作: {creatorMap[fish.fish]}）</span>
                                    ) : (
                                        <span className="creator">（読み込み中）</span>
                                    )}
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