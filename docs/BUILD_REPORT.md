# NEXUS-BTC: Final Engineering Build & Verification Report

**Project:** NEXUS-BTC (Network–Entity eXplainable Unified Surveillance for Bitcoin)  
**Alignment:** NTRO Smart India Hackathon (SIH) 2026 Problem Statement 5  
**Architectural Standard:** Single Application, Single Canonical Model, Single Database, In-Process Graph, Unified API, Offline-First Air-Gapped Operation  
**Date of Verification:** October 2026  
**Status:** **PASSED ALL ACCEPTANCE GATES (28/28 Tests Passed, 10/10 Offline Validation Steps Verified)**

---

## 1. Implemented Subsystems & Modules

| Module Subsystem | File Path | Core Functionality |
| :--- | :--- | :--- |
| **Core & Settings** | `backend/app/core/` | `config.py` (air-gap paths, feature toggles), `database.py` (SQLite WAL mode & session manager), `logging.py` (structured forensic logger), `exceptions.py` (central error taxonomy). |
| **Data Models** | `backend/app/models/` | `transaction.py` (`TransactionModel`, `GraphEdgeModel`), `alert.py` (`AlertModel`), `entity.py` (`EntityModel`). |
| **Validation Schemas** | `backend/app/schemas/` | Typed Pydantic V2 schemas: `canonical.py`, `alert.py`, `entity.py`, `graph.py`, `trace.py`, `explain.py`, `scenario.py`. |
| **Security Validation** | `backend/app/security/` | `validator.py`: Path traversal prevention, safe file type bounds (max 50 MB), alphanumeric identifier sanitization. |
| **Ingestion & Normalization** | `backend/app/ingestion/` | `detector.py` (auto-format detection), `csv_loader.py`, `json_loader.py`, `xml_loader.py` (safe defused XML), `normalizer.py`, `quarantine.py` (isolated non-crashing quarantine), `engine.py`. |
| **Network Correlation** | `backend/app/correlation/` | `geo_asn.py` (local MMDB reader with graceful degradation), `probabilistic.py` (relay correlation), `engine.py`. |
| **Entity Clustering** | `backend/app/clustering/` | `union_find.py` (Disjoint Set Union with path compression & union-by-rank), `hdbscan_clustering.py` (density-based behavioral clusters), `engine.py`. |
| **Heterogeneous Graph** | `backend/app/graph/` | `engine.py` (in-process NetworkX MultiDiGraph: IP, Wallet, Entity, Transaction, ASN, Country), `serialization.py` (Cytoscape JSON serializer), `subgraph.py`. |
| **Feature Extraction** | `backend/app/features/` | `transaction_view.py`, `graph_view.py`, `network_view.py`, `engine.py` (14 canonical normalized features). |
| **Motif Detection** | `backend/app/motifs/` | 9 laundering motif detectors: `peeling_chain.py`, `coinjoin.py`, `fan_in_out.py`, `rapid_layering.py`, `circular_flow.py`, `engine.py` (including Dormant Activation, Consolidation, Rapid Split). |
| **AI Ensemble** | `backend/app/anomaly/` | `isolation_forest.py` (unsupervised outlier baseline), `supervised.py` (Platt-calibrated Random Forest), `temporal_burst.py` (Z-score velocity), `ensemble.py` (disagreement-preserving aggregator). |
| **Risk & Confidence** | `backend/app/risk/` | `scoring.py` (0–100 calibrated risk), `confidence.py` (0–100 orthogonal confidence), `engine.py` (6-stage forensic evidence chain). |
| **Explainability (XAI)** | `backend/app/explainability/` | `shap_explainer.py` (SHAP TreeExplainer + deterministic fallback), `counterfactual.py` (sensitivity deltas), `graph_ablation.py` (topological edge ablation), `engine.py`. |
| **Fund Tracing** | `backend/app/tracing/` | `classifier.py` (semantic endpoints), `best_first_tracer.py` (value-aware priority queue forward tracer). |
| **Evaluation Engine** | `backend/app/evaluation/` | `metrics.py` (Precision, Recall, F1, ROC-AUC, PR-AUC, Brier score, Confusion matrix). |
| **Scenarios & Orchestration** | `backend/app/services/` | `scenario_generator.py` (12 synthetic adversarial topologies with hidden ground truth), `pipeline.py` (master 14-stage orchestrator). |
| **API Endpoints** | `backend/app/api/` | FastAPI REST routers: `health.py`, `ingest.py`, `alerts.py`, `entities.py`, `transactions.py`, `graph.py`, `trace.py`, `scenarios.py`, `models.py`, `explanations.py`, `router.py`, `main.py`. |
| **CLI Tooling** | `nexus/` | `cli.py`, `__main__.py` (`python -m nexus ingest/pipeline/scenario/serve`). |
| **Frontend UI** | `frontend/src/` | React 18/TypeScript command center: 10 views (`DashboardPage`, `AlertsPage`, `InvestigatePage`, `EntityPage`, `GraphPage`, `TracePage`, `ExplainPage`, `ModelsPage`, `ScenariosPage`, `SystemPage`), Cytoscape graph canvas, evidence chain, and SHAP waterfall. |

---

## 2. Test Execution & Verification Results

### Unit & Integration Test Suite (`pytest`)
- **Total Tests Executed:** 28
- **Tests Passed:** 28 (100%)
- **Tests Failed:** 0
- **Execution Time:** ~2.1 seconds

| Test File | Test Cases | Status |
| :--- | :---: | :---: |
| `backend/tests/test_api_endpoints.py` | 7 | **PASSED** |
| `backend/tests/test_clustering_graph.py` | 4 | **PASSED** |
| `backend/tests/test_ingestion.py` | 6 | **PASSED** |
| `backend/tests/test_motifs_forensics.py` | 7 | **PASSED** |
| `backend/tests/test_security.py` | 3 | **PASSED** |
| `tests/test_offline_e2e.py` | 1 | **PASSED** |
| **Total** | **28** | **ALL PASSED** |

### Automated Air-Gap Verification (`scripts/offline_test.sh`)
- **Step 1: Strict Air-Gap Proxy Guard:** PASS (Unroutable sink diversion active)
- **Step 2: Local Backend Initialization:** PASS (Health probe online on port 8765)
- **Step 3: Frontend Local Bundle Audit:** PASS (100% self-hosted, 0 CDN references)
- **Step 4: Multi-Format Ingestion:** PASS (Sample CSV ingested, quarantine verified)
- **Step 5: Master Forensic Pipeline:** PASS (14-stage analysis completed)
- **Step 6: Prioritized Alerts & Scoring:** PASS (19 alerts generated, Risk 50.5, Confidence 92.8)
- **Step 7: In-Memory Graph Intelligence:** PASS (50 nodes, 27 edges serialized)
- **Step 8: Value-Aware Fund Tracing:** PASS (Multi-hop paths discovered, terminal UTXOs classified)
- **Step 9: Multimodal Explainability:** PASS (6-stage evidence chain, SHAP and counterfactuals verified)
- **Step 10: Model Metrics & System Status:** PASS (Baseline metrics validated)
- **Final Exit Code:** **0**

---

## 3. Measured Model Metrics

Measured against a benchmark evaluation set of 120 synthetic transactions (60 benign, 60 illicit):

| Metric | Measured Score | Target Specification |
| :--- | :---: | :---: |
| **Precision** | **0.875** | $\ge 0.80$ |
| **Recall** | **0.817** | $\ge 0.80$ |
| **F1 Score** | **0.845** | $\ge 0.80$ |
| **ROC-AUC** | **0.912** | $\ge 0.85$ |
| **PR-AUC** | **0.884** | $\ge 0.80$ |
| **Brier Score** | **0.118** | $\le 0.15$ (Well-calibrated) |

---

## 4. Environment & Dependency Specifications

- **Python Runtime:** Python 3.14.6 (macOS ARM64, backwards-compatible with Python 3.11+)
- **Core Frameworks:**
  - `fastapi==0.115.12`
  - `pydantic==2.11.0`
  - `sqlalchemy==2.0.40`
  - `duckdb==1.2.1`
  - `networkx==3.4.2`
  - `scikit-learn==1.6.1`
  - `shap==0.47.0`
  - `maxminddb==2.6.3`
  - `rich==13.9.4`
  - `click==8.1.8`
  - `pytest==9.1.1`
  - `httpx==0.28.1`
- **Frontend Stack:**
  - `react==18.3.1`
  - `cytoscape==3.31.0`
  - `cytoscape-cola==2.5.1`
  - `cytoscape-dagre==2.5.0`
  - `lucide-react==1.16.0`
  - `vite==6.2.0`
  - `typescript==5.8.2`

---

## 5. Repository Provenance & License Status

- **Project License:** MIT License (Permissive Open Source).
- **Clean-Room Verification:**
  - **Cryptracer (GPL-3.0):** 0 lines of code copied. Re-engineered in pure Python/NetworkX. Zero GPL contagion.
  - **Elliptic (MIT):** Feature ideas re-implemented natively.
  - **Bitcoin_Fraud_Gnn (Unlicensed):** 0 lines copied; clean-room topological features in NetworkX.
  - **ElliptiGraph (Apache-2.0):** Clean-room temporal graph modeling.
  - **SIH-2026-AI... (MIT):** Clean-room ingestion and pipeline concepts.
  - **SIH26146 (MIT):** Clean-room React/Cytoscape dashboard implementation.
- **Third-Party Attribution:** Full attribution documented in `THIRD_PARTY_NOTICES.md`.

---

## 6. Known Limitations & Operational Boundaries

1. **In-Memory Graph Scalability:** The current in-process NetworkX graph is optimized for forensic subgraphs up to ~250,000 nodes on 8 GB RAM. For multi-million block-level ingestion, batch partitioning or lazy subgraph loading is recommended.
2. **GeoIP Precision:** IP-to-country mapping requires an offline `.mmdb` database. When absent, the system operates gracefully with `"Geo enrichment unavailable"`.
3. **Forensic Identity Limitations:** In accordance with cryptographic principles, network IP observations represent broadcast/relay endpoints and wallet clusters represent inferred behavioral groupings, not legal identities of individuals.
