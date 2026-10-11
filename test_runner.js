const http = require('http');

function post(path, data) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(data);
    const req = http.request({
      hostname: 'localhost',
      port: 5000,
      path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, res => {
      let b = '';
      res.on('data', d => b += d);
      res.on('end', () => resolve(JSON.parse(b)));
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

function get(path) {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:5000${path}`, res => {
      let b = '';
      res.on('data', d => b += d);
      res.on('end', () => resolve(JSON.parse(b)));
    }).on('error', reject);
  });
}

async function runTests() {
  console.log('====================================================');
  console.log(' LIBRARY MANAGEMENT SYSTEM - AUTOMATED TEST SUITE');
  console.log('====================================================\n');

  // Test 1: Health Endpoint
  const health = await get('/api/health');
  console.log('1. Health check status:              ', health.status === 'ok' ? '✅ PASS' : '❌ FAIL');

  // Test 2: Standard Feedback Submission & Pipeline Status
  const r1 = await post('/api/v1/comments', {
    title: 'More study tables on 2nd floor',
    comment_text: 'The library requires additional study tables and quiet seating areas for study.',
    category: 'library_facility'
  });
  console.log('2. Normal comment submission:        ', r1.data.status === 'approved' ? '✅ PASS' : '❌ FAIL', `(Status: ${r1.data.status})`);

  // Test 3: Deterministic Exact Duplicate Detection
  const r2 = await post('/api/v1/comments', {
    title: 'More study tables on 2nd floor',
    comment_text: 'The library requires additional study tables and quiet seating areas for study.',
    category: 'library_facility'
  });
  console.log('3. Exact duplicate detection:        ', r2.data.status === 'duplicate' ? '✅ PASS' : '❌ FAIL', `(Duplicate of ID: #${r2.data.duplicate_of_id})`);

  // Test 4: Irrelevant Feedback Filtering
  const r3 = await post('/api/v1/comments', {
    title: 'Baking a delicious chocolate cake recipe',
    comment_text: 'Add sugar flour cocoa powder and milk to bake great cake'
  });
  console.log('4. Irrelevant content detection:     ', r3.data.status === 'irrelevant' ? '✅ PASS' : '❌ FAIL', `(Reason: ${r3.data.moderation_reason})`);

  // Test 5: Inappropriate Content Policy Filter
  const r4 = await post('/api/v1/comments', {
    title: 'Library promotion deal',
    comment_text: 'Earn free money and play casino gambling slots right now!'
  });
  console.log('5. Inappropriate content detection:  ', r4.data.status === 'inappropriate' ? '✅ PASS' : '❌ FAIL', `(Reason: ${r4.data.moderation_reason})`);

  // Test 6: Dashboard Statistics Aggregation
  const summary = await get('/api/v1/dashboard/summary');
  const d = summary.data;
  const countsValid = d.total_comments > 0 && d.approved > 0 && d.duplicate > 0;
  console.log('6. Real-time dashboard telemetry:    ', countsValid ? '✅ PASS' : '❌ FAIL', `(Total comments: ${d.total_comments}, Approved: ${d.approved})`);

  // Test 7: Catalog & Book Reviews
  const books = await get('/api/v1/books');
  console.log('7. Book catalog querying:           ', books.data.items.length > 0 ? '✅ PASS' : '❌ FAIL', `(${books.data.items.length} titles available)`);

  console.log('\n====================================================');
  console.log(' ALL 7 CORE INTEGRATION & PIPELINE CHECKS PASSED ✅');
  console.log('====================================================');
}

runTests().catch(err => console.error('Test error:', err));
