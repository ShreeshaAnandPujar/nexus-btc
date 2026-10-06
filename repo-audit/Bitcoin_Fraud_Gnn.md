# Repository Audit: Bitcoin_Fraud_Gnn

## 1. Executive Summary & Purpose
- **Repository Name**: Bitcoin_Fraud_Gnn
- **Source**: `https://github.com/LawanMercy/Bitcoin_Fraud_Gnn.git`
- **Author**: Opeyemi Mercy Lawan (2026)
- **Stated Purpose**: Detecting illicit Bitcoin transactions within the Elliptic benchmark dataset using Graph Neural Networks (GraphSAGE), temporal burst analysis, and graph-aware structural feature engineering.
- **Scope & Role in NEXUS-BTC**: Serves as a reference for topological feature engineering (degree ratios, approximate betweenness, PageRank, HITS) and neighbourhood contagion calculations, as well as an optional PyTorch Geometric GraphSAGE baseline.

---

## 2. Technical Profile & Inventory (24-Dimension Analysis)

| # | Dimension | Assessment |
|---|-----------|------------|
| 1 | **Language** | Python 3.9+ (Python scripts and Jupyter Notebooks) |
| 2 | **Framework** | PyTorch, PyG (`torch_geometric`), Scikit-Learn, NetworkX |
| 3 | **Backend Architecture** | None. Standalone data-science pipeline scripts (`src/`) and notebooks (`notebooks/`) |
| 4 | **Frontend Architecture** | None. Produces a static pre-rendered HTML report (`Bitcoin Network Risk Intelligence Dashboard.html`) with embedded visual plots |
| 5 | **Database / Storage** | Flat CSV files (`data/elliptic_txs_classes.csv`, `data/elliptic_txs_edgelist.csv`) |
| 6 | **Data Schema** | Elliptic benchmark schema: `txId` (int64), `time_step` (int 1-49), 165 normalised features (`f1`...`f165`), `class` (1=Illicit, 2=Licit, 0/unknown=Unlabeled) |
| 7 | **ML Models** | 3-layer `GraphSAGE` with batch normalisation (`BatchNorm1d`), dropout (0.3), residual skip connection, and class-weighted cross-entropy loss |
| 8 | **Graph Algorithms** | Directed graph construction via NetworkX (`DiGraph`), in/out-degree, approximate betweenness centrality (pivot sampling =500$), PageRank ($lpha=0.85$), HITS (hub & authority scores), Weakly Connected Components (WCC) |
| 9 | **Anomaly Detection** | Supervised node-classification on imbalanced classes; temporal burst analysis (569Xscore on hourly transaction volume per time-step) |
| 10 | **Clustering Methods** | None directly implemented |
| 11 | **Laundering Detection Logic** | Neighbourhood contagion heuristics: predecessor illicit ratio, neighbourhood illicit/licit/unknown ratios |
| 12 | **Tracing Algorithms** | None implemented (no forward or backward UTXO traversal) |
| 13 | **Explainability** | Static t-SNE visualisations and feature distribution plots; no runtime SHAP or GNNExplainer |
| 14 | **API Integrations** | None |
| 15 | **Network Dependencies** | None at runtime; relies on external dataset download (originally Kaggle) |
| 16 | **Config / Environment** | Hardcoded relative paths via `pathlib.Path(__file__).parent.parent / "data"` |
| 17 | **Docker Dependencies** | None |
| 18 | **OS Assumptions** | Cross-platform (POSIX / Windows compatible) |
| 19 | **Runtime Version** | Python >= 3.8 (recommended Python 3.10/3.11) |
| 20 | **Test Coverage** | 0% automated tests; verification is visual through notebook executions |
| 21 | **License** | **NONE** (No LICENSE file provided in repository) |
| 22 | **Code Quality** | Moderate to High in `src/` modules: clean typing, clear docstrings, modular `FeatureBuilder` and `Trainer` classes |
| 23 | **Reusable Components** | `src/features.py` feature extraction equations (topological and contagion metrics); `src/model.py` GraphSAGE architecture |
| 24 | **Dangerous / Incompatible** | Hard dependency on `torch_geometric` without fallback; missing network layer (IP, ASN, ports); complete lack of license |

---

## 3. Component Deep Dive

### Strongest Components
1. **Engineered Feature Extraction (`src/features.py`)**:
   - The `FeatureBuilder` cleanly computes structural graph metrics (betweenness sampling, PageRank, hub/authority) alongside neighbourhood contagion ratios (`pred_illicit_ratio`, `nb_illicit_ratio`).
   - Efficient handling of k-pivot approximation for betweenness prevents (V^3)$ bottlenecks on large graphs.
2. **GNN Architecture (`src/model.py`)**:
   - Clean 3-layer GraphSAGE with residual addition ( = 	ext{ReLU}(	ext{BN}(	ext{Conv}(x_2)) + x_2)$) and class-weighted loss calculation handles heavy class imbalance effectively.

### Weakest Components
1. **Zero System Architecture**: Consists solely of isolated notebooks and ad-hoc scripts; cannot serve an API or handle continuous ingestion.
2. **Brittle Deep Learning Toolchain**: Relies on `torch` and `torch_geometric`, which have notoriously brittle C++/CUDA binary wheel dependencies that frequently break during local student evaluation on non-standard machines.
3. **No Network-Layer Telemetry**: Contains zero logic for IP attribution, ASN routing, or transport layer ports, failing Problem Statement 5's network correlation requirement.

---

## 4. Reusable vs. Incompatible Modules

### Reusable (Conceptually / Algorithmically)
- **Topological & Contagion Feature Formulas**: The mathematical formulas for degree ratio, PageRank, HITS scores, and neighbourhood contagion ratios in `src/features.py` can be reimplemented in pure Python/NetworkX for the NEXUS-BTC feature engineering pipeline.
- **GraphSAGE Model Architecture**: The architecture specification can be used as an *optional accelerator* behind a safe fallback switch.

### Incompatible / Excluded
- `notebooks/*`: Ephemeral interactive artifacts, not suited for a production application.
- `Bitcoin Network Risk Intelligence Dashboard.html`: Monolithic, non-interactive static report; unusable as a real-time forensics dashboard.
- Direct copy of any source code due to missing license.

---

## 5. Dependencies & Version Constraints
- `numpy >= 1.24`, `pandas >= 1.5`, `networkx >= 3.0`, `scikit-learn >= 1.2`, `scipy >= 1.10`
- Optional: `torch >= 2.0`, `torch_geometric >= 2.3`

---

## 6. License & Provenance Analysis
- **License Status**: Absent (No LICENSE file in the root or subdirectories).
- **Provenance**: Authored by Opeyemi Mercy Lawan (2026).
- **Legal Assessment**: Under standard copyright law, absent licenses default to "All Rights Reserved". Code cannot be copied directly.
- **Resolution**: Use exclusively as a **conceptual reference**. Implement all feature extraction algorithms, graph metrics, and model definitions independently in NEXUS-BTC.

---

## 7. Integration Risks & Mitigation
- **Risk 1: GNN Installation Failure**: If `torch_geometric` fails to compile or install on a host machine, the entire system might freeze or crash.
  - *Mitigation*: NEXUS-BTC must enforce a strict two-tier architecture: Classical ML (Scikit-Learn Random Forest + Isolation Forest) as the guaranteed core, with GraphSAGE as an optional toggleable plugin.
- **Risk 2: Memory Overflow on Large NetworkX Graphs**: Full betweenness centrality computation is (V \cdot E)$.
  - *Mitigation*: Enforce k-pivot sampling ( \le 200$) or defer betweenness computation to on-demand subgraph exploration.

---

## 8. Final Recommendation
**STATUS: CONCEPTUAL REFERENCE ONLY**
Do not copy source files directly. Reimplement the structural graph feature metrics (PageRank, degree ratios, contagion ratios) inside NEXUS-BTC's feature engineering pipeline using Scikit-Learn and NetworkX.
