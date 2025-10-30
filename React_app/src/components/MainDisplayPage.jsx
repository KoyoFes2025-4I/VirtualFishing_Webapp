import { useState, useEffect } from "react";
import RankingPage from "./RankingPage";
import UserFishPage from "./UserFishPage";

// RankingPageとUserFishPageを交互に表示させるメインページ
function MainDisplay() {
    const [rankingData, setRankingData] = useState([]); // APIからのレスポンス
    const [isRankingView, setIsRankingView] = useState(true); // ランキング表示ページであるフラグ
    const [selectedUser, setSelectedUser] = useState(null); // ランダムに選ばれた5人の中のユーザー

    // ranking_dataの取得
    const fetchRanking = async () => {
        try {
            // FlaskのAPIサーバへリクエストを送ってレスポンスを取得
            const response = await fetch("http://localhost:5000/GetRanking", {
                method: "GET",
            });

            const data = await response.json(); // JSONレスポンスを受け取る
            const ranking_data = data.ranking || []; // ranking_dataを取得
            setRankingData(ranking_data);
        } catch (err) {
            console.error("取得失敗:", err);
        }
    };

    // 5秒ごとにデータを更新するようにする
    useEffect(() => {
        fetchRanking();
        const interval = setInterval(fetchRanking, 5000);
        return () => clearInterval(interval);
    }, []);

    // 10秒ごとにページを切り替える設定
    useEffect(() => {
        const switchInterval = setInterval(() => {
            setIsRankingView((prev) => !prev);
        }, 10000);
        return () => clearInterval(switchInterval);
    }, []);

    // 5名の中からランダムに1人ユーザーを選出
    useEffect(() => {
        if (!isRankingView && rankingData.length > 0) {
            const randomIndex = Math.floor(Math.random() * rankingData.length);
            setSelectedUser(rankingData[randomIndex]);
        }
    }, [isRankingView]);

    return (
        <div>
            {isRankingView ? (
                <RankingPage ranking={rankingData} />
            ) : (
                <UserFishPage user={selectedUser} />
            )}
        </div>
    );
}

export default MainDisplay;