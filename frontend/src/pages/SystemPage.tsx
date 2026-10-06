import React, { useEffect, useState } from 'react';
import { Server, Database, Cpu, Globe, CheckCircle, ShieldCheck } from 'lucide-react';
import { fetchHealth } from '../services/api';
import { SystemHealth } from '../types';

export const SystemPage: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    setLoading(true);
    try {
      const data = await fetchHealth();
      setHealth(data);
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
          System Diagnostics &amp; Offline Governance
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px' }}>
          Air-gapped deployment verification and embedded subsystem health.
        </p>
      </div>

      {health && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 20 }}>
          {/* Storage Subsystem */}
          <div className="nexus-card">
            <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Database size={16} color="#38bdf8" /> Embedded Persistence Layer
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>Database Engine</span>
                <span style={{ color: '#10b981', fontWeight: 600 }}>{health.database.type}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>Connection Status</span>
                <span style={{ color: '#10b981', fontWeight: 600 }}>{health.database.status}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>Stored Transactions</span>
                <span style={{ fontFamily: 'monospace', color: '#f8fafc' }}>{health.database.transactions_count}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>Active Forensic Alerts</span>
                <span style={{ fontFamily: 'monospace', color: '#ef4444' }}>{health.database.alerts_count}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Inferred Entity Clusters</span>
                <span style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{health.database.entities_count}</span>
              </div>
            </div>
          </div>

          {/* Machine Learning Subsystem */}
          <div className="nexus-card">
            <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Cpu size={16} color="#10b981" /> AI Detection &amp; Explainability Tier
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: '13px' }}>
              {Object.entries(health.ml_models).map(([model, status]) => (
                <div key={model} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
                  <span style={{ color: '#94a3b8' }}>{model.replace(/_/g, ' ').toUpperCase()}</span>
                  <span style={{ color: '#38bdf8', fontWeight: 600 }}>{status}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Geolocation & Telemetry */}
          <div className="nexus-card">
            <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Globe size={16} color="#f59e0b" /> Geolocation &amp; BGP ASN Subsystem
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>MMDB Database</span>
                <span style={{ color: health.geolocation.status.includes('AVAILABLE') ? '#10b981' : '#f59e0b' }}>
                  {health.geolocation.status}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
                <span style={{ color: '#94a3b8' }}>Attribution</span>
                <span style={{ color: '#f8fafc' }}>{health.geolocation.attribution}</span>
              </div>
              <div style={{ fontSize: '11px', color: '#64748b', marginTop: 4 }}>
                Graceful degradation policy active: if local MMDB is absent, fallback to "UNKNOWN" prevents any application disruption.
              </div>
            </div>
          </div>

          {/* Academic & Defense Attribution */}
          <div className="nexus-card">
            <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <ShieldCheck size={16} color="#a855f7" /> Defense &amp; Academic Governance
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '13px', color: '#cbd5e1' }}>
              <div><strong>Project:</strong> NEXUS-BTC (Network–Entity eXplainable Unified Surveillance for Bitcoin)</div>
              <div><strong>Target Problem Statement:</strong> NTRO Smart India Hackathon (SIH) 2026 — PS-05</div>
              <div><strong>System Architecture:</strong> Unified Zero-Daemon Clean-Room Implementation</div>
              <div><strong>License:</strong> MIT Open-Source (Conceptual reimplementation, zero copyleft pollution)</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
