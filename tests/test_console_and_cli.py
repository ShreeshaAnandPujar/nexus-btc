"""Unit and regression tests for NEXUS-BTC console and CLI tools."""

import pytest
from pathlib import Path
from nexus.console import NexusMSFConsole, get_system_stats, NexusZphisherMenu
from app.core.database import SessionLocal
from app.models.transaction import TransactionModel


def test_console_system_stats():
    """Verify console system stats retrieval."""
    stats = get_system_stats()
    assert "tx_count" in stats
    assert "alert_count" in stats
    assert "entity_count" in stats
    assert stats["motifs_count"] == 9
    assert stats["models_count"] == 4
    assert stats["scenarios_count"] == 12


def test_msf_console_commands():
    """Verify MSF-style console commands execute without unhandled exceptions."""
    c = NexusMSFConsole()
    assert "tracing/best_first" in c.modules
    assert "scenarios/adversarial" in c.modules

    # Test show commands
    c.do_show("options")
    c.do_show("modules")
    c.do_show("motifs")
    c.do_show("scenarios")
    c.do_show("models")
    c.do_show("alerts")
    c.do_show("entities")
    c.do_show("transactions")
    c.do_status("")


def test_msf_module_lifecycle():
    """Verify selecting module, setting options, and running."""
    c = NexusMSFConsole()
    c.do_use("tracing/best_first")
    assert c.active_module == "tracing/best_first"

    c.do_set("HOPS 5")
    assert c.module_options["HOPS"]["value"] == 5

    c.do_back("")
    assert c.active_module is None


def test_ingest_sample_api_endpoint():
    """Verify POST /api/ingest/sample returns 200 and processes records."""
    from starlette.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.post("/api/ingest/sample?file_type=csv&run_pipeline=false")
    assert response.status_code == 200
    data = response.json()
    assert "ingestion_id" in data
    assert data["status"] == "COMPLETED"
    assert data["records_read"] > 0

