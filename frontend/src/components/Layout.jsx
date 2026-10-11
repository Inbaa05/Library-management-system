import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  BookOpen, 
  MessageSquare, 
  LayoutDashboard, 
  ShieldCheck, 
  FileText, 
  PlusCircle, 
  User, 
  LogOut, 
  LogIn,
  Sliders
} from 'lucide-react';

const Layout = ({ children }) => {
  const { user, isAuthenticated, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="app-container" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--color-bg)' }}>
      {/* Top Navbar */}
      <header style={{ backgroundColor: '#ffffff', borderBottom: '1px solid var(--color-border)', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none', color: 'var(--color-navy)', fontWeight: 700, fontSize: '1.15rem' }}>
            <BookOpen size={24} color="var(--color-emerald)" />
            <span>LibraryOpt</span>
          </Link>

          <nav style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <NavLink to="/feedback" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--color-emerald)' : 'var(--color-navy)', fontWeight: 500 })}>
              Explore Feedback
            </NavLink>
            <NavLink to="/books" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--color-emerald)' : 'var(--color-navy)', fontWeight: 500 })}>
              Books
            </NavLink>
            <NavLink to="/comment-optimizer" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--color-emerald)' : 'var(--color-navy)', fontWeight: 500 })}>
              Pipeline
            </NavLink>

            {isAuthenticated ? (
              <>
                <NavLink to="/student/submit" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--color-emerald)' : 'var(--color-navy)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px' })}>
                  <PlusCircle size={16} /> Submit
                </NavLink>

                {hasRole(['librarian', 'admin']) && (
                  <>
                    <NavLink to="/librarian/dashboard" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--color-emerald)' : 'var(--color-navy)', fontWeight: 500 })}>
                      Dashboard
                    </NavLink>
                    <NavLink to="/librarian/moderation" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--color-emerald)' : 'var(--color-navy)', fontWeight: 500 })}>
                      Moderation
                    </NavLink>
                    <NavLink to="/librarian/reports" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--color-emerald)' : 'var(--color-navy)', fontWeight: 500 })}>
                      Reports
                    </NavLink>
                  </>
                )}

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: '10px' }}>
                  <NavLink to="/student/profile" style={{ display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none', color: 'var(--color-navy)' }}>
                    <User size={18} />
                    <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{user?.name || 'Profile'}</span>
                  </NavLink>
                  <button onClick={handleLogout} className="btn-ghost" style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '6px 10px', fontSize: '0.85rem' }}>
                    <LogOut size={16} /> Logout
                  </button>
                </div>
              </>
            ) : (
              <div style={{ display: 'flex', gap: '10px' }}>
                <Link to="/login" className="btn-secondary" style={{ textDecoration: 'none', padding: '6px 14px', fontSize: '0.9rem' }}>
                  Login
                </Link>
                <Link to="/register" className="btn-primary" style={{ textDecoration: 'none', padding: '6px 14px', fontSize: '0.9rem' }}>
                  Register
                </Link>
              </div>
            )}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ flex: 1, maxWidth: '1200px', width: '100%', margin: '0 auto', padding: '30px 20px' }}>
        {children}
      </main>

      {/* Footer */}
      <footer style={{ backgroundColor: '#ffffff', borderTop: '1px solid var(--color-border)', padding: '24px 20px', textAlign: 'center', fontSize: '0.875rem', color: '#6b7280' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <p>© 2026 Library Management Comment Optimization System. Academic PBL for Clean Coding & DevOps (IBM).</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
