import React, { useEffect, useState } from 'react';
import { 
  getDashboardSummaryApi, 
  getDashboardTrendsApi, 
  getDashboardCategoriesApi, 
  getDashboardInsightsApi 
} from '../api/dashboard';
import { 
  MessageSquare, 
  CheckCircle2, 
  Clock, 
  Copy, 
  AlertTriangle, 
  ShieldAlert, 
  Star, 
  Users 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

const LibrarianDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllDashboardData = async () => {
      setLoading(true);
      try {
        const [sumRes, trendRes, catRes, insRes] = await Promise.all([
          getDashboardSummaryApi(),
          getDashboardTrendsApi(30),
          getDashboardCategoriesApi(),
          getDashboardInsightsApi()
        ]);
        setSummary(sumRes.data.data);
        setTrends(trendRes.data.data);
        setCategories(catRes.data.data);
        setInsights(insRes.data.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAllDashboardData();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '60px' }}>Loading librarian insights...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      <div>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '8px' }}>
          Librarian Decision Dashboard
        </h1>
        <p style={{ color: '#6b7280' }}>
          Real-time metrics, automated moderation telemetry, and student feedback distribution.
        </p>
      </div>

      {/* Summary KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#6b7280' }}>Total Feedback</span>
            <MessageSquare size={18} color="var(--color-navy)" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-navy)' }}>{summary?.total_comments || 0}</div>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#047857' }}>Approved</span>
            <CheckCircle2 size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#047857' }}>{summary?.approved || 0}</div>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#b45309' }}>Pending Review</span>
            <Clock size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#b45309' }}>{summary?.pending_review || 0}</div>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#1d4ed8' }}>Duplicates</span>
            <Copy size={18} color="#3b82f6" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1d4ed8' }}>
            {(summary?.duplicate || 0) + (summary?.near_duplicate || 0)}
          </div>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#b91c1c' }}>Flagged Content</span>
            <ShieldAlert size={18} color="#ef4444" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#b91c1c' }}>
            {(summary?.irrelevant || 0) + (summary?.inappropriate || 0)}
          </div>
        </div>
      </div>

      {/* Visual Analytics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '24px' }}>
        <div className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '20px' }}>Submission Volume Over Time</h3>
          <div style={{ width: '100%', height: 260 }}>
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="var(--color-emerald)" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#9ca3af' }}>No trend data recorded</div>
            )}
          </div>
        </div>

        <div className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '20px' }}>Feedback by Category</h3>
          <div style={{ width: '100%', height: 260 }}>
            {categories.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categories}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="label" fontSize={11} interval={0} angle={-15} textAnchor="end" height={50} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--color-navy)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#9ca3af' }}>No category metrics recorded</div>
            )}
          </div>
        </div>
      </div>

      {/* Actionable Insights */}
      {insights && (
        <div className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px' }}>Top Frequently Requested Improvements</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {insights.top_feedback_categories?.map((c) => (
              <div key={c.category} style={{ padding: '14px', borderRadius: '8px', backgroundColor: '#f9fafb', border: '1px solid var(--color-border)' }}>
                <div style={{ fontWeight: 600, color: 'var(--color-navy)' }}>{c.label}</div>
                <div style={{ fontSize: '0.85rem', color: '#6b7280', marginTop: '4px' }}>{c.count} approved submissions</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LibrarianDashboard;
