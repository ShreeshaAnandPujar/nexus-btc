"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db

init_db()
client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("HEALTHY", "DEGRADED")
    assert data["system"] == "NEXUS-BTC"
    assert data["offline_mode"] is True


def test_scenarios_catalog():
    resp = client.get("/api/scenarios/catalog")
    assert resp.status_code == 200
    catalog = resp.json()
    assert len(catalog) == 12
    types = [item["scenario_type"] for item in catalog]
    assert "PEELING_CHAIN" in types
    assert "MIXING_LIKE" in types
    assert "CIRCULAR_FLOW" in types


def test_scenario_generation():
    payload = {
        "scenario_type": "PEELING_CHAIN",
        "seed": 99,
        "transaction_count": 6,
        "base_volume_btc": 5.0,
    }
    resp = client.post("/api/scenarios/generate?auto_ingest=true", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_type"] == "PEELING_CHAIN"
    assert data["record_count"] >= 5


def test_alerts_endpoint():
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert "alerts" in data
    assert "critical_count" in data


def test_graph_endpoint():
    resp = client.get("/api/graph?max_nodes=50")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data


def test_fund_tracing_endpoint():
    payload = {
        "start_type": "wallet",
        "start_identifier": "1PeelOrigin_99",
        "direction": "forward",
        "max_hops": 5,
        "max_nodes": 50,
        "min_value_ratio": 0.01,
    }
    resp = client.post("/api/trace", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["target"] == "1PeelOrigin_99"
    assert "ranked_paths" in data


def test_model_metrics_endpoint():
    resp = client.get("/api/model/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "metrics" in data
    assert "precision" in data["metrics"]
    assert "recall" in data["metrics"]
    assert "f1_score" in data["metrics"]
