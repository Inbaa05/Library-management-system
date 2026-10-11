import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px' }}>
      <h1 style={{ fontSize: '4rem', fontWeight: 900, color: 'var(--color-navy)', marginBottom: '10px' }}>
        404
      </h1>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '12px' }}>
        Page Not Found
      </h2>
      <p style={{ color: '#6b7280', maxWidth: '400px', margin: '0 auto 24px' }}>
        The library resource or page you requested could not be located.
      </p>
      <Link to="/" className="btn-primary" style={{ padding: '10px 20px', textDecoration: 'none' }}>
        Back to Home
      </Link>
    </div>
  );
};

export default NotFoundPage;
