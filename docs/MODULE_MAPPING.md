# Module Mapping & Functional Lineage: NEXUS-BTC

This document specifies the exact functional mapping from the six reference repositories to the canonical modules of **NEXUS-BTC**. In accordance with Phase 2 clean-room standards, all selected capabilities are adopted as conceptual blueprints and independently reimplemented in native Python/TypeScript.

---

## 1. Complete Source-to-Target Module Mapping Matrix

| Source Repository | Source File / Module | Selected Functionality & Logic | Destination NEXUS-BTC Module | Rationale for Selection | License & Provenance Constraints |
|---|---|---|---|---|---|
| **SIH26146** | `backend/app/schemas/ingest.py` | 14-field NTRO canonical schema validation (regex TXID, IP validation, script types) | `nexus_btc/ingestion/schema.py` | Exact domain match for NTRO SIH 2026 Problem Statement 5 | UNLICENSED. Reimplemented in clean Pydantic v2 with defensive defaults. |
| **SIH26146** | `backend/app/services/parser.py` | Multi-format ingestion parser (CSV, JSON, array extraction) | `nexus_btc/ingestion/parser.py` | Robust row parsing and quality flag generation | UNLICENSED. Clean-room Python parser supporting CSV, JSON, XML. |
| **SIH26146** | `backend/app/services/enrichment.py` | Local MaxMind GeoLite2 (.mmdb) offline IP-to-Country & ASN enrichment | `nexus_btc/enrichment/network_enricher.py` | Enables offline air-gapped network layer attribution | UNLICENSED. Reimplemented using `maxminddb` with fallback to `"UNKNOWN"`. |
| **SIH26146** | `backend/scripts/detect_peeling_chains.py` | Peeling chain candidate identification (peel <= 0.05, change >= 0.80) and hop traversal (>= 5 hops) | `nexus_btc/motifs/peeling_chains.py` | High-precision structural detector for Bitcoin laundering | UNLICENSED. Reimplemented in NetworkX without requiring Neo4j Cypher. |
| **SIH26146** | `backend/scripts/detect_coinjoin.py` | Multi-party CoinJoin detection with sliding-window equal-output filter (+- 1%) | `nexus_btc/motifs/coinjoin.py` | Robust heuristic for detecting CoinJoin/Wasabi/Whirlpool mixes | UNLICENSED. Implemented in pure Python over transaction graph. |
| **SIH26146** | `backend/app/services/shap_service.py` | SHAP waterfall explanation data contract and attribution ranking | `nexus_btc/explainability/shap_engine.py` | Clear, explainable feature attributions for forensic analysts | UNLICENSED. Native Scikit-Learn `TreeExplainer` pipeline. |
| **SIH26146** | `backend/tests/test_*.py` (26 files) | Forensic validation test specifications (ingestion invariants, GeoIP, detectors) | `nexus_btc/tests/unit/` & `integration/` | Comprehensive test coverage ensuring zero regression | UNLICENSED. Test cases re-authored in Pytest against embedded SQLite. |
| **Cryptracer** | `internal/tracer/tracer.go` | Value-aware best-first forward fund tracing with semantic stop reasons (`utxo`, `service`, `mixer`, `cycle`, `max_hops`) | `nexus_btc/forensics/fund_tracer.py` | Prevents exponential BFS explosion while tracing laundering paths | **GPL-3.0**. ZERO Go code copied. Reimplemented in Python with priority queues. |
| **Cryptracer** | `internal/aggregator/Mixer.go` & `mixer_detection_advanced.go` | Academic mixer indicators (Wu et al.): P2SH output dominance (>= 5x), sweeper transactions, temporal ordering (a1/a2) | `nexus_btc/motifs/mixer_advanced.py` | Rigorous peer-reviewed detection rules for mixer topologies | **GPL-3.0**. Algorithmic specification only. Implemented in NetworkX. |
| **Cryptracer** | `public/graph.js` | Forensic graph canvas visual styling (node size by volume, edge arrows, high-risk node glows) | `nexus_btc_ui/src/components/GraphCanvas.tsx` | Visually compelling Cytoscape.js UX for forensic investigation | **GPL-3.0**. Rebuilt from scratch in modern React + Cytoscape.js. |
| **SIH-2026 (ChainTrace)** | `src/core/unionfind.js` | Disjoint Set Union (Union-Find) with path compression and union-by-rank | `nexus_btc/clustering/union_find.py` | Optimal O(alpha(N)) Common Input Ownership Heuristic clustering | MIT (unverified). Reimplemented in Python with full type annotations. |
| **SIH-2026 (ChainTrace)** | `src/analysis/behavior.js` | Behavioral feature extraction: transaction velocity, fan-in/fan-out ratios | `nexus_btc/features/transaction_view.py` | Captures high-velocity layering and rapid consolidation | MIT (unverified). Independent Python mathematical implementation. |
| **SIH-2026 (ChainTrace)** | `python/pipeline.py` | HDBSCAN clustering over behavioral feature vectors | `nexus_btc/clustering/hdbscan_clustering.py` | Density-based entity cohort identification without manual k | MIT (unverified). Native Scikit-Learn / HDBSCAN pipeline. |
| **Elliptic Anomaly** | `scripts/probability_calibration.py` | Platt scaling & isotonic regression probability calibration; Brier score loss | `nexus_btc/ml/calibration.py` | Prevents overconfident raw ML probabilities; provides calibrated risk | Absent license. Mathematical calibration implemented via Scikit-Learn. |
| **Elliptic Anomaly** | `scripts/structural_graph_features.py` | OddBall ego-net power-law outlier metrics (E proportional to N^alpha), clustering coefficients, avg neighbour degree | `nexus_btc/features/graph_view.py` | Detects structural topological anomalies without node labels | Absent license. Implemented in NetworkX using ego-graph metrics. |
| **Elliptic Anomaly** | `src/models.py` | Scikit-Learn model zoo: Random Forest, Isolation Forest, Local Outlier Factor | `nexus_btc/ml/model_zoo.py` | Lightweight, stable, CPU-friendly ML stack with zero CUDA dependency | Absent license. Standard Scikit-Learn estimators instantiated cleanly. |
| **Elliptic Anomaly** | `src/autoencoder.py` | F1-optimal threshold tuning algorithm on validation splits | `nexus_btc/evaluation/threshold_tuner.py` | Optimizes decision thresholds on severe class imbalances | Absent license. Implemented in Python evaluation module. |
| **Bitcoin_Fraud_Gnn** | `src/features.py` | Approximate betweenness (k=200 pivot sampling), PageRank, HITS, contagion ratios | `nexus_btc/features/graph_view.py` | Scalable centrality features and illicit contagion propagation | Absent license. Implemented in pure Python/NetworkX. |
| **Bitcoin_Fraud_Gnn** | `src/model.py` | 3-layer GraphSAGE architecture with residual addition and batch normalisation | `nexus_btc/ml/optional_gnn.py` | Optional deep learning accelerator behind a safe fallback switch | Absent license. Modular PyTorch/PyG module isolated in optional plugin. |
| **ElliptiGraph** | `analysis/eda.py` | Summary statistics, volume distribution percentiles, degree histograms | `nexus_btc/analytics/eda_profiler.py` | Comprehensive statistical reporting for offline forensic dashboards | Absent license. Implemented via Pandas/Numpy profiling. |

---

## 2. Architectural Evolution: From Bloated Microservices to Embedded Canonical Stack

```
+-------------------------------------------------------------+
|              Legacy Architecture (Friction)                 |
|  - PostgreSQL / TimescaleDB (External RDBMS container)       |
|  - Neo4j 5.26 Graph Database (2GB JVM Heap container)       |
|  - Redis 7 Broker + Celery Background Workers               |
|  - Next.js 16 Server-Side Rendering (Node.js daemon)        |
|  - External Public Blockchain APIs (Network Dependency)     |
+-------------------------------------------------------------+
                              |
                     CONSOLIDATED INTO
                              v
+-------------------------------------------------------------+
|              NEXUS-BTC Canonical Stack (Zero-Friction)      |
|  - Embedded SQLite 3 / DuckDB (Zero configuration, stdlib)  |
|  - In-Memory NetworkX MultiDiGraph Engine + Fast Indexing   |
|  - In-Process Python Async / ThreadPoolExecutor             |
|  - Static React 19 + Vite SPA served directly via FastAPI   |
|  - 100% Offline Synthetic Scenario Engine + MaxMind MMDB    |
+-------------------------------------------------------------+
```

---

## 3. Exclusion Register: What We Are Deliberately Omitting

| Component / Technology | Source Repository | Reason for Omission | Replacement in NEXUS-BTC |
|---|---|---|---|
| **Neo4j Database Server** | Cryptracer, SIH26146 | Requires 2GB+ JVM heap, complex Bolt protocols, and frequent connection timeouts during demos. | In-memory NetworkX directed multigraph + SQLite edge index. |
| **Celery + Redis** | SIH26146 | Adds 2 background daemon dependencies and brittle IPC. | FastAPI `BackgroundTasks` and Python `concurrent.futures.ThreadPoolExecutor`. |
| **PostgreSQL / TimescaleDB** | SIH26146 | Requires external Docker service or dedicated DB server. | Embedded SQLite with WAL mode enabled (or DuckDB for analytical queries). |
| **ArangoDB Multi-Model DB** | ElliptiGraph | Non-standard database requiring Docker installation and AQL language learning. | Standard relational SQLite + NetworkX. |
| **Next.js 16 App Router** | SIH26146 | Node.js server requirement; complex hydration errors; excessive build artifacts. | Static React + Vite SPA, pre-built into static assets served directly by FastAPI. |
| **Electron Shell** | SIH-2026 (ChainTrace) | 150MB+ bundle size, complex OS-specific window management and native bindings. | Standard responsive browser UI running on `http://localhost:8000`. |
| **Go Gin Web Server** | Cryptracer | Introduces a second runtime language (Go) alongside Python ML. | Unified single-language Python FastAPI backend. |
| **Mandatory Blockchain APIs** | Cryptracer, ChainTrace | Network latency, rate limiting, and failure when offline/air-gapped. | Local synthetic generator and pre-bundled forensic test files. |
| **Hard Deep Learning Dependency** | Bitcoin_Fraud_Gnn, SIH26146 | CUDA/PyG wheel mismatches cause catastrophic build crashes on student laptops. | Random Forest + Isolation Forest core; PyG GraphSAGE as optional toggle. |

---

## 4. Verification of Component Parity
The canonical architecture retains **100% of the forensic and scientific capabilities** present across the six source repositories:
- Full 14-field NTRO network-blockchain telemetry correlation.
- Peeling chain and CoinJoin motif identification.
- Union-Find address clustering and HDBSCAN behavioral grouping.
- Value-aware forward fund tracing with semantic stop reasons.
- SHAP feature attributions and counterfactual analysis.
- Offline MaxMind GeoIP and ASN attribution.
- Professional 12-view digital forensics command center.
