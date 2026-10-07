import {
  AlertQueueResponse,
  AlertResponse,
  EntitySummary,
  EntityDetail,
  GraphResponse,
  TraceResponse,
  ScenarioInfo,
  SystemHealth,
  ModelMetrics,
  TraceHop,
} from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health probe failed');
  return res.json();
}

export async function fetchAlerts(
  severity?: string,
  motif?: string,
  limit = 50,
  offset = 0
): Promise<AlertQueueResponse> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (severity) params.append('severity', severity);
  if (motif) params.append('motif', motif);
  const res = await fetch(`${API_BASE}/alerts?${params}`);
  if (!res.ok) throw new Error('Failed fetching alerts');
  return res.json();
}

export async function fetchAlertDetail(alertId: string): Promise<AlertResponse> {
  const res = await fetch(`${API_BASE}/alerts/${alertId}`);
  if (!res.ok) throw new Error(`Failed fetching alert ${alertId}`);
  return res.json();
}

export async function fetchEntities(limit = 50, offset = 0): Promise<EntitySummary[]> {
  const res = await fetch(`${API_BASE}/entities?limit=${limit}&offset=${offset}`);
  if (!res.ok) throw new Error('Failed fetching entities');
  return res.json();
}

export async function fetchEntityDetail(entityId: string): Promise<EntityDetail> {
  const res = await fetch(`${API_BASE}/entities/${entityId}`);
  if (!res.ok) throw new Error(`Failed fetching entity ${entityId}`);
  return res.json();
}

export async function fetchTransactions(query?: string, limit = 50, offset = 0): Promise<any[]> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (query) params.append('query', query);
  const res = await fetch(`${API_BASE}/transactions?${params}`);
  if (!res.ok) throw new Error('Failed fetching transactions');
  return res.json();
}

export async function fetchTransactionDetail(txid: string): Promise<any> {
  const res = await fetch(`${API_BASE}/transactions/${txid}`);
  if (!res.ok) throw new Error(`Failed fetching transaction ${txid}`);
  return res.json();
}

export async function fetchGlobalGraph(maxNodes = 100): Promise<GraphResponse> {
  const res = await fetch(`${API_BASE}/graph?max_nodes=${maxNodes}`);
  if (!res.ok) throw new Error('Failed fetching graph');
  return res.json();
}

export async function fetchEgoGraph(identifier: string, radius = 2, maxNodes = 80): Promise<GraphResponse> {
  const res = await fetch(`${API_BASE}/graph/${identifier}?radius=${radius}&max_nodes=${maxNodes}`);
  if (!res.ok) throw new Error(`Failed fetching ego graph for ${identifier}`);
  return res.json();
}

export async function postTrace(payload: {
  start_type: string;
  start_identifier: string;
  max_hops?: number;
  max_nodes?: number;
  min_value_ratio?: number;
}): Promise<TraceResponse> {
  const res = await fetch(`${API_BASE}/trace`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Fund tracing request failed');
  return res.json();
}

export async function fetchScenarioCatalog(): Promise<ScenarioInfo[]> {
  const res = await fetch(`${API_BASE}/scenarios/catalog`);
  if (!res.ok) throw new Error('Failed fetching scenario catalog');
  return res.json();
}

export async function postGenerateScenario(payload: {
  scenario_type: string;
  seed?: number;
  transaction_count?: number;
  base_volume_btc?: number;
  inject_noise?: boolean;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/scenarios/generate?auto_ingest=true`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed generating scenario');
  return res.json();
}

export async function fetchModelMetrics(): Promise<ModelMetrics> {
  const res = await fetch(`${API_BASE}/model/metrics`);
  if (!res.ok) throw new Error('Failed fetching model metrics');
  return res.json();
}

export async function postIngestFile(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('run_pipeline', 'true');
  const res = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Ingestion upload failed');
  return res.json();
}

export async function postIngestSample(fileType = 'csv'): Promise<any> {
  const res = await fetch(`${API_BASE}/ingest/sample?file_type=${fileType}&run_pipeline=true`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Sample ingestion failed');
  return res.json();
}

export async function postRunPipeline(): Promise<any> {
  const res = await fetch(`${API_BASE}/pipeline/run`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Pipeline execution failed');
  return res.json();
}

