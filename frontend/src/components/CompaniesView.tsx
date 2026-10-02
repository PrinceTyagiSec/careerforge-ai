import React, { useState, useEffect } from 'react';
import { Building2, Globe, MapPin, Star, Briefcase, ExternalLink } from 'lucide-react';
import { api } from '../api';

export const CompaniesView: React.FC = () => {
  const [companies, setCompanies] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const list = await api.listCompanies();
      setCompanies(list);
      if (list.length > 0) {
        const detail = await api.getCompanyDetail(list[0].id);
        setSelectedCompany(detail);
      }
    } catch (err) {
      console.error('Failed to load companies:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCompany = async (id: number) => {
    try {
      const detail = await api.getCompanyDetail(id);
      setSelectedCompany(detail);
    } catch (err) {
      console.error('Failed to load company detail:', err);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Company Intelligence Hub
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Directory of hiring employers discovered from live providers and your application history.
          </p>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
          Loading company profiles...
        </div>
      ) : companies.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <Building2 size={40} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
            No Companies Recorded
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            Companies are automatically aggregated when real-world jobs are discovered.
          </p>
        </div>
      ) : (
        <div className="grid-3" style={{ gridTemplateColumns: '1fr 1.5fr', gap: '24px' }}>
          {/* Companies List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {companies.map((c) => (
              <div
                key={c.id}
                onClick={() => handleSelectCompany(c.id)}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--radius-md)',
                  background: selectedCompany?.id === c.id ? 'rgba(59, 130, 246, 0.12)' : 'rgba(255,255,255,0.03)',
                  border: selectedCompany?.id === c.id ? '1px solid #3b82f6' : '1px solid var(--border-color)',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text-primary)', marginBottom: '2px' }}>
                    {c.name}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {c.location || 'India'} &bull; {c.industry || 'Technology'}
                  </div>
                </div>
                <span className="badge badge-blue">
                  {c.job_count} roles
                </span>
              </div>
            ))}
          </div>

          {/* Company Details */}
          {selectedCompany && (
            <div className="card">
              <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '18px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
                  {selectedCompany.name}
                </h2>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  {selectedCompany.location} &bull; {selectedCompany.industry || 'Tech & Software'}
                </div>
              </div>

              {/* Active Jobs at this Company */}
              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '10px' }}>
                  Open Positions ({selectedCompany.jobs.length})
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {selectedCompany.jobs.map((j: any) => (
                    <div key={j.id} style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>{j.title}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{j.location} &bull; {j.remote_status}</div>
                      </div>
                      <span className="badge badge-emerald">{j.freshness_status}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* User Previous Applications */}
              <div>
                <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '10px' }}>
                  Your Interaction History
                </h3>
                {selectedCompany.user_applications.length === 0 ? (
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    No previous applications submitted to this company.
                  </div>
                ) : (
                  selectedCompany.user_applications.map((a: any) => (
                    <div key={a.id} style={{ padding: '8px 12px', borderRadius: 'var(--radius-sm)', background: 'rgba(59, 130, 246, 0.08)', fontSize: '12px' }}>
                      Status: <strong>{a.status}</strong> &bull; Applied: {new Date(a.applied_at).toLocaleDateString()}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
