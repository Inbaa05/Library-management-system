import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getBookApi, getBookReviewsApi, submitReviewApi } from '../api/books';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/ui/Toast';
import { Star, Send } from 'lucide-react';

const BookDetail = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const { showSuccess, showError } = useToast();

  const [book, setBook] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      const [bRes, rRes] = await Promise.all([
        getBookApi(id),
        getBookReviewsApi(id)
      ]);
      setBook(bRes.data.data);
      setReviews(rRes.data.data.items);
    } catch (err) {
      console.error('Error loading book detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await submitReviewApi(id, {
        rating: parseInt(rating, 10),
        review_text: reviewText.trim()
      });
      showSuccess('Review submitted successfully');
      setReviewText('');
      loadData();
    } catch (err) {
      showError(err.response?.data?.error || 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '60px' }}>Loading book information...</div>;
  if (!book) return <div style={{ textAlign: 'center', padding: '60px' }}>Book not found.</div>;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '30px' }}>
      <div className="card" style={{ padding: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, padding: '3px 8px', borderRadius: '4px', backgroundColor: '#f3f4f6', color: '#4b5563' }}>
              {book.genre || 'General'}
            </span>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', margin: '8px 0 4px 0' }}>
              {book.title}
            </h1>
            <p style={{ color: '#6b7280', fontSize: '1.05rem', margin: 0 }}>
              by {book.author}
            </p>
          </div>
          {book.average_rating && (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Star size={22} fill="#f59e0b" /> {book.average_rating}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{book.review_count} ratings</div>
            </div>
          )}
        </div>

        <p style={{ color: '#4b5563', lineHeight: 1.6, fontSize: '0.95rem' }}>
          {book.description || 'No overview available for this catalog record.'}
        </p>
      </div>

      {/* Review Submission */}
      {isAuthenticated && (
        <form onSubmit={handleSubmitReview} className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '14px' }}>Leave a Review</h3>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '12px' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: 600 }}>Star Rating:</label>
            <select
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', backgroundColor: '#fff' }}
            >
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>{n} Stars</option>
              ))}
            </select>
          </div>
          <textarea
            rows={3}
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            placeholder="Share your thoughts about this book with peers..."
            style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem', marginBottom: '12px', resize: 'vertical' }}
          />
          <button type="submit" disabled={submitting} className="btn-primary" style={{ padding: '8px 16px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Send size={14} /> Submit Review
          </button>
        </form>
      )}

      {/* Reviews List */}
      <div>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '16px' }}>
          Reader Feedback ({reviews.length})
        </h3>
        {reviews.length === 0 ? (
          <p style={{ color: '#6b7280' }}>No reviews submitted yet for this title.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {reviews.map((r) => (
              <div key={r.id} className="card" style={{ padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{r.reviewer?.name || 'Student'}</span>
                  <span style={{ color: '#f59e0b', fontSize: '0.85rem', fontWeight: 700 }}>
                    {'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}
                  </span>
                </div>
                <p style={{ color: '#4b5563', fontSize: '0.9rem', margin: '0 0 6px 0' }}>{r.review_text}</p>
                <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{new Date(r.created_at).toLocaleDateString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BookDetail;
