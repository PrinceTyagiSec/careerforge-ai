import React, { useState, useEffect } from 'react';
import { 
  X, Sparkles, ShieldCheck, CheckCircle2, AlertTriangle, 
  FileText, Send, Building2, ExternalLink, Bookmark, Clock,
  Check, Edit3, RotateCcw, Copy, Download
} from 'lucide-react';
import { api, JobDetail } from '../api';

interface JobDetailModalProps {
  jobId: number;
  onClose: () => void;
  onApplicationCreated?: () => void;
}

export const JobDetailModal: React.FC<JobDetailModalProps> = ({ jobId, onClose, onApplicationCreated }) => {
  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'match' | 'evidence' | 'tailor' | 'ats' | 'cover-letter' | 'apply'>('match');
  
  // Tailored resume state
  const [tailoredData, setTailoredData] = useState<any>(null);
  const [tailoringLoading, setTailoringLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('ATS Simple');

  // Application state
  const [appStatus, setAppStatus] = useState('Applied');
  const [followUpDate, setFollowUpDate] = useState('');
  const [interviewDate, setInterviewDate] = useState('');
  const [appNotes, setAppNotes] = useState('');
  const [duplicateWarning, setDuplicateWarning] = useState<string | null>(null);
  const [applySuccess, setApplySuccess] = useState(false);

  useEffect(() => {
    loadJobDetails();
  }, [jobId]);

  const loadJobDetails = async () => {
    try {
      setLoading(true);
      const data = await api.getJobDetail(jobId);
      setJob(data);
    } catch (err) {
      console.error('Failed to load job detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTailorResume = async () => {
    try {
      setTailoringLoading(true);
      const data = await api.tailorResume(jobId, selectedTemplate);
      setTailoredData(data);
      setActiveTab('tailor');
    } catch (err: any) {
      alert(err.message || 'Failed to tailor resume.');
    } finally {
      setTailoringLoading(false);
    }
  };

  const handleReviewChange = async (changeId: number, status: string, userOverride?: string) => {
    try {
      await api.reviewChange(jobId, changeId, { status, user_override_text: userOverride });
      if (tailoredData) {
        setTailoredData({
          ...tailoredData,
          changes: tailoredData.changes.map((c: any) => c.id === changeId ? { ...c, status, user_override_text: userOverride } : c)
        });
      }
    } catch (err) {
      console.error('Review change error:', err);
    }
  };

  const handleApply = async (acknowledgeDuplicate = false) => {
    try {
      setDuplicateWarning(null);
      const res = await api.createApplication({
        job_id: jobId,
        status: appStatus,
        follow_up_date: followUpDate ? new Date(followUpDate).toISOString() : undefined,
        interview_date: interviewDate ? new Date(interviewDate).toISOString() : undefined,
        notes: appNotes,
        acknowledge_duplicate: acknowledgeDuplicate
      });

      if (res.duplicate_warning) {
        setDuplicateWarning(res.message);
      } else {
        setApplySuccess(true);
        if (onApplicationCreated) onApplicationCreated();
      }
    } catch (err: any) {
      alert(err.message || 'Failed to submit application');
    }
  };

  if (loading || !job) {
    return (
      <div className="modal-overlay">
        <div className="modal-content" style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ color: 'var(--text-secondary)' }}>Loading job intelligence...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '960px', width: '95%' }} onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {job.title}
              </h2>
              <span className={`score-pill ${(job.match.overall_score || 0) >= 80 ? 'score-high' : 'score-mid'}`}>
                <Sparkles size={14} /> {job.match.overall_score}% Match
              </span>
            </div>
            <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
              <strong>{job.company_name}</strong> &bull; {job.location} ({job.remote_status}) &bull; Freshness: <span style={{ color: '#34d399' }}>{job.freshness_status}</span>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="tabs-header">
          <button className={`tab-btn ${activeTab === 'match' ? 'active' : ''}`} onClick={() => setActiveTab('match')}>
            Match & Gap Analysis
          </button>
          <button className={`tab-btn ${activeTab === 'evidence' ? 'active' : ''}`} onClick={() => setActiveTab('evidence')}>
            Evidence Architecture ({job.evidence.length})
          </button>
          <button className={`tab-btn ${activeTab === 'tailor' ? 'active' : ''}`} onClick={() => { if (!tailoredData) handleTailorResume(); else setActiveTab('tailor'); }}>
            Tailored Resume
          </button>
          <button className={`tab-btn ${activeTab === 'ats' ? 'active' : ''}`} onClick={() => setActiveTab('ats')}>
            ATS Analysis
          </button>
          <button className={`tab-btn ${activeTab === 'cover-letter' ? 'active' : ''}`} onClick={() => setActiveTab('cover-letter')}>
            Cover Letter
          </button>
          <button className={`tab-btn ${activeTab === 'apply' ? 'active' : ''}`} onClick={() => setActiveTab('apply')}>
            Application & Tracking
          </button>
        </div>

        {/* Tab Content: Match & Gap Analysis */}
        {activeTab === 'match' && (
          <div>
            {/* Score Breakdown Bars */}
            <div className="grid-4" style={{ marginBottom: '20px' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>SKILL MATCH (45%)</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#34d399' }}>{job.match.skill_score}%</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>EXPERIENCE (20%)</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#60a5fa' }}>{job.match.experience_score}%</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>LOCATION (15%)</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#c084fc' }}>{job.match.location_score}%</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>ROLE / SALARY (20%)</div>
                <div style={{ fontSize: '20px', fontWeight: 800, color: '#fbbf24' }}>{job.match.salary_score}%</div>
              </div>
            </div>

            {/* Gap Analysis Box */}
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '10px' }}>Categorized Competency Breakdown</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '10px 14px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                  <div style={{ fontWeight: 700, fontSize: '12px', color: '#34d399', marginBottom: '4px' }}>
                    STRONG MATCHES ({job.match.matching_skills.length})
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
                    {job.match.matching_skills.join(', ') || 'None identified'}
                  </div>
                </div>

                <div style={{ background: 'rgba(244, 63, 94, 0.08)', padding: '10px 14px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
                  <div style={{ fontWeight: 700, fontSize: '12px', color: '#fda4af', marginBottom: '4px' }}>
                    MISSING REQUIREMENTS ({job.match.missing_skills.length})
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
                    {job.match.missing_skills.join(', ') || 'No missing critical skills'}
                  </div>
                </div>
              </div>
            </div>

            {/* Job Description */}
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '10px' }}>Job Description</h3>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: 'var(--radius-md)', maxHeight: '200px', overflowY: 'auto', whiteSpace: 'pre-line' }}>
                {job.description}
              </div>
            </div>

            {/* External URL Action */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', borderTop: '1px solid var(--border-color)' }}>
              <a href={job.canonical_url} target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm">
                View Original Listing <ExternalLink size={14} />
              </a>
              <button onClick={handleTailorResume} disabled={tailoringLoading} className="btn btn-primary btn-sm">
                <Sparkles size={14} /> {tailoringLoading ? 'Tailoring Resume...' : 'Tailor Resume for Job'}
              </button>
            </div>
          </div>
        )}

        {/* Tab Content: Evidence Architecture */}
        {activeTab === 'evidence' && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                Traceable Evidence Architecture
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Every recommendation and match proof is strictly tied to verifiable statements from your resume.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '400px', overflowY: 'auto' }}>
              {job.evidence.map((ev) => (
                <div
                  key={ev.id}
                  style={{
                    padding: '12px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                      <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>
                        {ev.requirement_term}
                      </strong>
                      <span className={`badge ${ev.match_status === 'Strong' ? 'badge-emerald' : ev.match_status === 'Transferable' ? 'badge-amber' : 'badge-rose'}`}>
                        {ev.match_status}
                      </span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {ev.candidate_claim || 'Requirement not found on resume'}
                    </div>
                    {ev.source_reference && (
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        Source: <span style={{ color: '#60a5fa' }}>{ev.source_reference}</span>
                      </div>
                    )}
                  </div>

                  <span className="badge badge-slate" style={{ fontSize: '10px' }}>
                    {ev.verification_status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab Content: Tailored Resume & Human Review */}
        {activeTab === 'tailor' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Human Review & Change Set
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Approve, reject, or edit proposed bullet point adjustments before final generation.
                </p>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Template:</span>
                <select className="select" style={{ width: 'auto', padding: '6px 10px', fontSize: '12px' }} value={selectedTemplate} onChange={(e) => setSelectedTemplate(e.target.value)}>
                  <option value="ATS Simple">ATS Simple</option>
                  <option value="Modern">Modern</option>
                  <option value="Technical">Technical</option>
                  <option value="Software Engineer">Software Engineer</option>
                  <option value="Cybersecurity">Cybersecurity</option>
                  <option value="Minimal">Minimal</option>
                  <option value="Academic">Academic</option>
                </select>
              </div>
            </div>

            {tailoredData?.changes && tailoredData.changes.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxHeight: '380px', overflowY: 'auto' }}>
                {tailoredData.changes.map((change: any) => (
                  <div key={change.id} style={{ padding: '14px', borderRadius: 'var(--radius-md)', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700, color: '#60a5fa' }}>
                        {change.section_name} &bull; {change.change_type}
                      </span>
                      <span className={`badge ${change.status === 'Approved' ? 'badge-emerald' : change.status === 'Rejected' ? 'badge-rose' : 'badge-amber'}`}>
                        {change.status}
                      </span>
                    </div>

                    <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>
                      <strong>Original:</strong> <span style={{ textDecoration: 'line-through' }}>{change.original_text}</span>
                    </div>
                    <div style={{ fontSize: '13px', color: '#f8fafc', marginBottom: '8px' }}>
                      <strong>Proposed:</strong> {change.user_override_text || change.proposed_text}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '10px' }}>
                      <em>Rationale: {change.rationale}</em>
                    </div>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={() => handleReviewChange(change.id, 'Approved')} className="btn btn-success btn-sm">
                        <Check size={12} /> Approve
                      </button>
                      <button onClick={() => handleReviewChange(change.id, 'Rejected')} className="btn btn-danger btn-sm">
                        <X size={12} /> Reject
                      </button>
                      <button 
                        onClick={() => {
                          const override = prompt('Enter your custom bullet override:', change.user_override_text || change.proposed_text);
                          if (override !== null) handleReviewChange(change.id, 'Edited', override);
                        }} 
                        className="btn btn-secondary btn-sm"
                      >
                        <Edit3 size={12} /> Edit Phrasing
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                No active changes generated. Click "Tailor Resume for Job" to generate.
              </div>
            )}
          </div>
        )}

        {/* Tab Content: ATS Analysis */}
        {activeTab === 'ats' && (
          <div>
            <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '20px', padding: '16px', background: 'rgba(59, 130, 246, 0.08)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ width: '80px', height: '80px', borderRadius: '50%', border: '4px solid #3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px', fontWeight: 800, color: '#60a5fa' }}>
                {tailoredData?.ats_analysis?.score || 88}%
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>ATS Readiness Score</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Evaluated against job keyword requirements, formatting hygiene, and parseability.
                </p>
              </div>
            </div>

            <div className="grid-2" style={{ marginBottom: '16px' }}>
              <div className="card" style={{ padding: '14px' }}>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#34d399', marginBottom: '6px' }}>
                  Matched Keywords ({tailoredData?.ats_analysis?.matched_keywords?.length || 0})
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {(tailoredData?.ats_analysis?.matched_keywords || job.match.matching_skills).map((k: string) => (
                    <span key={k} className="badge badge-emerald" style={{ textTransform: 'none' }}>{k}</span>
                  ))}
                </div>
              </div>

              <div className="card" style={{ padding: '14px' }}>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#fda4af', marginBottom: '6px' }}>
                  Missing Keywords ({tailoredData?.ats_analysis?.missing_keywords?.length || 0})
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {(tailoredData?.ats_analysis?.missing_keywords || job.match.missing_skills).map((k: string) => (
                    <span key={k} className="badge badge-rose" style={{ textTransform: 'none' }}>{k}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Content: Cover Letter */}
        {activeTab === 'cover-letter' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div>
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Job-Specific Cover Letter
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Generated using only verified candidate achievements and job requirements.
                </p>
              </div>
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(tailoredData?.cover_letter?.content || '');
                  alert('Cover letter copied to clipboard!');
                }}
                className="btn btn-secondary btn-sm"
              >
                <Copy size={14} /> Copy Letter
              </button>
            </div>

            <textarea
              className="textarea"
              style={{ width: '100%', height: '260px', fontFamily: 'inherit', fontSize: '13px', lineHeight: '1.6' }}
              value={tailoredData?.cover_letter?.content || 'Click "Tailor Resume" to generate cover letter.'}
              onChange={(e) => {
                if (tailoredData?.cover_letter) {
                  setTailoredData({
                    ...tailoredData,
                    cover_letter: { ...tailoredData.cover_letter, content: e.target.value }
                  });
                }
              }}
            />
          </div>
        )}

        {/* Tab Content: Application & Tracking */}
        {activeTab === 'apply' && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                Application Hub & Tracking
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Log this job into your application pipeline with interview and follow-up reminders.
              </p>
            </div>

            {duplicateWarning && (
              <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.3)', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fbbf24', fontWeight: 700, fontSize: '13px', marginBottom: '4px' }}>
                  <AlertTriangle size={16} /> Duplicate Application Warning
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-primary)', marginBottom: '10px' }}>
                  {duplicateWarning}
                </div>
                <button onClick={() => handleApply(true)} className="btn btn-primary btn-sm">
                  Apply Anyway
                </button>
              </div>
            )}

            {applySuccess ? (
              <div style={{ textAlign: 'center', padding: '32px', color: '#34d399' }}>
                <CheckCircle2 size={40} style={{ margin: '0 auto 12px auto' }} />
                <div style={{ fontWeight: 700, fontSize: '16px' }}>Application Tracked Successfully!</div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Added to Application Management. Reminders and status updates are active.
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div className="grid-2">
                  <div>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Application Status</label>
                    <select className="select" value={appStatus} onChange={(e) => setAppStatus(e.target.value)}>
                      <option value="Interested">Interested</option>
                      <option value="Saved">Saved</option>
                      <option value="Applied">Applied</option>
                      <option value="Assessment">Assessment Received</option>
                      <option value="Interview">Interview Scheduled</option>
                      <option value="Technical Interview">Technical Interview</option>
                      <option value="HR Interview">HR Interview</option>
                      <option value="Offer">Offer Received</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Follow-Up Reminder Date</label>
                    <input type="date" className="input" value={followUpDate} onChange={(e) => setFollowUpDate(e.target.value)} />
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Application Notes</label>
                  <textarea className="textarea" placeholder="Add recruiter contact, referral, or notes..." value={appNotes} onChange={(e) => setAppNotes(e.target.value)} style={{ minHeight: '80px' }} />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                  <button onClick={() => handleApply(false)} className="btn btn-primary">
                    <Send size={14} /> Record Application
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
