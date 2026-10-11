import React, { useEffect, useState } from 'react';
import { getCommentsApi } from '../api/comments';
import StatusBadge from '../components/ui/StatusBadge';
import { Search, Filter, RotateCcw, Calendar, Star } from 'lucide-react';

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'book_suggestion', label: 'Book Suggestion' },
  { value: 'book_review', label: 'Book Review' },
  { value: 'library_facility', label: 'Library Facility' },
  { value: 'library_service', label: 'Library Service' },
  { value: 'wifi_digital', label: 'Wi-Fi & Digital' },
  { value: 'reading_recommendation', label: 'Reading Recommendation' },
  { value: 'general_feedback', label: 'General Feedback' },
];

const FeedbackExplorer = () => {
  const [comments, setComments] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  const fetchComments = async () => {
    setLoading(true);
    try {
      const res = await getCommentsApi({
        page,
        per_page: 10,
        search: search.trim() || undefined,
        category: category || undefined,
        status: status || undefined,
        sort_by: sortBy,
      });
      const data = res.data.data;
      setComments(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      console.error('Error fetching comments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [page, category, status, sortBy]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchComments();
  };

  const clearFilters = () => {
    setSearch('');
    setCategory('');
    setStatus('');
    setSortBy('newest');
    setPage(1);
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '8px' }}>
          Feedback Explorer
        </h1>
        <p style={{ color: '#6b7280' }}>
          Browse, search, and filter verified community feedback and reviews across library categories.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 240px', position: 'relative' }}>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search feedback titles or keywords..."
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem' }}
            />
          </div>

          <select
            value={category}
            onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            style={{ padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem', backgroundColor: '#fff' }}
          >
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
            style={{ padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem', backgroundColor: '#fff' }}
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="rating">Highest Rating</option>
          </select>

          <button type="submit" className="btn-primary" style={{ padding: '10px 16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Search size={16} /> Search
          </button>

          <button type="button" onClick={clearFilters} className="btn-ghost" style={{ padding: '10px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <RotateCcw size={16} /> Reset
          </button>
        </form>
      </div>

      {/* Results List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading feedback entries...</div>
      ) : comments.length === 0 ? (
        <div className="card" style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          <p style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '6px' }}>No feedback entries found</p>
          <p style={{ fontSize: '0.875rem' }}>Try clearing filters or refining search terms.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {comments.map((c) => (
            <div key={c.id} className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px', gap: '12px' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: 'var(--color-navy)' }}>
                  {c.title}
                </h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <StatusBadge status={c.status} />
                </div>
              </div>

              <p style={{ color: '#4b5563', fontSize: '0.95rem', lineHeight: 1.5, margin: '0 0 14px 0' }}>
                {c.comment_text}
              </p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.8rem', color: '#6b7280', borderTop: '1px solid var(--color-border)', paddingTop: '12px' }}>
                <span><strong>Category:</strong> {c.category_label || c.category}</span>
                {c.book_title && <span><strong>Book:</strong> {c.book_title}</span>}
                {c.rating && <span><strong>Rating:</strong> {c.rating} ★</span>}
                {c.facility && <span><strong>Facility:</strong> {c.facility}</span>}
                <span><strong>Submitted:</strong> {new Date(c.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}

          {/* Pagination Controls */}
          {pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '20px' }}>
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="btn-secondary"
                style={{ padding: '8px 16px' }}
              >
                Previous
              </button>
              <span style={{ display: 'flex', alignItems: 'center', fontSize: '0.9rem', fontWeight: 600 }}>
                Page {page} of {pages}
              </span>
              <button
                disabled={page >= pages}
                onClick={() => setPage(page + 1)}
                className="btn-secondary"
                style={{ padding: '8px 16px' }}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FeedbackExplorer;
