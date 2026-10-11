import React from 'react';
import { 
  CheckCircle2, 
  Search, 
  Cpu, 
  ShieldCheck, 
  Sliders, 
  BarChart, 
  Layers,
  FileCheck2
} from 'lucide-react';

const CommentOptimizer = () => {
  const steps = [
    {
      num: '01',
      title: 'Feedback Intake',
      desc: 'System receives title, comment text, category hints, and optional star ratings or facility metadata via authenticated REST endpoints.',
      icon: <Layers size={22} color="var(--color-emerald)" />
    },
    {
      num: '02',
      title: 'Text Normalization',
      desc: 'Raw feedback strings are converted to lowercase, stripped of unnecessary special characters and extra whitespaces to establish a canonical base representation.',
      icon: <Cpu size={22} color="#2563eb" />
    },
    {
      num: '03',
      title: 'Automatic Categorization',
      desc: 'Rule-based keyword dictionary assigns categories (e.g. Wi-Fi, facilities, books) if the submitter left it unspecified.',
      icon: <Sliders size={22} color="#7c3aed" />
    },
    {
      num: '04',
      title: 'Exact Duplicate Detection',
      desc: 'Generates a deterministic SHA-256 hash of normalized text for instant O(1) indexed database lookups against prior submissions.',
      icon: <FileCheck2 size={22} color="#d97706" />
    },
    {
      num: '05',
      title: 'Near-Duplicate Jaccard Similarity',
      desc: 'Computes token set overlap against existing pending and approved feedback. Matches exceeding configurable similarity thresholds (e.g. 75%) are tagged for inspection.',
      icon: <Search size={22} color="#2563eb" />
    },
    {
      num: '06',
      title: 'Relevance & Policy Moderation',
      desc: 'Evaluates domain whitelist keywords (library, books, Wi-Fi, seating) and matches against moderation blocklists to catch spam or off-topic queries.',
      icon: <ShieldCheck size={22} color="#dc2626" />
    },
    {
      num: '07',
      title: 'Decision Routing & Telemetry',
      desc: 'Saves moderation audit trails, logs reasons, updates librarian work queues, and pushes metrics into analytics telemetry tables.',
      icon: <BarChart size={22} color="#059669" />
    }
  ];

  return (
    <div style={{ maxWidth: '850px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--color-navy)', marginBottom: '12px' }}>
          Comment Optimization Architecture
        </h1>
        <p style={{ color: '#4b5563', fontSize: '1.05rem', maxWidth: '650px', margin: '0 auto', lineHeight: 1.5 }}>
          An end-to-end overview of the multi-stage validation, similarity detection, and moderation pipeline powering our library feedback processing system.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {steps.map((st) => (
          <div key={st.num} className="card" style={{ padding: '24px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '10px', backgroundColor: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              {st.icon}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#9ca3af' }}>PHASE {st.num}</span>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: 'var(--color-navy)' }}>{st.title}</h3>
              </div>
              <p style={{ color: '#4b5563', fontSize: '0.95rem', margin: 0, lineHeight: 1.5 }}>
                {st.desc}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CommentOptimizer;
