import React, { useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  Users,
  Layers,
  Network,
  ArrowUpRight,
  TrendingUp,
} from 'lucide-react';
import { fetchHealth, fetchAlerts, fetchTransactions, fetchEntities } from '../services/api';
import { AlertSummary, EntitySummary } from '../types';

interface DashboardPageProps {
  onNavigate: (tab: string, targetId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState({
    transactions: 0,
    alerts: 0,
    critical: 0,
    high: 0,
    entities: 0,
  });
  const [recentAlerts, setRecentAlerts] = useState<AlertSummary[]>([]);
  const [highRiskEntities, setHighRiskEntities] = useState<EntitySummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [health, alertsRes, ents] = await Promise.all([
        fetchHealth(),
        fetchAlerts(undefined, undefined, 5),
        fetchEntities(5),
      ]);

      setStats({
        transactions: health.database.transactions_count,
        alerts: alertsRes.total_alerts,
        critical: alertsRes.critical_count,
        high: alertsRes.high_count,
        entities: health.database.entities_count,
      });
      setRecentAlerts(alertsRes.alerts);
      setHighRiskEntities(ents.filter((e) => e.risk_score >= 50));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-scrollable">
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
          Forensic Surveillance Command Center
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px' }}>
          Real-time Bitcoin blockchain and network correlation telemetry. Air-gapped offline operation.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-title">Monitored Transactions</div>
          <div className="metric-value">{stats.transactions}</div>
          <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>Canonical SQLite storage</div>
        </div>

        <div className="metric-card critical">
          <div className="metric-title">Critical Severity Alerts</div>
          <div className="metric-value" style={{ color: '#ef4444' }}>{stats.critical}</div>
          <div style={{ fontSize: '11px', color: '#ef4444', marginTop: '4px' }}>Actionable forensic findings</div>
        </div>

        <div className="metric-card warning">
          <div className="metric-title">High Priority Alerts</div>
          <div className="metric-value" style={{ color: '#f59e0b' }}>{stats.high}</div>
          <div style={{ fontSize: '11px', color: '#f59e0b', marginTop: '4px' }}>Risk score &gt;= 65 / 100</div>
        </div>

        <div className="metric-card success">
          <div className="metric-title">Inferred Entity Clusters</div>
          <div className="metric-value" style={{ color: '#10b981' }}>{stats.entities}</div>
          <div style={{ fontSize: '11px', color: '#10b981', marginTop: '4px' }}>Common-Input Union-Find</div>
        </div>
      </div>

      {/* Two-Column Grid: Priority Alerts & High-Risk Entities */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '20px' }}>
        {/* Recent Priority Alerts */}
        <div className="nexus-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 8 }}>
              <AlertTriangle size={16} color="#ef4444" />
              Prioritized Alert Queue
            </h2>
            <button
              onClick={() => onNavigate('alerts')}
              style={{ background: 'none', border: 'none', color: '#38bdf8', fontSize: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
            >
              View All <ArrowUpRight size={14} />
            </button>
          </div>

          {recentAlerts.length === 0 ? (
            <div style={{ color: '#64748b', fontSize: '13px', textAlign: 'center', padding: '30px 0' }}>
              No active alerts. Ingest transactions or generate a scenario to trigger analysis.
            </div>
          ) : (
            <div className="table-container">
              <table className="nexus-table">
                <thead>
                  <tr>
                    <th>Alert ID</th>
                    <th>Motif</th>
                    <th>Risk</th>
                    <th>Conf</th>
                    <th>Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAlerts.map((a) => (
                    <tr
                      key={a.alert_id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => onNavigate('alerts', a.alert_id)}
                    >
                      <td style={{ fontFamily: 'monospace', color: '#38bdf8', fontWeight: 600 }}>
                        {a.alert_id}
                      </td>
                      <td>
                        <span className="badge badge-critical" style={{ fontSize: '10px' }}>
                          {a.primary_motif || 'ANOMALY'}
                        </span>
                      </td>
                      <td>
                        <span className={`score-pill ${a.risk_score >= 80 ? 'score-critical' : 'score-high'}`}>
                          {a.risk_score.toFixed(0)}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'monospace', color: '#94a3b8' }}>
                        {a.confidence_score.toFixed(0)}%
                      </td>
                      <td style={{ fontFamily: 'monospace' }}>
                        {a.amount_btc.toFixed(4)} BTC
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* High Risk Entities */}
        <div className="nexus-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Users size={16} color="#38bdf8" />
              High-Risk Entity Clusters
            </h2>
            <button
              onClick={() => onNavigate('entities')}
              style={{ background: 'none', border: 'none', color: '#38bdf8', fontSize: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
            >
              View All <ArrowUpRight size={14} />
            </button>
          </div>

          {highRiskEntities.length === 0 ? (
            <div style={{ color: '#64748b', fontSize: '13px', textAlign: 'center', padding: '30px 0' }}>
              No elevated-risk entity clusters identified yet.
            </div>
          ) : (
            <div className="table-container">
              <table className="nexus-table">
                <thead>
                  <tr>
                    <th>Entity ID</th>
                    <th>Wallets</th>
                    <th>Cluster Type</th>
                    <th>Risk</th>
                    <th>Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {highRiskEntities.map((e) => (
                    <tr
                      key={e.entity_id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => onNavigate('entities', e.entity_id)}
                    >
                      <td style={{ fontFamily: 'monospace', color: '#10b981', fontWeight: 600 }}>
                        {e.entity_id}
                      </td>
                      <td>{e.wallet_count}</td>
                      <td>{e.cluster_type.replace('_', ' ')}</td>
                      <td>
                        <span className={`score-pill ${e.risk_score >= 80 ? 'score-critical' : 'score-high'}`}>
                          {e.risk_score.toFixed(0)}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'monospace' }}>
                        {e.total_volume_btc.toFixed(2)} BTC
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
