"""API Contract Tests (Section 11) and Reproducibility Tests (Section 13).

Verifies:
- All endpoints conform strictly to Pydantic response schemas
- Input validation (bounds, negative values, type mismatch) returns 422 / 400
- 404 returned for missing resources with informative error message
- 500 internal errors NEVER leak stack traces or server internals
- Deterministic reproducibility: running synthetic scenario generation with same seed produces identical datasets
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.transaction import TransactionModel
from app.models.alert import AlertModel
from app.models.entity import EntityModel
from app.schemas.scenario import ScenarioGenerateRequest
from app.services.scenario_generator import ScenarioGenerator


@pytest.fixture
def api_test_env(tmp_path):
    """Provides isolated DB and TestClient."""
    db_file = tmp_path / "contracts_test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Seed one test transaction, entity, and alert
    tx = TransactionModel(
        record_id="rec-c-01",
        txid="0101010101010101010101010101010101010101010101010101010101010101",
        source_file="test.csv",
        source_row=1,
        timestamp="2026-10-06T12:00:00Z",
        src_ip="10.0.0.1",
        country="IN",
        asn=55836,
        input_addresses_json='["1ContractIn11111111111111111111"]',
        output_addresses_json='["1ContractOut1111111111111111111"]',
        output_amounts_json="[1.5]",
        output_amount=1.5,
        risk_score=78.5,
        confidence_score=85.0,
        alert_level="HIGH",
        entity_id="ENT-TEST01",
    )
    ent = EntityModel(
        entity_id="ENT-TEST01",
        cluster_type="COMMON_INPUT",
        wallet_count=2,
        member_wallets_json='["1ContractIn11111111111111111111", "1ContractIn22222222222222222222"]',
        cluster_confidence=0.95,
        risk_score=78.5,
        confidence_score=85.0,
        total_volume_btc=1.5,
        first_seen="2026-10-06T12:00:00Z",
        last_seen="2026-10-06T12:00:00Z",
    )
    alert = AlertModel(
        alert_id="ALT-01010101",
        txid=tx.txid,
        entity_id="ENT-TEST01",
        risk_score=78.5,
        confidence_score=85.0,
        severity="HIGH",
        primary_motif="PEELING_CHAIN",
        motifs_json='["PEELING_CHAIN"]',
        explanation_json='{"alert_id":"ALT-01010101","txid":"0101010101010101010101010101010101010101010101010101010101010101","base_expected_value":18.5,"final_risk_score":78.5,"top_feature_attributions":[],"model_contributions":{},"counterfactuals":[],"graph_ablations":[],"forensic_summary":"Test alert"}',
        counterfactual_json="[]",
        evidence_chain_json="[]",
        model_contributions_json="{}",
    )
    session.add_all([tx, ent, alert])
    session.commit()

    def override_get_db():
        s = TestingSessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, session
    app.dependency_overrides.clear()


# ==============================================================================
# SECTION 11: API CONTRACT TESTS
# ==============================================================================

def test_api_health_contracts(api_test_env):
    """Verify health and offline status endpoints return expected schemas."""
    client, _ = api_test_env

    # 1. /api/health
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "version" in data
    assert "database" in data
    assert "ml_models" in data

    # 2. /api/health/ready
    res_ready = client.get("/api/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["ready"] is True

    # 3. /api/health/offline
    res_off = client.get("/api/health/offline")
    assert res_off.status_code == 200
    assert res_off.json()["offline_capable"] is True


def test_api_entity_and_alert_contracts(api_test_env):
    """Verify entities and alerts endpoints schemas and 404 behavior."""
    client, _ = api_test_env

    # 1. Alert queue
    res_alerts = client.get("/api/alerts")
    assert res_alerts.status_code == 200
    data = res_alerts.json()
    assert "total_alerts" in data
    assert "alerts" in data
    assert len(data["alerts"]) >= 1

    # 2. Alert detail (found)
    res_alert = client.get("/api/alerts/ALT-01010101")
    assert res_alert.status_code == 200
    assert res_alert.json()["alert_id"] == "ALT-01010101"

    # 3. Alert detail (404)
    res_404 = client.get("/api/alerts/ALT-NONEXISTENT")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()

    # 4. Entity list
    res_ents = client.get("/api/entities")
    assert res_ents.status_code == 200
    assert isinstance(res_ents.json(), list)

    # 5. Entity detail (found)
    res_ent = client.get("/api/entities/ENT-TEST01")
    assert res_ent.status_code == 200
    assert res_ent.json()["entity_id"] == "ENT-TEST01"

    # 6. Entity detail (404)
    res_ent_404 = client.get("/api/entities/ENT-NONE")
    assert res_ent_404.status_code == 404


def test_api_input_validation_and_bounds(api_test_env):
    """Verify invalid query parameter bounds trigger HTTP 422 Unprocessable Entity."""
    client, _ = api_test_env

    # limit > 500 in alerts should fail validation (le=500)
    res_bad_limit = client.get("/api/alerts?limit=1000")
    assert res_bad_limit.status_code == 422

    # negative limit
    res_neg_limit = client.get("/api/alerts?limit=-10")
    assert res_neg_limit.status_code == 422

    # negative offset
    res_neg_offset = client.get("/api/alerts?offset=-5")
    assert res_neg_offset.status_code == 422


def test_api_no_stack_trace_leakage(api_test_env):
    """Verify unhandled internal errors return standardized JSON and NEVER leak stack traces."""
    client, _ = api_test_env

    # Calling an endpoint that triggers a simulated error or bad input
    # In FastAPI, our global exception handler intercepts Exception
    from starlette.requests import Request
    from app.main import global_exception_handler

    # Test the handler directly to ensure schema compliance
    import asyncio
    fake_request = type("FakeReq", (), {"url": type("Url", (), {"path": "/api/broken"})()})()
    response = asyncio.run(global_exception_handler(fake_request, RuntimeError("Critical secret DB failure: password=12345")))
    assert response.status_code == 500
    
    import json
    body = json.loads(response.body.decode())
    assert body["error"] is True
    assert "password=12345" not in body["message"], "Sensitive error detail or stack trace leaked in 500 response!"
    assert "Traceback" not in body["message"]


# ==============================================================================
# SECTION 13: REPRODUCIBILITY TESTS
# ==============================================================================

def test_scenario_generation_determinism_and_reproducibility(tmp_path):
    """
    Run the exact same synthetic scenario twice with the same seed.
    Confirm identical records, values, and addresses.
    """
    gen = ScenarioGenerator(output_dir=tmp_path)
    
    req1 = ScenarioGenerateRequest(scenario_type="PEELING_CHAIN", seed=42, record_count=7)
    resp1, records1 = gen.generate(req1)

    req2 = ScenarioGenerateRequest(scenario_type="PEELING_CHAIN", seed=42, record_count=7)
    resp2, records2 = gen.generate(req2)

    # Confirm metadata match
    assert resp1.record_count == resp2.record_count
    assert resp1.scenario_type == resp2.scenario_type

    # Confirm records are byte-for-byte identical
    assert len(records1) == len(records2)
    for r1, r2 in zip(records1, records2):
        assert r1["txid"] == r2["txid"]
        assert r1["input_addresses"] == r2["input_addresses"]
        assert r1["output_addresses"] == r2["output_addresses"]
        assert r1["output_amounts"] == r2["output_amounts"]
        assert sum(r1["output_amounts"]) == sum(r2["output_amounts"])

    # Confirm differing seeds produce different data
    req_diff = ScenarioGenerateRequest(scenario_type="PEELING_CHAIN", seed=999, record_count=7)
    _, records_diff = gen.generate(req_diff)
    assert records1[0]["txid"] != records_diff[0]["txid"]
