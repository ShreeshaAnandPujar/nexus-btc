"""Red-Team QA Suite: Data Corruption & Resiliency Stress Tests.

Verifies that NEXUS-BTC gracefully ingests or quarantines malformed, corrupt,
and adversarial datasets without crashing the server or database.
"""

import json
import pytest
from pathlib import Path
from app.ingestion.engine import IngestionEngine
from app.ingestion.quarantine import QuarantineManager
from app.core.database import SessionLocal, init_db
from app.models.transaction import TransactionModel


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

@pytest.fixture
def isolated_db(tmp_path):
    db_file = tmp_path / "test_corruption.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_corrupt_json_missing_and_null_fields(isolated_db, tmp_path):
    """JSON with missing essential fields, nulls, and unexpected columns."""
    corrupt_data = [
        # Missing txid
        {"timestamp": "2026-03-01T12:00:00Z", "input_amount": 1.5, "output_amount": 1.4},
        # Null txid
        {"txid": None, "timestamp": "2026-03-01T12:00:00Z", "input_amount": 1.5, "output_amount": 1.4},
        # Negative amount
        {"txid": "aa" * 32, "timestamp": "2026-03-01T12:00:00Z", "input_amount": -5.0, "output_amount": -4.0},
        # Bad timestamp format
        {"txid": "bb" * 32, "timestamp": "INVALID-DATE-STRING", "input_amount": 1.0, "output_amount": 0.9},
        # Malformed arrays
        {"txid": "cc" * 32, "timestamp": "2026-03-01T12:00:00Z", "inputs": "NOT_A_LIST", "outputs": 123},
        # Valid row to confirm partial recovery
        {
            "txid": "11" * 32,
            "timestamp": "2026-03-01T12:00:00Z",
            "inputs": [{"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "amount_btc": 1.0}],
            "outputs": [{"address": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT", "amount_btc": 0.99}],
            "input_amount": 1.0,
            "output_amount": 0.99,
            "fee": 0.01,
            "unexpected_rogue_column": "ATTACK_PAYLOAD",
        },
    ]

    json_file = tmp_path / "corrupt_data.json"
    json_file.write_text(json.dumps(corrupt_data))

    engine = IngestionEngine(db=isolated_db)
    result = engine.ingest_file(json_file)

    assert result.status == "PARTIAL_SUCCESS" or result.status == "COMPLETED"
    assert result.records_read == 6
    assert result.records_valid == 1
    assert result.records_invalid == 5

    # Check quarantine directory
    quarantined = engine.quarantine.get_quarantined_records(result.ingestion_id)
    assert len(quarantined) == 5


def test_corrupt_csv_adversarial_values(isolated_db, tmp_path):
    """CSV with bad IPs, invalid ports, massive numbers, unknown scripts."""
    csv_content = """txid,timestamp,input_amount,output_amount,fee,inputs,outputs,source_ips,source_ports,script_types
3333333333333333333333333333333333333333333333333333333333333333,2026-03-01T12:00:00Z,1000000000.0,999999999.0,1.0,1AddrA:1000000000.0,1AddrB:999999999.0,999.999.999.999,999999,UNKNOWN_QUANTUM_SCRIPT
4444444444444444444444444444444444444444444444444444444444444444,2026-03-01T12:01:00Z,2.0,1.99,0.01,1InA:2.0,1OutB:1.99,192.168.1.1,8333,p2wpkh
INVALID_SHORT_HEX_TXID,2026-03-01T12:02:00Z,2.0,1.99,0.01,1InA:2.0,1OutB:1.99,10.0.0.1,8333,p2pkh
"""
    csv_file = tmp_path / "corrupt_data.csv"
    csv_file.write_text(csv_content)

    engine = IngestionEngine(db=isolated_db)
    result = engine.ingest_file(csv_file)

    assert result.records_read == 3
    # Row 1 and 2 are valid, Row 3 is quarantined
    assert result.records_invalid >= 1
    assert result.records_valid >= 1


def test_malformed_xml_and_syntax_error(isolated_db, tmp_path):
    """Unclosed XML tags or truncated XML should not crash the engine."""
    broken_xml = """<?xml version="1.0"?>
    <transactions>
        <transaction>
            <txid>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</txid>
            <timestamp>2026-03-01T12:00:00Z</timestamp>
            <!-- UNCLOSED TAGS BELOW -->
    """
    xml_file = tmp_path / "broken.xml"
    xml_file.write_text(broken_xml)

    engine = IngestionEngine(db=isolated_db)
    result = engine.ingest_file(xml_file)

    assert result.status == "FAILED" or result.records_invalid >= 0


def test_duplicate_transactions_filtering(isolated_db, tmp_path):
    """Submitting the identical transaction multiple times must not inflate the database."""
    tx = {
        "txid": "55" * 32,
        "timestamp": "2026-03-01T12:00:00Z",
        "inputs": [{"address": "1AddrDupIn", "amount_btc": 5.0}],
        "outputs": [{"address": "1AddrDupOut", "amount_btc": 4.99}],
        "input_amount": 5.0,
        "output_amount": 4.99,
        "fee": 0.01,
    }
    dup_file = tmp_path / "duplicates.json"
    dup_file.write_text(json.dumps([tx, tx, tx]))

    engine = IngestionEngine(db=isolated_db)
    result = engine.ingest_file(dup_file)

    assert result.records_read == 3
    assert result.records_valid == 1
    assert result.duplicates == 2


def test_malformed_json_syntax_and_empty_arrays(isolated_db, tmp_path):
    """Raw invalid JSON syntax and empty arrays must be handled gracefully without crashing."""
    # 1. Empty array
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("[]")
    engine = IngestionEngine(db=isolated_db)
    res_empty = engine.ingest_file(empty_file)
    assert res_empty.records_read == 0
    assert res_empty.records_valid == 0

    # 2. Syntax error in JSON (missing brackets/quotes)
    syntax_error_file = tmp_path / "syntax_error.json"
    syntax_error_file.write_text("{bad_json: missing_quotes, [unclosed")
    res_syntax = engine.ingest_file(syntax_error_file)
    assert res_syntax.records_read >= 1
    assert res_syntax.records_invalid >= 1

