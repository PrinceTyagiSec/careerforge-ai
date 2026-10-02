import React, { useState } from 'react';
import { X, Globe, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../api';

interface JobImportModalProps {
  onClose: () => void;
  onImportSuccess: (jobId: number) => void;
}

export const JobImportModal: React.FC<JobImportModalProps> = ({ onClose, onImportSuccess }) => {
  const [importType, setImportType] = useState<'url' | 'text'>('text');
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [location, setLocation] = useState('Remote India');
  const [description, setDescription] = useState('');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.importJob({
        import_type: importType,
        url: url || undefined,
        title: title || undefined,
        company_name: companyName || undefined,
        location: location || 'India',
        description: description || undefined,
        salary_min: salaryMin ? parseFloat(salaryMin) : undefined,
        salary_max: salaryMax ? parseFloat(salaryMax) : undefined,
      });

      if (res.job_id) {
        onImportSuccess(res.job_id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to import job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Import Real-World Job Listing
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Imports enter the same normalization, deduplication, and matching pipeline as API jobs.
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Import Type Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '18px' }}>
          <button
            type="button"
            className={`btn ${importType === 'text' ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setImportType('text')}
          >
            <FileText size={14} /> Paste Description / Manual
          </button>
          <button
            type="button"
            className={`btn ${importType === 'url' ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setImportType('url')}
          >
            <Globe size={14} /> Import from Job URL
          </button>
        </div>

        {error && (
          <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'rgba(244, 63, 94, 0.15)', color: '#fda4af', fontSize: '12px', marginBottom: '14px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {importType === 'url' ? (
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
                Job Posting URL
              </label>
              <input
                type="url"
                className="input"
                placeholder="https://company.com/careers/job-listing"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Title, company, and job requirements will be parsed automatically.
              </div>
            </div>
          ) : (
            <>
              <div className="grid-2">
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Job Title</label>
                  <input type="text" className="input" placeholder="e.g. Senior Backend Engineer" value={title} onChange={(e) => setTitle(e.target.value)} required />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Company Name</label>
                  <input type="text" className="input" placeholder="e.g. Razorpay or Cred" value={companyName} onChange={(e) => setCompanyName(e.target.value)} required />
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Location</label>
                  <input type="text" className="input" placeholder="e.g. Bengaluru or Remote India" value={location} onChange={(e) => setLocation(e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Original Listing URL (Optional)</label>
                  <input type="url" className="input" placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Min Salary (₹ INR Annual)</label>
                  <input type="number" className="input" placeholder="e.g. 1500000" value={salaryMin} onChange={(e) => setSalaryMin(e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Max Salary (₹ INR Annual)</label>
                  <input type="number" className="input" placeholder="e.g. 2500000" value={salaryMax} onChange={(e) => setSalaryMax(e.target.value)} />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Job Description & Requirements</label>
                <textarea
                  className="textarea"
                  placeholder="Paste complete job description, required technical skills, and experience criteria..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={{ minHeight: '140px' }}
                  required
                />
              </div>
            </>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
            <button type="button" onClick={onClose} className="btn btn-outline">Cancel</button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Normalizing & Matching...' : 'Process & Match Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
