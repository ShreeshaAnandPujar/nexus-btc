import React, { useEffect, useState } from 'react';
import { HelpCircle, Sliders, Activity, Shuffle, ShieldCheck } from 'lucide-react';
import { fetchAlerts, fetchAlertDetail } from '../services/api';
import { AlertSummary, AlertResponse } from '../types';
import { ShapWaterfall } from '../components/ShapWaterfall';

export const ExplainPage: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertSummary[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<AlertResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const res = await fetchAlerts(undefined, undefined, 20);
      setAlerts(res.alerts);
      if (res.alerts.length > 0) {
        const detail = await fetchAlertDetail(res.alerts[0].alert_id);
        setSelectedAlert(detail);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAlert = async (alertId: string) => {
    try {
      const detail = await fetchAlertDetail(alertId);
      setSelectedAlert(detail);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="page-scrollable" style={{ display: 'flex', gap: 20 }}>
      {/* Alert Selector */}
      <div style={{ width: '320px', flexShrink: 0 }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
          Explainability Studio
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: 16 }}>
          SHAP waterfall plots, model contributions, and counterfactuals.
        </p>

        <div className="table-container" style={{ maxHeight: 'calc(100vh - 180px)', overflowY: 'auto' }}>
          <table className="nexus-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Risk</th>
                <th>Motif</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr
                  key={a.alert_id}
                  onClick={() => handleSelectAlert(a.alert_id)}
                  style={{
                    cursor: 'pointer',
                    background: selectedAlert?.alert_id === a.alert_id ? 'rgba(56, 189, 248, 0.08)' : undefined,
                  }}
                >
                  <td style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{a.alert_id}</td>
                  <td>
                    <span className={`score-pill ${a.risk_score >= 80 ? 'score-critical' : 'score-high'}`}>
                      {a.risk_score.toFixed(0)}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-critical" style={{ fontSize: '9px' }}>
                      {a.primary_motif || 'ANOMALY'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Main Explainability Panels */}
      {selectedAlert ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Top Summary Banner */}
          <div className="nexus-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <div>
                <span style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 'bold' }}>FORENSIC REASONING SUMMARY</span>
                <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>
                  {selectedAlert.alert_id} — {selectedAlert.primary_motif || 'Statistical Anomaly'}
                </h2>
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>Risk: </span>
                  <strong style={{ color: '#ef4444', fontFamily: 'monospace' }}>{selectedAlert.risk_score.toFixed(1)}</strong>
                </div>
                <div>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>Confidence: </span>
                  <strong style={{ color: '#38bdf8', fontFamily: 'monospace' }}>{selectedAlert.confidence_score.toFixed(1)}</strong>
                </div>
              </div>
            </div>
            <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: 1.5 }}>
              {selectedAlert.explanation?.forensic_summary || 'Evaluation completed via ensemble model and structural detection.'}
            </p>
          </div>

          {/* Model Ensemble Contributions */}
          <div className="nexus-card">
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={16} color="#38bdf8" /> Independent Model Consensus &amp; Disagreement
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
              <div style={{ background: '#111827', padding: '10px 14px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>ISOLATION FOREST</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f8fafc' }}>
                  {selectedAlert.model_contributions?.iforest_score?.toFixed(1) || 'N/A'}
                </div>
                <div style={{ fontSize: '10px', color: '#64748b' }}>Unsupervised baseline</div>
              </div>

              <div style={{ background: '#111827', padding: '10px 14px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>PLATT-CALIBRATED RF</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f8fafc' }}>
                  {selectedAlert.model_contributions?.rf_score?.toFixed(1) || 'N/A'}
                </div>
                <div style={{ fontSize: '10px', color: '#64748b' }}>Supervised probability</div>
              </div>

              <div style={{ background: '#111827', padding: '10px 14px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>TEMPORAL BURST</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f8fafc' }}>
                  {selectedAlert.model_contributions?.temporal_burst_score?.toFixed(1) || '0.0'}
                </div>
                <div style={{ fontSize: '10px', color: '#64748b' }}>Velocity surge</div>
              </div>

              <div style={{ background: '#111827', padding: '10px 14px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>MODEL DISAGREEMENT</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: '#a855f7' }}>
                  {selectedAlert.model_contributions?.model_disagreement?.toFixed(1) || '0.0'} pts
                </div>
                <div style={{ fontSize: '10px', color: '#64748b' }}>|RF - IForest| delta</div>
              </div>
            </div>
          </div>

          {/* Two-Column: SHAP Waterfall & Counterfactuals */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            {/* SHAP Waterfall Chart */}
            <div className="nexus-card">
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Sliders size={16} color="#38bdf8" /> SHAP Feature Waterfall Attributions
              </h3>
              <ShapWaterfall
                baseValue={selectedAlert.explanation?.base_expected_value || 18.5}
                finalRisk={selectedAlert.risk_score}
                attributions={selectedAlert.explanation?.top_feature_attributions || []}
              />
            </div>

            {/* Counterfactual Sensitivity Analysis */}
            <div className="nexus-card">
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Shuffle size={16} color="#10b981" /> Counterfactual Sensitivity Simulation
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {selectedAlert.counterfactual && selectedAlert.counterfactual.map((cf, i) => (
                  <div
                    key={i}
                    style={{
                      background: '#111827',
                      border: '1px solid #1e293b',
                      borderRadius: '6px',
                      padding: '12px 14px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, fontSize: '13px', color: '#f8fafc' }}>
                        {cf.modified_feature_name}
                      </span>
                      <span style={{ fontFamily: 'monospace', color: '#10b981', fontWeight: 'bold', fontSize: '13px' }}>
                        Risk Delta: {cf.delta.toFixed(1)} pts
                      </span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#cbd5e1', marginBottom: 6 }}>
                      {cf.feature_removed_or_modified}
                    </div>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>
                      {cf.interpretation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
          Select an alert from the left to inspect explainability attributions.
        </div>
      )}
    </div>
  );
};
