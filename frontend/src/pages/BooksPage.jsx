import React, { useEffect, useState } from 'react';
import { getBooksApi } from '../api/books';
import { BookOpen, Star, Search } from 'lucide-react';
import { Link } from 'react-router-dom';

const BooksPage = () => {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const res = await getBooksApi({ search: search.trim() || undefined });
      setBooks(res.data.data.items);
    } catch (err) {
      console.error('Failed to load books:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchBooks();
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '8px' }}>
          Library Catalog & Reviews
        </h1>
        <p style={{ color: '#6b7280' }}>
          Discover available reading material, explore peer reviews, and submit ratings.
        </p>
      </div>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', maxWidth: '500px', marginBottom: '30px' }}>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by title, author, or genre..."
          style={{ flex: 1, padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem' }}
        />
        <button type="submit" className="btn-primary" style={{ padding: '10px 18px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Search size={16} /> Search
        </button>
      </form>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading books catalog...</div>
      ) : books.length === 0 ? (
        <div className="card" style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          No books found in catalog.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
          {books.map((b) => (
            <Link key={b.id} to={`/books/${b.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
              <div className="card" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, padding: '2px 8px', borderRadius: '4px', backgroundColor: '#f3f4f6', color: '#4b5563' }}>
                      {b.genre || 'General'}
                    </span>
                    {b.average_rating ? (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '3px', fontSize: '0.85rem', fontWeight: 700, color: '#f59e0b' }}>
                        <Star size={14} fill="#f59e0b" /> {b.average_rating}
                      </span>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>No ratings</span>
                    )}
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '4px' }}>
                    {b.title}
                  </h3>
                  <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '12px' }}>
                    by {b.author}
                  </p>
                  <p style={{ fontSize: '0.85rem', color: '#4b5563', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {b.description || 'No description provided.'}
                  </p>
                </div>
                <div style={{ marginTop: '16px', fontSize: '0.75rem', color: 'var(--color-emerald)', fontWeight: 600 }}>
                  {b.review_count} {b.review_count === 1 ? 'review' : 'reviews'} →
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default BooksPage;
