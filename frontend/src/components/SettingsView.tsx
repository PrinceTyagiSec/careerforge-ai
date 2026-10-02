import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, AlertCircle, RefreshCw, Key, Shield, User, MapPin, IndianRupee } from 'lucide-react';
import { api, CandidateProfile } from '../api';

export const SettingsView: React.FC = () => {
  const [healthData, setHealthData] = useState<any | null>(null);
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Credential forms
  const [adzunaId, setAdzunaId] = useState('');
  const [adzunaKey, setAdzunaKey] = useState('');
  const [joobleKey, setJoobleKey] = useState('');

  // Profile fields
  const [headline, setHeadline] = useState('');
  const [location, setLocation] = useState('Bengaluru, Karnataka');
  const [remotePref, setRemotePref] = useState('Flexible');
  const [expectedSalary, setExpectedSalary] = useState('1500000');
  const [yearsExp, setYearsExp] = useState('3.0');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const [h, p, t] = await Promise.all([
        api.getProvidersHealth(),
        api.getProfile(),
        api.listBackgroundTasks()
      ]);
      setHealthData(h);
      setProfile(p);
      setTasks(t);

      if (p) {
        setHeadline(p.headline || '');
        setLocation(p.location || 'Bengaluru, Karnataka');
        setRemotePref(p.remote_preference || 'Flexible');
        setExpectedSalary(p.expected_salary_min ? p.expected_salary_min.toString() : '1500000');
        setYearsExp(p.years_of_experience ? p.years_of_experience.toString() : '3.0');
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAdzuna = async () => {
    try {
      await api.updateCredentials({
        provider_name: 'adzuna',
        app_id_or_user: adzunaId,
        api_key_or_token: adzunaKey,
        is_enabled: true
      });
      alert('Adzuna API credentials updated! Checking health...');
      await loadSettings();
    } catch (err) {
      console.error('Save Adzuna error:', err);
    }
  };

  const handleSaveJooble = async () => {
    try {
      await api.updateCredentials({
        provider_name: 'jooble',
        api_key_or_token: joobleKey,
        is_enabled: true
      });
      alert('Jooble API key updated! Checking health...');
      await loadSettings();
    } catch (err) {
      console.error('Save Jooble error:', err);
    }
  };

  const handleSaveProfile = async () => {
    try {
      await api.updateProfile({
        headline,
        location,
        remote_preference: remotePref,
        expected_salary_min: parseFloat(expectedSalary),
        years_of_experience: parseFloat(yearsExp)
      });
      alert('Candidate Profile and India market preferences updated!');
    } catch (err) {
      console.error('Save profile error:', err);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            System Health & Provider Integrations
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Configure live job providers (Adzuna & Jooble), monitor Ollama AI status, and manage profile preferences.
          </p>
        </div>
        <button onClick={loadSettings} className="btn btn-secondary btn-sm">
          <RefreshCw size={14} /> Refresh Health
        </button>
      </div>

      {/* Provider Health Dashboard */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Provider Status & Graceful Degradation (Section 57)
        </h2>
        <div className="grid-3" style={{ gap: '14px' }}>
          {/* Adzuna */}
          <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>Adzuna Jobs API</strong>
              <span className={`badge ${healthData?.providers?.find((p: any) => p.provider_name === 'Adzuna')?.status === 'Connected' ? 'badge-emerald' : 'badge-amber'}`}>
                {healthData?.providers?.find((p: any) => p.provider_name === 'Adzuna')?.status || 'Configuring'}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Primary India Job Listings & Aggregation
            </div>
          </div>

          {/* Jooble */}
          <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>Jooble Jobs API</strong>
              <span className={`badge ${healthData?.providers?.find((p: any) => p.provider_name === 'Jooble')?.status === 'Connected' ? 'badge-emerald' : 'badge-amber'}`}>
                {healthData?.providers?.find((p: any) => p.provider_name === 'Jooble')?.status || 'Configuring'}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Secondary Aggregator & Global Search
            </div>
          </div>

          {/* Ollama Local AI */}
          <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>Ollama Local AI</strong>
              <span className={`badge ${healthData?.ollama?.status === 'Available' ? 'badge-emerald' : 'badge-blue'}`}>
                {healthData?.ollama?.status === 'Available' ? 'Available (Local)' : 'Deterministic Active'}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Offline-Safe Fallback: Enabled
            </div>
          </div>
        </div>
      </div>

      {/* Credentials Forms Grid */}
      <div className="grid-2" style={{ gap: '24px', marginBottom: '24px' }}>
        {/* Adzuna Config */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
            Adzuna API Credentials
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>App ID</label>
              <input type="text" className="input" placeholder="Enter Adzuna App ID" value={adzunaId} onChange={(e) => setAdzunaId(e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>App Key</label>
              <input type="password" className="input" placeholder="Enter Adzuna App Key" value={adzunaKey} onChange={(e) => setAdzunaKey(e.target.value)} />
            </div>
            <button onClick={handleSaveAdzuna} className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-start' }}>
              Save Adzuna Credentials
            </button>
          </div>
        </div>

        {/* Jooble Config */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>
            Jooble API Credentials
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Jooble API Key</label>
              <input type="password" className="input" placeholder="Enter Jooble API Key" value={joobleKey} onChange={(e) => setJoobleKey(e.target.value)} />
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Jobs are queried with real-time rate limiting, pagination, and multi-signal deduplication.
            </div>
            <button onClick={handleSaveJooble} className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-start' }}>
              Save Jooble Credentials
            </button>
          </div>
        </div>
      </div>

      {/* Candidate Preferences (India Focus) */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Candidate Profile & India Market Preferences
        </h2>
        <div className="grid-2" style={{ gap: '16px', marginBottom: '16px' }}>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Target Role / Headline</label>
            <input type="text" className="input" value={headline} onChange={(e) => setHeadline(e.target.value)} />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Primary City / Region</label>
            <input type="text" className="input" value={location} onChange={(e) => setLocation(e.target.value)} />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Remote Preference</label>
            <select className="select" value={remotePref} onChange={(e) => setRemotePref(e.target.value)}>
              <option value="Remote">Remote Only</option>
              <option value="Hybrid">Hybrid</option>
              <option value="On-site">On-site</option>
              <option value="Flexible">Flexible (Remote / Hybrid)</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Expected Annual Salary (₹ INR)</label>
            <input type="number" className="input" value={expectedSalary} onChange={(e) => setExpectedSalary(e.target.value)} />
          </div>
        </div>

        <button onClick={handleSaveProfile} className="btn btn-primary btn-sm">
          Save Preferences
        </button>
      </div>

      {/* Background Tasks Log */}
      <div className="card">
        <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Background Task Execution History (Section 8)
        </h2>
        {tasks.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No background tasks executed yet.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {tasks.map((t) => (
              <div key={t.id} style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>{t.task_name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    ID: {t.task_identifier} &bull; {t.result_summary || 'Running...'}
                  </div>
                </div>
                <span className={`badge ${t.status === 'Completed' ? 'badge-emerald' : t.status === 'Running' ? 'badge-blue' : 'badge-rose'}`}>
                  {t.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
