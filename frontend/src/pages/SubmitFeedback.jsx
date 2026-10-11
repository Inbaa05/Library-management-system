import React, { useState } from 'react';
import { submitCommentApi } from '../api/comments';
import { useToast } from '../components/ui/Toast';
import StatusBadge from '../components/ui/StatusBadge';
import { CheckCircle2, AlertTriangle, Send } from 'lucide-react';

const CATEGORIES = [
  { value: 'book_suggestion', label: 'Book Suggestion' },
  { value: 'book_review', label: 'Book Review' },
  { value: 'library_facility', label: 'Library Facility' },
  { value: 'library_service', label: 'Library Service' },
  { value: 'wifi_digital', label: 'Wi-Fi & Digital Facilities' },
  { value: 'reading_recommendation', label: 'Reading Recommendation' },
  { value: 'general_feedback', label: 'General Feedback' },
];

const SubmitFeedback = () => {
  const [title, setTitle] = useState('');
  const [commentText, setCommentText] = useState('');
  const [category, setCategory] = useState('general_feedback');
  const [bookTitle, setBookTitle] = useState('');
  const [rating, setRating] = useState('');
  const [facility, setFacility] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const { showSuccess, showError } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !commentText.trim()) {
      showError('Please provide a title and feedback description.');
      return;
    }

    setSubmitting(true);
    setResult(null);

    try {
      const payload = {
        title: title.trim(),
        comment_text: commentText.trim(),
        category,
        book_title: bookTitle.trim() || undefined,
        rating: rating ? parseInt(rating, 10) : undefined,
        facility: facility.trim() || undefined,
      };

      const res = await submitCommentApi(payload);
      const data = res.data.data;
      setResult(data);

      if (data.status === 'approved') {
        showSuccess('Feedback submitted and approved!');
      } else if (data.status === 'duplicate') {
        showError('Duplicate feedback detected.');
      } else if (data.is_flagged) {
        showError(`Feedback flagged: ${data.moderation_reason || 'Requires review'}`);
      } else {
        showSuccess('Feedback queued for librarian review.');
      }

      // Reset form fields
      setTitle('');
      setCommentText('');
      setBookTitle('');
      setRating('');
      setFacility('');
    } catch (err) {
      showError(err.response?.data?.error || 'Failed to submit feedback.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '8px' }}>
          Submit Library Feedback
        </h1>
        <p style={{ color: '#6b7280' }}>
          Your input is automatically processed through our optimization pipeline to help improve library resources and services.
        </p>
      </div>

      {result && (
        <div style={{ padding: '20px', borderRadius: '8px', border: '1px solid var(--color-border)', backgroundColor: '#fff', marginBottom: '24px', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h4 style={{ fontWeight: 700, margin: 0 }}>Server Processing Outcome:</h4>
            <StatusBadge status={result.status} />
          </div>
          <p style={{ margin: '0 0 8px 0', fontSize: '0.95rem' }}><strong>Title:</strong> {result.title}</p>
          <p style={{ margin: '0 0 8px 0', fontSize: '0.95rem' }}><strong>Assigned Category:</strong> {result.category_label || result.category}</p>
          {result.moderation_reason && (
            <p style={{ margin: '0', fontSize: '0.9rem', color: '#b91c1c' }}>
              <strong>Moderation Note:</strong> {result.moderation_reason}
            </p>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="card" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '6px', color: 'var(--color-navy)' }}>
            Feedback Title *
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Additional study chairs needed on 2nd floor"
            style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '6px', color: 'var(--color-navy)' }}>
            Category
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem', backgroundColor: '#fff' }}
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-navy)' }}>
              Feedback Description *
            </label>
            <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
              {commentText.length} characters (min 10)
            </span>
          </div>
          <textarea
            required
            rows={5}
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            placeholder="Provide clear details regarding your suggestion, review, or facility concern..."
            style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem', resize: 'vertical' }}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '6px', color: 'var(--color-navy)' }}>
              Book Title (Optional)
            </label>
            <input
              type="text"
              value={bookTitle}
              onChange={(e) => setBookTitle(e.target.value)}
              placeholder="e.g. Clean Code"
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '6px', color: 'var(--color-navy)' }}>
              Rating (Optional)
            </label>
            <select
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem', backgroundColor: '#fff' }}
            >
              <option value="">No rating</option>
              <option value="5">★★★★★ (5 - Excellent)</option>
              <option value="4">★★★★☆ (4 - Good)</option>
              <option value="3">★★★☆☆ (3 - Average)</option>
              <option value="2">★★☆☆☆ (2 - Poor)</option>
              <option value="1">★☆☆☆☆ (1 - Very Bad)</option>
            </select>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '6px', color: 'var(--color-navy)' }}>
            Facility / Area (Optional)
          </label>
          <input
            type="text"
            value={facility}
            onChange={(e) => setFacility(e.target.value)}
            placeholder="e.g. 2nd Floor Study Hall, Wi-Fi Zone"
            style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.95rem' }}
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="btn-primary"
          style={{ padding: '12px 20px', fontSize: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
        >
          <Send size={18} />
          {submitting ? 'Running Pipeline Analysis...' : 'Submit Feedback'}
        </button>
      </form>
    </div>
  );
};

export default SubmitFeedback;
