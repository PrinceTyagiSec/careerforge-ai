import React, { useState, useEffect } from 'react';
import { 
  FileText, Upload, Download, ShieldCheck, CheckCircle2, 
  AlertCircle, Sparkles, RefreshCw, Eye, Code, Briefcase, GraduationCap
} from 'lucide-react';
import { api, ResumeDetail } from '../api';

export const ResumeView: React.FC = () => {
  const [resumes, setResumes] = useState<any[]>([]);
  const [activeResume, setActiveResume] = useState<ResumeDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  // Export controls
  const [exportFormat, setExportFormat] = useState('pdf');
  const [exportTemplate, setExportTemplate] = useState('ATS Simple');
  const [activeSubTab, setActiveSubTab] = useState<'profile' | 'claims' | 'raw'>('profile');

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      setLoading(true);
      const list = await api.listResumes();
      setResumes(list);
      if (list.length > 0) {
        const detail = await api.getResumeDetail(list[0].id);
        setActiveResume(detail);
      }
    } catch (err) {
      console.error('Failed to load resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      await api.uploadResume(file);
      await loadResumes();
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Failed to process and parse uploaded resume.');
    } finally {
      setUploading(false);
    }
  };

  const handleExport = () => {
    if (!activeResume) return;
    const url = `/api/resumes/${activeResume.id}/export?format=${exportFormat}&template=${encodeURIComponent(exportTemplate)}`;
    window.open(url, '_blank');
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Resume Ingestion & Claim Protection
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Local parser, OCR fallback, atomic claim protection, and reproducible multi-template exporter.
          </p>
        </div>

        {/* Upload Button */}
        <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
          <Upload size={16} /> {uploading ? 'Processing File...' : 'Upload New Resume (PDF/DOCX/TXT)'}
          <input type="file" accept=".pdf,.docx,.doc,.txt,.md,.png,.jpg" onChange={handleFileUpload} style={{ display: 'none' }} />
        </label>
      </div>

      {/* Main Content */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
          Loading candidate resume data...
        </div>
      ) : !activeResume ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <FileText size={40} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
            No Resume Ingested Yet
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
            Upload your PDF, DOCX, or text resume. The system will extract your skills, experience, and protect factual integrity.
          </p>
        </div>
      ) : (
        <div>
          {/* Resume Meta Card */}
          <div className="card" style={{ padding: '20px', marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {activeResume.original_filename}
                  </span>
                  <span className="badge badge-blue">
                    {activeResume.file_type.toUpperCase()}
                  </span>
                  {activeResume.ocr_applied ? (
                    <span className="badge badge-amber">
                      OCR Fallback Applied ({Math.round((activeResume.ocr_confidence || 0.8) * 100)}% Conf)
                    </span>
                  ) : (
                    <span className="badge badge-emerald">
                      Native Text Parsed
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {activeResume.skills.length} Skills &bull; {activeResume.experiences.length} Positions &bull; {activeResume.claims.length} Verified Claims
                </div>
              </div>

              {/* Exporter Controls */}
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <select className="select" style={{ width: 'auto', padding: '8px 12px', fontSize: '13px' }} value={exportTemplate} onChange={(e) => setExportTemplate(e.target.value)}>
                  <option value="ATS Simple">Template: ATS Simple</option>
                  <option value="Modern">Template: Modern</option>
                  <option value="Technical">Template: Technical</option>
                  <option value="Software Engineer">Template: Software Engineer</option>
                  <option value="Cybersecurity">Template: Cybersecurity</option>
                  <option value="Minimal">Template: Minimal</option>
                  <option value="Academic">Template: Academic</option>
                </select>

                <select className="select" style={{ width: 'auto', padding: '8px 12px', fontSize: '13px' }} value={exportFormat} onChange={(e) => setExportFormat(e.target.value)}>
                  <option value="pdf">Format: PDF</option>
                  <option value="docx">Format: DOCX</option>
                  <option value="md">Format: Markdown</option>
                  <option value="txt">Format: TXT</option>
                </select>

                <button onClick={handleExport} className="btn btn-primary btn-sm">
                  <Download size={14} /> Export
                </button>
              </div>
            </div>
          </div>

          {/* Sub Navigation */}
          <div className="tabs-header">
            <button className={`tab-btn ${activeSubTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveSubTab('profile')}>
              Extracted Profile & Sections
            </button>
            <button className={`tab-btn ${activeSubTab === 'claims' ? 'active' : ''}`} onClick={() => setActiveSubTab('claims')}>
              Atomic Claims & Fact Protection ({activeResume.claims.length})
            </button>
            <button className={`tab-btn ${activeSubTab === 'raw' ? 'active' : ''}`} onClick={() => setActiveSubTab('raw')}>
              Raw Text Stream
            </button>
          </div>

          {/* SubTab: Extracted Profile */}
          {activeSubTab === 'profile' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Technical Skills Card */}
              <div className="card">
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
                  Extracted Technical Skills & Categories
                </h3>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {activeResume.skills.map((s) => (
                    <span key={s.id} className="badge badge-emerald" style={{ padding: '6px 12px', fontSize: '12px', textTransform: 'none' }}>
                      <strong>{s.canonical_name}</strong> &bull; <span style={{ opacity: 0.8 }}>{s.category}</span>
                    </span>
                  ))}
                </div>
              </div>

              {/* Experience Card */}
              <div className="card">
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
                  Work Experience
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {activeResume.experiences.map((exp) => (
                    <div key={exp.id} style={{ borderLeft: '3px solid #3b82f6', paddingLeft: '14px' }}>
                      <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text-primary)' }}>
                        {exp.title} &mdash; {exp.company}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                        {exp.start_date} &bull; {exp.end_date} | {exp.location}
                      </div>
                      <ul style={{ paddingLeft: '18px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                        {exp.bullets.map((b, idx) => (
                          <li key={idx} style={{ marginBottom: '4px' }}>{b}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* SubTab: Atomic Claims & Fact Protection */}
          {activeSubTab === 'claims' && (
            <div className="card">
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                  Factual Integrity Layer (Section 22)
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Atomic claims verified directly from your ingested document. The AI matching and tailoring engines are restricted to using only these verified claims.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '450px', overflowY: 'auto' }}>
                {activeResume.claims.map((claim) => (
                  <div
                    key={claim.id}
                    style={{
                      padding: '10px 14px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(255,255,255,0.02)',
                      border: '1px solid var(--border-color)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {claim.statement}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        Category: <strong style={{ color: '#60a5fa' }}>{claim.category}</strong> &bull; Section: {claim.source_section}
                      </div>
                    </div>
                    <span className="badge badge-emerald" style={{ fontSize: '10px' }}>
                      {claim.verification_status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SubTab: Raw Text */}
          {activeSubTab === 'raw' && (
            <div className="card">
              <pre style={{ fontSize: '12px', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', maxHeight: '500px', overflowY: 'auto', fontFamily: 'var(--font-mono)' }}>
                {activeResume.raw_text}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
