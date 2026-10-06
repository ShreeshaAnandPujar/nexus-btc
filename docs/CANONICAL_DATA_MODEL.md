# Canonical Data Model: NEXUS-BTC

## 1. Specification Overview
The Canonical Data Model defines the unified internal representation for all blockchain transactions, network telemetry, and forensic metadata ingested into **NEXUS-BTC**. It is engineered to:
1. Ingest heterogenous input formats (**CSV**, **JSON**, and **XML**) with zero data loss.
2. Defensively sanitize malformed, truncated, or absent attributes without crashing.
3. Guarantee end-to-end provenance by tagging every record with source lineage and audit flags.
4. Support fast querying via embedded SQLite 3 and DuckDB storage engines.

---

## 2. Ingestion Format Bindings

### 2.1. CSV Ingestion Format
Expected header fields:
```csv
timestamp,src_ip,dst_ip,src_port,dst_port,txid,input_addresses,output_addresses,input_amounts,output_amounts,fee,script_type,country,asn
```
*Note: Array fields (`input_addresses`, `input_amounts`, etc.) are parsed from semicolon-delimited (`addr1;addr2`) or pipe-delimited (`addr1|addr2`) strings, as well as bracketed JSON array strings (`["addr1","addr2"]`).*

### 2.2. JSON Ingestion Format
Hierarchical or array-of-objects structure:
```json
[
  {
    "timestamp": "2026-03-03T23:20:51Z",
    "src_ip": "198.51.100.23",
    "dst_ip": "203.0.113.88",
    "src_port": 8333,
    "dst_port": 54122,
    "txid": "7b8f9a2b4c6e8d1a3f5c7b9e1a3d5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e",
    "input_addresses": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"],
    "output_addresses": ["1BoatSLRHtKNngkdXEeobR76b53LETtpyT", "1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3"],
    "input_amounts": [1.25000000],
    "output_amounts": [0.05000000, 1.19985000],
    "fee": 0.00015000,
    "script_type": "P2PKH",
    "country": "US",
    "asn": 13335
  }
]
```

### 2.3. XML Ingestion Format
XML payload structure:
```xml
<transactions>
  <transaction>
    <timestamp>2026-03-03T23:20:51Z</timestamp>
    <src_ip>198.51.100.23</src_ip>
    <dst_ip>203.0.113.88</dst_ip>
    <src_port>8333</src_port>
    <dst_port>54122</dst_port>
    <txid>7b8f9a2b4c6e8d1a3f5c7b9e1a3d5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e</txid>
    <inputs>
      <input address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" amount="1.25000000"/>
    </inputs>
    <outputs>
      <output address="1BoatSLRHtKNngkdXEeobR76b53LETtpyT" amount="0.05000000"/>
      <output address="1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3" amount="1.19985000"/>
    </outputs>
    <fee>0.00015000</fee>
    <script_type>P2PKH</script_type>
    <country>US</country>
    <asn>13335</asn>
  </transaction>
</transactions>
```

---

## 3. Canonical Field Definitions & Data Dictionary

| Field Name | Type | Nullable | Validation Rules & Defaults | Description |
|---|---|---|---|---|
| `record_id` | UUIDv4 (str) | No | Auto-generated on ingest (`uuid.uuid4()`) | Unique system audit identifier |
| `source_file` | String | No | Ingest file name / path | Originating data source path |
| `source_row` | Integer | No | 1-indexed row number | Location within source file |
| `ingestion_timestamp` | ISO-8601 (str) | No | Auto-generated UTC timestamp | System ingest audit clock |
| `validation_status` | Enum | No | `VALID`, `WARNING`, `REPAIRED`, `INVALID` | Validation assessment |
| `data_quality_flags` | List[String] | No | Array of triggered anomaly flags | Specific quality warnings |
| `timestamp` | ISO-8601 (str) | No | Validated datetime; fallback to `ingestion_timestamp` | Block or observed packet timestamp |
| `src_ip` | IPv4/IPv6 (str) | Yes | Validated IP format; fallback to `0.0.0.0` or null | Originating node IP address |
| `dst_ip` | IPv4/IPv6 (str) | Yes | Validated IP format; fallback to `0.0.0.0` or null | Destination node IP address |
| `src_port` | Integer | Yes | Range `0 - 65535`; default `8333` | Originating transport port |
| `dst_port` | Integer | Yes | Range `0 - 65535`; default `8333` | Destination transport port |
| `txid` | Hex String (64) | No | `^[0-9a-fA-F]{64}$`; repaired or synthetic if missing | Bitcoin 32-byte transaction hash |
| `input_addresses` | List[String] | No | Array of Base58/Bech32 strings; `[]` if Coinbase | Source UTXO wallet addresses |
| `output_addresses`| List[String] | No | Array of Base58/Bech32 strings; min length 1 | Destination UTXO wallet addresses |
| `input_amounts` | List[Decimal] | No | Array of non-negative BTC amounts; `8` decimals | Satoshis or BTC values per input |
| `output_amounts`| List[Decimal] | No | Array of non-negative BTC amounts; `8` decimals | Satoshis or BTC values per output |
| `fee` | Decimal | Yes | Non-negative BTC amount; computed if absent | Miner fee (`sum(inputs) - sum(outputs)`) |
| `script_type` | Enum (String) | Yes | `P2PK`, `P2PKH`, `P2SH`, `P2WPKH`, `P2TR`, `UNKNOWN` | Output script bytecode category |
| `country` | String (ISO-2) | Yes | Uppercase 2-letter country code; default `XX` / `UNKNOWN` | Geolocation resolved from IP |
| `asn` | Integer | Yes | Positive integer Autonomous System Number; default `0` | BGP Autonomous System Number |

---

## 4. Defensive Ingestion & Fault-Tolerance Policy

To ensure the application never crashes during live demonstrations or stress evaluations, the ingest pipeline implements the following **Defensive Handling Rules**:

```
+------------------------------------+---------------------------------------------------------------+
| Failure Condition                  | Defensive Ingestion Handling                                  |
+------------------------------------+---------------------------------------------------------------+
| Missing Country / GeoIP failure    | Set country to "UNKNOWN", flag FLAG_GEO_MISSING               |
| Missing ASN / Route failure        | Set asn to 0, flag FLAG_ASN_MISSING                           |
| Null or Empty Addresses            | Replace with "UNKNOWN_COINBASE" or "UNKNOWN_OP_RETURN"        |
| Empty Arrays in Inputs/Outputs     | Allow empty inputs (Coinbase tx); flag if outputs are empty   |
| Malformed Amount (string, negative)| Clamp negative to 0.0, coerce string, flag FLAG_AMOUNT_CORRUPT|
| Malformed / Missing Timestamp      | Default to current UTC time, flag FLAG_TIMESTAMP_SYNTHETIC    |
| Duplicate TXID within Batch        | Preserve first, merge telemetry, flag FLAG_DUPLICATE_TXID     |
| Invalid IP Address                 | Set to "0.0.0.0", flag FLAG_IP_MALFORMED                      |
| Unknown Script Type                | Set script_type to "UNKNOWN", flag FLAG_SCRIPT_UNKNOWN        |
+------------------------------------+---------------------------------------------------------------+
```

---

## 5. Storage Schema (SQLite DDL & DuckDB Schema)

```sql
-- SQLite 3 Canonical Storage Schema (WAL Mode Enabled)
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS transactions (
    record_id TEXT PRIMARY KEY,
    source_file TEXT NOT NULL,
    source_row INTEGER NOT NULL,
    ingestion_timestamp TEXT NOT NULL,
    validation_status TEXT NOT NULL,
    data_quality_flags TEXT NOT NULL, -- JSON array of strings
    
    timestamp TEXT NOT NULL,
    src_ip TEXT,
    dst_ip TEXT,
    src_port INTEGER,
    dst_port INTEGER,
    txid TEXT UNIQUE NOT NULL,
    
    input_addresses TEXT NOT NULL,  -- JSON array of strings
    output_addresses TEXT NOT NULL, -- JSON array of strings
    input_amounts TEXT NOT NULL,    -- JSON array of floats/decimals
    output_amounts TEXT NOT NULL,   -- JSON array of floats/decimals
    
    total_input_btc REAL NOT NULL DEFAULT 0.0,
    total_output_btc REAL NOT NULL DEFAULT 0.0,
    fee REAL NOT NULL DEFAULT 0.0,
    script_type TEXT DEFAULT 'UNKNOWN',
    country TEXT DEFAULT 'UNKNOWN',
    asn INTEGER DEFAULT 0,
    
    -- Forensic & Graph Cluster Annotations
    cluster_id TEXT,
    is_mixing BOOLEAN DEFAULT 0,
    risk_score REAL DEFAULT 0.0,
    confidence_score REAL DEFAULT 0.0,
    alert_level TEXT DEFAULT 'NORMAL'
);

-- Indices for Low-Latency Querying & Forensics
CREATE INDEX IF NOT EXISTS idx_tx_txid ON transactions(txid);
CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_tx_src_ip ON transactions(src_ip);
CREATE INDEX IF NOT EXISTS idx_tx_risk_score ON transactions(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_tx_cluster_id ON transactions(cluster_id);
CREATE INDEX IF NOT EXISTS idx_tx_alert_level ON transactions(alert_level);

-- Forensic Graph Edge Cache Table
CREATE TABLE IF NOT EXISTS graph_edges (
    edge_id TEXT PRIMARY KEY,
    txid TEXT NOT NULL,
    source_address TEXT NOT NULL,
    target_address TEXT NOT NULL,
    amount_btc REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(txid) REFERENCES transactions(txid) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_edge_source ON graph_edges(source_address);
CREATE INDEX IF NOT EXISTS idx_edge_target ON graph_edges(target_address);
```
