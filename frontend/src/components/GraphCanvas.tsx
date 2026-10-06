import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
// @ts-ignore
import cola from 'cytoscape-cola';
// @ts-ignore
import dagre from 'cytoscape-dagre';
import { ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-react';
import { GraphResponse, CytoscapeNodeData } from '../types';

// Register layouts if available
try {
  cytoscape.use(cola);
  cytoscape.use(dagre);
} catch (e) {
  // Ignored if already registered
}

interface GraphCanvasProps {
  graphData: GraphResponse | null;
  onNodeSelect?: (nodeData: CytoscapeNodeData) => void;
  height?: string;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({
  graphData,
  onNodeSelect,
  height = '600px',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<CytoscapeNodeData | null>(null);
  const [layoutName, setLayoutName] = useState<'cola' | 'dagre' | 'concentric' | 'circle'>('cola');

  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    // Build elements
    const elements = [
      ...graphData.nodes.map((n) => ({
        group: 'nodes' as const,
        data: {
          ...n.data,
          id: n.data.id,
          label: n.data.label,
        },
      })),
      ...graphData.edges.map((e) => ({
        group: 'edges' as const,
        data: {
          ...e.data,
          id: e.data.id,
          source: e.data.source,
          target: e.data.target,
          label: e.data.relationship,
        },
      })),
    ];

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#1e293b',
            label: 'data(label)',
            color: '#f8fafc',
            'font-size': '11px',
            'font-family': 'ui-monospace, monospace',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            width: 36,
            height: 36,
            'border-width': 2,
            'border-color': '#38bdf8',
          },
        },
        {
          selector: 'node[type = "TRANSACTION"]',
          style: {
            shape: 'round-rectangle',
            width: 44,
            height: 28,
            'background-color': '#0f172a',
            'border-color': '#f59e0b',
          },
        },
        {
          selector: 'node[type = "TRANSACTION"][risk >= 70]',
          style: {
            'background-color': '#450a0a',
            'border-color': '#ef4444',
            'border-width': 3,
          },
        },
        {
          selector: 'node[type = "WALLET"]',
          style: {
            shape: 'ellipse',
            'background-color': '#0369a1',
            'border-color': '#38bdf8',
          },
        },
        {
          selector: 'node[type = "ENTITY"]',
          style: {
            shape: 'hexagon',
            width: 48,
            height: 48,
            'background-color': '#065f46',
            'border-color': '#10b981',
          },
        },
        {
          selector: 'node[type = "IP"]',
          style: {
            shape: 'diamond',
            'background-color': '#581c87',
            'border-color': '#a855f7',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#334155',
            'target-arrow-color': '#64748b',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.2,
            label: 'data(label)',
            'font-size': '9px',
            color: '#94a3b8',
            'text-rotation': 'autorotate',
            'text-margin-y': -8,
          },
        },
        {
          selector: 'edge[relationship = "SPENT"]',
          style: {
            'line-color': '#0284c7',
            'target-arrow-color': '#0284c7',
          },
        },
        {
          selector: 'edge[relationship = "CREATED"]',
          style: {
            'line-color': '#10b981',
            'target-arrow-color': '#10b981',
          },
        },
        {
          selector: 'edge[relationship = "OBSERVED"]',
          style: {
            'line-color': '#a855f7',
            'target-arrow-color': '#a855f7',
            'line-style': 'dashed',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#ffffff',
            'border-width': 4,
          },
        },
      ],
      layout: {
        name: layoutName,
        animate: false,
      },
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const data = node.data() as CytoscapeNodeData;
      setSelectedNode(data);
      if (onNodeSelect) onNodeSelect(data);
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [graphData, layoutName]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit();

  return (
    <div style={{ position: 'relative', width: '100%', height, background: '#090d16', borderRadius: '8px', border: '1px solid #1e293b' }}>
      {/* Controls Overlay */}
      <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 10, display: 'flex', gap: 6 }}>
        <select
          value={layoutName}
          onChange={(e) => setLayoutName(e.target.value as any)}
          style={{
            background: '#111827',
            color: '#f8fafc',
            border: '1px solid #334155',
            borderRadius: '4px',
            padding: '4px 8px',
            fontSize: '12px',
          }}
        >
          <option value="cola">Cola (Physics)</option>
          <option value="dagre">Dagre (Hierarchical)</option>
          <option value="concentric">Concentric</option>
          <option value="circle">Circle</option>
        </select>
        <button className="btn-secondary" onClick={handleZoomIn} style={{ padding: '6px 10px' }} title="Zoom In">
          <ZoomIn size={14} />
        </button>
        <button className="btn-secondary" onClick={handleZoomOut} style={{ padding: '6px 10px' }} title="Zoom Out">
          <ZoomOut size={14} />
        </button>
        <button className="btn-secondary" onClick={handleFit} style={{ padding: '6px 10px' }} title="Fit View">
          <Maximize2 size={14} />
        </button>
      </div>

      {/* Selected Node Inspector Drawer */}
      {selectedNode && (
        <div
          style={{
            position: 'absolute',
            bottom: 12,
            left: 12,
            zIndex: 10,
            background: 'rgba(17, 24, 39, 0.95)',
            backdropFilter: 'blur(6px)',
            border: '1px solid #334155',
            borderRadius: '8px',
            padding: '12px 16px',
            maxWidth: '360px',
            fontSize: '12px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <span style={{ fontWeight: 'bold', color: '#38bdf8' }}>{selectedNode.type}</span>
            <button
              onClick={() => setSelectedNode(null)}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '14px' }}
            >
              ×
            </button>
          </div>
          <div style={{ wordBreak: 'break-all', fontFamily: 'monospace', marginBottom: 6, color: '#f8fafc' }}>
            {selectedNode.label}
          </div>
          {selectedNode.risk !== undefined && (
            <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
              <span>Risk: <strong>{selectedNode.risk.toFixed(1)}</strong></span>
              {selectedNode.amount > 0 && <span>BTC: <strong>{selectedNode.amount.toFixed(4)}</strong></span>}
            </div>
          )}
        </div>
      )}

      {/* Cytoscape Canvas Container */}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};
