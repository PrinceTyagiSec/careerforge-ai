import React, { useState, useEffect } from 'react';
import { 
  Bookmark, Play, Trash2, Plus, Clock, Bell, CheckCircle2, AlertCircle
} from 'lucide-react';
import { api, SavedSearchItem } from '../api';

export const SavedSearchesView: React.FC = () => {
  const [searches, setSearches] = useState<SavedSearchItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('Remote India');
  const [minSalary, setMinSalary] = useState('');
  const [frequency, setFrequency] = useState('360');
  const [notifyTelegram, setNotifyTelegram] = useState(true);
  const [minThreshold, setMinThreshold] = useState('75');

  useEffect(() => {
    loadSearches();
  }, []);

  const loadSearches = async () => {
    try {
      setLoading(true);
      const list = await api.listSavedSearches();
      setSearches(list);
    } catch (err) {
      console.error('Failed to load saved searches:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createSavedSearch({
        name,
        keywords: keywords || undefined,
        location,
        min_salary: minSalary ? parseFloat(minSalary) : undefined,
        frequency_minutes: parseInt(frequency),
        notify_telegram: notifyTelegram,
        min_match_threshold: parseFloat(minThreshold)
      });
      setShowCreateModal(false);
      resetForm();
      await loadSearches();
    } catch (err) {
      console.error('Create search failed:', err);
    }
  };

  const handleRunNow = async (id: number) => {
    try {
      await api.runSavedSearchNow(id);
      alert('Background monitoring triggered for saved search. Results will refresh shortly.');
      await loadSearches();
    } catch (err) {
      console.error('Run search error:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this saved search?')) return;
    try {
      await api.deleteSavedSearch(id);
      await loadSearches();
    } catch (err) {
      console.error('Delete search error:', err);
    }
  };

  const resetForm = () => {
    setName('');
    setKeywords('');
    setLocation('Remote India');
    setMinSalary('');
    setFrequency('360');
    setNotifyTelegram(true);
    setMinThreshold('75');
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Automated Job Monitoring & Saved Searches
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Continuous background discovery, deduplication, personalized ranking, and Telegram alerts.
          </p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
          <Plus size={16} /> New Saved Search
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
          Loading saved searches...
        </div>
      ) : searches.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <Bookmark size={40} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
            No Saved Searches Configured
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
            Create an automated search monitor to continuously query Adzuna & Jooble in the background.
          </p>
          <button onClick={() => setShowCreateModal(true)} className="btn btn-primary btn-sm">
            Create First Saved Search
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {searches.map((s) => (
            <div key={s.id} className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {s.name}
                    </span>
                    <span className="badge badge-blue">
                      Every {s.frequency_minutes >= 60 ? `${s.frequency_minutes / 60} hrs` : `${s.frequency_minutes} mins`}
                    </span>
                    {s.notify_telegram && (
                      <span className="badge badge-emerald">
                        Telegram Alerts (&ge;{s.min_match_threshold}%)
                      </span>
                    )}
                  </div>

                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                    Keywords: <strong>{s.keywords || 'Any Tech Role'}</strong> &bull; Location: <strong>{s.location}</strong>
                  </div>

                  <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--text-muted)' }}>
                    <span>Total Discovered: <strong style={{ color: 'var(--text-primary)' }}>{s.total_found_count}</strong></span> &bull;
                    <span>High Matches: <strong style={{ color: '#34d399' }}>{s.high_match_count}</strong></span> &bull;
                    <span>Last Run: {s.last_run_at ? new Date(s.last_run_at).toLocaleString() : 'Pending initial run'}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button onClick={() => handleRunNow(s.id)} className="btn btn-secondary btn-sm" title="Execute background monitor immediately">
                    <Play size={14} /> Run Now
                  </button>
                  <button onClick={() => handleDelete(s.id)} className="btn btn-outline btn-sm" title="Delete monitor">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Create Saved Search */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '16px' }}>
              Create Automated Search Monitor
            </h2>
            <form onSubmit={handleCreateSearch} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Monitor Name</label>
                <input type="text" className="input" placeholder="e.g. Remote Python Backend Roles" value={name} onChange={(e) => setName(e.target.value)} required />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Search Keywords</label>
                <input type="text" className="input" placeholder="e.g. Python, FastAPI, Django" value={keywords} onChange={(e) => setKeywords(e.target.value)} />
              </div>

              <div className="grid-2">
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Location</label>
                  <input type="text" className="input" placeholder="e.g. Remote India or Bengaluru" value={location} onChange={(e) => setLocation(e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Run Frequency</label>
                  <select className="select" value={frequency} onChange={(e) => setFrequency(e.target.value)}>
                    <option value="60">Every 1 Hour</option>
                    <option value="180">Every 3 Hours</option>
                    <option value="360">Every 6 Hours (Recommended)</option>
                    <option value="720">Every 12 Hours</option>
                    <option value="1440">Every 24 Hours</option>
                  </select>
                </div>
              </div>

              <div className="grid-2">
                <div>
                  <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Min Match Score Alert Threshold</label>
                  <input type="number" className="input" value={minThreshold} onChange={(e) => setMinThreshold(e.target.value)} min="50" max="95" />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', paddingTop: '20px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', color: 'var(--text-primary)' }}>
                    <input type="checkbox" checked={notifyTelegram} onChange={(e) => setNotifyTelegram(e.target.checked)} />
                    Dispatch Telegram Job Alerts
                  </label>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn btn-outline">Cancel</button>
                <button type="submit" className="btn btn-primary">Create Monitor</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
