# Third-Party Notices & Intellectual Property Audit: NEXUS-BTC

## 1. Compliance Policy & Legal Doctrine
NEXUS-BTC (Network–Entity eXplainable Unified Surveillance for Bitcoin) enforces a strict **Clean-Room Implementation & Provenance Policy** for all codebase integrations:

1. **GPLv3 / Copyleft Restrictions**: Source code licensed under strong copyleft licenses (e.g. GNU GPLv3) is strictly forbidden from direct copying, bundling, or linking into the canonical codebase. Any algorithmic insights or mathematical formulations derived from such sources must be implemented completely independently from scratch.
2. **Unlicensed / Ambiguous Repositories**: Source code from repositories lacking an explicit open-source license (or marked `UNLICENSED`) remains the exclusive intellectual property of the original authors ("All Rights Reserved"). Under Phase 2 instructions, **NO direct copy-paste or derivative reproduction is permitted**. These codebases are utilized strictly as **conceptual architectures, algorithmic blueprints, and behavioral specifications**.
3. **Attribution & Academic Integrity**: Every technical inspiration, mathematical formulation, research paper citation, and conceptual architecture is transparently documented with full author attribution below.

---

## 2. Inventory of Source Repositories & Legal Assessment

| Repository Name | Upstream URL | Author / Organisation | Declared License | Legal Classification | Allowed Usage in NEXUS-BTC |
|---|---|---|---|---|---|
| **Cryptracer** | `https://github.com/Cathe0n/Cryptracer.git` | Cathe0n | **GNU GPL v3.0** | Strong Copyleft | **Conceptual Reference Only**. Zero Go/JS code copied. Algorithms reimplemented in Python. |
| **SIH26146** | `https://github.com/kaiizer777/SIH26146.git` | kaiizer777 (NTRO SIH 2026 Team) | **UNLICENSED** | Proprietary / All Rights Reserved | **Architectural & Conceptual Blueprint**. Schemas, detector logic, and test cases cleanly reimplemented. |
| **Elliptic-Bitcoin-Anomaly-Detection** | `https://github.com/Sajjad-Shahali/Elliptic-Bitcoin-Anomaly-Detection.git` | Sajjad Shahali (Master's Thesis s340464) | **None** (Absent) | All Rights Reserved | **Scientific & Empirical Reference**. Calibration equations and structural metrics independently coded. |
| **SIH-2026-AI-Powered-Monitoring-And-Analysis-Of-Bitcoin-Transaction-Traffic** | `https://github.com/official-imvoiid/SIH-2026-AI-Powered-Monitoring-And-Analysis-Of-Bitcoin-Transaction-Traffic.git` | Team-Unfilter / official-imvoiid | **MIT** (Declared in package.json, no file) | Ambiguous / Missing Notice | **Algorithmic Blueprint**. Union-Find and Best-First Tracing re-engineered in Python. |
| **Bitcoin_Fraud_Gnn** | `https://github.com/LawanMercy/Bitcoin_Fraud_Gnn.git` | Opeyemi Mercy Lawan | **None** (Absent) | All Rights Reserved | **Feature Engineering Reference**. Topological metrics reimplemented in Scikit-Learn/NetworkX. |
| **ElliptiGraph** | `https://github.com/0xnomy/ElliptiGraph.git` | 0xnomy | **None** (Absent) | All Rights Reserved | **EDA & Query Reference**. Summary statistic concepts independently integrated. |

---

## 3. Detailed Provenance & Clean-Room Mapping

### 3.1. Cryptracer
- **GitHub URL**: `https://github.com/Cathe0n/Cryptracer.git`
- **Author**: Cathe0n
- **License**: GNU General Public License v3.0 (GPL-3.0)
- **Attribution Notice**:
  > Copyright (C) 2025-2026 Cathe0n. Distributed under the terms of the GNU General Public License v3.0.
- **Components Reused**: **ZERO lines of code copied.**
- **Components Used as Conceptual Reference**:
  - The value-aware fund tracing state machine and semantic stop conditions (`utxo`, `known_service`, `mixer_detected`, `cycle`, `max_hops`) in `internal/tracer/tracer.go`.
  - Topological mixer detection heuristics based on Wu et al. (P2SH output ratios $\ge 5	imes$, 1-in 2-out sweeper transactions, cycle durations $< 3	ext{ h}$) in `internal/aggregator/Mixer.go`.
  - Cytoscape.js visual graph canvas styling, node sizing by transaction volume, and color palettes.
- **Modifications / Clean-Room Implementation**:
  - Fully rewritten in Python (FastAPI backend + pure NetworkX graph engine) and modern React/TypeScript/Cytoscape.js.
  - Eliminated external API dependencies (Bitquery, Mempool.space, Blockstream) in favor of local offline storage.

---

### 3.2. SIH26146
- **GitHub URL**: `https://github.com/kaiizer777/SIH26146.git`
- **Author**: kaiizer777
- **License**: UNLICENSED (Proprietary)
- **Attribution Notice**:
  > Based on the NTRO SIH 2026 Problem Statement 5 reference architecture by kaiizer777.
- **Components Reused**: **ZERO verbatim code copied.**
- **Components Used as Conceptual Reference**:
  - 14-field canonical telemetry schema: `ts`, `src_ip`, `dst_ip`, `src_port`, `dst_port`, `txid`, `input_addresses[]`, `output_addresses[]`, `input_amounts[]`, `output_amounts[]`, `fee`, `script_type`, `geo_country`, `asn`.
  - MaxMind GeoLite2 offline enrichment pipeline.
  - Peeling chain detection parameters (peel ratio $\le 0.05$, change ratio $\ge 0.80$, minimum chain depth $\ge 5$).
  - CoinJoin sliding-window equal-output matching algorithm ($\pm 1\%$ relative tolerance).
  - SHAP waterfall attribution schema for explainable AI.
  - Test scenario parameters from `test_1000.csv` and `test_2000.csv`.
- **Modifications / Clean-Room Implementation**:
  - Completely replaced the 4-container infrastructure stack (Postgres + Neo4j + Redis + Celery) with an embedded zero-dependency architecture (SQLite/DuckDB + NetworkX + in-process async tasks).
  - Replaced Next.js 16 SSR with a static React/Vite SPA.
  - Implemented clean Pydantic v2 schemas and pure-Python NetworkX graph motif detection.

---

### 3.3. Elliptic-Bitcoin-Anomaly-Detection
- **GitHub URL**: `https://github.com/Sajjad-Shahali/Elliptic-Bitcoin-Anomaly-Detection.git`
- **Author**: Sajjad Shahali (Master's Thesis s340464)
- **License**: None (All Rights Reserved)
- **Attribution Notice**:
  > Inspired by the academic research and thesis "Elliptic Bitcoin Anomaly Detection" by Sajjad Shahali (2025-2026).
- **Components Reused**: **ZERO code or binary model checkpoints copied.**
- **Components Used as Conceptual Reference**:
  - Platt scaling and isotonic regression probability calibration algorithms for mitigating model overconfidence.
  - OddBall ego-network power-law outlier metrics ( \propto N^lpha$) and structural graph features (clustering coefficient, average neighbor degree).
  - Strict temporal validation split methodologies (preventing temporal data leakage across sequential transaction windows).
  - SHAP TreeExplainer attribution methodology for tree ensembles.
- **Modifications / Clean-Room Implementation**:
  - Implemented calibration and structural metrics using standard Scikit-Learn and pure NetworkX within NEXUS-BTC.
  - Avoided fragile, heavy PyTorch/DOMINANT/GAT binary dependencies to guarantee 100% offline CPU execution on student laptops.

---

### 3.4. SIH-2026-AI-Powered-Monitoring-And-Analysis-Of-Bitcoin-Transaction-Traffic (ChainTrace)
- **GitHub URL**: `https://github.com/official-imvoiid/SIH-2026-AI-Powered-Monitoring-And-Analysis-Of-Bitcoin-Transaction-Traffic.git`
- **Author**: Team-Unfilter / official-imvoiid
- **License**: Declared as MIT in `package.json` (missing standalone notice)
- **Attribution Notice**:
  > Conceptually inspired by the ChainTrace application by Team-Unfilter.
- **Components Reused**: **ZERO code copied.**
- **Components Used as Conceptual Reference**:
  - Disjoint Set Union (Union-Find) with path compression and rank optimization for multi-input address clustering.
  - Priority-queue driven Best-First forward money flow traversal avoiding exponential BFS fan-out.
  - Operational indicators: transaction velocity (time deltas), fan-in/fan-out ratios.
- **Modifications / Clean-Room Implementation**:
  - Eliminated the Node.js / Electron / Python multi-process IPC runtime.
  - Rewrote the Union-Find entity clustering and best-first tracer in high-performance Python classes.

---

### 3.5. Bitcoin_Fraud_Gnn
- **GitHub URL**: `https://github.com/LawanMercy/Bitcoin_Fraud_Gnn.git`
- **Author**: Opeyemi Mercy Lawan
- **License**: None (All Rights Reserved)
- **Attribution Notice**:
  > Feature engineering formulations inspired by "Bitcoin Fraud Detection with Graph Neural Networks" by Opeyemi Mercy Lawan (2026).
- **Components Reused**: **ZERO code copied.**
- **Components Used as Conceptual Reference**:
  - Neighbourhood contagion metrics (`pred_illicit_ratio`, `nb_illicit_ratio`).
  - Graph-aware structural metrics (approximate betweenness pivot sampling, PageRank, HITS hub/authority scores).
- **Modifications / Clean-Room Implementation**:
  - Reimplemented feature extraction in Python using NetworkX and Scikit-Learn.
  - Made deep learning (GraphSAGE) an optional secondary accelerator behind classical ML models.

---

### 3.6. ElliptiGraph
- **GitHub URL**: `https://github.com/0xnomy/ElliptiGraph.git`
- **Author**: 0xnomy
- **License**: None (All Rights Reserved)
- **Attribution Notice**:
  > Inspired by the ElliptiGraph pipeline by 0xnomy.
- **Components Reused**: **ZERO code copied.**
- **Components Used as Conceptual Reference**:
  - Exploratory data analysis (EDA) profiling metrics and multi-hop graph expansion patterns.
- **Modifications / Clean-Room Implementation**:
  - Replaced ArangoDB and Dash with embedded SQLite/DuckDB and FastAPI + React/Cytoscape.js.

---

## 4. Benchmark Datasets & Public Academic References
- **Elliptic Benchmark Dataset**:
  - Source: Weber et al., "Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Technologies", KDD 2019.
  - Usage in NEXUS-BTC: Synthetic offline scenarios and schema compatibility only.
- **Wu et al. Mixer Detection Heuristics**:
  - Reference: Wu et al., "Detecting Mixing Transactions on the Bitcoin Network", IEEE Transactions on Network and Service Management.
  - Usage: Algorithmic rules for P2SH output ratios and temporal ordering.
- **MaxMind GeoLite2**:
  - Source: MaxMind, Inc. (GeoLite2 Open Database).
  - Usage: Local `.mmdb` files loaded offline without remote API calls.

---

## 5. Certification of Independent Implementation
I certify that NEXUS-BTC is architected from clean-room specifications. No copyrighted, proprietary, or GPL-copyleft source code is bundled into the distribution. All algorithms, schemas, services, and visual interfaces are independently implemented and fully documented.
