# NEXUS-BTC: Air-Gapped Offline Deployment Specification

NEXUS-BTC is engineered from the ground up for high-security, classified, and air-gapped forensic environments where **no external network connections are permitted**.

---

## 1. Zero External Dependencies Architectural Audit

| Subsystem | Conventional Design | NEXUS-BTC Offline Implementation |
| :--- | :--- | :--- |
| **Frontend Assets** | External CDNs (unpkg, cdnjs, Google Fonts) | **100% self-contained bundle:** Compiled static assets (`index.html`, JavaScript, CSS) are stored locally in `frontend/dist` and served directly by FastAPI. Zero Google Fonts or external stylesheet imports. |
| **Graph Database** | Remote Neo4j server or AWS Neptune | **In-Process NetworkX MultiDiGraph:** Serialized in-memory with sub-second graph traversal and offline JSON export to Cytoscape.js. |
| **Relational Storage**| Cloud PostgreSQL or Snowflake | **Local Embedded SQLite / DuckDB:** Operating in Write-Ahead Logging (WAL) mode with zero external socket requirements. |
| **AI / Machine Learning**| OpenAI / Anthropic cloud APIs | **Local CPU/GPU Scikit-Learn / SHAP:** Fitted models saved as deterministic Joblib checkpoints in `models/` with zero cloud inference calls. |
| **IP Geolocation** | Remote REST API (e.g., ipinfo.io, ipapi.co) | **Local MMDB Reader:** Fast offline binary lookups against `geo/GeoLite2-City.mmdb` or `geo/dbip-city-lite.mmdb`. |

---

## 2. Air-Gap Deployment Procedure

### Step 1: Package Artifacts on an Internet-Connected Machine
On a build machine with internet access:
```bash
# Clone and build local dependencies
git clone <repo-url> nexus-btc
cd nexus-btc
make install
make build

# Package entire directory including virtual environment and dist
tar -czvf nexus-btc-airgap.tar.gz nexus-btc/
```

### Step 2: Transfer to Air-Gapped Linux Host
Transfer `nexus-btc-airgap.tar.gz` via approved physical optical media or secure hardware token to the isolated workstation.

### Step 3: Extract and Launch
```bash
tar -xzvf nexus-btc-airgap.tar.gz
cd nexus-btc

# Verify that host is completely air-gapped
bash scripts/offline_test.sh

# Start the offline surveillance platform
python -m nexus serve --host 127.0.0.1 --port 8000
```

---

## 3. Automated Air-Gap Verification (`scripts/offline_test.sh`)

To satisfy regulatory and security audit requirements, NEXUS-BTC provides `scripts/offline_test.sh`, which automatically:
1. Diverts outbound application traffic to an unroutable loopback sink (`http_proxy=http://127.0.0.1:0`).
2. Bootstraps the local backend and serves the embedded single-page application.
3. Audits the root HTML document to ensure zero CDN, Google Fonts, or remote asset URLs are present.
4. Performs an automated end-to-end ingestion, clustering, motif detection, risk scoring, fund trace, and explanation pass.
5. Returns exit code `0` only if all 10 non-negotiable verification criteria succeed.
