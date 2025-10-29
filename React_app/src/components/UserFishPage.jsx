// ある1人のユーザーが釣れた魚を表示するページ

function UserFishPage({ user }) {
    if (!user) {
        return (
            <div className="container ranking-container text-center">
                <p>データを読み込み中...</p>
            </div>
        );
    }

    return (
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
                                {fish.fish} × {fish.quantity}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default UserFishPage;