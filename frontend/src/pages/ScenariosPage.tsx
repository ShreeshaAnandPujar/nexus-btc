import React, { useEffect, useState } from 'react';
import { Cpu, Play, CheckCircle2, ShieldAlert, FileText } from 'lucide-react';
import { fetchScenarioCatalog, postGenerateScenario } from '../services/api';
import { ScenarioInfo } from '../types';

interface ScenariosPageProps {
  onScenarioGenerated?: () => void;
}

export const ScenariosPage: React.FC<ScenariosPageProps> = ({ onScenarioGenerated }) => {
  const [catalog, setCatalog] = useState<ScenarioInfo[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<ScenarioInfo | null>(null);
  const [seed, setSeed] = useState(42);
  const [txCount, setTxCount] = useState(15);
  const [baseVolume, setBaseVolume] = useState(10.0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [resultMsg, setResultMsg] = useState<string | null>(null);

  useEffect(() => {
    loadCatalog();
  }, []);

  const loadCatalog = async () => {
    try {
      const data = await fetchScenarioCatalog();
      setCatalog(data);
      if (data.length > 0) setSelectedScenario(data[2]); // Default to Peeling Chain
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerate = async () => {
    if (!selectedScenario) return;

    setIsGenerating(true);
    setResultMsg(null);
    try {
      const res = await postGenerateScenario({
        scenario_type: selectedScenario.scenario_type,
        seed: Number(seed),
        transaction_count: Number(txCount),
        base_volume_btc: Number(baseVolume),
      });
      setResultMsg(`Generated and ingested ${res.record_count} transactions. Forensic analysis executed.`);
      if (onScenarioGenerated) onScenarioGenerated();
    } catch (err: any) {
      setResultMsg(`Generation failed: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="page-scrollable">
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
          Synthetic Adversarial Scenario Studio
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px' }}>
          Generate, inject, and stress-test 12 deterministic laundering topologies with isolated ground truth.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 20 }}>
        {/* Scenario Catalog */}
        <div className="nexus-card">
          <h2 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: 12 }}>
            Forensic Topologies Catalog ({catalog.length})
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}>
            {catalog.map((scen) => (
              <div
                key={scen.scenario_id}
                onClick={() => setSelectedScenario(scen)}
                style={{
                  background: selectedScenario?.scenario_id === scen.scenario_id ? 'rgba(56, 189, 248, 0.12)' : '#111827',
                  border: '1px solid #1e293b',
                  borderRadius: '6px',
                  padding: '10px 12px',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc' }}>
                    {scen.title}
                  </span>
                  <span className={`badge ${scen.ground_truth_illicit ? 'badge-critical' : 'badge-low'}`} style={{ fontSize: '9px' }}>
                    {scen.ground_truth_illicit ? 'ILLICIT' : 'BENIGN'}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: '#94a3b8', lineHeight: 1.4 }}>
                  {scen.description}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Generator Controls & Ground Truth Panel */}
        {selectedScenario && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div className="nexus-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, borderBottom: '1px solid #1e293b', paddingBottom: 10 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 'bold' }}>{selectedScenario.scenario_id}</span>
                    <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>
                      {selectedScenario.title}
                    </h2>
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: 2 }}>
                    {selectedScenario.scenario_type}
                  </div>
                </div>

                <span className={`badge ${selectedScenario.ground_truth_illicit ? 'badge-critical' : 'badge-low'}`} style={{ fontSize: '11px' }}>
                  GROUND TRUTH: {selectedScenario.ground_truth_illicit ? 'ILLICIT LAUNDERING' : 'BENIGN PAYMENT'}
                </span>
              </div>

              {/* Description & Expected Signature */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: '13px', marginBottom: 16 }}>
                <div>
                  <span style={{ color: '#94a3b8', fontWeight: 600 }}>Description: </span>
                  <span style={{ color: '#cbd5e1' }}>{selectedScenario.description}</span>
                </div>
                <div>
                  <span style={{ color: '#94a3b8', fontWeight: 600 }}>Expected Forensic Signature: </span>
                  <span style={{ color: '#38bdf8', fontFamily: 'monospace' }}>{selectedScenario.expected_pattern}</span>
                </div>
                {selectedScenario.expected_motifs.length > 0 && (
                  <div>
                    <span style={{ color: '#94a3b8', fontWeight: 600 }}>Target Motifs: </span>
                    {selectedScenario.expected_motifs.map((m, i) => (
                      <span key={i} className="badge badge-critical" style={{ marginLeft: 6, fontSize: '10px' }}>
                        {m}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Parameter Inputs */}
              <div style={{ background: '#111827', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b', marginBottom: 16 }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc', marginBottom: 12 }}>
                  Scenario Hyperparameters
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
                  <div>
                    <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>
                      Random Seed
                    </label>
                    <input
                      type="number"
                      value={seed}
                      onChange={(e) => setSeed(Number(e.target.value))}
                      style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>
                      Transaction Count
                    </label>
                    <input
                      type="number"
                      value={txCount}
                      onChange={(e) => setTxCount(Number(e.target.value))}
                      min={1}
                      max={50}
                      style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: 4 }}>
                      Base Volume (BTC)
                    </label>
                    <input
                      type="number"
                      value={baseVolume}
                      onChange={(e) => setBaseVolume(Number(e.target.value))}
                      min={0.1}
                      max={100}
                      step={0.5}
                      style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid #334155', borderRadius: '4px', color: '#f8fafc', fontSize: '12px' }}
                    />
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <button
                  className="btn-primary"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  style={{ padding: '10px 20px', fontSize: '13px' }}
                >
                  <Play size={15} />
                  <span>{isGenerating ? 'Generating...' : 'Generate & Analyze Scenario'}</span>
                </button>
                {resultMsg && (
                  <span style={{ fontSize: '12px', color: '#10b981' }}>
                    {resultMsg}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
