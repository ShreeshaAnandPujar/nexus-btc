# Repository Audit: ElliptiGraph

## 1. Executive Summary & Purpose
- **Repository Name**: ElliptiGraph
- **Source**: `https://github.com/0xnomy/ElliptiGraph.git`
- **Author**: 0xnomy
- **Stated Purpose**: Bitcoin transaction network analysis pipeline utilizing ArangoDB for graph storage and Plotly/Dash for interactive exploratory dashboards on the Elliptic dataset.
- **Scope & Role in NEXUS-BTC**: Serves as a technical reference for exploratory data analysis (EDA) profiling and multi-hop graph query patterns. Not suitable for direct adoption due to hard dependencies on an ArangoDB database daemon and Dash monolithic rendering.

---

## 2. Technical Profile & Inventory (24-Dimension Analysis)

| # | Dimension | Assessment |
|---|-----------|------------|
| 1 | **Language** | Python 3.9+ |
| 2 | **Framework** | Dash, Dash Bootstrap Components (`dbc`), Plotly, `pyArango` |
| 3 | **Backend Architecture** | Integrated Dash web application serving server-rendered Plotly views (`visualization/dash_app.py`) |
| 4 | **Frontend Architecture** | Plotly / Dash UI components with reactive Python callbacks |
| 5 | **Database / Storage** | ArangoDB (Multi-model graph database) managed via `pyArango` |
| 6 | **Data Schema** | Document collections: `transactions`, `features`; Edge collections: `transaction_edges` |
| 7 | **ML Models** | None. Pure graph visualization and exploratory query engine |
| 8 | **Graph Algorithms** | ArangoDB AQL graph traversals (k-hop neighbor queries, ego-nets) |
| 9 | **Anomaly Detection** | Basic volume and degree threshold filtering |
| 10 | **Clustering Methods** | Relies on ArangoDB graph grouping |
| 11 | **Laundering Detection Logic** | None implemented |
| 12 | **Tracing Algorithms** | Two-hop neighbor extraction via AQL query |
| 13 | **Explainability** | None |
| 14 | **API Integrations** | None |
| 15 | **Network Dependencies** | Local/remote ArangoDB database connection |
| 16 | **Config / Environment** | Hardcoded credentials in `graph/arango_setup.py` (default `root:password` on `localhost:8529`) |
| 17 | **Docker Dependencies** | Requires an ArangoDB Docker container (`docker run -p 8529:8529 -e ARANGO_ROOT_PASSWORD=password arangodb`) |
| 18 | **OS Assumptions** | Cross-platform |
| 19 | **Runtime Version** | Python >= 3.8 |
| 20 | **Test Coverage** | 0% automated tests |
| 21 | **License** | **NONE** (No LICENSE file provided in repository) |
| 22 | **Code Quality** | Moderate: well-organized module folders, but tightly coupled to ArangoDB and monolithic Dash callbacks |
| 23 | **Reusable Components** | Data validation & preprocessing routines in `analysis/preprocessing.py`, statistical summary logic in `analysis/eda.py` |
| 24 | **Dangerous / Incompatible** | Hard dependency on external ArangoDB service; monolithic Dash architecture; absent license |

---

## 3. Component Deep Dive

### Strongest Components
1. **Preprocessing & EDA Profiling (`analysis/preprocessing.py`, `analysis/eda.py`)**:
   - Clean data loaders that handle raw Elliptic dataset merges, class mappings (1=Illicit, 2=Licit, 0=Unknown), and output statistical summaries.
2. **Multi-Hop Query Formulations (`graph/queries_complex.py`)**:
   - Useful conceptual templates for 2-hop neighbourhood expansion and ego-network isolation.

### Weakest Components
1. **Database Friction (ArangoDB)**:
   - Forcing students to install and run ArangoDB via Docker or daemon introduces high operational fragility during evaluation.
2. **Dash Monolith**:
   - Dash compiles Python callbacks into React components via web sockets, creating sluggish graph visualisations for large networks compared to client-side Cytoscape.js.
3. **No Forensics or AML Engines**:
   - Lacks peeling chain detection, CoinJoin heuristics, risk scoring, confidence calibration, and fund tracing.

---

## 4. Reusable vs. Incompatible Modules

### Reusable (Conceptually)
- Preprocessing and data profiling logic from `analysis/preprocessing.py`.
- Graph aggregation query structures for ego-networks.

### Incompatible / Excluded
- `graph/arango_setup.py`: Excluded because NEXUS-BTC uses an embedded zero-dependency SQLite / DuckDB + NetworkX architecture.
- `visualization/dash_app.py`: Excluded in favour of a responsive FastAPI + React/Vite Cytoscape.js frontend.

---

## 5. Dependencies & Version Constraints
- `pandas`, `numpy`, `pyArango`, `matplotlib`, `seaborn`, `plotly`, `dash`, `dash-bootstrap-components`, `scikit-learn`, `requests`, `networkx`

---

## 6. License & Provenance Analysis
- **License Status**: Absent (All Rights Reserved by default).
- **Resolution**: Use exclusively as **conceptual inspiration**. Reimplement any dataset loading or statistical routines independently.

---

## 7. Integration Risks & Mitigation
- **Risk 1: Database Startup Failure**: ArangoDB failure halts all functionality.
  - *Mitigation*: Abandon ArangoDB; use embedded SQLite/DuckDB and in-memory NetworkX with zero external daemons.
- **Risk 2: Performance Bottlenecks**: Python-side Dash graph rendering lags on > 500 nodes.
  - *Mitigation*: Use WebGL-accelerated Canvas / Cytoscape.js rendering in the browser.

---

## 8. Final Recommendation
**STATUS: CONCEPTUAL REFERENCE ONLY**
Do not import modules or deploy ArangoDB. Adapt the EDA statistical profiling concepts into NEXUS-BTC's data ingestion and scenario generation pipeline.
