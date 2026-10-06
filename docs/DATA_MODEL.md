# NEXUS-BTC: Canonical Data Model Specification

NEXUS-BTC enforces a **single canonical schema** across all ingested data formats (CSV, JSON, XML). All raw inputs are normalized, deduplicated, and validated through Pydantic V2 before being persisted to the relational database (SQLite/DuckDB) and indexed into the NetworkX heterogeneous graph.

---

## 1. Canonical Transaction Schema (`CanonicalTransaction`)

Every Bitcoin transaction record conforms to the following schema:

| Field | Type | Description |
| :--- | :--- | :--- |
| `txid` | `str` (64 hex) | Bitcoin Transaction Hash (SHA-256d). |
| `timestamp` | `datetime` | UTC timestamp of block inclusion or network propagation. |
| `inputs` | `list[TxInput]` | Sequence of spent UTXOs (`prev_txid`, `output_index`, `address`, `amount_btc`). |
| `outputs` | `list[TxOutput]` | Sequence of created UTXOs (`output_index`, `address`, `amount_btc`, `script_type`). |
| `input_amount` | `float` | Aggregate input volume in BTC. |
| `output_amount`| `float` | Aggregate output volume in BTC. |
| `fee` | `float` | Miner fee in BTC (`input_amount - output_amount`). |
| `fee_rate_sat_vb`| `float` | Fee rate in satoshis per virtual byte. |
| `script_types` | `list[str]` | Detected script types (e.g., `p2pkh`, `p2wpkh`, `p2sh`, `p2tr`, `multisig`). |
| `source_ips` | `list[str]` | IP addresses from which transaction was initially broadcast. |
| `destination_ips`| `list[str]` | Peer relay IPs receiving transaction broadcast. |
| `source_ports` | `list[int]` | Network ports observed on broadcast. |
| `destination_ports`| `list[int]` | Destination peer ports (e.g., 8333 for mainnet). |
| `country` | `str` | ISO-3166 2-letter country code resolved from IP, or `UNKNOWN`. |
| `asn` | `str` | Autonomous System Number (e.g., `AS13335`), or `UNKNOWN`. |
| `provenance` | `ProvenanceMetadata` | Ingestion timestamp, source file, hash, and format version. |

---

## 2. Ingestion & Quarantine Mechanics

When raw transactions are ingested via `POST /api/ingest` or `python -m nexus ingest`:

1. **Format Auto-Detection:** Analyzes file signatures (magic bytes, XML tags, JSON curly brackets, or CSV delimiter headers).
2. **Safe Parsing:** Uses defused parsing to prevent XML External Entity (XXE) and billion laughs DoS attacks.
3. **Validation & Normalization:** Converts amounts from satoshis or floating BTC to canonical floating BTC, formats addresses, and parses ISO timestamps.
4. **Quarantine Isolation:** If a record contains invalid hexadecimal TXIDs, negative amounts, or malformed addresses, it is quarantined into `data/normalized/quarantine/<ingestion_id>_quarantined.json` with an explicit diagnostic reason. **The ingestion engine never crashes on corrupt rows.**
5. **Deduplication:** Repeated transactions matching existing `txid` records are filtered with duplicate count tracked.

---

## 3. Entity Data Model (`EntityModel`)

An entity represents an inferred behavioral cluster of wallet addresses:

| Field | Type | Description |
| :--- | :--- | :--- |
| `entity_id` | `str` | Unique cluster identifier (e.g., `ENT-A1B2C3D4`). |
| `member_wallets` | `list[str]` | All Bitcoin addresses clustered under this entity. |
| `cluster_confidence`| `float` | Heuristic confidence (0.0 to 1.0) based on clustering heuristics. |
| `cluster_evidence` | `list[str]` | Forensic rationale (e.g., `COMMON_INPUT_HEURISTIC`, `ADDRESS_REUSE`). |
| `risk_score` | `float` | Calibrated risk score (0 to 100). |
| `total_volume_btc`| `float` | Cumulative transaction volume across all member addresses. |
| `transaction_count`| `int` | Total transactions associated with member wallets. |

> **Forensic Constraint:** A cluster represents a *probable behavioral entity*, never a confirmed legal person.

---

## 4. Alert Data Model (`AlertModel`)

| Field | Type | Description |
| :--- | :--- | :--- |
| `alert_id` | `str` | Unique identifier (e.g., `ALT-7B92708A`). |
| `txid` | `str` | Transaction that triggered the alert. |
| `entity_id` | `str` | Inferred entity involved, if applicable. |
| `risk_score` | `float` (0–100) | Probability of illicit or high-risk activity. |
| `confidence_score`| `float` (0–100) | Measurement of evidence completeness and model agreement. |
| `severity` | `str` | `CRITICAL` (>=80), `HIGH` (>=60), `MEDIUM` (>=40), `LOW` (<40). |
| `primary_motif` | `str` | Dominant laundering topology (e.g., `PEELING_CHAIN`, `RAPID_LAYERING`). |
| `motifs` | `list[str]` | All laundering topologies detected in transaction subgraph. |
| `explanation` | `dict` | SHAP feature attributions and baseline expected values. |
| `counterfactual` | `list[dict]` | Feature sensitivity deltas ("what-if" risk deductions). |
| `evidence_chain` | `list[dict]` | Step-by-step forensic progression from network observation to motif. |
| `model_contributions`| `dict` | Disaggregated model scores (`isolation_forest`, `random_forest`, `temporal_burst`). |
