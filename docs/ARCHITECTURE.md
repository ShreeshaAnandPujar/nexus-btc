# NEXUS-BTC: Canonical System Architecture Specification
### Network–Entity eXplainable Unified Surveillance for Bitcoin
**Academic Context:** VTU 5th-Semester Engineering Mini Project  
**Problem Statement Reference:** NTRO Smart India Hackathon (SIH) 2026 — Problem Statement 5  
**Document Classification:** Master Reference Document & Technical Architecture (MRD-01)

---

## 1. Executive Summary & Design Philosophy
NEXUS-BTC is a specialized, production-grade, offline-first digital forensics and transaction surveillance platform engineered for monitoring Bitcoin network traffic and tracking money-laundering topologies.

### Core Engineering Directives:
1. **Zero-Daemon Offline Autonomy**: The platform must execute entirely within an air-gapped environment. It requires no Docker containers, no external database servers (Neo4j, Postgres, Redis), no cloud APIs, and no mandatory API keys.
2. **Student-Manageable & Defense-Ready**: Built using standard Python 3 and modern web primitives (FastAPI + React/Vite + Cytoscape.js + SQLite/DuckDB) to guarantee that any engineering student can install, run, demonstrate, and defend the codebase on ordinary hardware during an evaluation viva.
3. **Calibrated Forensic Honesty**: Complete mathematical separation between **Risk** (how suspicious the observed behavior is) and **Confidence** (the statistical strength and completeness of supporting evidence).
4. **Multimodal Interpretability**: Every flagged alert must provide feature-level explanations (SHAP waterfall attributions), graph-level structural subgraphs, and counterfactual sensitivity deltas.

---

## 2. Canonical Forensic Data Pipeline

```
+-------------------------------------------------------------------------------------------------+
|                                     NEXUS-BTC PIPELINE                                          |
+-------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
                                      [ 1. DATA INGESTION ]
                           Multi-Format Parser (CSV, JSON, XML)
                                                  |
                                                  v
                               [ 2. VALIDATION & NORMALIZATION ]
                     Defensive Pydantic V2 Sanitizer + Quality Flags
                                                  |
                                                  v
                           [ 3. NETWORK-BLOCKCHAIN CORRELATION ]
                   MaxMind GeoIP + ASN Mapping + Probabilistic Binds
                                                  |
                                                  v
                                 [ 4. FEATURE ENGINEERING ]
                 Multi-View Extraction: Transaction, Graph & Network
                                                  |
                                                  v
                            [ 5. ENTITY RESOLUTION / CLUSTERING ]
                     Common Input Ownership (Union-Find) + HDBSCAN
                                                  |
                                                  v
                           [ 6. HETEROGENEOUS TEMPORAL GRAPH ]
                    In-Memory NetworkX MultiDiGraph (Address/Tx Nodes)
                                                  |
                                                  v
                            [ 7. AI REPRESENTATION LEARNING ]
                    Topological Embeddings + Optional GraphSAGE
                                                  |
                                                  v
                                 [ 8. ANOMALY DETECTION ]
                   Isolation Forest + Local Outlier Factor + Autoencoder
                                                  |
                                                  v
                             [ 9. LAUNDERING MOTIF DETECTION ]
                  Structural Detectors (Peeling, CoinJoin, Fan-In/Out)
                                                  |
                                                  v
                             [ 10. RISK + CONFIDENCE FUSION ]
                   Platt-Calibrated Risk (0-100) & Evidence Confidence
                                                  |
                                                  v
                                  [ 11. EXPLAINABLE AI ]
                   SHAP Waterfall Trees + Graph Perturbation Ablation
                                                  |
                                                  v
                                  [ 12. ALERT RANKING ]
                     Prioritized Queue & Forensic Dossier Generation
                                                  |
                                                  v
                              [ 13. FORENSIC EVIDENCE GRAPH ]
                     Induced Ego-Subgraphs + Cytoscape JSON Payloads
                                                  |
                                                  v
                                   [ 14. FUND TRACING ]
                     Value-Aware Best-First Search with Stop Reasons
                                                  |
                                                  v
                                [ 15. OFFLINE DASHBOARD ]
                   12-View Investigative Command Center (React/Vite)
```

---

## 3. High-Level System Architecture & Component Topology

```
+-----------------------------------------------------------------------------------------------+
|                                    NEXUS-BTC RUNTIME TOPOLOGY                                 |
+-----------------------------------------------------------------------------------------------+

  [ PRESENTATION LAYER - BROWSER SPA ]
  +-------------------------------------------------------------------------------------------+
  |  React 19 + TypeScript + Vite + Tailwind/Vanilla CSS + Cytoscape.js                        |
  |  12 Dedicated Views: Command Center, Alert Queue, Tx/Entity Investigator, Graph Forensics,  |
  |  Fund Tracer, SHAP XAI, Network Map, Model Benchmarks, Scenario Studio, Dossier History  |
  +-------------------------------------------------------------------------------------------+
                                              ^
                                              | REST JSON / SSE WebSockets
                                              v
  [ APPLICATION LAYER - FASTAPI ENGINE ]
  +-------------------------------------------------------------------------------------------+
  |  FastAPI Gateway (Uvicorn ASGI)                                                           |
  |  - Ingestion Router     - Graph Forensics Router    - Explainability Router               |
  |  - Alert Queue Router   - Fund Tracing Router       - Synthetic Studio Router             |
  |  - In-Process Background Task Manager (ThreadPoolExecutor)                                |
  +-------------------------------------------------------------------------------------------+
         |                        |                          |                      |
         v                        v                          v                      v
  [ CORE ENGINES ]        [ AI/ML ENGINE ]           [ MOTIF ENGINE ]      [ GRAPH ENGINE ]
  +------------------+    +--------------------+     +------------------+  +------------------+
  | Ingestion Parser |    | Scikit-Learn Model |     | Peeling Chains   |  | In-Memory        |
  | Network Enricher |    | Zoo (RF, IF, LOF)  |     | CoinJoin/Mixer   |  | NetworkX Multi-  |
  | Entity Resolver  |    | Platt Calibrator   |     | Fan-In / Fan-Out |  | DiGraph Storage  |
  | (Union-Find)     |    | SHAP TreeExplainer |     | Layering Tracer  |  | Ego-Net Extractor|
  +------------------+    +--------------------+     +------------------+  +------------------+
         |                        |                          |                      |
         +------------------------+--------------------------+----------------------+
                                              |
                                              v
  [ EMBEDDED DATA & PERSISTENCE LAYER ]
  +-------------------------------------------------------------------------------------------+
  |  - SQLite 3 (WAL Mode, Transactions, Alerts, Edge Cache) / DuckDB Analytical Parquet     |
  |  - Local MaxMind GeoLite2 (.mmdb) Offline IP Database                                     |
  |  - Serialized Scikit-Learn Models & Calibration Artifacts (.joblib)                       |
  |  - Offline Pre-Bundled Test Scenarios & Historical Dossiers                              |
  +-------------------------------------------------------------------------------------------+
```

---

## 4. Multi-View AI Feature Architecture

To provide full coverage of suspicious activity without relying on a single fallible indicator, NEXUS-BTC constructs a **Three-View Feature Representation**:

### View 1: Transaction Behavioral View
- **BTC Volume & Value Concentration**: Total input amount, total output amount, Gini coefficient of output value distribution.
- **Transaction Velocity**: Duration in seconds since previous hop in transaction chain; inputs-per-minute rate.
- **Input/Output Fan Ratios**: Fan-in count ($N_{in}$), fan-out count ($N_{out}$), ratio $R_{fan} = N_{out} / (N_{in} + \epsilon)$.
- **Fee Behavior**: Miner fee satoshis/byte, fee-to-volume ratio, fee deviation from block average.
- **Script Type Entropy**: Shannon entropy of output script bytecode classes.

### View 2: Topological Graph View
- **Degree Centrality**: In-degree, out-degree, total degree, degree ratio.
- **Clustering & Ego-Net Metrics**: Local clustering coefficient ($C_i$), ego-network density, edge-to-node power law deviations (OddBall metrics).
- **Global Centrality**: Approximate betweenness centrality ($k=200$ pivot nodes), PageRank ($lpha=0.85$), HITS Hub and Authority scores.
- **Neighbourhood Contagion Ratios**: Ratio of known illicit/high-risk counterparties in 1-hop and 2-hop topological neighbourhoods.

### View 3: Network Telemetry View
- **IP Concentration & Entropy**: Frequency of transaction emissions per IP, unique transaction count per Autonomous System (ASN).
- **Temporal Proximity**: Latency difference between transaction broadcast timestamp and packet capture time ($\Delta t = |t_{tx} - t_{net}|$).
- **Network Repetition**: Repeated observations of identical IP/Port endpoints across distinct wallet clusters.
- **Geographic & Routing Consistency**: BGP prefix stability, country hop frequency, cross-border velocity.

---

## 5. Machine Learning Architecture & Modular Fallback

```
+-----------------------------------------------------------------------------------------+
|                              NEXUS-BTC ML INFERENCE TIER                                |
+-----------------------------------------------------------------------------------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
         [ SUPERVISED BRANCH ]                             [ UNSUPERVISED BRANCH ]
    Random Forest / Gradient Boost                    Isolation Forest + Local Outlier
  Class-Weighted Tabular Prediction                  Contamination & Novelty Detection
                     |                                                 |
                     +------------------------+------------------------+
                                              |
                                              v
                              [ PROBABILITY CALIBRATION ]
                       Platt Scaling + Isotonic Regression
                                              |
                                              v
                                  [ ENSEMBLE RISK SCORE ]
                         Calibrated Model Risk Probability (0 - 100)
                                              |
                                              v (Optional Hardware Accelerator)
                               [ OPTIONAL DEEP LEARNING ]
                           PyTorch Geometric GraphSAGE Plugin
                           (Degrades to classical ML if missing)
```

### Fallback Guarantee:
If PyTorch Geometric or CUDA is unavailable on the student evaluation machine, the system defaults to the **Scikit-Learn Random Forest + Isolation Forest + Platt Calibration** pipeline with zero operational disruption.

---

## 6. Laundering Motif Detection Engine

The Motif Engine executes deterministic, interpretable structural detectors across the transaction graph:

1. **Peeling Chains**:
   - **Signature**: $1 	ext{ input} 	o 2 	ext{ outputs}$, where smaller output $V_{peel} \le 0.05 \cdot V_{in}$ (peeled spending) and larger output $V_{change} \ge 0.80 \cdot V_{in}$ (change output).
   - **Chaining**: Follows the change output forward across $\ge 5$ sequential hops within a maximum inter-hop delay of 24 hours.
2. **CoinJoin / Mixing Motifs**:
   - **Signature**: $\ge 3$ distinct input wallets, $\ge 3$ distinct output wallets, total volume $\ge 0.05	ext{ BTC}$.
   - **Equal Output Constraint**: Sliding-window group of $\ge 2$ outputs with identical amounts within a $\pm 1\%$ relative tolerance ($|a - b| / \max(a, b) \le 0.01$).
3. **Advanced Mixer Signatures (Wu et al.)**:
   - $P2SH$ output ratio $\ge 5	imes$ non-$P2SH$ outputs.
   - Sweeper transactions (single input consolidation).
   - Temporal ordering: receive-then-send $a_1$ dominance over $a_2$ within $\delta = 3	ext{ hours}$.
4. **Rapid Multi-Hop Layering**:
   - Fast sequential hops with decreasing balance and hop transit times $< 10	ext{ minutes}$.
5. **Circular Flow Detection**:
   - Directed cycles in the fund graph ($u 	o v 	o w 	o u$) indicating wash trading or artificial volume inflation.
6. **Dormant Wallet Activation**:
   - Address with zero activity for $> 180	ext{ days}$ suddenly emitting high-volume transactions.

### Structured Motif Evidence Contract:
```json
{
  "motif_id": "MOTIF-PEEL-9821",
  "motif_type": "potential_peeling_chain",
  "nodes": ["1A1z...", "1Boat...", "1Q2TW..."],
  "edges": ["tx_001", "tx_002", "tx_003"],
  "start_time": "2026-03-03T20:10:00Z",
  "end_time": "2026-03-03T22:45:00Z",
  "total_amount_btc": 14.85,
  "hop_count": 6,
  "duration_seconds": 9300,
  "confidence": 92.5,
  "supporting_transactions": ["tx_001", "tx_002"]
}
```

---

## 7. Probabilistic Network Attribution

NEXUS-BTC explicitly enforces the investigative principle: **IP $
eq$ Wallet Owner**.

The Network Attribution Engine evaluates three association tiers:
1. **OBSERVED**: Direct packet capture observation of transaction broadcast from node IP within $\pm 2.0	ext{ seconds}$ of network propagation.
2. **INFERRED**: Repeated observation of identical IP/Port communicating transactions from the same Union-Find address cluster.
3. **PROBABILISTIC**: Geographically or temporally correlated relay activity weighted by transit latency:

$$P(	ext{IP} \mid 	ext{Tx}) = \sigma\left( w_1 \Delta t_{proximity} + w_2 N_{historical\_obs} + w_3 C_{asn\_stability} ight)$$

---

## 8. Calibrated Risk and Confidence Fusion

Risk and Confidence are strictly orthogonal metrics:
- **Risk Score ($0 - 100$)**: The calibrated likelihood that observed patterns reflect illicit or laundering operations.
- **Confidence Score ($0 - 100$)**: The statistical robustness, completeness, and mutual corroboration of the supporting evidence.

```
                  HIGH RISK (80-100)
                          ^
                          |  [PRIORITY ALERT]
        [INVESTIGATIVE    |  High Risk + High Confidence
         LEAD]            |  (Actionable forensic finding)
                          |
                          |  [DATA GAP]
                          |  High Risk + Low Confidence
                          |  (Needs additional telemetry)
                          +----------------------------> HIGH CONFIDENCE (80-100)
                          |  [BENIGN]
        [NORMAL NOISE]    |  Low Risk + High Confidence
                          |  (Verified regular merchant)
                          v
                   LOW RISK (0-20)
```

---

## 9. Explainable AI & Counterfactual Engine

### Feature-Level Explanations:
SHAP (SHapley Additive exPlanations) values computed on tree ensembles illustrate exact feature contributions:
```
Base Expected Value: 18.2
+ 32.4 [peel_ratio_extreme]
+ 21.8 [high_velocity_layering]
+ 14.5 [known_high_risk_neighbourhood]
-  5.2 [standard_fee_rate]
= Final Risk Score: 81.7
```

### Graph-Level Perturbation & Counterfactuals:
To explain graph predictions without brittle GNNExplainer dependencies, NEXUS-BTC uses a **Deterministic Subgraph Perturbation / Ablation Engine**:
1. Remove a specific structural feature or motif (e.g. peeling chain edges).
2. Re-evaluate risk through the calibrated ensemble.
3. Output the **Counterfactual Delta**:
   - *Original Risk:* 94
   - *Ablated Motif:* Peeling Chain removed
   - *New Risk:* 61 ($\Delta = -33$)
   - *Finding:* Peeling chain accounts for $35.1\%$ of the alert priority.

---

## 10. Value-Aware Best-First Fund Tracing Engine

NEXUS-BTC eliminates exponential breadth-first graph explosion by using a **Value-Aware Priority-Queue Tracer**:
- **Frontier Ranking**: Evaluates outgoing candidate UTXOs ordered by transferred BTC amount and temporal proximity.
- **Pruning**: Automatically terminates branches below a configurable minimum value threshold (default: $0.001	ext{ BTC}$ or $1\%$ of source volume).
- **Defensive Horizon Limits**: Configurable maximum hop depth (default: 10 hops) and maximum node capacity (default: 100 nodes).
- **Forensic Endpoint Classification**:
  - `unspent_utxo`: Money remains dormant at output address.
  - `known_service`: Funds reached an identifiable exchange or custodial service.
  - `mixer_detected`: Funds entered a CoinJoin or mixing pattern.
  - `cycle_detected`: Funds returned to an earlier address in the trail.
  - `horizon_reached`: Tracing reached maximum hop limit without terminating.

---

## 11. Offline-First Design & Local Asset Governance

The core platform runs completely air-gapped:
- **Local Storage**: Embedded SQLite 3 database with WAL mode enabled.
- **Local Machine Learning**: Bundled Scikit-Learn `.joblib` estimators.
- **Local GeoIP & Routing**: Local MaxMind GeoLite2 `.mmdb` files.
- **Local UI Assets**: Bundled React/Vite single-page application served directly from FastAPI's static file mount.
- **Zero Remote Dependencies**: No external RPC nodes, block explorers, or cloud services required.

---

## 12. Dashboard Architecture (12 Forensic Views)

The web dashboard is designed with a high-contrast dark forensic aesthetics (tactical navy/slate, cyber emerald, amber warning, crimson alert):

1. **Command Center**: Real-time throughput metrics, alert velocity, geographical risk map.
2. **Alert Queue**: Prioritized list of high-risk transactions with filter controls.
3. **Transaction Investigator**: Detailed breakdown of transaction inputs, outputs, and script types.
4. **Entity Investigator**: Wallet cluster profiles, historical balance, counterparties.
5. **Graph Forensics**: Interactive Cytoscape.js canvas showing transaction and address topologies.
6. **Fund Tracer**: Visual flow diagram of traced money paths with endpoint labels.
7. **AI Explanation Studio**: SHAP waterfall plots and counterfactual ablation sliders.
8. **Network Intelligence**: Source IP geolocation, ASN distribution, and timing correlation.
9. **Model Performance**: ROC-AUC, PR-AUC, calibration curves, and Brier score metrics.
10. **Synthetic Scenario Studio**: On-demand generation of laundering test scenarios.
11. **Investigation History**: Audit trail of analyst annotations, bookmarks, and exports.
12. **System Health**: Database latency, memory utilization, and pipeline throughput.

---

## 13. Synthetic Scenario Generator & Hidden Ground Truth

To support thorough offline evaluation without external network access, NEXUS-BTC bundles a local **Synthetic Scenario Generator**:
- Generates realistic transactions for 10 distinct scenario types:
  1. Normal consumer payment
  2. High-volume exchange hot-wallet
  3. Classic peeling chain (5-10 hops)
  4. Rapid fan-out dispersion
  5. Fan-in consolidation
  6. High-velocity multi-hop layering
  7. Multi-party CoinJoin mixing
  8. Dormant wallet reactivation
  9. Circular wash trading
  10. Benign high-activity false-positive stress test
- **Ground Truth Isolation**: Ground-truth labels are stored separately in an evaluation harness and are strictly inaccessible to the model inference engine during testing.

---

## 14. Evaluation Metrics & Academic Rigor

- **Classification Quality**: Precision, Recall, F1-Score, ROC-AUC, PR-AUC.
- **Calibration Quality**: Brier Score Loss ($B \le 0.08$), Reliability Diagrams.
- **Operational Efficiency**: Ingestion throughput ($> 500	ext{ tx/sec}$ on standard CPU), end-to-end trace latency ($< 150	ext{ms}$).
- **Temporal Split Validation**: Strict chronological splits (train on time steps $1-34$, validate on $35-40$, test on $41-49$) to prevent temporal lookahead leakage.
