# Implementation Roadmap: NEXUS-BTC

## Phase-by-Phase Execution Plan

```
Sprint 1: Foundation & Data Layer
[Canonical Ingest] ---> [Data Model & SQLite] ---> [GeoIP Enrichment]
                                                          |
Sprint 2: Graph & Forensics                               v
[NetworkX Engine] <--- [Union-Find Clusters] <--- [Motif Detectors]
       |
       v
Sprint 3: AI/ML & Explainability
[Model Zoo (RF/IF)] ---> [Platt Calibration] ---> [SHAP XAI Engine]
                                                          |
Sprint 4: API, UI & Validation                            v
[FastAPI Gateway] ---> [React/Cytoscape UI] ---> [Test Suites & Scenarios]
```

---

## Detailed Sprint Milestones

### Sprint 1: Data Ingestion, Sanitization & Persistence
- **Deliverables**:
  - Implement `nexus_btc/ingestion/schema.py` (Pydantic v2 validation).
  - Implement `nexus_btc/ingestion/parser.py` (CSV, JSON, and XML parsers).
  - Implement `nexus_btc/database/sqlite_manager.py` (SQLite schema, WAL mode, indexing).
  - Implement `nexus_btc/enrichment/network_enricher.py` (Offline MaxMind GeoIP & ASN lookup).
- **Exit Criteria**: Can ingest 2,000 malformed transactions without crashing; database correctly populated.

### Sprint 2: Graph Topologies, Entity Clustering & Motif Detection
- **Deliverables**:
  - Implement `nexus_btc/clustering/union_find.py` (Co-spend Disjoint Set Union clustering).
  - Implement `nexus_btc/graph/graph_engine.py` (NetworkX MultiDiGraph in-memory engine).
  - Implement `nexus_btc/motifs/peeling_chains.py` (Peeling chain candidate filter and hop traversal).
  - Implement `nexus_btc/motifs/coinjoin.py` (Multi-party equal-output sliding window detector).
  - Implement `nexus_btc/forensics/fund_tracer.py` (Value-aware best-first search with stop reasons).
- **Exit Criteria**: Accurately detects simulated peeling chains (>= 5 hops) and CoinJoin transactions in < 100ms.

### Sprint 3: Modular AI/ML, Probability Calibration & Explainability
- **Deliverables**:
  - Implement `nexus_btc/features/feature_extractor.py` (Multi-view feature extraction).
  - Implement `nexus_btc/ml/model_zoo.py` (Random Forest, Isolation Forest, LOF).
  - Implement `nexus_btc/ml/calibration.py` (Platt scaling & Isotonic regression).
  - Implement `nexus_btc/explainability/shap_engine.py` (SHAP TreeExplainer & waterfall generator).
  - Implement `nexus_btc/explainability/counterfactual.py` (Ablation sensitivity deltas).
- **Exit Criteria**: Generates calibrated risk scores (0-100) and SHAP attribution payloads for every alert.

### Sprint 4: Unified API, Interactive Dashboard & Evaluation Harness
- **Deliverables**:
  - Implement `nexus_btc/api/` (FastAPI routers for Ingest, Alerts, Graph, Trace, Scenarios).
  - Implement `nexus_btc/simulation/scenario_generator.py` (10 offline forensic scenarios).
  - Build `nexus_btc_ui/` (Vite + React 19 + Cytoscape.js 12-view forensic dashboard).
  - Author `tests/` (Unit, integration, ML, graph, and E2E test suites).
- **Exit Criteria**: Complete end-to-end demonstration running offline on `http://localhost:8000`.
