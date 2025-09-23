import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";

import '../styles/App.css'

import RegisterUsersPage from './RegisterUsersPage';
import RankingPage from './RankingPage';

function App() {
  return (
    <Router>
      <nav>
        <Link to="/register">ユーザー登録画面</Link> | 
        <Link to="/ranking">ランキング表示画面</Link>
      </nav>
      <Routes>
        <Route path="/register" element={<RegisterUsersPage />} />
        <Route path="/ranking" element={<RankingPage />} />
      </Routes>
    </Router>
  );
}

export default App