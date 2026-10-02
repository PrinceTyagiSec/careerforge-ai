import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, AlertTriangle, AlertCircle, CheckCircle2, 
  BarChart2, FileText, Zap, HelpCircle
} from 'lucide-react';
import { api, ResumeQuality } from '../api';

export const ResumeQualityView: React.FC = () => {
  const [quality, setQuality] = useState<ResumeQuality | null>(null);
  const [loading, setLoading] = useState(false);
  const [resumeId, setResumeId] = useState<number | null>(null);

  useEffect(() => {
    loadQuality();
  }, []);

  const loadQuality = async () => {
    try {
      setLoading(true);
      const list = await api.listResumes();
      if (list.length > 0) {
        setResumeId(list[0].id);
        const data = await api.getResumeQuality(list[0].id);
        setQuality(data);
      }
    } catch (err) {
      console.error('Failed to load resume quality:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
        Analyzing resume quality, readability, and ATS metrics...
      </div>
    );
  }

  if (!quality) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
        <FileText size={40} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
          No Resume Uploaded
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
          Please upload a resume first to run the Resume Quality Engine.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Resume Quality & ATS Engine
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Rigorous factual evaluation across Content, Readability, ATS Compliance, and Completeness.
          </p>
        </div>
      </div>

      {/* Main Score Hero Card */}
      <div className="card" style={{ padding: '28px', marginBottom: '24px', background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '28px' }}>
          <div style={{
            width: '110px', height: '110px', borderRadius: '50%',
            background: 'conic-gradient(#10b981 0% 88%, #334155 88% 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 25px rgba(16, 185, 129, 0.25)', flexShrink: 0
          }}>
            <div style={{ width: '92px', height: '92px', borderRadius: '50%', background: '#0b0f19', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontSize: '26px', fontWeight: 800, color: '#34d399' }}>{quality.overall_quality_score}%</span>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Overall</span>
            </div>
          </div>

          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
              Resume Quality Health Check
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
              Evaluated against modern hiring standards for Indian software and engineering roles.
            </p>
            <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--text-muted)' }}>
              <span>{quality.metrics.total_skills} Skills Found</span> &bull; 
              <span>{quality.metrics.total_bullets} Bullet Points</span> &bull; 
              <span>{quality.metrics.measurable_outcomes_count} Measurable Metrics</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4 Pillars Breakdown */}
      <div className="grid-4" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Content Quality</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#60a5fa' }}>{quality.category_scores.content}%</div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Action verbs, outcomes, impact</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Readability</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#34d399' }}>{quality.category_scores.readability}%</div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Bullet length, capitalization</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>ATS Compatibility</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#c084fc' }}>{quality.category_scores.ats}%</div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Standard fonts, keywords</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>Completeness</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#fbbf24' }}>{quality.category_scores.completeness}%</div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Contacts, links, education</div>
        </div>
      </div>

      {/* Actionable Findings */}
      <div className="card">
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '16px' }}>
          Actionable Improvement Recommendations
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Content issues */}
          {quality.issues.content.map((issue, idx) => (
            <div key={`c-${idx}`} style={{ display: 'flex', gap: '12px', padding: '12px', borderRadius: 'var(--radius-md)', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <AlertTriangle size={18} color="#fbbf24" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '13px', color: '#fbbf24', display: 'block', marginBottom: '2px' }}>Content Refinement:</strong>
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{issue.message}</span>
              </div>
            </div>
          ))}

          {/* Readability issues */}
          {quality.issues.readability.map((issue, idx) => (
            <div key={`r-${idx}`} style={{ display: 'flex', gap: '12px', padding: '12px', borderRadius: 'var(--radius-md)', background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              <FileText size={18} color="#60a5fa" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '13px', color: '#60a5fa', display: 'block', marginBottom: '2px' }}>Readability:</strong>
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{issue.message}</span>
              </div>
            </div>
          ))}

          {/* Completeness issues */}
          {quality.issues.completeness.map((issue, idx) => (
            <div key={`comp-${idx}`} style={{ display: 'flex', gap: '12px', padding: '12px', borderRadius: 'var(--radius-md)', background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
              <AlertCircle size={18} color="#fda4af" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '13px', color: '#fda4af', display: 'block', marginBottom: '2px' }}>Missing Element:</strong>
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{issue.message}</span>
              </div>
            </div>
          ))}

          {quality.issues.content.length === 0 && quality.issues.completeness.length === 0 && (
            <div style={{ textAlign: 'center', padding: '24px', color: '#34d399' }}>
              <CheckCircle2 size={32} style={{ margin: '0 auto 8px auto' }} />
              <div style={{ fontWeight: 700 }}>Excellent Resume Quality!</div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>No high-severity content or completeness issues detected.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
