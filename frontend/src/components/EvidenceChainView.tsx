import React from 'react';
import { ArrowDown, Radio, CheckCircle, HelpCircle } from 'lucide-react';
import { EvidenceChainStep } from '../types';

interface EvidenceChainViewProps {
  chain: EvidenceChainStep[];
  onSelectStep?: (step: EvidenceChainStep) => void;
}

export const EvidenceChainView: React.FC<EvidenceChainViewProps> = ({ chain, onSelectStep }) => {
  if (!chain || chain.length === 0) {
    return <div style={{ color: '#94a3b8', fontStyle: 'italic' }}>No forensic evidence chain recorded.</div>;
  }

  const getRelationshipBadge = (rel: string) => {
    switch (rel) {
      case 'observed':
        return <span style={{ color: '#10b981', fontSize: '11px', fontWeight: 'bold' }}>[OBSERVED]</span>;
      case 'inferred':
        return <span style={{ color: '#38bdf8', fontSize: '11px', fontWeight: 'bold' }}>[INFERRED]</span>;
      case 'probabilistic':
        return <span style={{ color: '#f59e0b', fontSize: '11px', fontWeight: 'bold' }}>[PROBABILISTIC]</span>;
      default:
        return <span style={{ color: '#94a3b8', fontSize: '11px' }}>[{rel.toUpperCase()}]</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {chain.map((step, idx) => (
        <React.Fragment key={idx}>
          <div
            onClick={() => onSelectStep && onSelectStep(step)}
            style={{
              background: '#111827',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              padding: '12px 16px',
              cursor: onSelectStep ? 'pointer' : 'default',
              transition: 'border-color 0.2s',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    background: '#1e293b',
                    fontSize: '11px',
                    color: '#f8fafc',
                    fontWeight: 'bold',
                  }}
                >
                  {step.step_number}
                </span>
                <span style={{ fontWeight: 'bold', fontSize: '12px', color: '#f8fafc' }}>
                  {step.step_type.replace('_', ' ')}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {getRelationshipBadge(step.relationship)}
                <span style={{ fontSize: '11px', color: '#94a3b8', fontFamily: 'monospace' }}>
                  {(step.confidence * 100).toFixed(0)}% conf
                </span>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: 4 }}>
              {step.description}
            </div>
            <div style={{ fontSize: '11px', fontFamily: 'monospace', color: '#38bdf8', wordBreak: 'break-all' }}>
              {step.identifier}
            </div>
          </div>

          {idx < chain.length - 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', color: '#475569' }}>
              <ArrowDown size={16} />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
};
