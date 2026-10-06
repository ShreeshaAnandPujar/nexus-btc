# Repository Audit: Cryptracer

## 1. Executive Summary & Purpose
- **Repository Name**: Cryptracer
- **Source**: `https://github.com/Cathe0n/Cryptracer.git`
- **Author**: Cathe0n (2025-2026)
- **Stated Purpose**: Bitcoin transaction forensics & money flow analysis dashboard. Provides automated transaction tracing, coin mixer detection, address clustering, and on-chain intelligence.
- **Scope & Role in NEXUS-BTC**: Serves as a primary reference for **forward fund tracing**, **mixer topological detection** (Wu et al. metrics), and **Cytoscape.js interactive graph styling**. However, it is licensed under **GPL-3.0**, meaning NO source code can be copied directly into NEXUS-BTC. All algorithms must be cleanly reimplemented.

---

## 2. Technical Profile & Inventory (24-Dimension Analysis)

| # | Dimension | Assessment |
|---|-----------|------------|
| 1 | **Language** | Go 1.24 (Backend) and Vanilla JavaScript ES6 (Frontend) |
| 2 | **Framework** | Gin Web Framework (`github.com/gin-gonic/gin`), Cytoscape.js |
| 3 | **Backend Architecture** | Modular Go HTTP REST service (`main.go` and `internal/*`) exposing endpoints for `/api/trace`, `/api/cluster`, `/api/mixer`, `/api/search` |
| 4 | **Frontend Architecture** | Static Vanilla HTML/CSS/JS in `public/` with deep Cytoscape.js integration (`public/graph.js`, 152 KB) |
| 5 | **Database / Storage** | Neo4j Graph Database (via `github.com/neo4j/neo4j-go-driver/v5`) |
| 6 | **Data Schema** | Graph nodes: `:Address`, `:Transaction`; Relationships: `:INPUT_OF`, `:OUTPUT_TO`, `:CO_SPENT_WITH`; Blockchair TSV schema |
| 7 | **ML Models** | None. Purely topological and heuristic algorithms |
| 8 | **Graph Algorithms** | Union-Find (Disjoint Set Union) for common-input co-spend clustering; Best-first forward graph traversal; Directed cycle detection |
| 9 | **Anomaly Detection** | Heuristic threshold detectors for suspicious flows and high-value movements |
| 10 | **Clustering Methods** | Common-input ownership heuristic (co-spend clustering) via Union-Find algorithm |
| 11 | **Laundering Detection Logic** | Rigorous mixer detection based on published research (Wu et al. §IV-A): P2SH output ratio $\ge 5	imes$, 1-in 2-out sweeper transactions, temporal ordering ($ receive-then-send vs $ within $\delta=3	ext{ h}$), cycle duration $< 3	ext{ h}$ |
| 12 | **Tracing Algorithms** | Value-aware forward transaction tracer with multi-factor stopping criteria (`utxo`, `high_risk`, `known_service`, `mixer_detected`, `cycle`, `max_hops`, `timeout`) |
| 13 | **Explainability** | Explicit stop-reason labels (`StopReasonLabel`) and indicator breakdowns for mixer scoring |
| 14 | **API Integrations** | Blockstream Esplora API (`blockstream.info/api`), Mempool.space API, Bitquery GraphQL API (`graphql.bitquery.io`), Chainabuse API |
| 15 | **Network Dependencies** | Heavy runtime dependency on external APIs in live mode; breaks in air-gapped environments without preloaded Neo4j |
| 16 | **Config / Environment** | `.env` file containing `BITQUERY_KEY`, `CHAINABUSE_KEY`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASS` |
| 17 | **Docker Dependencies** | None provided; expects host Neo4j instance running |
| 18 | **OS Assumptions** | Includes Windows PE resources (`rsrc.syso`, `app.manifest`), but Go code compiles cross-platform |
| 19 | **Runtime Version** | Go >= 1.24.0 |
| 20 | **Test Coverage** | 0% automated tests (no `*_test.go` files present) |
| 21 | **License** | **GPL-3.0 (GNU General Public License v3.0)** — Strong Copyleft |
| 22 | **Code Quality** | Backend Go code is high-quality, idiomatic, and robust. Frontend JS is monolithic and unmodularized |
| 23 | **Reusable Components** | Conceptual designs: Value-aware tracing state machine, stopping heuristics, Wu et al. mixer detection metrics, Cytoscape graph configuration |
| 24 | **Dangerous / Incompatible** | **GPL-3.0 copyleft forbids direct copying**; live external API keys hardcoded in `.env`; heavy Neo4j requirement |

---

## 3. Component Deep Dive

### Strongest Components
1. **Topological Mixer Detector (`internal/aggregator/Mixer.go`, `mixer_detection_advanced.go`)**:
   - Accurately implements academic forensic heuristics:
     -  / a_2$ temporal ordering (receive-then-send within 3 hours).
     - P2SH value dominance ( / Non-P2SH \ge 5.0$).
     - Sweeper transaction patterns (1 input, 2 outputs with high value concentration).
     - Cycle duration metrics.
2. **Best-First Forward Fund Tracer (`internal/tracer/tracer.go`)**:
   - Avoids naive breadth-first graph explosion by prioritising highest-value UTXO descendants.
   - Provides explicit semantic termination states: `utxo`, `known_service`, `mixer_detected`, `cycle`, `max_hops`.

### Weakest Components
1. **Monolithic Frontend**: `public/graph.js` is a 152 KB monolithic vanilla script with global state, tightly coupled DOM manipulation, and difficult maintainability.
2. **External API Fragility**: Heavy reliance on live public endpoints (Blockstream, Mempool, Bitquery) makes it incapable of functioning in an offline/air-gapped evaluation setting.
3. **Neo4j Overhead**: Requires a full Java/Neo4j database installation to query local TSVs.

---

## 4. Reusable vs. Incompatible Modules

### Reusable (Conceptually / Independently Reimplemented)
- **Forward Fund Tracing State Machine**: Reimplement the best-first search with stop reasons in Python/FastAPI.
- **Mixer Detection Heuristics**: Reimplement Wu et al. metrics in Python NetworkX.
- **Cytoscape Layout & Styling**: Reimplement graph layout styles, edge arrow scaling, and node colouring in the NEXUS-BTC React frontend.

### Incompatible / Excluded
- **All Go Source Files**: Must NOT be copied due to GPL-3.0 copyleft license.
- **All Precompiled Binaries**: `rsrc.syso`, `build.log`.
- `.env` API keys: Security risk; remove immediately.

---

## 5. Dependencies & Version Constraints
- Go 1.24+
- Neo4j Go Driver v5.28.4
- Gin Gonic v1.11.0

---

## 6. License & Provenance Analysis
- **License Status**: GNU General Public License v3.0 (GPL-3.0).
- **Attribution & Copyleft**: GPL-3.0 is a strong copyleft license. If any part of Cryptracer's code is copied or linked into a project, the entire derived project must be open-sourced under GPL-3.0.
- **Resolution**: Under Phase 2 rules, **DO NOT copy any implementation files from Cryptracer**. Use Cryptracer strictly as an **algorithmic and conceptual specification**. Independently implement the tracer and mixer detectors in Python within NEXUS-BTC.

---

## 7. Integration Risks & Mitigation
- **Risk 1: License Contamination**: Inadvertent copying of Go code into NEXUS-BTC.
  - *Mitigation*: Complete clean-room reimplementation in Python.
- **Risk 2: Offline Breakage**: Reliance on live Blockstream/Mempool APIs.
  - *Mitigation*: Core NEXUS-BTC tracing queries local SQLite/DuckDB transactions, with external APIs as strictly optional enrichment.

---

## 8. Final Recommendation
**STATUS: ALGORITHMIC SPECIFICATION ONLY (DO NOT COPY CODE)**
Adopt the tracing stopping criteria and the Wu et al. mixer detection heuristics by implementing them cleanly in Python within NEXUS-BTC's `forensics/` and `motifs/` modules.
