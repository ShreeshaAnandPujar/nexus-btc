import React, { useEffect, useState } from 'react';
import { Network, Filter, Search, RotateCcw } from 'lucide-react';
import { fetchGlobalGraph, fetchEgoGraph } from '../services/api';
import { GraphResponse, CytoscapeNodeData } from '../types';
import { GraphCanvas } from '../components/GraphCanvas';

interface GraphPageProps {
  initialFocusId?: string;
  onNavigateToTrace?: (id: string) => void;
}

export const GraphPage: React.FC<GraphPageProps> = ({
  initialFocusId,
  onNavigateToTrace,
}) => {
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [targetId, setTargetId] = useState(initialFocusId || '');
  const [radius, setRadius] = useState(2);
  const [maxNodes, setMaxNodes] = useState(100);
  const [selectedNode, setSelectedNode] = useState<CytoscapeNodeData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialFocusId) {
      loadEgoGraph(initialFocusId);
    } else {
      loadGlobalGraph();
    }
  }, [initialFocusId]);

  const loadGlobalGraph = async () => {
    setLoading(true);
    try {
      const data = await fetchGlobalGraph(maxNodes);
      setGraphData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadEgoGraph = async (id: string) => {
    if (!id.trim()) return;
    setLoading(true);
    try {
      const data = await fetchEgoGraph(id.trim(), radius, maxNodes);
      setGraphData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (targetId.trim()) {
      loadEgoGraph(targetId.trim());
    } else {
      loadGlobalGraph();
    }
  };

  return (
    <div className="page-scrollable" style={{ display: 'flex', flexDirection: 'column', gap: 16, height: '100%' }}>
      {/* Top Header & Search Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
            Heterogeneous Forensic Graph
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '13px' }}>
            In-memory directed topological graph. Node types: WALLET, TRANSACTION, IP, ENTITY.
          </p>
        </div>

        {/* Filter controls */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Focus on Entity, Wallet, or TXID..."
            value={targetId}
            onChange={(e) => setTargetId(e.target.value)}
            style={{
              padding: '8px 12px',
              background: '#111827',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#f8fafc',
              fontSize: '12px',
              width: '260px',
              fontFamily: 'monospace',
            }}
          />
          <button type="submit" className="btn-primary" style={{ padding: '8px 12px' }}>
            <Search size={14} /> Subgraph
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={loadGlobalGraph}
            title="Reset to global graph"
            style={{ padding: '8px 12px' }}
          >
            <RotateCcw size={14} /> Reset
          </button>
        </form>
      </div>

      {/* Graph Metrics Ribbon */}
      <div style={{ display: 'flex', gap: 20, fontSize: '12px', color: '#94a3b8', borderBottom: '1px solid #1e293b', paddingBottom: 8 }}>
        <span>View Type: <strong style={{ color: '#38bdf8' }}>{graphData?.subgraph_type || 'global'}</strong></span>
        <span>Rendered Nodes: <strong style={{ color: '#f8fafc' }}>{graphData?.node_count || 0}</strong></span>
        <span>Rendered Edges: <strong style={{ color: '#f8fafc' }}>{graphData?.edge_count || 0}</strong></span>
        {graphData?.focus_id && <span>Center Node: <strong style={{ fontFamily: 'monospace', color: '#10b981' }}>{graphData.focus_id}</strong></span>}
      </div>

      {/* Cytoscape Canvas */}
      <div style={{ flex: 1, minHeight: '520px' }}>
        <GraphCanvas
          graphData={graphData}
          onNodeSelect={(node) => setSelectedNode(node)}
          height="100%"
        />
      </div>
    </div>
  );
};
