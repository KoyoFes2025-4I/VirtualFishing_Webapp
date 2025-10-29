import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";

import '../styles/App.css'

import RegisterUsersPage from './RegisterUsersPage';
import RankingPage from './RankingPage';
import PlayingPage from "./Playing";

function Nav() {
  const location = useLocation();
  // ルート("/")にいる時だけリンクを表示するようにする
  if (location.pathname !== "/") return null;

  return (
    <nav>
      <Link to="/register">User Register</Link> |                 
      <Link to="/ranking">Realtime Ranking</Link>
    </nav>
  );
}

// vite.config.jsで設定しているのでそれぞれのページは直接URLからもアクセス可能

function App() {
  return (
    <Router>
      <Nav />
      <Routes>
        <Route path="/" element={<h1>Home</h1>} />
        <Route path="/register" element={<RegisterUsersPage />} />
        <Route path="/ranking" element={<RankingPage />} />
        <Route path="/playing" element={<PlayingPage />} />
        <Route path="*" element={<h1>404 Not Found</h1>} />
      </Routes>
    </Router>
  );
}

export default App