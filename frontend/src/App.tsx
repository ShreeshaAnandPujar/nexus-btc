import React, { useState, useEffect } from 'react';
import { Navigation } from './components/Navigation';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { AlertsPage } from './pages/AlertsPage';
import { InvestigatePage } from './pages/InvestigatePage';
import { EntityPage } from './pages/EntityPage';
import { GraphPage } from './pages/GraphPage';
import { TracePage } from './pages/TracePage';
import { ExplainPage } from './pages/ExplainPage';
import { ModelsPage } from './pages/ModelsPage';
import { ScenariosPage } from './pages/ScenariosPage';
import { SystemPage } from './pages/SystemPage';
import { fetchAlerts } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeAlertId, setActiveAlertId] = useState<string | undefined>(undefined);
  const [activeEntityId, setActiveEntityId] = useState<string | undefined>(undefined);
  const [activeGraphTarget, setActiveGraphTarget] = useState<string | undefined>(undefined);
  const [activeTraceTarget, setActiveTraceTarget] = useState<string | undefined>(undefined);
  const [alertCount, setAlertCount] = useState<number>(0);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  useEffect(() => {
    loadAlertCount();
  }, [refreshTrigger]);

  const loadAlertCount = async () => {
    try {
      const res = await fetchAlerts(undefined, undefined, 1);
      setAlertCount(res.total_alerts);
    } catch (e) {
      // offline fallback
    }
  };

  const handleDataRefreshed = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleNavigate = (tab: string, targetId?: string) => {
    if (tab === 'alerts' && targetId) {
      setActiveAlertId(targetId);
    } else if (tab === 'entities' && targetId) {
      setActiveEntityId(targetId);
    } else if (tab === 'graph' && targetId) {
      setActiveGraphTarget(targetId);
    } else if (tab === 'trace' && targetId) {
      setActiveTraceTarget(targetId);
    }
    setCurrentTab(tab);
  };

  return (
    <div className="app-container">
      <Navigation
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setActiveAlertId(undefined);
          setActiveEntityId(undefined);
          setActiveGraphTarget(undefined);
          setActiveTraceTarget(undefined);
          setCurrentTab(tab);
        }}
        alertCount={alertCount}
      />

      <div className="main-content">
        <Header onDataRefreshed={handleDataRefreshed} />

        <main style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {currentTab === 'dashboard' && (
            <DashboardPage onNavigate={handleNavigate} key={refreshTrigger} />
          )}
          {currentTab === 'alerts' && (
            <AlertsPage
              initialAlertId={activeAlertId}
              onNavigateToTrace={(txid) => handleNavigate('trace', txid)}
              onNavigateToGraph={(txid) => handleNavigate('graph', txid)}
              key={refreshTrigger}
            />
          )}
          {currentTab === 'investigate' && (
            <InvestigatePage
              onNavigateToTrace={(txid) => handleNavigate('trace', txid)}
              onNavigateToGraph={(txid) => handleNavigate('graph', txid)}
            />
          )}
          {currentTab === 'entities' && (
            <EntityPage
              initialEntityId={activeEntityId}
              onNavigateToGraph={(entId) => handleNavigate('graph', entId)}
              key={refreshTrigger}
            />
          )}
          {currentTab === 'graph' && (
            <GraphPage
              initialFocusId={activeGraphTarget}
              onNavigateToTrace={(id) => handleNavigate('trace', id)}
              key={refreshTrigger}
            />
          )}
          {currentTab === 'trace' && (
            <TracePage
              initialIdentifier={activeTraceTarget}
              initialType={activeTraceTarget?.length === 64 ? 'txid' : 'wallet'}
              key={refreshTrigger}
            />
          )}
          {currentTab === 'explain' && <ExplainPage key={refreshTrigger} />}
          {currentTab === 'models' && <ModelsPage key={refreshTrigger} />}
          {currentTab === 'scenarios' && (
            <ScenariosPage onScenarioGenerated={handleDataRefreshed} />
          )}
          {currentTab === 'system' && <SystemPage key={refreshTrigger} />}
        </main>
      </div>
    </div>
  );
};
