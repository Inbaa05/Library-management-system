import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getCommentsApi } from '../api/comments';
import StatusBadge from '../components/ui/StatusBadge';
import { Link } from 'react-router-dom';
import { PlusCircle, BookOpen, MessageSquare } from 'lucide-react';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMyComments = async () => {
      try {
        const res = await getCommentsApi({ per_page: 5 });
        setComments(res.data.data.items);
      } catch (err) {
        console.error('Error fetching submissions:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMyComments();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '6px' }}>
            Welcome back, {user?.name || 'Student'}!
          </h1>
          <p style={{ color: '#6b7280' }}>
            Track your submitted feedback, check review outcomes, and explore resources.
          </p>
        </div>
        <Link to="/student/submit" className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '10px 18px', textDecoration: 'none' }}>
          <PlusCircle size={16} /> Submit Feedback
        </Link>
      </div>

      {/* Quick shortcuts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        <Link to="/student/submit" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '6px', color: 'var(--color-navy)' }}>
              Propose a Book
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#6b7280', margin: 0 }}>
              Recommend new textbooks, research papers, or novels for acquisition.
            </p>
          </div>
        </Link>

        <Link to="/books" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '6px', color: 'var(--color-navy)' }}>
              Browse Catalog
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#6b7280', margin: 0 }}>
              View student reviews and average ratings for academic books.
            </p>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '16px' }}>
          Your Recent Feedback Submissions
        </h2>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>Loading your submissions...</div>
        ) : comments.length === 0 ? (
          <div className="card" style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
            <p style={{ fontWeight: 600, marginBottom: '6px' }}>You haven't submitted any feedback yet.</p>
            <p style={{ fontSize: '0.875rem' }}>Share suggestions about Wi-Fi, facilities, or book reviews to help improve our library!</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {comments.map((c) => (
              <div key={c.id} className="card" style={{ padding: '18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h4 style={{ margin: 0, fontWeight: 700, fontSize: '1.05rem', color: 'var(--color-navy)' }}>
                    {c.title}
                  </h4>
                  <StatusBadge status={c.status} />
                </div>
                <p style={{ color: '#4b5563', fontSize: '0.9rem', margin: '0 0 10px 0' }}>
                  {c.comment_text}
                </p>
                {c.moderation_reason && (
                  <div style={{ fontSize: '0.8rem', color: '#b91c1c', marginBottom: '8px' }}>
                    <strong>Note:</strong> {c.moderation_reason}
                  </div>
                )}
                <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                  Submitted on {new Date(c.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDashboard;
