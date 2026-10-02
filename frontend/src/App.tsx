import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { DashboardView } from './components/DashboardView';
import { JobsView } from './components/JobsView';
import { SavedSearchesView } from './components/SavedSearchesView';
import { ResumeView } from './components/ResumeView';
import { ResumeQualityView } from './components/ResumeQualityView';
import { ApplicationsView } from './components/ApplicationsView';
import { CompaniesView } from './components/CompaniesView';
import { TelegramView } from './components/TelegramView';
import { SettingsView } from './components/SettingsView';
import { JobDetailModal } from './components/JobDetailModal';
import { JobImportModal } from './components/JobImportModal';
import { api } from './api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [showImportModal, setShowImportModal] = useState(false);
  
  // Header badges status
  const [ollamaStatus, setOllamaStatus] = useState('Unavailable');
  const [telegramConnected, setTelegramConnected] = useState(false);

  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const data = await api.getDashboardAnalytics();
      setOllamaStatus(data.ollama_status);
      setTelegramConnected(data.telegram_connected);
    } catch (err) {
      console.error('Failed to query system status:', err);
    }
  };

  const handleNavigate = (tab: string, jobId?: number) => {
    setCurrentTab(tab);
    if (jobId) {
      setSelectedJobId(jobId);
    }
  };

  const handleImportSuccess = (jobId: number) => {
    setShowImportModal(false);
    setSelectedJobId(jobId);
    setCurrentTab('jobs');
  };

  return (
    <div className="app-container">
      {/* Fixed Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        ollamaStatus={ollamaStatus}
        telegramConnected={telegramConnected}
      />

      {/* Main Content Area */}
      <main className="main-content">
        {currentTab === 'dashboard' && (
          <DashboardView
            onNavigate={handleNavigate}
            onOpenImport={() => setShowImportModal(true)}
          />
        )}

        {currentTab === 'jobs' && (
          <JobsView
            onSelectJob={(id) => setSelectedJobId(id)}
            onOpenImport={() => setShowImportModal(true)}
            selectedJobId={selectedJobId || undefined}
          />
        )}

        {currentTab === 'saved-searches' && (
          <SavedSearchesView />
        )}

        {currentTab === 'resume' && (
          <ResumeView />
        )}

        {currentTab === 'quality' && (
          <ResumeQualityView />
        )}

        {currentTab === 'applications' && (
          <ApplicationsView />
        )}

        {currentTab === 'companies' && (
          <CompaniesView />
        )}

        {currentTab === 'telegram' && (
          <TelegramView />
        )}

        {currentTab === 'providers' && (
          <SettingsView />
        )}

        {/* Global Modals */}
        {selectedJobId !== null && (
          <JobDetailModal
            jobId={selectedJobId}
            onClose={() => setSelectedJobId(null)}
            onApplicationCreated={() => {
              checkSystemStatus();
            }}
          />
        )}

        {showImportModal && (
          <JobImportModal
            onClose={() => setShowImportModal(false)}
            onImportSuccess={handleImportSuccess}
          />
        )}
      </main>
    </div>
  );
};

export default App;
