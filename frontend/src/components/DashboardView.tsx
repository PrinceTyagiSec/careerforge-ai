import React, { useEffect, useState } from 'react';
import { 
  BarChart3, Briefcase, Bookmark, Award, AlertCircle, 
  TrendingUp, ArrowRight, ShieldCheck, Compass, Upload, CheckCircle2
} from 'lucide-react';
import { api, DashboardAnalytics, JobItem } from '../api';

interface DashboardProps {
  onNavigate: (tab: string, jobId?: number) => void;
  onOpenImport: () => void;
}

export const DashboardView: React.FC<DashboardProps> = ({ onNavigate, onOpenImport }) => {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [topJobs, setTopJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const [analyticsData, jobsData] = await Promise.all([
        api.getDashboardAnalytics(),
        api.listJobs({ page: 1, page_size: 4 })
      ]);
      setAnalytics(analyticsData);
      setTopJobs(jobsData.results || []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !analytics) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Loading CareerForge Operating System...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Top Banner / Welcome */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Candidate Overview & Intelligence
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Target Market: <strong style={{ color: '#60a5fa' }}>India Tech Ecosystem</strong> (INR &bull; Remote & Hubs: Bengaluru, Noida, Gurugram, Pune, Hyderabad)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => onNavigate('resume')} className="btn btn-secondary btn-sm">
            <Upload size={14} /> Upload Resume
          </button>
          <button onClick={onOpenImport} className="btn btn-secondary btn-sm">
            <Compass size={14} /> Import Job
          </button>
          <button onClick={() => onNavigate('jobs')} className="btn btn-primary btn-sm">
            Discover Real Jobs <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase' }}>Jobs Discovered</span>
            <Compass size={18} color="#60a5fa" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)' }}>
            {analytics?.total_jobs_discovered || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Adzuna + Jooble + Imports
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase' }}>Applications Active</span>
            <Briefcase size={18} color="#34d399" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)' }}>
            {analytics?.total_applied || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Tracked in Application Hub
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase' }}>Interviews & Outcomes</span>
            <Award size={18} color="#fbbf24" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)' }}>
            {analytics?.total_interviews || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Response Rate: <strong style={{ color: '#34d399' }}>{analytics?.response_rate_pct || 0}%</strong>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase' }}>Resume Quality</span>
            <ShieldCheck size={18} color="#c084fc" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)' }}>
            {analytics?.resume_quality_score ? `${analytics.resume_quality_score}%` : '85%'}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            ATS Structural & Fact Integrity
          </div>
        </div>
      </div>

      {/* Main Grid: Recommended Jobs & Skill Gaps */}
      <div className="grid-3" style={{ gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '28px' }}>
        {/* Recommended Jobs */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Top Matched Opportunities
            </h2>
            <button onClick={() => onNavigate('jobs')} className="btn btn-outline btn-sm">
              View All
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {topJobs.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                No jobs in database yet. Click "Discover Real Jobs" to query live providers.
              </div>
            ) : (
              topJobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => onNavigate('jobs', job.id)}
                  style={{
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-color)',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'all 0.15s ease'
                  }}
                  className="card-clickable"
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text-primary)' }}>
                        {job.title}
                      </span>
                      <span className="badge badge-blue" style={{ fontSize: '10px' }}>
                        {job.remote_status}
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                      {job.company_name} &bull; {job.location}
                    </div>
                    <div style={{ display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' }}>
                      {job.matching_skills.slice(0, 3).map((sk) => (
                        <span key={sk} className="badge badge-emerald" style={{ fontSize: '10px', textTransform: 'none' }}>
                          ✓ {sk}
                        </span>
                      ))}
                      {job.missing_skills.slice(0, 1).map((sk) => (
                        <span key={sk} className="badge badge-rose" style={{ fontSize: '10px', textTransform: 'none' }}>
                          ✗ {sk}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div className={`score-pill ${(job.match_score || 0) >= 80 ? 'score-high' : 'score-mid'}`}>
                      {job.match_score || 75}% Match
                    </div>
                    {job.salary_min && (
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', fontWeight: 600 }}>
                        ₹{(job.salary_min / 100000).toFixed(1)}L - ₹{((job.salary_max || job.salary_min * 1.5) / 100000).toFixed(1)}L
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Skill Gap Analysis */}
        <div className="card">
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
            Top Indian Market Skill Gaps
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Skills demanded by matching job listings that were not found on your verified resume:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {analytics?.top_skill_gaps && analytics.top_skill_gaps.length > 0 ? (
              analytics.top_skill_gaps.map((item) => (
                <div
                  key={item.skill}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(244, 63, 94, 0.08)',
                    border: '1px solid rgba(244, 63, 94, 0.2)'
                  }}
                >
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#fda4af' }}>
                    {item.skill}
                  </span>
                  <span className="badge badge-rose" style={{ fontSize: '10px' }}>
                    {item.count} roles
                  </span>
                </div>
              ))
            ) : (
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                No significant gaps identified. Great coverage!
              </div>
            )}
          </div>

          <div style={{ marginTop: '24px', padding: '12px', borderRadius: 'var(--radius-md)', background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#60a5fa', fontWeight: 600, fontSize: '12px', marginBottom: '4px' }}>
              <ShieldCheck size={16} /> Factual Claim Protection
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              CareerForge never invents experience or skills. You can add newly acquired skills in your Candidate Profile.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
