import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { resourceApi, setUserIdHeader } from '../api/api';

export default function FridgePage({ userId }: { userId: number }) {
  const [resources, setResources] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newExpires, setNewExpires] = useState('');
  const [showPermModal, setShowPermModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [targetResourceId, setTargetResourceId] = useState<number | null>(null);
  const [targetUserId, setTargetUserId] = useState('');
  const [permRead, setPermRead] = useState(false);
  const [permUpdate, setPermUpdate] = useState(false);
  const [permDelete, setPermDelete] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editExpires, setEditExpires] = useState('');
  const navigate = useNavigate();

  const loadResources = async () => {
    try {
      const response = await resourceApi.getResources();
      setResources(response.data);
      setError('');
    } catch (err: any) {
      setError('Не удалось загрузить продукты');
    }
  };

  useEffect(() => {
    setUserIdHeader(userId);
    loadResources();
  }, [userId]);

  const handleLogout = () => {
    localStorage.removeItem('userId');
    setUserIdHeader(null);
    navigate('/register');
  };

  const handleAddResource = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await resourceApi.createResource({ title: newTitle, description: newDesc, expires_at: newExpires });
      setSuccess('Продукт добавлен!');
      setNewTitle('');
      setNewDesc('');
      setNewExpires('');
      loadResources();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при добавлении');
    }
  };

  const openEditModal = (res: any) => {
    setTargetResourceId(res.id);
    setEditTitle(res.title);
    setEditDesc(res.description);
    setEditExpires(res.expires_at || '');
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!targetResourceId) return;
    try {
      await resourceApi.updateResource(targetResourceId, { title: editTitle, description: editDesc, expires_at: editExpires });
      setSuccess('Продукт изменён!');
      setShowEditModal(false);
      loadResources();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при изменении');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Точно удалить?')) return;
    try {
      await resourceApi.deleteResource(id);
      setSuccess('Продукт удалён!');
      loadResources();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Нет прав на удаление (403)');
    }
  };

  const openPermModal = (resourceId: number) => {
    setTargetResourceId(resourceId);
    setTargetUserId('');
    setPermRead(false);
    setPermUpdate(false);
    setPermDelete(false);
    setShowPermModal(true);
  };

  const handleSavePermissions = async () => {
    if (!targetResourceId || !targetUserId) return;
    try {
      await resourceApi.setPermissions(targetResourceId, parseInt(targetUserId), {
        can_read: permRead,
        can_update: permUpdate,
        can_delete: permDelete,
      });
      setSuccess('Права выданы!');
      setShowPermModal(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при выдаче прав');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <h1 style={{ margin: 0, fontSize: '32px', whiteSpace: 'nowrap' }}>🧊 Общий холодильник</h1>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ background: '#e0e7ff', padding: '8px 16px', borderRadius: '8px', whiteSpace: 'nowrap' }}>
            Твой User ID: <strong>{userId}</strong>
          </div>
          <button onClick={handleLogout} style={{ padding: '8px 16px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Выйти
          </button>
        </div>
      </div>

      {error && <div style={{ color: 'red', background: '#ffe6e6', padding: '10px', borderRadius: '4px', marginBottom: '15px' }}>{error}</div>}
      {success && <div style={{ color: 'green', background: '#e6ffe6', padding: '10px', borderRadius: '4px', marginBottom: '15px' }}>{success}</div>}

      <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <h3>Положить продукт в холодильник</h3>
        <form onSubmit={handleAddResource} style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <input placeholder="Название (напр. Пицца)" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} required style={{ padding: '8px', flex: '1', minWidth: '150px' }} />
          <input placeholder="Описание (напр. 4 куска)" value={newDesc} onChange={(e) => setNewDesc(e.target.value)} required style={{ padding: '8px', flex: '1', minWidth: '150px' }} />
          <input placeholder="Срок (напр. До завтра)" value={newExpires} onChange={(e) => setNewExpires(e.target.value)} style={{ padding: '8px', flex: '1', minWidth: '150px' }} />
          <button type="submit" style={{ padding: '8px 16px', background: '#863bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Добавить</button>
        </form>
      </div>

      <h3>Содержимое холодильника</h3>
      {resources.length === 0 ? (
        <p>Холодильник пуст. Добавь что-нибудь!</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {resources.map((res) => (
            <div key={res.id} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', background: res.is_owner ? '#f0fdf4' : '#fff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                <div style={{ flex: '1', minWidth: '200px' }}>
                  <h4 style={{ margin: '0 0 5px 0' }}>{res.title} {res.is_owner && '👑 (Твоё)'}</h4>
                  <p style={{ margin: '0 0 5px 0', color: '#555' }}>{res.description}</p>
                  <small style={{ color: '#888' }}>Срок: {res.expires_at || 'не указан'} | Владелец ID: {res.owner_id}</small>
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {res.is_owner && (
                    <button onClick={() => openPermModal(res.id)} style={{ padding: '6px 12px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>🔑 Права</button>
                  )}
                  {res.can_update && (
                    <button onClick={() => openEditModal(res)} style={{ padding: '6px 12px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>✏️ Изменить</button>
                  )}
                  {res.can_delete && (
                    <button onClick={() => handleDelete(res.id)} style={{ padding: '6px 12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>🗑️ Удалить</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showEditModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', width: '350px' }}>
            <h3>✏️ Изменить продукт</h3>
            <label style={{ display: 'block', marginBottom: '10px' }}>
              Название:
              <input type="text" value={editTitle} onChange={(e) => setEditTitle(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }} />
            </label>
            <label style={{ display: 'block', marginBottom: '10px' }}>
              Описание:
              <input type="text" value={editDesc} onChange={(e) => setEditDesc(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }} />
            </label>
            <label style={{ display: 'block', marginBottom: '15px' }}>
              Срок годности:
              <input type="text" value={editExpires} onChange={(e) => setEditExpires(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }} />
            </label>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowEditModal(false)} style={{ padding: '8px 12px', cursor: 'pointer' }}>Отмена</button>
              <button onClick={handleSaveEdit} style={{ padding: '8px 12px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Сохранить</button>
            </div>
          </div>
        </div>
      )}

      {showPermModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', width: '300px' }}>
            <h3>🔑 Выдача прав (DAC)</h3>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '15px' }}>Укажи ID пользователя, которому хочешь дать доступ.</p>
            <label style={{ display: 'block', marginBottom: '10px' }}>
              ID пользователя (напр. 2):
              <input type="number" value={targetUserId} onChange={(e) => setTargetUserId(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }} />
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <input type="checkbox" checked={permRead} onChange={(e) => setPermRead(e.target.checked)} /> can_read (видеть)
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <input type="checkbox" checked={permUpdate} onChange={(e) => setPermUpdate(e.target.checked)} /> can_update (редактировать)
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
              <input type="checkbox" checked={permDelete} onChange={(e) => setPermDelete(e.target.checked)} /> can_delete (удалять)
            </label>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowPermModal(false)} style={{ padding: '8px 12px', cursor: 'pointer' }}>Отмена</button>
              <button onClick={handleSavePermissions} style={{ padding: '8px 12px', background: '#863bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Сохранить права</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
