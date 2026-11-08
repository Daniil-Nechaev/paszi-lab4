import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import AuthPage from './pages/AuthPage';
import FridgePage from './pages/FridgePage';
import { setUserIdHeader } from './api/api';

export default function App() {
  const [userId, setUserId] = useState<number | null>(() => {
    const saved = localStorage.getItem('userId');
    return saved ? parseInt(saved) : null;
  });

  useEffect(() => {
    if (userId) {
      localStorage.setItem('userId', userId.toString());
      setUserIdHeader(userId);
    } else {
      localStorage.removeItem('userId');
    }
  }, [userId]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/register" element={<AuthPage onLogin={setUserId} />} />
        <Route path="/fridge" element={userId ? <FridgePage userId={userId} /> : <Navigate to="/register" replace />} />
        <Route path="/" element={<Navigate to="/register" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
