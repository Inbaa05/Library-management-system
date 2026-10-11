import React, { useEffect, useState } from 'react';
import { 
  getModerationQueueApi, 
  approveCommentApi, 
  flagCommentApi, 
  archiveCommentApi,
  getModerationHistoryApi 
} from '../api/moderation';
import StatusBadge from '../components/ui/StatusBadge';
import { useToast } from '../components/ui/Toast';
import { Check, Flag, Archive, History, Search } from 'lucide-react';

const ModerationPage = () => {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [history, setHistory] = useState([]);

  const { showSuccess, showError } = useToast();

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const res = await getModerationQueueApi({
        page,
        per_page: 10,
        status: statusFilter || undefined,
      });
      const data = res.data.data;
      setItems(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      showError('Failed to fetch moderation queue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [page, statusFilter]);

  const handleApprove = async (id) => {
    try {
      await approveCommentApi(id, 'Approved via Moderation Workspace');
      showSuccess(`Comment #${id} approved`);
      fetchQueue();
    } catch (err) {
      showError(err.response?.data?.error || 'Approve action failed');
    }
  };

  const handleFlag = async (id) => {
    const reason = window.prompt('Enter reason for flagging:');
    if (!reason) return;
    try {
      await flagCommentApi(id, reason);
      showSuccess(`Comment #${id} flagged`);
      fetchQueue();
    } catch (err) {
      showError(err.response?.data?.error || 'Flag action failed');
    }
  };

  const handleArchive = async (id) => {
    if (!window.confirm('Are you sure you want to archive this feedback?')) return;
    try {
      await archiveCommentApi(id, 'Archived by librarian');
      showSuccess(`Comment #${id} archived`);
      fetchQueue();
    } catch (err) {
      showError(err.response?.data?.error || 'Archive action failed');
    }
  };

  const viewHistory = async (comment) => {
    setSelectedItem(comment);
    try {
      const res = await getModerationHistoryApi(comment.id);
      setHistory(res.data.data);
    } catch (err) {
      setHistory([]);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '8px' }}>
          Comment Moderation Center
        </h1>
        <p style={{ color: '#6b7280' }}>
          Review pending submissions, inspect automated similarity and relevance tags, and audit decision logs.
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        {['', 'pending_review', 'near_duplicate', 'irrelevant', 'inappropriate'].map((st) => (
          <button
            key={st}
            onClick={() => { setStatusFilter(st); setPage(1); }}
            className={statusFilter === st ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '8px 14px', fontSize: '0.85rem', textTransform: 'capitalize' }}
          >
            {st ? st.replace('_', ' ') : 'All Needs Review'}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading moderation items...</div>
      ) : items.length === 0 ? (
        <div className="card" style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          Queue is clear. No comments currently pending moderation.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {items.map((item) => (
            <div key={item.id} className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#9ca3af' }}>#{item.id}</span>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-navy)', margin: '2px 0 0 0' }}>
                    {item.title}
                  </h3>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <StatusBadge status={item.status} />
                  <button onClick={() => viewHistory(item)} className="btn-ghost" title="Audit Log" style={{ padding: '6px' }}>
                    <History size={16} />
                  </button>
                </div>
              </div>

              <p style={{ color: '#4b5563', fontSize: '0.95rem', margin: '0 0 12px 0' }}>
                {item.comment_text}
              </p>

              {item.moderation_reason && (
                <div style={{ padding: '10px 14px', backgroundColor: '#fef2f2', borderRadius: '6px', color: '#b91c1c', fontSize: '0.85rem', marginBottom: '12px' }}>
                  <strong>Automated Flag:</strong> {item.moderation_reason}
                </div>
              )}

              {/* Actions */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--color-border)', paddingTop: '12px' }}>
                <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                  Category: <strong>{item.category_label || item.category}</strong> | Author: <strong>{item.author?.name || 'Student'}</strong>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button onClick={() => handleApprove(item.id)} className="btn-primary" style={{ padding: '6px 12px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Check size={14} /> Approve
                  </button>
                  <button onClick={() => handleFlag(item.id)} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Flag size={14} /> Flag
                  </button>
                  <button onClick={() => handleArchive(item.id)} className="btn-ghost" style={{ padding: '6px 12px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px', color: '#dc2626' }}>
                    <Archive size={14} /> Archive
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* History Modal / Drawer */}
      {selectedItem && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: '90%', maxWidth: '600px', maxHeight: '80vh', overflowY: 'auto', padding: '24px', backgroundColor: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>
                Audit History: #{selectedItem.id}
              </h3>
              <button onClick={() => setSelectedItem(null)} className="btn-ghost" style={{ padding: '4px 8px' }}>✕</button>
            </div>
            {history.length === 0 ? (
              <p style={{ color: '#6b7280' }}>No moderation actions logged yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {history.map((log) => (
                  <div key={log.id} style={{ padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.85rem' }}>
                    <div style={{ fontWeight: 600 }}>Action: {log.action} ({log.previous_status || 'none'} ➔ {log.new_status})</div>
                    <div style={{ color: '#4b5563', margin: '4px 0' }}>Reason: {log.reason || 'N/A'}</div>
                    <div style={{ color: '#9ca3af', fontSize: '0.75rem' }}>By: {log.moderator?.name} on {new Date(log.created_at).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModerationPage;
