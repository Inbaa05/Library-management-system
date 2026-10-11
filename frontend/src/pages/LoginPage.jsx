import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { loginApi } from '../api/auth';
import { Lock, Mail, AlertCircle } from 'lucide-react';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await loginApi(email, password);
      const { token, user } = res.data.data;
      login(token, user);

      if (user.role === 'librarian' || user.role === 'admin') {
        navigate('/librarian/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '420px', margin: '40px auto', padding: '30px', backgroundColor: '#fff', borderRadius: '12px', border: '1px solid var(--color-border)', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, textAlign: 'center', marginBottom: '8px', color: 'var(--color-navy)' }}>
        Sign In
      </h2>
      <p style={{ textAlign: 'center', color: '#6b7280', fontSize: '0.875rem', marginBottom: '24px' }}>
        Access your library feedback account
      </p>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: '6px', backgroundColor: '#fef2f2', color: '#b91c1c', fontSize: '0.875rem', marginBottom: '16px' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '6px', color: 'var(--color-navy)' }}>
            Email Address
          </label>
          <div style={{ position: 'relative' }}>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. student@library.edu"
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem' }}
            />
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '6px', color: 'var(--color-navy)' }}>
            Password
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem' }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary"
          style={{ padding: '12px', fontSize: '1rem', marginTop: '8px' }}
        >
          {loading ? 'Authenticating...' : 'Sign In'}
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '0.875rem', color: '#6b7280' }}>
        Don't have an account?{' '}
        <Link to="/register" style={{ color: 'var(--color-emerald)', fontWeight: 600, textDecoration: 'none' }}>
          Register here
        </Link>
      </div>

      <div style={{ marginTop: '24px', padding: '12px', borderRadius: '6px', backgroundColor: '#f9fafb', fontSize: '0.75rem', color: '#6b7280' }}>
        <strong>Dev credentials:</strong><br />
        Librarian: <code>librarian@library.edu</code> / <code>Librarian@2024</code><br />
        Student: <code>student@library.edu</code> / <code>Student@2024</code>
      </div>
    </div>
  );
};

export default LoginPage;
