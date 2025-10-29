import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import "../styles/PlayingPage.css";

// スライドパズルのミニゲーム

const SIZE = 3; // 3x3

function shuffleArray(arr) {
    const copy = [...arr];
    for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
    }

    return copy;
}

function isSolvable(puzzle) {
    // 3x3 の場合、逆順数が偶数なら解ける
    const invCount = puzzle
        .filter((n) => n !== 0)
        .reduce((count, curr, i, arr) => {
        return (
            count +
            arr.slice(i + 1).filter((next) => next < curr && next !== 0).length
        );
        }, 0);
    return invCount % 2 === 0;
}

function PlayingPage() {
    const [tiles, setTiles] = useState([]);
    const [moves, setMoves] = useState(0);
    const [won, setWon] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        resetGame();
    }, []);

    const resetGame = () => {
        let newTiles;
        do {
        newTiles = shuffleArray([...Array(SIZE * SIZE).keys()]);
        } while (!isSolvable(newTiles));
        setTiles(newTiles);
        setMoves(0);
        setWon(false);
    };

    const handleClick = (index) => {
        if (won) return;
        const emptyIndex = tiles.indexOf(0);
        const row = Math.floor(index / SIZE);
        const col = index % SIZE;
        const emptyRow = Math.floor(emptyIndex / SIZE);
        const emptyCol = emptyIndex % SIZE;

        const isAdjacent =
        (Math.abs(row - emptyRow) === 1 && col === emptyCol) ||
        (Math.abs(col - emptyCol) === 1 && row === emptyRow);

        if (isAdjacent) {
        const newTiles = [...tiles];
        [newTiles[index], newTiles[emptyIndex]] = [newTiles[emptyIndex], newTiles[index]];
        setTiles(newTiles);
        setMoves(moves + 1);

        if (newTiles.slice(0, -1).every((t, i) => t === i + 1) && newTiles[newTiles.length - 1] === 0) {
            setWon(true);
        }
        }
    };

    return (
        <div className="puzzle-container">
            <h2>スライドパズル</h2>
            <p>{won ? "🎉 完成！おめでとう！" : `手数：${moves}`}</p>

            <div
                className="puzzle-grid"
                style={{
                gridTemplateColumns: `repeat(${SIZE}, 100px)`,
                }}
            >
                {tiles.map((num, i) => (
                <div
                    key={i}
                    onClick={() => handleClick(i)}
                    className={`puzzle-tile ${num === 0 ? "empty" : ""}`}
                >
                    {num !== 0 && num}
                </div>
                ))}
            </div>

            <button className="puzzle-button" onClick={resetGame}>
                {won ? "リプレイ" : "リセット"}
            </button>
            <button className="return-button" onClick={() => navigate("/register")}>
                戻る
            </button>
        </div>
    );
}

export default PlayingPage;