# Risk Register & Mitigation Strategy: NEXUS-BTC

## 1. Overview
This register catalogs technical, operational, algorithmic, and evaluation risks associated with building and demonstrating NEXUS-BTC, along with verified mitigation mechanisms.

---

## 2. Risk Assessment Matrix

| ID | Category | Risk Description | Severity | Likelihood | Mitigation Strategy |
|---|---|---|---|---|---|
| **R-01** | Technical | **Dependency Hell / Wheel Mismatches**: Heavy deep learning libraries (`torch`, `torch_geometric`) fail to compile or install on standard student machines. | **HIGH** | **HIGH** | Architect a strict two-tier ML design: Scikit-Learn (Random Forest, Isolation Forest, LOF) serves as the primary zero-dependency engine. PyG is strictly optional. |
| **R-02** | Operational | **Container Startup Crashes**: Multi-container Docker topologies (Neo4j, Postgres, Redis, Celery) exhaust RAM and crash during live viva evaluations. | **CRITICAL** | **HIGH** | Completely eliminate all background service daemons. Consolidate persistence into embedded SQLite 3 / DuckDB and in-memory NetworkX. |
| **R-03** | Algorithmic | **Exponential Graph Traversal Explosion**: Naive Breadth-First Search (BFS) explodes exponentially on high-fanout Bitcoin transactions. | **HIGH** | **MEDIUM** | Implement Value-Aware Best-First Search with priority queues, value pruning thresholds (> 0.001 BTC), and hard hop/node horizons. |
| **R-04** | Algorithmic | **Uncalibrated Model Overconfidence**: Raw classifier probabilities output false 99% risk scores on borderline normal transactions. | **MEDIUM** | **HIGH** | Enforce Platt scaling and isotonic regression probability calibration, validating against Brier score loss. |
| **R-05** | Legal | **License Contamination (GPLv3 / Proprietary)**: Direct copying of source code from Cryptracer (GPLv3) or unlicensed repos violates copyright. | **HIGH** | **LOW** | Enforce clean-room engineering: zero code copied; all algorithms and schemas independently implemented in Python. |
| **R-06** | Operational | **Offline Demonstration Failure**: System fails or hangs due to hardcoded external network requests to block explorers or APIs. | **CRITICAL** | **MEDIUM** | Enforce offline-first design: bundle local MaxMind `.mmdb` files and an offline synthetic scenario generator. No mandatory internet access. |
| **R-07** | Forensics | **False Attribution (IP = Wallet Owner)**: Presenting IP address as definitive wallet identity creates forensic inaccuracy. | **MEDIUM** | **MEDIUM** | Explicitly distinguish between OBSERVED, INFERRED, and PROBABILISTIC association tiers, reporting evidence confidence scores. |
| **R-08** | Academic | **Complexity Defense Failure**: Student is unable to explain opaque deep learning architectures during viva questioning. | **HIGH** | **MEDIUM** | Prioritize interpretable models: SHAP waterfall feature attributions, topological ego-net metrics, and counterfactual ablation analysis. |
