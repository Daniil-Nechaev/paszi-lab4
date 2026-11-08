import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, setUserIdHeader } from '../api/api';

interface AuthPageProps {
  onLogin: (id: number) => void;
}

export default function AuthPage({ onLogin }: AuthPageProps) {
  const [isLogin, setIsLogin] = useState(false);
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = isLogin 
        ? await authApi.login(login, password)
        : await authApi.register(login, password);
      
      const userId = response.data.id;
      setUserIdHeader(userId);
      onLogin(userId);
      navigate('/fridge');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '100px auto', padding: '20px', border: '1px solid #ddd', borderRadius: '8px', fontFamily: 'sans-serif' }}>
      <h1 style={{ textAlign: 'center' }}>🧊 {isLogin ? 'Вход' : 'Регистрация'}</h1>
      
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <button 
          onClick={() => { setIsLogin(false); setError(''); }}
          style={{ padding: '8px 16px', margin: '0 5px', background: !isLogin ? '#863bff' : '#fff', color: !isLogin ? '#fff' : '#333', border: '1px solid #863bff', borderRadius: '4px', cursor: 'pointer' }}
        >
          Регистрация
        </button>
        <button 
          onClick={() => { setIsLogin(true); setError(''); }}
          style={{ padding: '8px 16px', margin: '0 5px', background: isLogin ? '#863bff' : '#fff', color: isLogin ? '#fff' : '#333', border: '1px solid #863bff', borderRadius: '4px', cursor: 'pointer' }}
        >
          Вход
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Логин:</label>
          <input type="text" value={login} onChange={(e) => setLogin(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc', boxSizing: 'border-box' }} />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Пароль:</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc', boxSizing: 'border-box' }} />
        </div>
        {error && <div style={{ color: 'red', marginBottom: '15px', padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '4px' }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ width: '100%', padding: '10px', backgroundColor: loading ? '#ccc' : '#863bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px', fontWeight: 'bold' }}>
          {loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
        </button>
      </form>
    </div>
  );
}
