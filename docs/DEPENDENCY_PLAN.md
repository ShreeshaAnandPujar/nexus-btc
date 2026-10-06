# Dependency Plan & Hardware Execution Blueprint: NEXUS-BTC

## 1. Zero-Friction Dependency Philosophy
The NEXUS-BTC dependency architecture is engineered around the **Student Demonstration Guarantee**:
- The application must install cleanly via a single `pip install -r requirements.txt` and `npm install`.
- It must run smoothly on standard student laptops (Intel i5/Ryzen 5, 8GB RAM, integrated graphics, no CUDA).
- It must operate entirely without Docker containers, background daemon services, or network calls.

---

## 2. Core Python Runtime Dependencies

```ini
# NEXUS-BTC Backend Dependencies (pyproject.toml / requirements.txt)

# Web & API Framework
fastapi>=0.110.0,<0.115.0       # High-performance async ASGI web framework
uvicorn[standard]>=0.28.0       # Production ASGI web server
pydantic>=2.6.0,<3.0.0          # Strict schema validation & type enforcement
pydantic-settings>=2.2.0        # Environment configuration management

# Storage & Embedded Database
sqlalchemy>=2.0.28              # Modern Python SQL toolkit & ORM
# sqlite3 is part of Python Standard Library (Primary storage engine)
duckdb>=0.10.0                  # Fast analytical OLAP database for large forensic queries

# Graph Analytics & Network Topologies
networkx>=3.2.1                 # Directed graph algorithms (centrality, paths, ego-nets)
scipy>=1.12.0                   # Sparse matrix calculations & statistical distance

# Machine Learning & AI
numpy>=1.26.0,<2.0.0            # Core array manipulation
pandas>=2.2.0                   # Dataframe operations and time-series grouping
scikit-learn>=1.4.0             # Random Forest, Isolation Forest, LOF, Platt calibration
joblib>=1.3.2                   # Model persistence & multi-threaded CPU parallelization
shap>=0.45.0                    # TreeExplainer for feature attribution waterfalls

# Network Telemetry & Offline Geolocation
maxminddb>=2.6.0                # Fast C/Python reader for local MaxMind GeoLite2 databases

# Testing & Quality Assurance
pytest>=8.0.0                   # Unit & integration testing harness
pytest-asyncio>=0.23.0          # Async test fixtures for FastAPI
httpx>=0.27.0                   # Async test client for API integration tests
```

### Optional Deep Learning Accelerator (Plugin Tier):
```ini
# Optional GNN Accelerator - Activated ONLY if hardware & wheels support it
# torch>=2.2.0
# torch-geometric>=2.5.0
```
*Note: If torch/PyG is absent or fails to import, NEXUS-BTC gracefully defaults to the Scikit-Learn Random Forest + Isolation Forest pipeline without throwing exceptions.*

---

## 3. Frontend Runtime Dependencies

```json
{
  "name": "nexus-btc-ui",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.363.0",
    "cytoscape": "^3.28.1",
    "cytoscape-cola": "^2.5.1",
    "cytoscape-dagre": "^2.5.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.2"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@types/cytoscape": "^3.19.16",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.4.3",
    "vite": "^5.2.0"
  }
}
```

---

## 4. Hardware Sizing & Performance Targets

| Metric | Target Specification | Minimum Supported Hardware |
|---|---|---|
| **CPU Architecture** | x86_64 or Apple Silicon (ARM64) | 2 Cores (Intel Core i3 / Celeron) |
| **RAM Utilization** | Baseline: ~250 MB; Under 10k Ingest: ~600 MB | 4 GB Total System RAM |
| **Storage Footprint** | App Code: ~35 MB; Preloaded Models & GeoIP: ~95 MB | 500 MB Available Disk Space |
| **Ingestion Throughput** | > 750 transactions / second | Single thread standard CPU |
| **Inference Latency** | < 25 ms per transaction | Scikit-Learn CPU inference |
| **Graph Query Latency** | < 50 ms for 5-hop ego-network | NetworkX in-memory representation |
