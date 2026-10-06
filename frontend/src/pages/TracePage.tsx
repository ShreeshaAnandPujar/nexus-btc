import React, { useState, useEffect } from 'react';
import { GitFork, Play, ArrowRight, ShieldAlert, Clock } from 'lucide-react';
import { postTrace } from '../services/api';
import { TraceResponse, TracePath } from '../types';

interface TracePageProps {
  initialIdentifier?: string;
  initialType?: string;
}

export const TracePage: React.FC<TracePageProps> = ({
  initialIdentifier = '',
  initialType = 'wallet',
}) => {
  const [startType, setStartType] = useState(initialType);
  const [startIdentifier, setStartIdentifier] = useState(initialIdentifier);
  const [maxHops, setMaxHops] = useState(8);
  const [maxNodes, setMaxNodes] = useState(60);
  const [minValueRatio, setMinValueRatio] = useState(0.01);

  const [traceResult, setTraceResult] = useState<TraceResponse | null>(null);
  const [selectedPath, setSelectedPath] = useState<TracePath | null>(null);
  const [isTracing, setIsTracing] = useState(false);

  useEffect(() => {
    if (initialIdentifier) {
      handleTrace();
    }
  }, [initialIdentifier]);

  const handleTrace = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!startIdentifier.trim()) return;

    setIsTracing(true);
    setSelectedPath(null);
    try {
      const res = await postTrace({
        start_type: startType,
        start_identifier: startIdentifier.trim(),
        max_hops: maxHops,
        max_nodes: maxNodes,
        min_value_ratio: minValueRatio,
      });
      setTraceResult(res);
      if (res.ranked_paths.length > 0) {
        setSelectedPath(res.ranked_paths[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTracing(false);
    }
  };

  const getEndpointBadge = (type: string) => {
    switch (type) {
      case 'DORMANT':
        return <span className="badge badge-low">Dormant UTXO</span>;
      case 'MIXER_LIKE':
        return <span className="badge badge-critical">Mixer / CoinJoin</span>;
      case 'SERVICE':
        return <span className="badge badge-high">Custodial Service</span>;
      case 'CYCLE':
        return <span className="badge badge-critical">Circular Flow</span>;
      case 'HORIZON':
        return <span className="badge badge-medium">Hop Horizon</span>;
      default:
        return <span className="badge" style={{ background: '#1e293b', color: '#94a3b8' }}>{type}</span>;
    }
  };

  return (
    <div className="page-scrollable">
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
          Value-Aware Best-First Fund Tracer
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px' }}>
          Forward money flow traversal prioritizing high-magnitude UTXOs with semantic terminal stop reasons.
        </p>
      </div>

      {/* Control Box */}
      <form onSubmit={handleTrace} className="nexus-card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr 100px 100px 120px auto', gap: 12, alignItems: 'center' }}>
          <div>
            <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>Target Type</label>
            <select
              value={startType}
              onChange={(e) => setStartType(e.target.value)}
              style={{ width: '100%', padding: '8px', background: '#111827', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px' }}
            >
              <option value="wallet">Wallet</option>
              <option value="txid">Transaction ID</option>
              <option value="entity">Entity ID</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>Identifier</label>
            <input
              type="text"
              placeholder="e.g. 1A1zP1eP... or TXID hash..."
              value={startIdentifier}
              onChange={(e) => setStartIdentifier(e.target.value)}
              style={{ width: '100%', padding: '8px', background: '#111827', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px', fontFamily: 'monospace' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>Max Hops</label>
            <input
              type="number"
              value={maxHops}
              onChange={(e) => setMaxHops(Number(e.target.value))}
              min={1}
              max={25}
              style={{ width: '100%', padding: '8px', background: '#111827', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>Max Nodes</label>
            <input
              type="number"
              value={maxNodes}
              onChange={(e) => setMaxNodes(Number(e.target.value))}
              min={10}
              max={200}
              style={{ width: '100%', padding: '8px', background: '#111827', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>Min Cutoff Ratio</label>
            <select
              value={minValueRatio}
              onChange={(e) => setMinValueRatio(Number(e.target.value))}
              style={{ width: '100%', padding: '8px', background: '#111827', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px' }}
            >
              <option value={0.01}>1% Threshold</option>
              <option value={0.05}>5% Threshold</option>
              <option value={0.10}>10% Threshold</option>
            </select>
          </div>

          <div style={{ paddingTop: '18px' }}>
            <button type="submit" className="btn-primary" disabled={isTracing} style={{ height: '36px' }}>
              <Play size={14} /> Trace
            </button>
          </div>
        </div>
      </form>

      {/* Trace Results */}
      {traceResult && (
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 20 }}>
          {/* Ranked Paths List */}
          <div className="nexus-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h2 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc' }}>
                Ranked Traversal Paths ({traceResult.ranked_paths.length})
              </h2>
              <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                {traceResult.execution_time_ms.toFixed(0)} ms
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 'calc(100vh - 300px)', overflowY: 'auto' }}>
              {traceResult.ranked_paths.map((path, idx) => (
                <div
                  key={path.path_id}
                  onClick={() => setSelectedPath(path)}
                  style={{
                    background: selectedPath?.path_id === path.path_id ? 'rgba(56, 189, 248, 0.12)' : '#111827',
                    border: '1px solid #1e293b',
                    borderRadius: '6px',
                    padding: '10px 12px',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#38bdf8' }}>
                      Path #{idx + 1} ({path.path_length} hops)
                    </span>
                    {getEndpointBadge(path.endpoint_type)}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#94a3b8' }}>
                    <span>Initial Volume: <strong style={{ color: '#f8fafc' }}>{path.total_btc_traced.toFixed(4)} BTC</strong></span>
                    <span>Avg Risk: <strong style={{ color: path.cumulative_risk >= 70 ? '#ef4444' : '#f59e0b' }}>{path.cumulative_risk.toFixed(0)}</strong></span>
                  </div>
                  <div style={{ fontSize: '10px', color: '#64748b', marginTop: 4, fontFamily: 'monospace' }}>
                    Endpoint: {path.endpoint_wallet.slice(0, 14)}...
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Selected Path Sequence Visualizer */}
          <div className="nexus-card">
            {selectedPath ? (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, borderBottom: '1px solid #1e293b', paddingBottom: 10 }}>
                  <div>
                    <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc' }}>
                      Hop-by-Hop Flow Sequence
                    </h3>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                      Tracing path through {selectedPath.hops.length} sequential transaction hops
                    </div>
                  </div>
                  {getEndpointBadge(selectedPath.endpoint_type)}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {selectedPath.hops.map((hop, hIdx) => (
                    <div
                      key={hIdx}
                      style={{
                        background: '#111827',
                        border: '1px solid #1e293b',
                        borderRadius: '6px',
                        padding: '12px 16px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                        <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#10b981' }}>
                          HOP #{hop.hop_index}
                        </span>
                        <span style={{ fontSize: '11px', color: '#94a3b8', fontFamily: 'monospace' }}>
                          Risk: {hop.hop_risk.toFixed(1)} / 100
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                        <div style={{ flex: 1, background: '#090d16', padding: '6px 8px', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px', color: '#cbd5e1' }}>
                          {hop.from_wallet}
                        </div>
                        <ArrowRight size={16} color="#38bdf8" />
                        <div style={{ flex: 1, background: '#090d16', padding: '6px 8px', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px', color: '#cbd5e1' }}>
                          {hop.to_wallet}
                        </div>
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#94a3b8' }}>
                        <span>Amount: <strong style={{ color: '#f8fafc' }}>{hop.amount_btc.toFixed(4)} BTC</strong></span>
                        <span>TXID: <strong style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{hop.txid.slice(0, 12)}...</strong></span>
                        <span>Time: {hop.timestamp.replace('T', ' ').slice(0, 19)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ color: '#64748b', textAlign: 'center', padding: '60px 0' }}>
                Select a ranked path from the left to inspect hop progression.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
