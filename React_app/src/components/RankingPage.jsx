import '../styles/RankingPage.css'

// 上位5名のランキング表示ページ
function RankingPage({ ranking = []}){
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
                                    {ranking[i]?.username || "No player yet"}
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