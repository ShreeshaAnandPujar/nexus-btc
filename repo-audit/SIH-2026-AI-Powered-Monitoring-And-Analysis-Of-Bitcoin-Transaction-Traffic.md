# Repository Audit: SIH-2026-AI-Powered-Monitoring-And-Analysis-Of-Bitcoin-Transaction-Traffic (ChainTrace)

## 1. Executive Summary & Purpose
- **Repository Name**: SIH-2026-AI-Powered-Monitoring-And-Analysis-Of-Bitcoin-Transaction-Traffic (Internal Title: **ChainTrace**)
- **Source**: `https://github.com/official-imvoiid/SIH-2026-AI-Powered-Monitoring-And-Analysis-Of-Bitcoin-Transaction-Traffic.git`
- **Author**: Team-Unfilter / official-imvoiid (2026)
- **Stated Purpose**: AI-powered monitoring and analysis of Bitcoin transaction traffic for Smart India Hackathon 2026. Desktop application that ingests real blocks from public explorers, detects money laundering motifs (layering, peeling, fan-in/fan-out), clusters entities via Union-Find, and traces funds forward to identifiable endpoints.
- **Scope & Role in NEXUS-BTC**: Serves as a vital reference for:
  1. The **Union-Find co-spend entity clustering** algorithm (`src/core/unionfind.js`).
  2. The **Value-Aware Best-First Fund Tracing** paradigm (`src/analysis/trace.js`) over naive BFS.
  3. **Behavioral feature engineering** (velocity, fan-out, peeling) (`src/analysis/behavior.js`).
  4. **HDBSCAN clustering** over behavioral vectors in Python (`python/pipeline.py`).

---

## 2. Technical Profile & Inventory (24-Dimension Analysis)

| # | Dimension | Assessment |
|---|-----------|------------|
| 1 | **Language** | JavaScript (Node.js ES6, Electron) and Python 3 |
| 2 | **Framework** | Express.js, Electron (Desktop shell), Scikit-Learn, HDBSCAN |
| 3 | **Backend Architecture** | Node.js Express HTTP service (`src/server/app.js`) orchestrating data pipelines and shelling out to Python scripts |
| 4 | **Frontend Architecture** | Custom forensic console in Vanilla HTML5/CSS3/JS (`ui/index.html`, `ui/console.js`, `ui/plot.js`, `ui/app.css`) rendered inside Electron |
| 5 | **Database / Storage** | Ephemeral JSON files on disk; in-memory transaction window representation |
| 6 | **Data Schema** | Custom blockchain JSON schema: blocks, transactions (`txid`, `vin`, `vout`, `amount`, `script_type`, `block_height`, `timestamp`) |
| 7 | **ML Models** | HDBSCAN for density-based cohort clustering; Scikit-learn Random Forest / ensemble for risk propagation |
| 8 | **Graph Algorithms** | Union-Find with path compression & union-by-rank for address clustering; Best-First forward graph traversal |
| 9 | **Anomaly Detection** | HDBSCAN outlier probability scores + heuristic behavioral thresholds |
| 10 | **Clustering Methods** | Common Input Ownership Heuristic (co-spend) via Disjoint Set Union + HDBSCAN behavioral clustering |
| 11 | **Laundering Detection Logic** | High-velocity layering, peeling chains, fan-in / fast fan-out, rapid consolidation |
| 12 | **Tracing Algorithms** | **Value-Aware Best-First Tracing**: prioritises largest outgoing UTXOs; classifies stop reasons (`unspent_utxo`, `exchange_deposit`, `mixer`, `cycle`, `max_hops`) |
| 13 | **Explainability** | Human-readable stop-reason labels and behavioral indicator flags |
| 14 | **API Integrations** | Blockstream Esplora API and Mempool.space API (`src/chain/sources.js`, `src/chain/providers.js`) |
| 15 | **Network Dependencies** | Runtime dependency on external block explorers to download blocks; lacks bundled offline datasets |
| 16 | **Config / Environment** | CLI parameters (`node scripts/ingest.js --days 2`) |
| 17 | **Docker Dependencies** | None |
| 18 | **OS Assumptions** | Electron desktop packaging across Linux/macOS/Windows |
| 19 | **Runtime Version** | Node.js >= 18, Python >= 3.9 |
| 20 | **Test Coverage** | 0% automated tests |
| 21 | **License** | Marked as `"license": "MIT"` in `package.json`, but lacks a standalone LICENSE file or copyright notice |
| 22 | **Code Quality** | High architectural clarity and thoughtful documentation; modular JS classes (`UnionFind`, `TraceEngine`) |
| 23 | **Reusable Components** | Union-Find implementation logic; Best-first tracing algorithm; Behavioral feature calculations; HDBSCAN pipeline |
| 24 | **Dangerous / Incompatible** | Polyglot multi-process runtime (Node + Electron + Python) causes deployment friction; no network-layer telemetry (no IP, ASN); live network calls hang if offline |

---

## 3. Component Deep Dive

### Strongest Components
1. **Value-Aware Best-First Tracing Architecture (`src/analysis/trace.js`)**:
   - Explicitly rejects naive BFS (which causes exponential state explosion on Bitcoin fan-out transactions).
   - Ranks child paths by transferred value fraction and temporal recency, maintaining a prioritized frontier while pruning dust transactions.
2. **Deterministic Entity Resolution (`src/core/unionfind.js`)**:
   - Clean Disjoint Set Union implementation with both path compression and union-by-rank, achieving near (lpha(N))$ performance on multi-input clustering.
3. **Behavioral Feature Engine (`src/analysis/behavior.js`)**:
   - Computes interpretable operational indicators: fan-in ratio, fan-out ratio, transaction velocity (minutes between hops), and peeling delta.

### Weakest Components
1. **Fragmented Execution Stack**:
   - Orchestrates Node.js, Electron, Express, and Python sub-processes, resulting in multiple process failures and inter-process communication bugs.
2. **Hard Dependency on External Blockchain APIs**:
   - Ingest script (`scripts/ingest.js`) pulls live blocks from Blockstream and Mempool over the public Internet; it has no bundled offline dataset and freezes when air-gapped.
3. **No Network Telemetry**:
   - Ignores network-layer traffic (IPs, BGP ASNs, ports, geolocation), which is a key mandate of NTRO SIH 2026 Problem Statement 5.

---

## 4. Reusable vs. Incompatible Modules

### Reusable (Conceptually / Algorithmically Reimplemented)
- **Union-Find Clustering**: Reimplement in Python within NEXUS-BTC's `clustering/entity_resolution.py`.
- **Value-Aware Tracing Engine**: Port the best-first search algorithm and endpoint classification directly to Python in `forensics/fund_trace.py`.
- **Behavioral Indicators**: Reimplement velocity, fan-in/fan-out, and peeling formulas in NEXUS-BTC's feature engineering pipeline.

### Incompatible / Excluded
- Electron desktop wrapper (`electron/*`): Excluded in favour of a lightweight browser-based React/Vite dashboard served by FastAPI.
- Node.js Express server: Excluded to unify the backend under Python FastAPI.

---

## 5. Dependencies & Version Constraints
- Node.js: `express >= 4.22`, `electron >= 32.0`
- Python: `numpy >= 1.24`, `scikit-learn >= 1.3`, `joblib >= 1.3`, `hdbscan`

---

## 6. License & Provenance Analysis
- **License Status**: `"MIT"` declared in `package.json`, but no standalone LICENSE file exists.
- **Resolution**: Under Phase 2 rules, to avoid any ambiguity or copyright conflict, do not copy raw JavaScript files. Reimplement all core algorithms (Union-Find, Best-First Tracing, Behavioral metrics) natively in Python.

---

## 7. Integration Risks & Mitigation
- **Risk 1: Multi-Process IPC Crashes**: Node calling Python via child processes is fragile across differing operating systems.
  - *Mitigation*: Unify all data ingestion, graph clustering, tracing, and ML inference inside a single Python/FastAPI backend process.
- **Risk 2: Live Ingest Freezes**: External explorer rate-limiting blocks data loading.
  - *Mitigation*: Bundle offline JSON/CSV block scenarios locally inside NEXUS-BTC with zero external API calls needed.

---

## 8. Final Recommendation
**STATUS: ALGORITHMIC SPECIFICATION ONLY (REIMPLEMENT IN PYTHON)**
Incorporate the best-first tracing heuristics and Union-Find entity clustering directly into NEXUS-BTC's unified Python backend, consolidating away the fragmented Node/Electron stack.
