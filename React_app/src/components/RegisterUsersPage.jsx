import { useState } from "react";
import { useNavigate } from "react-router-dom";

import "../styles/RegisterUsersPage.css";

function UserRegister() {
    const [username, setUsername] = useState(""); // ユーザー名
    const [registerLoading, setRegisterLoading] = useState(false); // 新規登録のローディング中フラグ
    const [loginLoading, setLoginLoading] = useState(false); // ログインのローディング中フラグ
    const [message, setMessage] = useState(""); // 成功・失敗時のメッセージ表示用
    const [alertType, setAlertType] = useState("info"); // アラートの表示用

    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();

        if(registerLoading || loginLoading) return; // ローディング中の重複送信を防ぐ

        setRegisterLoading(true); // ローディング開始

        if (!username.trim()) {
            setAlertType("danger");
            setMessage("⚠️ ユーザー名を入力してください");
            setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            setRegisterLoading(false);
            return;
        }

        if (username.length > 50) {
            setAlertType("danger");
            setMessage("⚠️ ユーザー名が長すぎます");
            setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            setRegisterLoading(false);
            return;
        }

        try {
            // FlaskのAPIサーバへPOSTリクエストを送ってレスポンスを取得
            // ユーザー新規登録のAPI
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
                setRegisterLoading(false);
                setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            } else if (data.error && data.error.includes("Duplicate")) {
                // ユーザー名の重複エラー
                setAlertType("danger");
                setMessage("⚠️ このユーザー名は既に存在しています");
                setRegisterLoading(false);
                setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            } else {
                // データベースへの追加エラー
                setAlertType("danger");
                setMessage("❌ ユーザーの追加に失敗しました");
                setRegisterLoading(false);
                setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            }
            } catch (error) {
            // データベースとの接続エラー
            setAlertType("danger");
            setMessage("❌ データベース接続エラー");
            setRegisterLoading(false);
            setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
        }
    };

    const handleLogin = async (e) => {
        e.preventDefault();

        if(registerLoading || loginLoading) return; // ローディング中の重複送信を防ぐ

        setLoginLoading(true); // ローディング開始

        if (!username.trim()) {
            setAlertType("danger");
            setMessage("⚠️ ユーザー名を入力してください");
            setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            setLoginLoading(false);
            return;
        }
        
        try {
            // FlaskのAPIサーバへGETパラメータを送ってレスポンスを取得
            // 2回目以降来た人用のloadedフラグを0に戻すAPI
            const response = await fetch(`http://localhost:5000/RestoreLoaded?username=${encodeURIComponent(username)}`, {
                method: "GET",
            });

            if (response.ok) {
                // loadedフラグを戻す処理が正常終了
                setAlertType("success");
                setMessage("✅ 登録に成功しました！");
                setLoginLoading(false);
                setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            } 
        } catch (error) {
            if (error.message.includes("not defined")){
                // ユーザーが存在しない場合のエラー
                setAlertType("danger");
                setMessage("⚠️ ユーザーが存在しません");
                setLoginLoading(false);
                setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
            }
            // データベースとの接続エラー
            setAlertType("danger");
            setMessage("❌ データベース接続エラー");
            setLoginLoading(false);
            setTimeout(() => setMessage(""), 5000); // 5秒間だけ表示
        }
    }

    return (
        <div className="register-container">
            <div className="logo-body">
                <img src="virtualfishing.png" alt="ロゴ" width="300" height="300"></img>
            </div>
            <div className="card shadow-sm register-card">
                <div className="card-body">
                    <h3 className="card-title text-center mb-4">ユーザー登録</h3>
                    <form>
                        <div className="mb-3">
                            <input
                                type="text"
                                className="form-control"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)} // ユーザー名をStateに入れる
                                placeholder="ユーザー名を入力"
                            />
                        </div>

                        {/* 新規登録の場合のボタン */}
                        <button
                            type="button"
                            className="btn btn-primary w-100 mb-2"
                            disabled={registerLoading}
                            onClick={handleRegister}
                        >
                            {registerLoading ? "処理中..." : "新規登録"}
                        </button>

                        {/* 既に登録済みの場合のボタン */}
                        <button
                            type="button"
                            className="btn btn-outline-primary w-100"
                            disabled={loginLoading}
                            onClick={handleLogin}
                        >
                            {loginLoading ? "処理中..." : "既に登録している方はこちら"}
                        </button>
                    </form>

                    {message && (
                        <div className={`alert alert-${alertType} mt-3 text-center`} role="alert">
                            {message}
                        </div>
                    )}
                </div>
            </div>
            <div className="play-body">
                <button className="play-button" onClick={() => navigate("/playing")}>
                    ひまつぶし
                </button>
            </div>
        </div>
    );
}

export default UserRegister;