import React from 'react';
import { 
  Compass, Briefcase, Bookmark, FileText, CheckCircle2, 
  Send, Building2, Bell, Cpu, BarChart3, ShieldCheck
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  ollamaStatus?: string;
  telegramConnected?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  ollamaStatus = 'Unavailable',
  telegramConnected = false
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'jobs', label: 'Job Discovery', icon: Compass },
    { id: 'saved-searches', label: 'Saved Searches', icon: Bookmark },
    { id: 'resume', label: 'Resume & Claims', icon: FileText },
    { id: 'quality', label: 'Resume Quality', icon: ShieldCheck },
    { id: 'applications', label: 'Applications', icon: Briefcase },
    { id: 'companies', label: 'Companies', icon: Building2 },
    { id: 'telegram', label: 'Telegram Alerts', icon: Bell },
    { id: 'providers', label: 'Settings & Health', icon: Cpu },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ padding: '24px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '38px', height: '38px', borderRadius: '10px',
          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
        }}>
          <Compass size={22} color="#ffffff" />
        </div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '16px', letterSpacing: '-0.3px', color: '#ffffff' }}>
            CareerForge <span style={{ color: '#60a5fa' }}>AI</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
            India Career OS &bull; Local-First
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: '16px 0', overflowY: 'auto' }}>
        <div style={{ padding: '0 20px 8px 20px', fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
          Workspace
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
              style={{ width: 'calc(100% - 24px)', border: 'none', background: 'transparent', textAlign: 'left' }}
            >
              <Icon size={18} style={{ flexShrink: 0 }} />
              <span className="nav-text">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* System Status Indicators at bottom */}
      <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Ollama AI Engine</span>
          <span className={`badge ${ollamaStatus === 'Available' ? 'badge-emerald' : 'badge-amber'}`} style={{ fontSize: '9px' }}>
            {ollamaStatus === 'Available' ? 'Local LLM Active' : 'Deterministic'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Telegram Notifier</span>
          <span className={`badge ${telegramConnected ? 'badge-emerald' : 'badge-slate'}`} style={{ fontSize: '9px' }}>
            {telegramConnected ? 'Connected' : 'Offline'}
          </span>
        </div>
      </div>
    </aside>
  );
};
