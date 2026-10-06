# NEXUS-BTC: Installation and Setup Guide

This guide describes how to install, build, and configure NEXUS-BTC in 100% offline air-gapped environments, as well as on developer workstations (Linux, macOS, Windows/WSL2).

---

## 1. System Requirements

- **Operating System:** Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+), macOS (Apple Silicon or Intel), or Windows (via WSL2).
- **Python:** Python 3.11, 3.12, 3.13, or 3.14.
- **Node.js:** Node 18+ and npm (only needed if building frontend from source; pre-built bundle is included in `frontend/dist`).
- **RAM:** Minimum 4 GB (8 GB recommended for processing graphs > 100,000 nodes).
- **Storage:** 500 MB for core application and models.
- **Network:** Zero internet connectivity required. Completely functional air-gapped.

---

## 2. 5-Minute Quickstart (Single-Command Setup)

If Python 3.11+ is already available on your machine:

```bash
# 1. Navigate to the project root
cd nexus-btc

# 2. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install backend dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. (Optional) Compile frontend if modifying UI code:
# cd frontend && npm install && npm run build && cd ..

# 5. Ingest sample forensic dataset and run analysis:
python -m nexus ingest data/sample/transactions_sample.csv

# 6. Launch the forensic command center:
python -m nexus serve --host 127.0.0.1 --port 8000
```

Open your browser to [http://127.0.0.1:8000](http://127.0.0.1:8000). The dashboard and all interactive views are now running locally.

---

## 3. Makefile Automation

For automated workflow operations, NEXUS-BTC provides a unified `Makefile`:

```bash
make install       # Sets up virtualenv and installs Python/npm packages
make build         # Builds production offline React single-page bundle
make test          # Executes all 28 unit, integration, and e2e tests
make test-offline  # Runs the full 10-step air-gapped verification script
make serve         # Launches local server at http://127.0.0.1:8000
make scenario      # Generates a synthetic laundering scenario
make clean         # Cleans caches and temporary databases
```

---

## 4. Docker Deployment (Air-Gapped Container)

To build and run in a Docker container with an isolated, non-routable internal bridge:

```bash
# Build the self-contained container
docker build -f docker/Dockerfile -t nexus-btc:latest .

# Run container with volume persistence
docker run -d \
  --name nexus-btc \
  -p 8000:8000 \
  -v nexus-data:/app/data \
  nexus-btc:latest
```

Or using Docker Compose:

```bash
cd docker
docker-compose up -d
```

---

## 5. Offline Geolocation Database (Optional)

To enable offline IP geolocation and ASN mapping:
1. Obtain `GeoLite2-City.mmdb` or `dbip-city-lite.mmdb` (free offline databases).
2. Place the file inside the `geo/` directory:
   ```bash
   cp GeoLite2-City.mmdb geo/GeoLite2-City.mmdb
   ```
3. Set environment variable `GEOIP_DB_PATH=geo/GeoLite2-City.mmdb` or let NEXUS-BTC auto-detect it.

If no MMDB file is present, NEXUS-BTC runs with **graceful degradation**, displaying `"Geo enrichment unavailable"` while retaining 100% of blockchain, clustering, graph, and ML capabilities.
