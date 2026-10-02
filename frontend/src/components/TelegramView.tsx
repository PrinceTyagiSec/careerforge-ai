import React, { useState, useEffect } from 'react';
import { Bell, Send, CheckCircle2, AlertCircle, Shield, Clock } from 'lucide-react';
import { api } from '../api';

export const TelegramView: React.FC = () => {
  const [status, setStatus] = useState<any | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Form State
  const [botToken, setBotToken] = useState('');
  const [chatId, setChatId] = useState('');
  const [minMatch, setMinMatch] = useState(75);
  const [dailyLimit, setDailyLimit] = useState(15);
  const [quietHours, setQuietHours] = useState(false);
  const [quietStart, setQuietStart] = useState('22:00');
  const [quietEnd, setQuietEnd] = useState('08:00');

  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  useEffect(() => {
    loadTelegramData();
  }, []);

  const loadTelegramData = async () => {
    try {
      setLoading(true);
      const [s, h] = await Promise.all([
        api.getTelegramStatus(),
        api.getTelegramHistory()
      ]);
      setStatus(s);
      setHistory(h);
      if (s.chat_id) setChatId(s.chat_id);
      if (s.preferences) {
        setMinMatch(s.preferences.min_match_percentage);
        setDailyLimit(s.preferences.daily_notification_limit);
        setQuietHours(s.preferences.quiet_hours_enabled);
        setQuietStart(s.preferences.quiet_hours_start);
        setQuietEnd(s.preferences.quiet_hours_end);
      }
    } catch (err) {
      console.error('Failed to load telegram data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setTesting(true);
      setTestResult(null);
      const res = await api.configureTelegram(botToken, chatId, true);
      if (res.success) {
        setTestResult('Success: Telegram connected and verification message sent!');
        await loadTelegramData();
      } else {
        setTestResult(`Error: ${res.error}`);
      }
    } catch (err: any) {
      setTestResult(`Error: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  const handleSavePreferences = async () => {
    try {
      await api.updateTelegramPrefs({
        min_match_percentage: minMatch,
        daily_notification_limit: dailyLimit,
        quiet_hours_enabled: quietHours,
        quiet_hours_start: quietStart,
        quiet_hours_end: quietEnd
      });
      alert('Notification preferences updated!');
    } catch (err) {
      console.error('Failed to update preferences:', err);
    }
  };

  const handleTestNow = async () => {
    try {
      setTesting(true);
      const res = await api.testTelegram();
      if (res.success) {
        alert('Test notification delivered to Telegram!');
      } else {
        alert(`Failed: ${res.error}`);
      }
    } catch (err: any) {
      alert(`Test failed: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Telegram Job Alerts & Interview Reminders
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Instant notifications for high-match opportunities, scheduled interviews, and follow-ups.
          </p>
        </div>
        {status?.is_connected && (
          <button onClick={handleTestNow} disabled={testing} className="btn btn-secondary btn-sm">
            <Send size={14} /> {testing ? 'Sending Test...' : 'Send Test Notification'}
          </button>
        )}
      </div>

      <div className="grid-2" style={{ gap: '24px', marginBottom: '24px' }}>
        {/* Bot Credentials Form */}
        <div className="card">
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
            Telegram Bot Configuration
          </h2>
          <form onSubmit={handleSaveConfig} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
                Telegram Bot Token
              </label>
              <input
                type="password"
                className="input"
                placeholder={status?.masked_token ? `Current: ${status.masked_token}` : 'Paste @BotFather token (e.g. 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)'}
                value={botToken}
                onChange={(e) => setBotToken(e.target.value)}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
                Chat ID
              </label>
              <input
                type="text"
                className="input"
                placeholder="Your Telegram User/Chat ID (e.g. 123456789)"
                value={chatId}
                onChange={(e) => setChatId(e.target.value)}
                required
              />
            </div>

            {testResult && (
              <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: testResult.startsWith('Success') ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)', fontSize: '12px', color: testResult.startsWith('Success') ? '#34d399' : '#fda4af' }}>
                {testResult}
              </div>
            )}

            <button type="submit" disabled={testing} className="btn btn-primary">
              <Send size={14} /> {testing ? 'Connecting & Verifying...' : 'Save & Verify Connection'}
            </button>
          </form>
        </div>

        {/* Quality Thresholds & Quiet Hours */}
        <div className="card">
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
            Alert Quality & Spam Prevention (Section 32)
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                <span>Minimum Match Percentage Threshold</span>
                <strong style={{ color: '#34d399' }}>{minMatch}%</strong>
              </div>
              <input type="range" min="60" max="95" value={minMatch} onChange={(e) => setMinMatch(parseInt(e.target.value))} style={{ width: '100%' }} />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
                Daily Notification Maximum
              </label>
              <input type="number" className="input" min="1" max="50" value={dailyLimit} onChange={(e) => setDailyLimit(parseInt(e.target.value))} />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input type="checkbox" checked={quietHours} onChange={(e) => setQuietHours(e.target.checked)} id="quiet-check" />
              <label htmlFor="quiet-check" style={{ fontSize: '13px', color: 'var(--text-primary)', cursor: 'pointer' }}>
                Enable Quiet Hours (No alerts sent during night)
              </label>
            </div>

            {quietHours && (
              <div className="grid-2">
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Quiet Start</label>
                  <input type="time" className="input" value={quietStart} onChange={(e) => setQuietStart(e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Quiet End</label>
                  <input type="time" className="input" value={quietEnd} onChange={(e) => setQuietEnd(e.target.value)} />
                </div>
              </div>
            )}

            <button onClick={handleSavePreferences} className="btn btn-secondary btn-sm">
              Save Alert Rules
            </button>
          </div>
        </div>
      </div>

      {/* Notification Logs */}
      <div className="card">
        <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>
          Recent Notification History
        </h2>
        {history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No Telegram notifications dispatched yet.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {history.map((item) => (
              <div key={item.id} style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>{item.title}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{new Date(item.sent_at).toLocaleString()}</div>
                </div>
                <span className={`badge ${item.is_sent ? 'badge-emerald' : 'badge-rose'}`}>
                  {item.is_sent ? 'Delivered' : 'Failed'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
