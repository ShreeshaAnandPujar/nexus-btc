import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Filter,
  Eye,
  GitFork,
  Network,
  X,
  Sliders,
} from 'lucide-react';
import { fetchAlerts, fetchAlertDetail } from '../services/api';
import { AlertSummary, AlertResponse } from '../types';
import { EvidenceChainView } from '../components/EvidenceChainView';
import { ShapWaterfall } from '../components/ShapWaterfall';

interface AlertsPageProps {
  initialAlertId?: string;
  onNavigateToTrace?: (txid: string) => void;
  onNavigateToGraph?: (txid: string) => void;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({
  initialAlertId,
  onNavigateToTrace,
  onNavigateToGraph,
}) => {
  const [alerts, setAlerts] = useState<AlertSummary[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [motifFilter, setMotifFilter] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<AlertResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, [severityFilter, motifFilter]);

  useEffect(() => {
    if (initialAlertId) {
      loadDetail(initialAlertId);
    }
  }, [initialAlertId]);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const res = await fetchAlerts(severityFilter || undefined, motifFilter || undefined);
      setAlerts(res.alerts);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadDetail = async (alertId: string) => {
    try {
      const detail = await fetchAlertDetail(alertId);
      setSelectedAlert(detail);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="page-scrollable" style={{ display: 'flex', gap: 20, position: 'relative' }}>
      {/* Alert Queue Table */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
              Ranked Alert Queue
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '13px' }}>
              Prioritized by calibrated Risk (0-100) and orthogonal Confidence (0-100).
            </p>
          </div>

          {/* Filters */}
          <div style={{ display: 'flex', gap: 10 }}>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              style={{
                background: '#111827',
                color: '#f8fafc',
                border: '1px solid #334155',
                borderRadius: '6px',
                padding: '6px 10px',
                fontSize: '12px',
              }}
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High Priority</option>
              <option value="MEDIUM">Medium Priority</option>
            </select>

            <select
              value={motifFilter}
              onChange={(e) => setMotifFilter(e.target.value)}
              style={{
                background: '#111827',
                color: '#f8fafc',
                border: '1px solid #334155',
                borderRadius: '6px',
                padding: '6px 10px',
                fontSize: '12px',
              }}
            >
              <option value="">All Motifs</option>
              <option value="PEELING_CHAIN">Peeling Chain</option>
              <option value="MIXING_LIKE">Mixing / CoinJoin</option>
              <option value="FAN_IN">Fan-In Consolidation</option>
              <option value="FAN_OUT">Fan-Out Dispersion</option>
              <option value="RAPID_LAYERING">Rapid Layering</option>
              <option value="CIRCULAR_FLOW">Circular Flow</option>
              <option value="DORMANT_ACTIVATION">Dormant Activation</option>
              <option value="SUSPICIOUS_CONSOLIDATION">Suspicious Consolidation</option>
              <option value="RAPID_SPLIT">Rapid Split</option>
            </select>

          </div>
        </div>

        <div className="table-container">
          <table className="nexus-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Transaction</th>
                <th>Entity</th>
                <th>Motif</th>
                <th>Severity</th>
                <th>Risk</th>
                <th>Confidence</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>
                    No alerts match active filters.
                  </td>
                </tr>
              ) : (
                alerts.map((a) => (
                  <tr
                    key={a.alert_id}
                    style={{ background: selectedAlert?.alert_id === a.alert_id ? 'rgba(56, 189, 248, 0.08)' : undefined }}
                  >
                    <td style={{ fontFamily: 'monospace', color: '#38bdf8', fontWeight: 600 }}>
                      {a.alert_id}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '11px', color: '#94a3b8' }}>
                      {a.txid.slice(0, 10)}...{a.txid.slice(-6)}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '11px', color: '#10b981' }}>
                      {a.entity_id || 'Unclustered'}
                    </td>
                    <td>
                      <span className="badge badge-critical" style={{ fontSize: '10px' }}>
                        {a.primary_motif || 'ANOMALY'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${a.severity === 'CRITICAL' ? 'badge-critical' : a.severity === 'HIGH' ? 'badge-high' : 'badge-medium'}`}>
                        {a.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`score-pill ${a.risk_score >= 80 ? 'score-critical' : a.risk_score >= 65 ? 'score-high' : 'score-medium'}`}>
                        {a.risk_score.toFixed(0)}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'monospace', color: '#94a3b8' }}>
                      {a.confidence_score.toFixed(0)}%
                    </td>
                    <td>
                      <button
                        className="btn-secondary"
                        onClick={() => loadDetail(a.alert_id)}
                        style={{ padding: '4px 8px', fontSize: '11px' }}
                      >
                        <Eye size={12} /> Dossier
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Forensic Dossier Side Panel */}
      {selectedAlert && (
        <div
          style={{
            width: '480px',
            background: '#0d131f',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            maxHeight: 'calc(100vh - 110px)',
            overflowY: 'auto',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 12 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontWeight: 800, fontSize: '16px', color: '#f8fafc' }}>
                  {selectedAlert.alert_id}
                </span>
                <span className={`badge ${selectedAlert.severity === 'CRITICAL' ? 'badge-critical' : 'badge-high'}`}>
                  {selectedAlert.severity}
                </span>
              </div>
              <div style={{ fontSize: '11px', color: '#94a3b8', fontFamily: 'monospace', marginTop: 2 }}>
                TXID: {selectedAlert.txid}
              </div>
            </div>
            <button
              onClick={() => setSelectedAlert(null)}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
            >
              <X size={18} />
            </button>
          </div>

          {/* Quick Actions */}
          <div style={{ display: 'flex', gap: 8 }}>
            {onNavigateToTrace && (
              <button
                className="btn-secondary"
                onClick={() => onNavigateToTrace(selectedAlert.txid)}
                style={{ flex: 1, justifyContent: 'center', fontSize: '12px' }}
              >
                <GitFork size={13} /> Trace Funds
              </button>
            )}
            {onNavigateToGraph && (
              <button
                className="btn-secondary"
                onClick={() => onNavigateToGraph(selectedAlert.txid)}
                style={{ flex: 1, justifyContent: 'center', fontSize: '12px' }}
              >
                <Network size={13} /> View Graph
              </button>
            )}
          </div>

          {/* Risk & Confidence Badges */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div style={{ background: '#111827', padding: '10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8' }}>RISK SCORE</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: selectedAlert.risk_score >= 80 ? '#ef4444' : '#f59e0b', fontFamily: 'monospace' }}>
                {selectedAlert.risk_score.toFixed(1)} / 100
              </div>
            </div>
            <div style={{ background: '#111827', padding: '10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8' }}>EVIDENCE CONFIDENCE</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#38bdf8', fontFamily: 'monospace' }}>
                {selectedAlert.confidence_score.toFixed(1)} / 100
              </div>
            </div>
          </div>

          {/* Explainability: SHAP Waterfall */}
          <div>
            <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Sliders size={14} color="#38bdf8" /> SHAP Feature Attribution
            </h3>
            <ShapWaterfall
              baseValue={selectedAlert.explanation?.base_expected_value || 18.5}
              finalRisk={selectedAlert.risk_score}
              attributions={selectedAlert.explanation?.top_feature_attributions || []}
            />
          </div>

          {/* Counterfactual Sensitivity Analysis */}
          {selectedAlert.counterfactual && selectedAlert.counterfactual.length > 0 && (
            <div>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', marginBottom: 8 }}>
                Counterfactual Sensitivity Analysis
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {selectedAlert.counterfactual.map((cf, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: '#111827',
                      border: '1px solid #1e293b',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      fontSize: '12px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                      <span style={{ color: '#94a3b8' }}>{cf.modified_feature_name}</span>
                      <span style={{ fontFamily: 'monospace', color: '#10b981', fontWeight: 'bold' }}>
                        Delta: {cf.delta.toFixed(1)} pts
                      </span>
                    </div>
                    <div style={{ color: '#cbd5e1' }}>{cf.interpretation}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Forensic Evidence Chain */}
          <div>
            <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', marginBottom: 8 }}>
              Forensic Evidence Chain
            </h3>
            <EvidenceChainView chain={selectedAlert.evidence_chain || []} />
          </div>
        </div>
      )}
    </div>
  );
};
