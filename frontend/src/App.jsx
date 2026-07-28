import React, { useEffect, useMemo, useState } from 'react';

// Vite proxies these paths in development, avoiding browser cross-origin requests.
const AUTH_BASE_URL = '';
const CRUD_BASE_URL = '';

function App() {
  const [authMode, setAuthMode] = useState('login');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('user') || 'null'));
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [message, setMessage] = useState('');
  const [items, setItems] = useState([]);
  const [itemForm, setItemForm] = useState({ title: '', description: '' });
  const [editingId, setEditingId] = useState(null);

  const isLoggedIn = useMemo(() => Boolean(token), [token]);

  useEffect(() => {
    if (token) {
      fetchItems();
    }
  }, [token]);

  async function fetchItems() {
    const response = await fetch(`${CRUD_BASE_URL}/items`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const payload = await response.json();
    if (response.ok) {
      setItems(payload.items || []);
    }
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setMessage('');

    const endpoint = authMode === 'login' ? '/auth/login' : '/auth/register';
    const response = await fetch(`${AUTH_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    const payload = await response.json();

    if (!response.ok) {
      setMessage(payload.error || 'Authentication failed');
      return;
    }

    if (authMode === 'register') {
      setMessage('Registration successful. You can now log in.');
      setAuthMode('login');
      setForm({ name: '', email: '', password: '' });
      return;
    }

    setToken(payload.token);
    setUser(payload.user);
    localStorage.setItem('token', payload.token);
    localStorage.setItem('user', JSON.stringify(payload.user));
    setMessage('Login successful.');
    setForm({ name: '', email: '', password: '' });
  }

  async function handleCrudSubmit(event) {
    event.preventDefault();
    const payload = { title: itemForm.title, description: itemForm.description };

    const method = editingId ? 'PUT' : 'POST';
    const url = editingId
      ? `${CRUD_BASE_URL}/items/${editingId}`
      : `${CRUD_BASE_URL}/items`;

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok) {
      setMessage(result.error || 'Failed to save item');
      return;
    }

    setMessage(editingId ? 'Item updated.' : 'Item created.');
    setEditingId(null);
    setItemForm({ title: '', description: '' });
    fetchItems();
  }

  async function handleDelete(id) {
    const response = await fetch(`${CRUD_BASE_URL}/items/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      setMessage('Item deleted.');
      fetchItems();
    }
  }

  function startEdit(item) {
    setEditingId(item.id);
    setItemForm({ title: item.title, description: item.description });
  }

  function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken('');
    setUser(null);
    setItems([]);
    setMessage('Logged out successfully.');
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Microservice CRUD Demo</h1>
          <p>React frontend with Flask auth and CRUD services</p>
        </div>
        {isLoggedIn && (
          <button className="outline-btn" onClick={logout}>
            Logout
          </button>
        )}
      </header>

      {!isLoggedIn ? (
        <section className="card auth-card">
          <div className="auth-toggle">
            <button className={authMode === 'login' ? 'active' : ''} onClick={() => setAuthMode('login')}>
              Login
            </button>
            <button className={authMode === 'register' ? 'active' : ''} onClick={() => setAuthMode('register')}>
              Register
            </button>
          </div>

          <form onSubmit={handleAuthSubmit} className="form-grid">
            {authMode === 'register' && (
              <label>
                Name
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </label>
            )}
            <label>
              Email
              <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </label>
            <label>
              Password
              <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </label>
            <button type="submit">{authMode === 'login' ? 'Login' : 'Register'}</button>
          </form>
        </section>
      ) : (
        <section className="workspace-grid">
          <div className="card">
            <h2>Welcome, {user?.name || 'User'}</h2>
            <p>Use the form below to create or update records.</p>
            <form onSubmit={handleCrudSubmit} className="form-grid">
              <label>
                Title
                <input value={itemForm.title} onChange={(e) => setItemForm({ ...itemForm, title: e.target.value })} required />
              </label>
              <label>
                Description
                <textarea value={itemForm.description} onChange={(e) => setItemForm({ ...itemForm, description: e.target.value })} required />
              </label>
              <button type="submit">{editingId ? 'Update Item' : 'Create Item'}</button>
              {editingId && (
                <button type="button" className="outline-btn" onClick={() => {
                  setEditingId(null);
                  setItemForm({ title: '', description: '' });
                }}>
                  Cancel
                </button>
              )}
            </form>
          </div>

          <div className="card">
            <h2>Records</h2>
            <div className="items-list">
              {items.map((item) => (
                <div key={item.id} className="item-card">
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.description}</p>
                  </div>
                  <div className="item-actions">
                    <button className="outline-btn" onClick={() => startEdit(item)}>Edit</button>
                    <button className="danger-btn" onClick={() => handleDelete(item.id)}>Delete</button>
                  </div>
                </div>
              ))}
              {items.length === 0 && <p>No items yet.</p>}
            </div>
          </div>
        </section>
      )}

      {message && <div className="message">{message}</div>}
    </div>
  );
}

export default App;
