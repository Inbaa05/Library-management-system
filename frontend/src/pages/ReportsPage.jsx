import React, { useEffect, useState } from 'react';
import { getReportsApi, exportReportCsvApi } from '../api/dashboard';
import StatusBadge from '../components/ui/StatusBadge';
import { Download, Filter, FileSpreadsheet } from 'lucide-react';
import { useToast } from '../components/ui/Toast';

const ReportsPage = () => {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  const { showError, showSuccess } = useToast();

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await getReportsApi({
        page,
        per_page: 15,
        category: category || undefined,
        status: status || undefined,
      });
      setItems(res.data.data.items);
      setTotal(res.data.data.total);
    } catch (err) {
      showError('Failed to fetch reporting data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [page, category, status]);

  const handleExportCsv = async () => {
    setExporting(true);
    try {
      const res = await exportReportCsvApi({
        category: category || undefined,
        status: status || undefined,
      });
      const blob = new Blob([res.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `library_feedback_report_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      showSuccess('CSV export generated successfully');
    } catch (err) {
      showError('Failed to download CSV export');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '8px' }}>
            Reports & Data Export
          </h1>
          <p style={{ color: '#6b7280' }}>
            Generate filtered institutional feedback reports and export compliance-ready CSVs.
          </p>
        </div>
        <button
          onClick={handleExportCsv}
          disabled={exporting}
          className="btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 18px' }}
        >
          <Download size={16} />
          {exporting ? 'Generating CSV...' : 'Export to CSV'}
        </button>
      </div>

      {/* Filters */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '20px', display: 'flex', gap: '16px' }}>
        <select
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem', backgroundColor: '#fff' }}
        >
          <option value="">All Categories</option>
          <option value="book_suggestion">Book Suggestion</option>
          <option value="book_review">Book Review</option>
          <option value="library_facility">Library Facility</option>
          <option value="library_service">Library Service</option>
          <option value="wifi_digital">Wi-Fi & Digital</option>
          <option value="general_feedback">General Feedback</option>
        </select>

        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--color-border)', fontSize: '0.9rem', backgroundColor: '#fff' }}
        >
          <option value="">All Statuses</option>
          <option value="approved">Approved</option>
          <option value="pending_review">Pending Review</option>
          <option value="duplicate">Duplicate</option>
          <option value="irrelevant">Irrelevant</option>
          <option value="inappropriate">Inappropriate</option>
        </select>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
          <thead style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid var(--color-border)' }}>
            <tr>
              <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy)' }}>ID</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy)' }}>Title</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy)' }}>Category</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy)' }}>Status</th>
              <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-navy)' }}>Date</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="5" style={{ padding: '30px', textAlign: 'center' }}>Loading reports...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan="5" style={{ padding: '30px', textAlign: 'center', color: '#6b7280' }}>No records match criteria.</td></tr>
            ) : (
              items.map((it) => (
                <tr key={it.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 600, color: '#6b7280' }}>#{it.id}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 500 }}>{it.title}</td>
                  <td style={{ padding: '12px 16px' }}>{it.category_label || it.category}</td>
                  <td style={{ padding: '12px 16px' }}><StatusBadge status={it.status} /></td>
                  <td style={{ padding: '12px 16px', color: '#6b7280' }}>{new Date(it.created_at).toLocaleDateString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReportsPage;
