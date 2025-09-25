import { useState, useEffect } from 'react'

import '../styles/RankingPage.css'

// ランキング表示ページ
function RankingPage(){
    const [ranking, setRanking] = useState([]); // 上位5名ランキング

    // ランキングを表示するためのリスト情報をAPIから取得
    const fetchRanking = async () => {
        try {
            // FlaskのAPIサーバへリクエストを送ってレスポンスを取得
            const response = await fetch("http://localhost:5000/GetRanking", {
                method: "POST", // JSONファイルをPOSTで受け取る
                headers: { "Content-Type": "application/json" },
            });

            const data = await response.json(); // JSONファイルを取得

            if (response.ok && data.success !== false) {
                // Flaskからのレスポンスを { usernames: [], ranked_score: [] } で受け取る
                const usernames = data.usernames || [];
                const scores = data.ranked_score || [];

                // 2つのリストを「ユーザー名とスコアのオブジェクト」にまとめる
                const combined = usernames.map((name, i) => ({
                    name,
                    score: scores[i],
                }));

                setRanking(combined);
            } else {
                // 何も表示しない
            }
        } catch (error) {
            // 何も表示しない
        }
    };

    // リアルタイム更新のための処理
    useEffect(() => {
        fetchRanking(); // 初回ロード時
        const interval = setInterval(fetchRanking, 5000); // 5秒ごとに更新
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="container ranking-container">
            <div className="card shadow-sm ranking-card">
                <div className="card-body">
                    <h3 className="card-title text-center mb-4">🏆 本日のランキング</h3>
                    <ul className="list-group list-group-flush">
                        {[0, 1, 2, 3, 4].map((i) => (
                            // 未決定のランキングの部分は名前を"Not yet"、スコアを"-"で表示
                            <li
                                key={i}
                                className="list-group-item d-flex justify-content-between align-items-center"
                            >
                                <span>
                                    <span className="badge bg-primary me-2">
                                        {i + 1}
                                    </span>
                                    {ranking[i]?.name || "No player yet"}
                                </span>
                                <span>
                                    {ranking[i]?.score !== undefined
                                        ? ranking[i].score
                                        : "-"}
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default RankingPage