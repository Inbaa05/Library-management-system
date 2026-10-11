import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, ShieldAlert, Sparkles, Filter, Database, TrendingUp, Layers } from 'lucide-react';
import axios from 'axios';

const LandingPage = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Attempt to load live server stats gracefully
    axios.get('http://localhost:5000/api/health')
      .then(() => {
        // Backend is up, fetch basic metrics if available
        setStats({ online: true });
      })
      .catch(() => {
        setStats({ online: false });
      });
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '60px' }}>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '40px 0 20px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '999px', backgroundColor: '#e6f4ea', color: 'var(--color-emerald)', fontWeight: 600, fontSize: '0.85rem', marginBottom: '20px' }}>
          <Sparkles size={16} /> Intelligent Academic Library Optimization
        </div>
        <h1 style={{ fontSize: '2.75rem', fontWeight: 800, color: 'var(--color-navy)', lineHeight: 1.2, marginBottom: '20px' }}>
          Turn Library Feedback into Better Decisions
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#4b5563', maxWidth: '750px', margin: '0 auto 30px', lineHeight: 1.6 }}>
          A centralized digital platform automating comment validation, duplicate detection, relevance filtering, and actionable insights for library systems.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
          <Link to="/student/submit" className="btn-primary" style={{ padding: '12px 24px', fontSize: '1rem', textDecoration: 'none' }}>
            Get Started
          </Link>
          <Link to="/feedback" className="btn-secondary" style={{ padding: '12px 24px', fontSize: '1rem', textDecoration: 'none' }}>
            Explore Feedback
          </Link>
        </div>
      </section>

      {/* Feature Cards */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: '#ecfdf5', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <Layers color="var(--color-emerald)" size={20} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '10px' }}>Automated Categorization</h3>
          <p style={{ color: '#6b7280', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Instantly assigns structured categories like facility requests, book suggestions, and digital resources using keyword-matching logic.
          </p>
        </div>

        <div className="card" style={{ padding: '24px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <Filter color="#2563eb" size={20} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '10px' }}>Exact & Near Duplicate Check</h3>
          <p style={{ color: '#6b7280', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Combines deterministic SHA-256 hashing for exact duplicates with token Jaccard similarity for near-duplicate feedback flags.
          </p>
        </div>

        <div className="card" style={{ padding: '24px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: '#fef2f2', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <ShieldAlert color="#dc2626" size={20} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '10px' }}>Relevance & Content Filtering</h3>
          <p style={{ color: '#6b7280', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Screens submitted text with configurable relevance rules and an inappropriate content blocklist before queuing.
          </p>
        </div>
      </section>

      {/* How It Works */}
      <section style={{ backgroundColor: '#ffffff', padding: '40px', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
        <h2 style={{ textAlign: 'center', fontSize: '1.85rem', fontWeight: 700, marginBottom: '30px' }}>
          Comment Optimization Pipeline
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', textAlign: 'center' }}>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-emerald)', marginBottom: '8px' }}>01</div>
            <h4 style={{ fontWeight: 600, marginBottom: '6px' }}>Submission</h4>
            <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Student submits feedback with optional book and rating metadata.</p>
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-emerald)', marginBottom: '8px' }}>02</div>
            <h4 style={{ fontWeight: 600, marginBottom: '6px' }}>Analysis</h4>
            <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Pipeline normalizes text, hashes tokens, and evaluates similarity.</p>
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-emerald)', marginBottom: '8px' }}>03</div>
            <h4 style={{ fontWeight: 600, marginBottom: '6px' }}>Status Tagging</h4>
            <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Classified as Approved, Duplicate, Irrelevant, or Inappropriate.</p>
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-emerald)', marginBottom: '8px' }}>04</div>
            <h4 style={{ fontWeight: 600, marginBottom: '6px' }}>Actionable Insights</h4>
            <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Librarians review queues, audit logs, and analytics dashboards.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
