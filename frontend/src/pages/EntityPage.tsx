import React, { useEffect, useState } from 'react';
import { Users, ShieldAlert, Network, ArrowRight } from 'lucide-react';
import { fetchEntities, fetchEntityDetail } from '../services/api';
import { EntitySummary, EntityDetail } from '../types';

interface EntityPageProps {
  initialEntityId?: string;
  onNavigateToGraph?: (entityId: string) => void;
}

export const EntityPage: React.FC<EntityPageProps> = ({
  initialEntityId,
  onNavigateToGraph,
}) => {
  const [entities, setEntities] = useState<EntitySummary[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<EntityDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEntities();
  }, []);

  useEffect(() => {
    if (initialEntityId) {
      loadDetail(initialEntityId);
    }
  }, [initialEntityId]);

  const loadEntities = async () => {
    setLoading(true);
    try {
      const data = await fetchEntities(50);
      setEntities(data);
      if (data.length > 0 && !initialEntityId) {
        loadDetail(data[0].entity_id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadDetail = async (id: string) => {
    try {
      const detail = await fetchEntityDetail(id);
      setSelectedEntity(detail);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="page-scrollable" style={{ display: 'flex', gap: 20 }}>
      {/* Entity List */}
      <div style={{ width: '380px', flexShrink: 0 }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
          Inferred Entity Clusters
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: 16 }}>
          Common Input Ownership Heuristic &amp; behavioral cohorts.
        </p>

        <div className="table-container" style={{ maxHeight: 'calc(100vh - 180px)', overflowY: 'auto' }}>
          <table className="nexus-table">
            <thead>
              <tr>
                <th>Entity ID</th>
                <th>Wallets</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {entities.map((e) => (
                <tr
                  key={e.entity_id}
                  onClick={() => loadDetail(e.entity_id)}
                  style={{
                    cursor: 'pointer',
                    background: selectedEntity?.entity_id === e.entity_id ? 'rgba(56, 189, 248, 0.08)' : undefined,
                  }}
                >
                  <td style={{ fontFamily: 'monospace', color: '#10b981', fontWeight: 600 }}>
                    {e.entity_id}
                  </td>
                  <td>{e.wallet_count}</td>
                  <td>
                    <span className={`score-pill ${e.risk_score >= 80 ? 'score-critical' : e.risk_score >= 50 ? 'score-high' : 'score-low'}`}>
                      {e.risk_score.toFixed(0)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Entity Dossier */}
      {selectedEntity ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="nexus-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <h2 style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'monospace', color: '#f8fafc' }}>
                    {selectedEntity.entity_id}
                  </h2>
                  <span className="badge badge-medium">
                    {selectedEntity.cluster_type.replace('_', ' ')}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: 4 }}>
                  Attribution: Inferred behavioural cluster (Non-legal identity guarantee)
                </div>
              </div>

              {onNavigateToGraph && (
                <button
                  className="btn-secondary"
                  onClick={() => onNavigateToGraph(selectedEntity.entity_id)}
                >
                  <Network size={14} /> View Subgraph
                </button>
              )}
            </div>

            {/* Metrics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
              <div style={{ background: '#111827', padding: '12px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>MEMBER WALLETS</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace' }}>
                  {selectedEntity.wallet_count}
                </div>
              </div>
              <div style={{ background: '#111827', padding: '12px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>TOTAL VOLUME</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace' }}>
                  {selectedEntity.total_volume_btc.toFixed(2)} BTC
                </div>
              </div>
              <div style={{ background: '#111827', padding: '12px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>RISK SCORE</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: selectedEntity.risk_score >= 80 ? '#ef4444' : '#f59e0b' }}>
                  {selectedEntity.risk_score.toFixed(1)} / 100
                </div>
              </div>
              <div style={{ background: '#111827', padding: '12px', borderRadius: '6px' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>CLUSTER CONFIDENCE</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: '#38bdf8' }}>
                  {(selectedEntity.cluster_confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>

          {/* Member Wallets and Forensic Evidence */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {/* Member Addresses */}
            <div className="nexus-card">
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: 10 }}>
                Co-Spent Member Wallets ({selectedEntity.member_wallets.length})
              </h3>
              <div style={{ maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {selectedEntity.member_wallets.map((addr, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: '#090d16',
                      padding: '8px 10px',
                      borderRadius: '4px',
                      fontFamily: 'monospace',
                      fontSize: '11px',
                      color: '#cbd5e1',
                    }}
                  >
                    {addr}
                  </div>
                ))}
              </div>
            </div>

            {/* Cluster Evidence */}
            <div className="nexus-card">
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: 10 }}>
                Cluster Evidence Rationale
              </h3>
              <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: 8, fontSize: '13px', color: '#cbd5e1' }}>
                {selectedEntity.cluster_evidence.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>

              {selectedEntity.associated_ips.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: 6 }}>
                    Observed Emission IPs
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {selectedEntity.associated_ips.map((ip, i) => (
                      <span key={i} style={{ background: '#1e293b', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontFamily: 'monospace' }}>
                        {ip}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
          Select an entity cluster to inspect profile
        </div>
      )}
    </div>
  );
};
