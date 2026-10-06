import React from 'react';
import { FeatureAttribution } from '../types';

interface ShapWaterfallProps {
  baseValue: number;
  finalRisk: number;
  attributions: FeatureAttribution[];
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({
  baseValue,
  finalRisk,
  attributions,
}) => {
  if (!attributions || attributions.length === 0) {
    return <div style={{ color: '#94a3b8', fontStyle: 'italic' }}>No SHAP attributions computed.</div>;
  }

  const maxAbsContrib = Math.max(...attributions.map((a) => Math.abs(a.contribution)), 10);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, width: '100%' }}>
      {/* Header bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94a3b8', borderBottom: '1px solid #1e293b', paddingBottom: 6 }}>
        <span>Base Expected Prior: <strong style={{ color: '#f8fafc' }}>{baseValue.toFixed(1)}</strong></span>
        <span>Final Calibrated Risk: <strong style={{ color: finalRisk >= 70 ? '#ef4444' : '#f59e0b' }}>{finalRisk.toFixed(1)} / 100</strong></span>
      </div>

      {attributions.slice(0, 7).map((attr, idx) => {
        const isPositive = attr.contribution >= 0;
        const barWidthPct = Math.min(100, (Math.abs(attr.contribution) / maxAbsContrib) * 100);

        return (
          <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
              <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{attr.display_name}</span>
              <span style={{ fontFamily: 'monospace', color: isPositive ? '#ef4444' : '#10b981', fontWeight: 'bold' }}>
                {isPositive ? `+${attr.contribution.toFixed(1)}` : attr.contribution.toFixed(1)} pts
              </span>
            </div>
            
            {/* Visual Contribution Bar */}
            <div style={{ height: '8px', width: '100%', background: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
              <div
                style={{
                  height: '100%',
                  width: `${barWidthPct}%`,
                  background: isPositive ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : 'linear-gradient(90deg, #06b6d4, #10b981)',
                  borderRadius: '4px',
                  transition: 'width 0.4s ease-out',
                }}
              />
            </div>
            <span style={{ fontSize: '11px', color: '#64748b' }}>{attr.interpretation}</span>
          </div>
        );
      })}
    </div>
  );
};
