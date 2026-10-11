import React from 'react';

const StatusBadge = ({ status, type = 'status' }) => {
  if (!status) return null;

  const statusStyles = {
    approved: { bg: '#ecfdf5', color: '#047857', border: '#a7f3d0' },
    pending_review: { bg: '#fffbeb', color: '#b45309', border: '#fde68a' },
    duplicate: { bg: '#eff6ff', color: '#1d4ed8', border: '#bfdbfe' },
    near_duplicate: { bg: '#f5f3ff', color: '#6d28d9', border: '#ddd6fe' },
    irrelevant: { bg: '#f3f4f6', color: '#4b5563', border: '#e5e7eb' },
    inappropriate: { bg: '#fef2f2', color: '#b91c1c', border: '#fecaca' },
    archived: { bg: '#f1f5f9', color: '#334155', border: '#cbd5e1' },
  };

  const current = statusStyles[status] || { bg: '#f3f4f6', color: '#4b5563', border: '#e5e7eb' };
  const label = status.replace('_', ' ').toUpperCase();

  return (
    <span
      className={`badge badge-${status}`}
      style={{
        display: 'inline-block',
        padding: '3px 8px',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: current.bg,
        color: current.color,
        border: `1px solid ${current.border}`,
        textTransform: 'capitalize',
      }}
    >
      {label}
    </span>
  );
};

export default StatusBadge;
