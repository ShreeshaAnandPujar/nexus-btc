export interface EvidenceChainStep {
  step_number: number;
  step_type: string;
  identifier: string;
  description: string;
  relationship: 'observed' | 'inferred' | 'probabilistic';
  confidence: number;
  metadata?: Record<string, any>;
}

export interface FeatureAttribution {
  feature_name: string;
  feature_value: number;
  contribution: number;
  display_name: string;
  category: string;
  interpretation: string;
}

export interface CounterfactualResult {
  original_risk: number;
  modified_feature_name: string;
  feature_removed_or_modified: string;
  new_risk: number;
  delta: number;
  interpretation: string;
}

export interface GraphAblationResult {
  original_risk: number;
  ablated_motif_or_subgraph: string;
  risk_after_ablation: number;
  delta: number;
  structural_influence_pct: number;
}

export interface ExplanationResponse {
  alert_id: string;
  txid: string;
  base_expected_value: number;
  final_risk_score: number;
  top_feature_attributions: FeatureAttribution[];
  model_contributions: Record<string, number>;
  counterfactuals: CounterfactualResult[];
  graph_ablations: GraphAblationResult[];
  forensic_summary: string;
}

export interface AlertSummary {
  alert_id: string;
  txid: string;
  entity_id?: string;
  risk_score: number;
  confidence_score: number;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  primary_motif?: string;
  created_at: string;
  status: string;
  amount_btc: number;
  country: string;
}

export interface AlertQueueResponse {
  total_alerts: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  alerts: AlertSummary[];
}

export interface AlertResponse {
  alert_id: string;
  txid: string;
  entity_id?: string;
  risk_score: number;
  confidence_score: number;
  severity: string;
  primary_motif?: string;
  motifs: string[];
  created_at: string;
  status: string;
  explanation: ExplanationResponse;
  counterfactual: CounterfactualResult[];
  evidence_chain: EvidenceChainStep[];
  model_contributions: Record<string, number>;
}

export interface EntitySummary {
  entity_id: string;
  cluster_type: string;
  wallet_count: number;
  risk_score: number;
  confidence_score: number;
  total_volume_btc: number;
}

export interface EntityDetail extends EntitySummary {
  cluster_confidence: number;
  member_wallets: string[];
  first_seen?: string;
  last_seen?: string;
  cluster_features: Record<string, any>;
  cluster_evidence: string[];
  recent_transactions: any[];
  detected_motifs: string[];
  associated_ips: string[];
}

export interface CytoscapeNodeData {
  id: string;
  label: string;
  type: 'WALLET' | 'TRANSACTION' | 'IP' | 'ENTITY' | 'ASN' | 'COUNTRY' | string;
  risk: number;
  confidence: number;
  amount: number;
  cluster_id?: string;
  sublabel?: string;
  metadata?: Record<string, any>;
}

export interface CytoscapeEdgeData {
  id: string;
  source: string;
  target: string;
  relationship: string;
  amount: number;
  timestamp?: string;
  confidence: number;
  provenance: string;
}

export interface GraphResponse {
  nodes: { data: CytoscapeNodeData }[];
  edges: { data: CytoscapeEdgeData }[];
  node_count: number;
  edge_count: number;
  subgraph_type: string;
  focus_id?: string;
}

export interface TraceHop {
  hop_index: number;
  txid: string;
  from_wallet: string;
  to_wallet: string;
  amount_btc: number;
  timestamp: string;
  hop_risk: number;
  stop_reason?: string;
}

export interface TracePath {
  path_id: string;
  hops: TraceHop[];
  total_btc_traced: number;
  endpoint_wallet: string;
  endpoint_type: 'SERVICE' | 'DORMANT' | 'MIXER_LIKE' | 'HORIZON' | 'CYCLE' | 'UNKNOWN';
  path_length: number;
  duration_seconds: number;
  cumulative_risk: number;
}

export interface TraceResponse {
  target: string;
  target_type: string;
  paths_explored: number;
  nodes_visited: number;
  execution_time_ms: number;
  ranked_paths: TracePath[];
  endpoints_summary: Record<string, number>;
}

export interface ScenarioInfo {
  scenario_id: string;
  scenario_type: string;
  title: string;
  description: string;
  expected_pattern: string;
  ground_truth_illicit: boolean;
  expected_motifs: string[];
}

export interface SystemHealth {
  status: string;
  system: string;
  version: string;
  offline_mode: boolean;
  database: {
    type: string;
    status: string;
    path: string;
    transactions_count: number;
    alerts_count: number;
    entities_count: number;
  };
  ml_models: Record<string, string>;
  geolocation: {
    status: string;
    path: string;
    attribution: string;
  };
}

export interface ModelMetrics {
  model_name: string;
  model_version: string;
  models_included: string[];
  calibration: string;
  validation_strategy: string;
  metrics: {
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    pr_auc: number;
    brier_score: number;
    decision_threshold: number;
    confusion_matrix: {
      true_positives: number;
      false_positives: number;
      true_negatives: number;
      false_negatives: number;
    };
    sample_counts: {
      total: number;
      illicit: number;
      benign: number;
    };
  };
}
