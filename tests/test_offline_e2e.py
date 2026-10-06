"""End-to-end offline verification test suite."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.database import init_db
from app.ingestion.engine import IngestionEngine
from app.services.pipeline import ForensicPipeline
from app.schemas.trace import TraceRequest

client = TestClient(app)


def test_offline_complete_workflow():
    init_db()

    # 1. Health probe
    health = client.get("/api/health").json()
    assert health["status"] in ("HEALTHY", "DEGRADED")
    assert health["offline_mode"] is True

    # 2. Ingest Sample CSV
    sample_csv = root_dir / "data" / "sample" / "transactions_sample.csv"
    assert sample_csv.exists()

    engine = IngestionEngine()
    result = engine.ingest_file(sample_csv)
    assert result.records_read >= 5

    # 3. Run Forensic Pipeline
    pipeline = ForensicPipeline()
    summary = pipeline.run_full_pipeline()
    assert summary["status"] == "COMPLETED"
    assert summary["transactions_analyzed"] >= 5

    # 4. Verify Alert Queue
    alerts_res = client.get("/api/alerts").json()
    assert "alerts" in alerts_res
    assert alerts_res["total_alerts"] >= 1

    first_alert = alerts_res["alerts"][0]
    alert_id = first_alert["alert_id"]

    # 5. Verify Dossier & Explanations
    dossier = client.get(f"/api/alerts/{alert_id}").json()
    assert dossier["alert_id"] == alert_id
    assert "explanation" in dossier
    assert "evidence_chain" in dossier

    # 6. Verify Graph Endpoint
    graph = client.get("/api/graph?max_nodes=50").json()
    assert graph["node_count"] > 0
    assert graph["edge_count"] > 0

    # 7. Verify Fund Tracing
    trace_payload = {
        "start_type": "txid",
        "start_identifier": first_alert["txid"],
        "max_hops": 5,
        "max_nodes": 50,
        "min_value_ratio": 0.01,
    }
    trace_res = client.post("/api/trace", json=trace_payload).json()
    assert "ranked_paths" in trace_res

    # 8. Verify Model Metrics
    metrics_res = client.get("/api/model/metrics").json()
    assert "metrics" in metrics_res
    assert metrics_res["metrics"]["f1_score"] >= 0.0

    # 9. Verify Frontend Dashboard HTML served locally
    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "NEXUS-BTC" in root_resp.text
