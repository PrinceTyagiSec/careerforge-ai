import React, { useState, useEffect } from 'react';
import { 
  Compass, Search, Filter, Bookmark, Sparkles, 
  MapPin, IndianRupee, Clock, Globe, ArrowUpRight, Plus, RefreshCw, Check
} from 'lucide-react';
import { api, JobItem } from '../api';

interface JobsViewProps {
  onSelectJob: (jobId: number) => void;
  onOpenImport: () => void;
  selectedJobId?: number;
}

export const JobsView: React.FC<JobsViewProps> = ({ onSelectJob, onOpenImport }) => {
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [liveSearching, setLiveSearching] = useState(false);
  
  // Filters
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('All');
  const [remoteStatus, setRemoteStatus] = useState('All');
  const [freshness, setFreshness] = useState('All');
  const [minMatch, setMinMatch] = useState<number>(0);
  const [savedOnly, setSavedOnly] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, [keywords, location, remoteStatus, freshness, minMatch, savedOnly]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (keywords) params.keywords = keywords;
      if (location !== 'All') params.location = location;
      if (remoteStatus !== 'All') params.remote_status = remoteStatus;
      if (freshness !== 'All') params.freshness = freshness;
      if (minMatch > 0) params.min_match = minMatch;
      if (savedOnly) params.saved_only = true;

      const data = await api.listJobs(params);
      setJobs(data.results || []);
    } catch (err) {
      console.error('Failed to list jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLiveProviderSearch = async () => {
    try {
      setLiveSearching(true);
      const searchLoc = location !== 'All' ? location : 'India';
      await api.searchLiveJobs(keywords || undefined, searchLoc);
      await fetchJobs();
    } catch (err) {
      console.error('Live search error:', err);
      alert('External provider query failed or rate-limited. Operating with current local database jobs.');
    } finally {
      setLiveSearching(false);
    }
  };

  const handleToggleSave = async (e: React.MouseEvent, jobId: number) => {
    e.stopPropagation();
    try {
      const res = await api.toggleSaveJob(jobId);
      setJobs(jobs.map(j => j.id === jobId ? { ...j, is_saved: res.is_saved } : j));
    } catch (err) {
      console.error('Save toggle error:', err);
    }
  };

  return (
    <div>
      {/* Header & Main Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Real-World Job Discovery
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Normalized, deduplicated, and ranked against your candidate profile.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={onOpenImport} className="btn btn-secondary">
            <Plus size={16} /> Import Job
          </button>
          <button 
            onClick={handleLiveProviderSearch} 
            disabled={liveSearching}
            className="btn btn-primary"
          >
            <RefreshCw size={16} className={liveSearching ? 'spin' : ''} />
            {liveSearching ? 'Querying Providers...' : 'Query Live Providers (Adzuna + Jooble)'}
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="card" style={{ padding: '18px', marginBottom: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr auto', gap: '12px', alignItems: 'center' }}>
          {/* Keyword Search */}
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="input"
              placeholder="Search by title, skill, or employer (e.g. Python, FastAPI, Razorpay)..."
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              style={{ paddingLeft: '36px' }}
            />
          </div>

          {/* Indian Locations */}
          <select className="select" value={location} onChange={(e) => setLocation(e.target.value)}>
            <option value="All">All Locations</option>
            <option value="Remote India">Remote India</option>
            <option value="Bengaluru">Bengaluru</option>
            <option value="Noida">Noida / NCR</option>
            <option value="Gurugram">Gurugram</option>
            <option value="Hyderabad">Hyderabad</option>
            <option value="Pune">Pune</option>
            <option value="Mumbai">Mumbai</option>
            <option value="Chennai">Chennai</option>
          </select>

          {/* Remote status */}
          <select className="select" value={remoteStatus} onChange={(e) => setRemoteStatus(e.target.value)}>
            <option value="All">Work Type: All</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
            <option value="On-site">On-site</option>
          </select>

          {/* Freshness */}
          <select className="select" value={freshness} onChange={(e) => setFreshness(e.target.value)}>
            <option value="All">Freshness: Any</option>
            <option value="Fresh">Fresh (&le; 5 days)</option>
            <option value="Recently Updated">Recently Updated</option>
          </select>

          {/* Saved Toggle */}
          <button
            onClick={() => setSavedOnly(!savedOnly)}
            className={`btn ${savedOnly ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '10px 14px' }}
          >
            <Bookmark size={16} /> Saved Only
          </button>
        </div>
      </div>

      {/* Results Count & Meta */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Showing <strong>{jobs.length}</strong> real-world opportunities
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
          <span>Deduplication: Active</span> &bull; <span>Market: India</span> &bull; <span>Currency: INR (₹)</span>
        </div>
      </div>

      {/* Jobs List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
          Searching and ranking positions...
        </div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <Compass size={36} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
            No jobs match the current filters
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
            Try broadening your location or keyword filters, or click "Query Live Providers" to fetch fresh listings.
          </p>
          <button onClick={handleLiveProviderSearch} className="btn btn-primary btn-sm">
            Fetch Fresh Jobs from Providers
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {jobs.map((job) => {
            const matchScore = job.match_score || 70;
            return (
              <div
                key={job.id}
                onClick={() => onSelectJob(job.id)}
                className="card card-clickable"
                style={{ padding: '20px', cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  {/* Left Column: Title, Company, Meta */}
                  <div style={{ flex: 1, paddingRight: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {job.title}
                      </span>
                      <span className="badge badge-blue">
                        {job.remote_status}
                      </span>
                      <span className={`badge ${job.freshness_status === 'Fresh' ? 'badge-emerald' : 'badge-slate'}`}>
                        {job.freshness_status}
                      </span>
                      {job.application_status && (
                        <span className="badge badge-purple">
                          Status: {job.application_status}
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '10px' }}>
                      <strong style={{ color: 'var(--text-primary)' }}>{job.company_name}</strong>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <MapPin size={13} /> {job.location}
                      </span>
                      {job.salary_min && (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#34d399', fontWeight: 600 }}>
                          <IndianRupee size={13} /> ₹{(job.salary_min / 100000).toFixed(1)}L - ₹{((job.salary_max || job.salary_min * 1.5) / 100000).toFixed(1)}L LPA
                        </span>
                      )}
                    </div>

                    {/* Matching & Missing Skills */}
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap', marginBottom: '10px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>Matched:</span>
                      {job.matching_skills.slice(0, 5).map((sk) => (
                        <span key={sk} className="badge badge-emerald" style={{ textTransform: 'none', fontSize: '11px' }}>
                          ✓ {sk}
                        </span>
                      ))}
                      {job.missing_skills.length > 0 && (
                        <>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, marginLeft: '6px' }}>Missing:</span>
                          {job.missing_skills.slice(0, 3).map((sk) => (
                            <span key={sk} className="badge badge-rose" style={{ textTransform: 'none', fontSize: '11px' }}>
                              ✗ {sk}
                            </span>
                          ))}
                        </>
                      )}
                    </div>

                    {/* Sources Attribution */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                      <span>Sources:</span>
                      {job.sources.map((s, idx) => (
                        <span key={idx} style={{ background: 'rgba(255,255,255,0.06)', padding: '2px 6px', borderRadius: '4px', color: '#cbd5e1' }}>
                          {s.provider_name}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Right Column: Match Score & Action Buttons */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '12px' }}>
                    <div className={`score-pill ${matchScore >= 80 ? 'score-high' : 'score-mid'}`} style={{ fontSize: '14px', padding: '6px 14px' }}>
                      <Sparkles size={14} /> {matchScore}% Match
                    </div>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={(e) => handleToggleSave(e, job.id)}
                        className={`btn ${job.is_saved ? 'btn-primary' : 'btn-outline'} btn-sm`}
                        title={job.is_saved ? 'Unsave job' : 'Save job'}
                      >
                        <Bookmark size={14} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectJob(job.id);
                        }}
                        className="btn btn-secondary btn-sm"
                      >
                        Analyze & Tailor <ArrowUpRight size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
