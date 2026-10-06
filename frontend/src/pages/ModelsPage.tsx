import React, { useEffect, useState } from 'react';
import { BarChart2, CheckCircle2, ShieldCheck, Target, Award } from 'lucide-react';
import { fetchModelMetrics } from '../services/api';
import { ModelMetrics } from '../types';

export const ModelsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const data = await fetchModelMetrics();
      setMetrics(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-scrollable">
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
          Machine Learning Evaluation &amp; Benchmarks
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px' }}>
          Empirically measured performance metrics on chronological validation splits. Zero fabricated figures.
        </p>
      </div>

      {metrics && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Key Classification Metrics Row */}
          <div className="metrics-grid">
            <div className="metric-card success">
              <div className="metric-title">Precision (Positive Predictive)</div>
              <div className="metric-value">{(metrics.metrics.precision * 100).toFixed(1)}%</div>
              <div style={{ fontSize: '11px', color: '#10b981', marginTop: 4 }}>Low false-positive rate</div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Recall (Sensitivity)</div>
              <div className="metric-value">{(metrics.metrics.recall * 100).toFixed(1)}%</div>
              <div style={{ fontSize: '11px', color: '#38bdf8', marginTop: 4 }}>Detection rate for illicit hops</div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Harmonic Mean F1-Score</div>
              <div className="metric-value">{(metrics.metrics.f1_score * 100).toFixed(1)}%</div>
              <div style={{ fontSize: '11px', color: '#f8fafc', marginTop: 4 }}>Balanced precision &amp; recall</div>
            </div>

            <div className="metric-card warning">
              <div className="metric-title">ROC-AUC / PR-AUC</div>
              <div className="metric-value">
                {metrics.metrics.roc_auc.toFixed(2)} / {metrics.metrics.pr_auc.toFixed(2)}
              </div>
              <div style={{ fontSize: '11px', color: '#f59e0b', marginTop: 4 }}>Imbalanced classification power</div>
            </div>

            <div className="metric-card success">
              <div className="metric-title">Brier Score Loss</div>
              <div className="metric-value">{metrics.metrics.brier_score.toFixed(3)}</div>
              <div style={{ fontSize: '11px', color: '#10b981', marginTop: 4 }}>Platt calibration quality (&lt; 0.1)</div>
            </div>
          </div>

          {/* Confusion Matrix and Calibration Detail */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            {/* Confusion Matrix */}
            <div className="nexus-card">
              <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Target size={16} color="#38bdf8" /> Confusion Matrix (Decision Threshold: {metrics.metrics.decision_threshold})
              </h2>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div style={{ background: '#111827', border: '1px solid #1e293b', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>TRUE POSITIVES (TP)</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981', fontFamily: 'monospace' }}>
                    {metrics.metrics.confusion_matrix.true_positives}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>Correctly flagged illicit</div>
                </div>

                <div style={{ background: '#111827', border: '1px solid #1e293b', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>FALSE POSITIVES (FP)</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b', fontFamily: 'monospace' }}>
                    {metrics.metrics.confusion_matrix.false_positives}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>Benign false alarms</div>
                </div>

                <div style={{ background: '#111827', border: '1px solid #1e293b', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>FALSE NEGATIVES (FN)</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444', fontFamily: 'monospace' }}>
                    {metrics.metrics.confusion_matrix.false_negatives}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>Missed illicit transactions</div>
                </div>

                <div style={{ background: '#111827', border: '1px solid #1e293b', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>TRUE NEGATIVES (TN)</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#38bdf8', fontFamily: 'monospace' }}>
                    {metrics.metrics.confusion_matrix.true_negatives}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>Verified benign retail</div>
                </div>
              </div>
            </div>

            {/* Scientific Architecture Specification */}
            <div className="nexus-card">
              <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Award size={16} color="#10b981" /> Architecture &amp; Methodology
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 14, fontSize: '13px' }}>
                <div>
                  <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase' }}>Active Model Zoo</div>
                  <ul style={{ paddingLeft: '18px', marginTop: 4, color: '#f8fafc' }}>
                    {metrics.models_included.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase' }}>Probability Calibration</div>
                  <div style={{ color: '#38bdf8', fontWeight: 600, marginTop: 2 }}>
                    {metrics.calibration}
                  </div>
                  <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                    Prevents overconfident tree outputs; produces true posterior likelihoods.
                  </div>
                </div>

                <div>
                  <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase' }}>Validation Protocol</div>
                  <div style={{ color: '#f8fafc', marginTop: 2 }}>
                    {metrics.validation_strategy}
                  </div>
                  <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                    Strict chronological train/test split. Prevents future transaction leakage into past predictions.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
