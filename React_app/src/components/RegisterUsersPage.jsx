import React, { useState } from "react";

import "../styles/RegisterUsersPage.css";

function UserRegister() {
    const [username, setUsername] = useState(""); // ユーザー名
    const [message, setMessage] = useState(""); // 成功・失敗時のメッセージ表示用
    const [alertType, setAlertType] = useState("info"); // アラートの表示用

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!username.trim()) {
            setAlertType("danger");
            setMessage("⚠️ ユーザー名を入力してください");
            setTimeout(() => setMessage(""), 3000); // 3秒間だけ表示
            return;
        }

        if (username.length > 50) {
            setAlertType("danger");
            setMessage("⚠️ ユーザー名が長すぎます");
            setTimeout(() => setMessage(""), 3000); // 3秒間だけ表示
            return;
        }

        try {
            // FlaskのAPIサーバへリクエストを送ってレスポンスを取得
            const response = await fetch("http://localhost:5000/Add", {
                method: "POST",
                headers: { "Content-Type": "application/json" }, // JSONファイルをPOSTで送る
                body: JSON.stringify({ name: username }), // FlaskのAPIサーバのフィールド名に合わせる
            });

            const data = await response.json(); // JSONを取得

            if (response.ok && data.success) {
                // データベースへの登録成功
                setAlertType("success");
                setMessage("✅ 登録に成功しました！");
                setTimeout(() => setMessage(""), 3000); // 3秒間だけ表示
            } else if (data.error && data.error.includes("UNIQUE")) {
                // ユーザー名の重複エラー
                setAlertType("danger");
                setMessage("⚠️ このユーザ名は既に存在します。");
                setTimeout(() => setMessage(""), 3000); // 3秒間だけ表示
            } else {
                // データベースへの追加エラー
                setAlertType("danger");
                setMessage("❌ エラー: " + data.error);
                setTimeout(() => setMessage(""), 3000); // 3秒間だけ表示
            }
            } catch (error) {
            // データベースとの接続エラー
            setAlertType("danger");
            setMessage("❌ データベース接続エラー");
            setTimeout(() => setMessage(""), 3000); // 3秒間だけ表示
        }
    };

    return (
        <div className="register-container">
        <div className="card shadow-sm register-card">
            <div className="card-body">
            <h3 className="card-title text-center mb-4">ユーザー登録</h3>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                <label className="form-label">ユーザー名</label>
                <input
                    type="text"
                    className="form-control"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)} // ユーザー名をStateに入れる
                    placeholder="ユーザー名を入力"
                />
                </div>
                <button type="submit" className="btn btn-primary w-100">
                登録
                </button>
            </form>

            {message && (
                <div
                className={`alert alert-${alertType} mt-3 text-center`}
                role="alert"
                >
                {message}
                </div>
            )}
            </div>
        </div>
        </div>
    );
}

export default UserRegister;