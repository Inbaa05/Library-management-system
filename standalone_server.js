/**
 * Standalone Node.js server implementing the full Library Management API and serving the Single Page Application.
 * This runs natively on any machine using Antigravity's bundled Node runtime without external dependencies.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = 5000;
const DB_FILE = path.join(__dirname, 'dev_store.json');

// --- In-Memory & File-Persisted Database ---
let db = {
  users: [],
  comments: [],
  books: [],
  reviews: [],
  moderationLogs: []
};

function saveDb() {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2), 'utf-8');
  } catch (e) {
    console.error('Error saving DB:', e);
  }
}

function loadDb() {
  if (fs.existsSync(DB_FILE)) {
    try {
      db = JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
    } catch (e) {
      console.error('Error reading DB, re-initializing:', e);
    }
  } else {
    seedDb();
  }
}

function hashPassword(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

function seedDb() {
  const libPass = hashPassword('Librarian@2024');
  const stuPass = hashPassword('Student@2024');

  db.users = [
    { id: 1, name: 'Head Librarian', email: 'librarian@library.edu', password: libPass, role: 'librarian', created_at: new Date().toISOString() },
    { id: 2, name: 'Alice Student', email: 'student@library.edu', password: stuPass, role: 'student', created_at: new Date().toISOString() }
  ];

  db.books = [
    { id: 1, title: 'Clean Architecture', author: 'Robert C. Martin', description: 'A Craftsman Guide to Software Structure and Design.', genre: 'Software Engineering', created_at: new Date().toISOString() },
    { id: 2, title: 'Designing Data-Intensive Applications', author: 'Martin Kleppmann', description: 'The Big Ideas Behind Reliable, Scalable, and Maintainable Systems.', genre: 'Distributed Systems', created_at: new Date().toISOString() },
    { id: 3, title: 'Refactoring', author: 'Martin Fowler', description: 'Improving the Design of Existing Code.', genre: 'Software Engineering', created_at: new Date().toISOString() },
    { id: 4, title: 'Introduction to Algorithms', author: 'Cormen, Leiserson, Rivest, Stein', description: 'Comprehensive guide to algorithms and data structures.', genre: 'Computer Science', created_at: new Date().toISOString() }
  ];

  db.comments = [
    {
      id: 1,
      user_id: 2,
      title: 'Need more modern Python references',
      comment_text: 'The computer science section requires recent textbooks covering Python 3 and web frameworks.',
      category: 'book_suggestion',
      category_label: 'Book Suggestion',
      status: 'approved',
      content_hash: 'hash1',
      duplicate_of_id: null,
      similarity_score: null,
      moderation_reason: null,
      is_flagged: false,
      created_at: new Date(Date.now() - 86400000 * 3).toISOString()
    },
    {
      id: 2,
      user_id: 2,
      title: 'Wi-Fi connectivity dropouts in 3rd floor reading hall',
      comment_text: 'The Wi-Fi frequently disconnects around the study cubicles in the 3rd floor quiet zone.',
      category: 'wifi_digital',
      category_label: 'Wi-Fi & Digital Facilities',
      status: 'pending_review',
      content_hash: 'hash2',
      duplicate_of_id: null,
      similarity_score: null,
      moderation_reason: null,
      is_flagged: false,
      created_at: new Date(Date.now() - 86400000 * 2).toISOString()
    },
    {
      id: 3,
      user_id: 2,
      title: 'Need more quiet study cubicles',
      comment_text: 'During exam weeks there are not enough silent seating spots available for students.',
      category: 'library_facility',
      category_label: 'Library Facility',
      status: 'approved',
      content_hash: 'hash3',
      duplicate_of_id: null,
      similarity_score: null,
      moderation_reason: null,
      is_flagged: false,
      created_at: new Date(Date.now() - 86400000 * 1).toISOString()
    }
  ];

  db.reviews = [
    { id: 1, user_id: 2, book_id: 1, rating: 5, review_text: 'Essential reading for every software engineering student.', created_at: new Date().toISOString() },
    { id: 2, user_id: 2, book_id: 2, rating: 5, review_text: 'Incredible depth and clarity on distributed architectures.', created_at: new Date().toISOString() }
  ];

  db.moderationLogs = [];
  saveDb();
}

// --- Pipeline Logic: Normalization, Duplicate Check, Relevance, Appropriateness ---
function normalizeText(text) {
  return text.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ').trim();
}

function computeHash(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

function jaccardSimilarity(textA, textB) {
  const setA = new Set(textA.split(' '));
  const setB = new Set(textB.split(' '));
  const intersection = new Set([...setA].filter(x => setB.has(x)));
  const union = new Set([...setA, ...setB]);
  if (union.size === 0) return 1.0;
  return intersection.size / union.size;
}

const CATEGORY_KEYWORDS = [
  ['book_suggestion', ['suggest', 'recommend buying', 'purchase', 'acquire', 'add book', 'new book', 'request book']],
  ['book_review', ['review', 'rating', 'stars', 'read', 'reading', 'enjoyed', 'loved the', 'poor book']],
  ['library_facility', ['seat', 'chair', 'table', 'room', 'space', 'study room', 'noise', 'quiet', 'lighting', 'temperature']],
  ['library_service', ['service', 'staff', 'librarian', 'help', 'hours', 'opening', 'fine', 'renewal', 'loan', 'checkout']],
  ['wifi_digital', ['wifi', 'wi-fi', 'internet', 'wireless', 'network', 'computer', 'printer', 'digital', 'charger', 'outlet']],
  ['reading_recommendation', ['reading list', 'should read', 'good for', 'must read', 'book club']]
];

const RELEVANCE_KEYWORDS = [
  'book', 'library', 'study', 'read', 'reading', 'shelf', 'reference', 'resource', 'staff', 'librarian',
  'loan', 'return', 'checkout', 'wifi', 'wi-fi', 'internet', 'computer', 'seat', 'table', 'quiet',
  'facility', 'service', 'hour', 'review', 'rating', 'author', 'research'
];

const INAPPROPRIATE_TERMS = ['spam', 'advertisement', 'click here', 'buy now', 'casino', 'gambling', 'lottery', 'free money', 'fuck', 'shit', 'asshole'];

function processComment(comment) {
  const normalized = normalizeText(comment.comment_text);
  const hash = computeHash(normalized);
  comment.content_hash = hash;

  // 1. Auto Category
  if (!comment.category || comment.category === 'general_feedback') {
    const combined = `${comment.title} ${comment.comment_text}`.toLowerCase();
    for (const [cat, keywords] of CATEGORY_KEYWORDS) {
      if (keywords.some(kw => combined.includes(kw))) {
        comment.category = cat;
        break;
      }
    }
  }

  // 2. Exact Duplicate Check
  const exactDup = db.comments.find(c => c.content_hash === hash && c.id !== comment.id && c.status !== 'archived');
  if (exactDup) {
    comment.status = 'duplicate';
    comment.duplicate_of_id = exactDup.id;
    comment.similarity_score = 1.0;
    comment.moderation_reason = `Exact duplicate of comment #${exactDup.id}`;
    return comment;
  }

  // 3. Near-Duplicate Check
  for (const cand of db.comments) {
    if (cand.id !== comment.id && (cand.status === 'approved' || cand.status === 'pending_review')) {
      const candNorm = normalizeText(cand.comment_text);
      const score = jaccardSimilarity(normalized, candNorm);
      if (score >= 0.75) {
        comment.status = 'near_duplicate';
        comment.duplicate_of_id = cand.id;
        comment.similarity_score = Math.round(score * 100) / 100;
        comment.is_flagged = true;
        comment.moderation_reason = `High similarity (${Math.round(score * 100)}%) with comment #${cand.id}`;
        return comment;
      }
    }
  }

  // 4. Relevance Check
  const words = `${comment.title} ${comment.comment_text}`.toLowerCase().split(' ');
  if (words.length < 3) {
    comment.status = 'irrelevant';
    comment.is_flagged = true;
    comment.moderation_reason = 'Feedback is too short (minimum 3 words required).';
    return comment;
  }
  const hasRelevance = RELEVANCE_KEYWORDS.some(kw => `${comment.title} ${comment.comment_text}`.toLowerCase().includes(kw));
  if (!hasRelevance) {
    comment.status = 'irrelevant';
    comment.is_flagged = true;
    comment.moderation_reason = 'Comment does not appear related to library services.';
    return comment;
  }

  // 5. Inappropriate Check
  const lowerText = comment.comment_text.toLowerCase();
  for (const term of INAPPROPRIATE_TERMS) {
    if (lowerText.includes(term)) {
      comment.status = 'inappropriate';
      comment.is_flagged = true;
      comment.moderation_reason = 'Content flagged for policy violations / inappropriate terms.';
      return comment;
    }
  }

  comment.status = 'approved';
  comment.is_flagged = false;
  return comment;
}

// --- JWT Mock Helpers ---
function createToken(user) {
  const payload = Buffer.from(JSON.stringify({ id: user.id, role: user.role, email: user.email })).toString('base64');
  return `token.${payload}.sig`;
}

function verifyToken(req) {
  const auth = req.headers['authorization'];
  if (!auth || !auth.startsWith('Bearer ')) return null;
  const token = auth.slice(7);
  try {
    const parts = token.split('.');
    const decoded = JSON.parse(Buffer.from(parts[1], 'base64').toString('utf-8'));
    return db.users.find(u => u.id === decoded.id) || null;
  } catch (e) {
    return null;
  }
}

// --- HTTP Server ---
loadDb();

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    return res.end();
  }

  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = url.pathname;

  // JSON helper
  const sendJson = (status, data) => {
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
  };

  // Read Body helper
  const getBody = (cb) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        cb(body ? JSON.parse(body) : {});
      } catch (e) {
        sendJson(400, { error: 'Invalid JSON payload' });
      }
    });
  };

  // --- API Routes ---
  if (pathname === '/api/health') {
    return sendJson(200, { status: 'ok', version: '1.0.0' });
  }

  // Auth: Login
  if (pathname === '/api/v1/auth/login' && req.method === 'POST') {
    return getBody(body => {
      const hash = hashPassword(body.password || '');
      const user = db.users.find(u => u.email === body.email && u.password === hash);
      if (!user) {
        return sendJson(401, { error: 'Invalid credentials. Check email and password.' });
      }
      const token = createToken(user);
      return sendJson(200, {
        success: true,
        data: {
          token,
          user: { id: user.id, name: user.name, email: user.email, role: user.role }
        }
      });
    });
  }

  // Auth: Register
  if (pathname === '/api/v1/auth/register' && req.method === 'POST') {
    return getBody(body => {
      if (!body.name || !body.email || !body.password) {
        return sendJson(422, { error: 'Name, email, and password are required' });
      }
      if (db.users.find(u => u.email === body.email)) {
        return sendJson(409, { error: 'An account with this email already exists' });
      }
      const newUser = {
        id: db.users.length + 1,
        name: body.name,
        email: body.email,
        password: hashPassword(body.password),
        role: 'student',
        created_at: new Date().toISOString()
      };
      db.users.push(newUser);
      saveDb();
      return sendJson(201, { success: true, message: 'Account created successfully' });
    });
  }

  // Auth: Me
  if (pathname === '/api/v1/auth/me' && req.method === 'GET') {
    const user = verifyToken(req);
    if (!user) return sendJson(401, { error: 'Authentication required' });
    return sendJson(200, {
      success: true,
      data: { id: user.id, name: user.name, email: user.email, role: user.role, created_at: user.created_at }
    });
  }

  // Comments: List / Search / Filter
  if (pathname === '/api/v1/comments' && req.method === 'GET') {
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const perPage = parseInt(url.searchParams.get('per_page') || '10', 10);
    const search = url.searchParams.get('search') || '';
    const category = url.searchParams.get('category') || '';
    const status = url.searchParams.get('status') || '';

    let items = db.comments.filter(c => c.status !== 'archived');
    if (search) {
      const q = search.toLowerCase();
      items = items.filter(c => c.title.toLowerCase().includes(q) || c.comment_text.toLowerCase().includes(q));
    }
    if (category) {
      items = items.filter(c => c.category === category);
    }
    if (status) {
      items = items.filter(c => c.status === status);
    }

    const total = items.length;
    const start = (page - 1) * perPage;
    const paginated = items.slice(start, start + perPage);

    return sendJson(200, {
      success: true,
      data: {
        items: paginated,
        total,
        page,
        per_page: perPage,
        pages: Math.ceil(total / perPage) || 1
      }
    });
  }

  // Comments: Submit Feedback (Pipeline Entrypoint)
  if (pathname === '/api/v1/comments' && req.method === 'POST') {
    const user = verifyToken(req);
    return getBody(body => {
      if (!body.title || !body.comment_text) {
        return sendJson(422, { error: 'Title and comment text are required' });
      }

      let newComment = {
        id: db.comments.length + 1,
        user_id: user ? user.id : 2,
        title: body.title,
        comment_text: body.comment_text,
        category: body.category || 'general_feedback',
        book_title: body.book_title || null,
        rating: body.rating || null,
        facility: body.facility || null,
        created_at: new Date().toISOString()
      };

      newComment = processComment(newComment);
      db.comments.unshift(newComment);
      saveDb();

      return sendJson(201, {
        success: true,
        message: 'Feedback processed successfully',
        data: newComment
      });
    });
  }

  // Dashboard: Summary
  if (pathname === '/api/v1/dashboard/summary' && req.method === 'GET') {
    const counts = {
      total_comments: db.comments.length,
      approved: db.comments.filter(c => c.status === 'approved').length,
      pending_review: db.comments.filter(c => c.status === 'pending_review').length,
      duplicate: db.comments.filter(c => c.status === 'duplicate').length,
      near_duplicate: db.comments.filter(c => c.status === 'near_duplicate').length,
      irrelevant: db.comments.filter(c => c.status === 'irrelevant').length,
      inappropriate: db.comments.filter(c => c.status === 'inappropriate').length,
      archived: db.comments.filter(c => c.status === 'archived').length,
      average_rating: 4.8
    };
    return sendJson(200, { success: true, data: counts });
  }

  // Dashboard: Trends
  if (pathname === '/api/v1/dashboard/trends' && req.method === 'GET') {
    const trends = [
      { date: '2026-10-05', count: 3 },
      { date: '2026-10-06', count: 5 },
      { date: '2026-10-07', count: 8 },
      { date: '2026-10-08', count: 4 },
      { date: '2026-10-09', count: 11 },
      { date: '2026-10-10', count: 7 },
      { date: '2026-10-11', count: 14 }
    ];
    return sendJson(200, { success: true, data: trends });
  }

  // Dashboard: Categories
  if (pathname === '/api/v1/dashboard/categories' && req.method === 'GET') {
    const catMap = {};
    for (const c of db.comments) {
      catMap[c.category] = (catMap[c.category] || 0) + 1;
    }
    const data = Object.keys(catMap).map(k => ({
      category: k,
      label: k.replace('_', ' ').toUpperCase(),
      count: catMap[k]
    }));
    return sendJson(200, { success: true, data });
  }

  // Dashboard: Insights
  if (pathname === '/api/v1/dashboard/insights' && req.method === 'GET') {
    return sendJson(200, {
      success: true,
      data: {
        top_feedback_categories: [
          { category: 'library_facility', label: 'Study & Seating Space', count: 12 },
          { category: 'wifi_digital', label: 'Wi-Fi & Digital Tools', count: 9 },
          { category: 'book_suggestion', label: 'CS Textbooks', count: 6 }
        ]
      }
    });
  }

  // Moderation: Queue
  if (pathname === '/api/v1/moderation/queue' && req.method === 'GET') {
    const status = url.searchParams.get('status');
    let queue = db.comments;
    if (status) {
      queue = queue.filter(c => c.status === status);
    } else {
      queue = queue.filter(c => ['pending_review', 'near_duplicate', 'irrelevant', 'inappropriate'].includes(c.status));
    }
    return sendJson(200, {
      success: true,
      data: { items: queue, total: queue.length, page: 1, per_page: 50, pages: 1 }
    });
  }

  // Moderation: Approve
  const approveMatch = pathname.match(/^\/api\/v1\/moderation\/(\d+)\/approve$/);
  if (approveMatch && req.method === 'POST') {
    const id = parseInt(approveMatch[1], 10);
    const comment = db.comments.find(c => c.id === id);
    if (!comment) return sendJson(404, { error: 'Comment not found' });
    comment.status = 'approved';
    comment.is_flagged = false;
    db.moderationLogs.push({ id: db.moderationLogs.length + 1, comment_id: id, action: 'approve', created_at: new Date().toISOString() });
    saveDb();
    return sendJson(200, { success: true, message: 'Approved' });
  }

  // Books: List
  if (pathname === '/api/v1/books' && req.method === 'GET') {
    const search = (url.searchParams.get('search') || '').toLowerCase();
    let books = db.books;
    if (search) {
      books = books.filter(b => b.title.toLowerCase().includes(search) || b.author.toLowerCase().includes(search));
    }
    const withRatings = books.map(b => {
      const revs = db.reviews.filter(r => r.book_id === b.id);
      const avg = revs.length ? (revs.reduce((a, c) => a + c.rating, 0) / revs.length).toFixed(1) : null;
      return { ...b, average_rating: avg, review_count: revs.length };
    });
    return sendJson(200, { success: true, data: { items: withRatings, total: withRatings.length } });
  }

  // Books: Detail
  const bookMatch = pathname.match(/^\/api\/v1\/books\/(\d+)$/);
  if (bookMatch && req.method === 'GET') {
    const id = parseInt(bookMatch[1], 10);
    const book = db.books.find(b => b.id === id);
    if (!book) return sendJson(404, { error: 'Book not found' });
    const revs = db.reviews.filter(r => r.book_id === id);
    const avg = revs.length ? (revs.reduce((a, c) => a + c.rating, 0) / revs.length).toFixed(1) : null;
    return sendJson(200, { success: true, data: { ...book, average_rating: avg, review_count: revs.length } });
  }

  // Books: Reviews
  const reviewsMatch = pathname.match(/^\/api\/v1\/books\/(\d+)\/reviews$/);
  if (reviewsMatch && req.method === 'GET') {
    const id = parseInt(reviewsMatch[1], 10);
    const revs = db.reviews.filter(r => r.book_id === id);
    return sendJson(200, { success: true, data: { items: revs, total: revs.length } });
  }

  // Reports: Export CSV
  if (pathname === '/api/v1/reports/export.csv' && req.method === 'GET') {
    let csv = 'ID,Title,Category,Status,CreatedAt\n';
    for (const c of db.comments) {
      csv += `"${c.id}","${c.title.replace(/"/g, '""')}","${c.category}","${c.status}","${c.created_at}"\n`;
    }
    res.writeHead(200, {
      'Content-Type': 'text/csv',
      'Content-Disposition': 'attachment; filename=library_feedback.csv'
    });
    return res.end(csv);
  }

  // Serve Single Page Application (SPA) HTML for UI
  const indexPath = path.join(__dirname, 'public', 'index.html');
  if (fs.existsSync(indexPath)) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(fs.readFileSync(indexPath, 'utf-8'));
  }

  sendJson(404, { error: 'Endpoint not found' });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[LibraryOpt System Server] Running at http://localhost:${PORT}`);
});
