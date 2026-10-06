# NEXUS-BTC: 5th-Semester VTU Mini-Project / Evaluator Demo Script

This document provides a step-by-step walkthrough script for evaluators, professors, and engineering students demonstrating NEXUS-BTC locally in under 10 minutes.

---

## Prerequisites
- Terminal open to `nexus-btc` root.
- Python virtual environment activated: `source .venv/bin/activate`.
- Zero internet access required.

---

## 13-Step Forensic Demonstration Walkthrough

### Step 1: Launch the Surveillance Platform
```bash
python -m nexus serve --host 127.0.0.1 --port 8000
```
Open your browser to [http://127.0.0.1:8000](http://127.0.0.1:8000). Note the tactical cyber-forensics dark-theme interface with zero external web fonts or CDN scripts.

### Step 2: Ingest Multi-Format Forensic Data
Open a second terminal window or use the Ingestion CLI:
```bash
python -m nexus ingest data/sample/transactions_sample.csv
```
Highlight:
- Automatic format detection (`CSV`).
- Validation against canonical Pydantic schemas.
- Non-crashing quarantine isolation for corrupt rows.

### Step 3: Run Master Forensic Pipeline
The pipeline runs automatically upon ingestion, or can be triggered manually:
```bash
python -m nexus pipeline
```
Point out the terminal summary showing transactions analyzed, entities clustered, and alerts generated.

### Step 4: Explore the Command Center (`/dashboard`)
Navigate to **Dashboard**:
- Review high-level surveillance metrics: Total Transactions, Clustered Wallets, Inferred Entities, and Alert Distribution.
- Observe high-risk cluster widgets and geographic origin breakdown.

### Step 5: Prioritized Alert Queue (`/alerts`)
Navigate to **Alerts**:
- View the ranked alert table sorted by `Risk Score` in descending order.
- Explain the visual severity badges: `CRITICAL` (red), `HIGH` (orange), `MEDIUM` (yellow), and `LOW` (green).

### Step 6: Orthogonal Risk & Confidence Scoring
Click on the top alert in the table:
- **Risk Score (e.g., 88.5 / 100):** Represents high illicit probability.
- **Confidence Score (e.g., 94.2 / 100):** Represents high data completeness and ensemble agreement.
- Explain why these two metrics are strictly orthogonal and why high risk with low confidence requires further data collection.

### Step 7: Inspect Graph Intelligence (`/graph`)
Click **"Open in Graph"** or navigate to `/graph`:
- Observe the interactive Cytoscape.js canvas showing heterogeneous nodes:
  - Yellow: Inferred Entities
  - Red: Transactions
  - Cyan: Wallets
  - Green: IP addresses
- Demonstrate interactivity: zoom, drag nodes, click a wallet to inspect degree and volume, and switch between layout algorithms (Force-Directed Cola, Circular, Grid).

### Step 8: Laundering Motif Detection
In the alert details panel, point out the **Primary Motif**:
- Example: `PEELING_CHAIN` or `RAPID_LAYERING`.
- Show how the algorithm detected 5 sequential hops stripping 0.1 BTC change outputs with 91% value preservation.

### Step 9: Network-Blockchain Temporal Correlation
Review the Network Correlation panel:
- Point out the source IP, destination peer, Autonomous System (`AS13335`), and country code.
- Highlight the forensic disclaimer: *"Probabilistic relay observation: IP indicates network broadcast endpoint, not legal identity of wallet owner."*

### Step 10: Multimodal SHAP & Counterfactual Explanations (`/explain`)
Navigate to **Explain**:
- **SHAP Waterfall:** Walk through the top positive feature contributors (e.g., `peeling_chain_hops +24.1`, `velocity +18.4`).
- **Counterfactual Sensitivity:** Highlight the "what-if" delta:
  > *"If rapid layering is ablated: Risk drops by 31.2 points to 61.2."*
  Explain how this proves the model's sensitivity is tied to behavioral mechanics rather than arbitrary bias.

### Step 11: Value-Aware Fund Tracing (`/trace`)
Navigate to **Fund Trace**:
- Enter the TXID or start wallet.
- Set `Max Hops: 5`, `Min Value Ratio: 0.01`.
- Click **"Execute Best-First Trace"**.
- View ranked money flow paths and notice the semantic endpoint tags (`DORMANT / UTXO`, `SERVICE`, or `MIXER_LIKE`).

### Step 12: Forensic Evidence Chain
Inspect the chronological evidence chain:
```
NETWORK OBSERVATION → TRANSACTION → INPUT WALLET → ENTITY → OUTPUT WALLET → MOTIF
```
Click each step to show that every relationship is mathematically justified (`observed`, `inferred`, or `probabilistic`).

### Step 13: Model Evaluation & Benchmarks (`/models`)
Navigate to **Models**:
- Review Precision (0.875), Recall (0.817), F1 Score (0.845), ROC-AUC (0.912), and the Confusion Matrix.
- Emphasize that NEXUS-BTC reports real measured metrics rather than fabricated 100% claims.
