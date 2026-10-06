import React, { useRef, useState } from 'react';
import { Upload, Play, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import { postIngestFile, postRunPipeline } from '../services/api';

interface HeaderProps {
  onDataRefreshed: () => void;
  systemStatus?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onDataRefreshed,
  systemStatus = 'HEALTHY',
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    setStatusMsg(`Ingesting ${file.name}...`);
    try {
      const res = await postIngestFile(file);
      setStatusMsg(`Ingested ${res.records_valid} records (${res.records_invalid} quarantined)`);
      onDataRefreshed();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setStatusMsg(null), 4000);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleRunPipeline = async () => {
    setIsProcessing(true);
    setStatusMsg('Executing 14-stage forensic analysis...');
    try {
      const summary = await postRunPipeline();
      setStatusMsg(`Analysis finished: ${summary.alerts_generated} alerts generated in ${summary.execution_time_seconds}s`);
      onDataRefreshed();
    } catch (err: any) {
      setStatusMsg(`Pipeline error: ${err.message}`);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setStatusMsg(null), 4000);
    }
  };

  return (
    <header className="header">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '12px', color: '#10b981', fontWeight: 600 }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
          AIR-GAPPED OFFLINE MODE
        </span>
        {statusMsg && (
          <span style={{ fontSize: '12px', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
            {statusMsg}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".csv,.json,.xml"
          style={{ display: 'none' }}
        />
        <button
          className="btn-secondary"
          onClick={() => fileInputRef.current?.click()}
          disabled={isProcessing}
          title="Upload CSV, JSON, or XML transaction file"
        >
          <Upload size={14} />
          <span>Ingest Data</span>
        </button>

        <button
          className="btn-primary"
          onClick={handleRunPipeline}
          disabled={isProcessing}
          title="Run Entity Clustering, Laundering Motifs, and AI Anomaly Ensemble"
        >
          <Play size={14} />
          <span>Run Analysis</span>
        </button>
      </div>
    </header>
  );
};
