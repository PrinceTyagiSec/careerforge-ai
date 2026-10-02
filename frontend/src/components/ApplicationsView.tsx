import React, { useState, useEffect } from 'react';
import { 
  Briefcase, Calendar, Clock, CheckCircle2, ChevronRight, 
  MessageSquare, Plus, AlertCircle, FileText
} from 'lucide-react';
import { api, ApplicationItem } from '../api';

export const ApplicationsView: React.FC = () => {
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [selectedApp, setSelectedApp] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [newNote, setNewNote] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      setLoading(true);
      const list = await api.listApplications();
      setApplications(list);
      if (list.length > 0 && !selectedApp) {
        loadDetail(list[0].id);
      }
    } catch (err) {
      console.error('Failed to load applications:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadDetail = async (id: number) => {
    try {
      setDetailLoading(true);
      const detail = await api.getApplicationDetail(id);
      setSelectedApp(detail);
    } catch (err) {
      console.error('Failed to load detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedApp) return;
    try {
      await api.updateApplicationStatus(selectedApp.id, { status: newStatus });
      await loadDetail(selectedApp.id);
      await loadApplications();
    } catch (err) {
      console.error('Status update failed:', err);
    }
  };

  const handleAddNote = async () => {
    if (!selectedApp || !newNote.trim()) return;
    try {
      await api.addApplicationNote(selectedApp.id, newNote);
      setNewNote('');
      await loadDetail(selectedApp.id);
    } catch (err) {
      console.error('Add note failed:', err);
    }
  };

  const filteredApps = statusFilter === 'All' 
    ? applications 
    : applications.filter(a => a.status === statusFilter);

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Application Management & Timeline
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Track interviews, follow-up deadlines, notes, and full application history.
          </p>
        </div>

        {/* Status Filter */}
        <select className="select" style={{ width: 'auto' }} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="All">All Stages</option>
          <option value="Applied">Applied</option>
          <option value="Assessment">Assessment</option>
          <option value="Interview">Interview</option>
          <option value="Technical Interview">Technical Interview</option>
          <option value="Offer">Offer</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
          Loading tracked applications...
        </div>
      ) : applications.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <Briefcase size={40} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
            No Active Applications Yet
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            Find a job in Job Discovery, tailor your resume, and click "Record Application".
          </p>
        </div>
      ) : (
        <div className="grid-3" style={{ gridTemplateColumns: '1fr 1.5fr', gap: '24px' }}>
          {/* Applications Master List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {filteredApps.map((app) => (
              <div
                key={app.id}
                onClick={() => loadDetail(app.id)}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--radius-md)',
                  background: selectedApp?.id === app.id ? 'rgba(59, 130, 246, 0.12)' : 'rgba(255,255,255,0.03)',
                  border: selectedApp?.id === app.id ? '1px solid #3b82f6' : '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text-primary)' }}>
                    {app.job_title}
                  </span>
                  <span className={`badge ${app.status === 'Offer' ? 'badge-emerald' : app.status.includes('Interview') ? 'badge-purple' : 'badge-blue'}`}>
                    {app.status}
                  </span>
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  {app.company_name} &bull; {app.location}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span>Applied: {new Date(app.applied_at).toLocaleDateString()}</span>
                  {app.interview_date && (
                    <span style={{ color: '#fbbf24', fontWeight: 600 }}>
                      Interview: {new Date(app.interview_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Selected Application Timeline & Detail */}
          {selectedApp && (
            <div className="card">
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '18px' }}>
                <div>
                  <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {selectedApp.job_title}
                  </h2>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                    {selectedApp.company_name} &bull; {selectedApp.location}
                  </div>
                </div>

                {/* Stage Progression Selector */}
                <select
                  className="select"
                  style={{ width: 'auto', padding: '6px 12px', fontSize: '12px' }}
                  value={selectedApp.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                >
                  <option value="Interested">Interested</option>
                  <option value="Saved">Saved</option>
                  <option value="Applied">Applied</option>
                  <option value="Assessment">Assessment</option>
                  <option value="Interview">Interview</option>
                  <option value="Technical Interview">Technical Interview</option>
                  <option value="HR Interview">HR Interview</option>
                  <option value="Offer">Offer</option>
                  <option value="Rejected">Rejected</option>
                  <option value="Withdrawn">Withdrawn</option>
                </select>
              </div>

              {/* Reminders Pill */}
              {(selectedApp.follow_up_date || selectedApp.interview_date) && (
                <div style={{ display: 'flex', gap: '12px', padding: '12px', borderRadius: 'var(--radius-md)', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.25)', marginBottom: '18px' }}>
                  <Calendar size={18} color="#fbbf24" style={{ flexShrink: 0 }} />
                  <div style={{ fontSize: '12px', color: 'var(--text-primary)' }}>
                    {selectedApp.interview_date && (
                      <div>Scheduled Interview: <strong>{new Date(selectedApp.interview_date).toLocaleString()}</strong></div>
                    )}
                    {selectedApp.follow_up_date && (
                      <div>Follow-Up Reminder: <strong>{new Date(selectedApp.follow_up_date).toLocaleDateString()}</strong></div>
                    )}
                  </div>
                </div>
              )}

              {/* Application Timeline */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
                  Chronological Timeline Events (Section 29)
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', borderLeft: '2px solid rgba(255,255,255,0.1)', paddingLeft: '16px' }}>
                  {selectedApp.events.map((ev: any) => (
                    <div key={ev.id} style={{ position: 'relative' }}>
                      <div style={{ position: 'absolute', left: '-21px', top: '4px', width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6' }} />
                      <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {ev.title}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {ev.description}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {new Date(ev.occurred_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Application Notes */}
              <div>
                <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '10px' }}>
                  Application Notes & Contacts
                </h3>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                  <input
                    type="text"
                    className="input"
                    placeholder="Add interview notes or recruiter contacts..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAddNote(); }}
                  />
                  <button onClick={handleAddNote} className="btn btn-primary btn-sm">
                    <Plus size={14} /> Add Note
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
                  {selectedApp.notes.map((n: any) => (
                    <div key={n.id} style={{ padding: '8px 12px', borderRadius: 'var(--radius-sm)', background: 'rgba(255,255,255,0.03)', fontSize: '12px' }}>
                      <div style={{ color: 'var(--text-primary)' }}>{n.content}</div>
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {new Date(n.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
