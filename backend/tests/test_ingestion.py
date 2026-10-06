"""Unit tests for ingestion engine and loaders."""

import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.ingestion.engine import IngestionEngine
from app.ingestion.detector import detect_format


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_format_detector():
    assert detect_format(b"txid,ts,src_ip", "data.csv") == "csv"
    assert detect_format(b'[{"txid": "abc"}]', "data.json") == "json"
    assert detect_format(b'<transactions></transactions>', "data.xml") == "xml"
    assert detect_format(b'{"txid": "123"}') == "json"
    assert detect_format(b'<test></test>') == "xml"


def test_csv_ingestion(test_db, tmp_path):
    engine = IngestionEngine(db=test_db)
    engine.quarantine.quarantine_dir = tmp_path

    csv_data = """txid,ts,src_ip,dst_ip,src_port,dst_port,input_addresses,output_addresses,input_amounts,output_amounts,fee,script_type,country,asn
0000000000000000000000000000000000000000000000000000000000000001,2026-03-01T12:00:00Z,1.1.1.1,8.8.8.8,8333,8333,{addr1;addr2},{addr3},"{1.0, 2.0}",{2.99},0.01,P2PKH,US,13335
0000000000000000000000000000000000000000000000000000000000000002,2026-03-01T12:05:00Z,2.2.2.2,8.8.8.8,8333,8333,[addr4],[addr5],[5.0],[4.99],0.01,P2TR,DE,3320
"""
    result = engine.ingest_content(csv_data, "test.csv")
    assert result.records_read == 2
    assert result.records_valid == 2
    assert result.records_invalid == 0
    assert result.duplicates == 0


def test_json_ingestion(test_db, tmp_path):
    engine = IngestionEngine(db=test_db)
    engine.quarantine.quarantine_dir = tmp_path

    records = [
        {
            "txid": "1111111111111111111111111111111111111111111111111111111111111111",
            "ts": "2026-03-01T10:00:00Z",
            "src_ip": "192.168.1.1",
            "dst_ip": "10.0.0.1",
            "input_addresses": ["wallet_a"],
            "output_addresses": ["wallet_b", "wallet_c"],
            "input_amounts": [10.0],
            "output_amounts": [0.5, 9.49],
            "fee": 0.01,
            "script_type": "P2WPKH",
        }
    ]
    result = engine.ingest_content(json.dumps(records), "test.json")
    assert result.records_read == 1
    assert result.records_valid == 1


def test_xml_ingestion(test_db, tmp_path):
    engine = IngestionEngine(db=test_db)
    engine.quarantine.quarantine_dir = tmp_path

    xml_data = """<transactions>
      <transaction>
        <txid>2222222222222222222222222222222222222222222222222222222222222222</txid>
        <timestamp>2026-03-01T11:00:00Z</timestamp>
        <src_ip>10.0.0.2</src_ip>
        <dst_ip>10.0.0.3</dst_ip>
        <inputs>
          <input address="wallet_x" amount="4.0"/>
        </inputs>
        <outputs>
          <output address="wallet_y" amount="3.99"/>
        </outputs>
        <fee>0.01</fee>
        <script_type>P2SH</script_type>
      </transaction>
    </transactions>"""
    result = engine.ingest_content(xml_data, "test.xml")
    assert result.records_read == 1
    assert result.records_valid == 1


def test_deduplication(test_db, tmp_path):
    engine = IngestionEngine(db=test_db)
    engine.quarantine.quarantine_dir = tmp_path

    csv_data = """txid,ts,src_ip,dst_ip,src_port,dst_port,input_addresses,output_addresses,input_amounts,output_amounts,fee,script_type,country,asn
3333333333333333333333333333333333333333333333333333333333333333,2026-03-01T12:00:00Z,1.1.1.1,8.8.8.8,8333,8333,{addr1},{addr2},{1.0},{0.99},0.01,P2PKH,US,13335
3333333333333333333333333333333333333333333333333333333333333333,2026-03-01T12:00:00Z,1.1.1.1,8.8.8.8,8333,8333,{addr1},{addr2},{1.0},{0.99},0.01,P2PKH,US,13335
"""
    result = engine.ingest_content(csv_data, "test_dups.csv")
    assert result.records_read == 2
    assert result.records_valid == 1
    assert result.duplicates == 1


def test_malformed_quarantine(test_db, tmp_path):
    engine = IngestionEngine(db=test_db)
    engine.quarantine.quarantine_dir = tmp_path

    # Row with bad json
    bad_json = 'not a valid json at all'
    result = engine.ingest_content(bad_json, "corrupt.json", format_hint="json")
    assert result.records_invalid >= 1
    assert list(tmp_path.glob("quarantine_*.json"))
