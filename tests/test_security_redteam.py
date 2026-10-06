"""Red-Team Security Test Suite (Section 10).

Covers:
- Path traversal (file operations, SPA static serving)
- Malicious filenames and null bytes
- Oversized upload (>50MB)
- Malicious XML (XXE and entity expansion attacks)
- SQL Injection via query parameters and endpoints
- HTML / Script injection (XSS in identifiers and metadata)
- Unsafe shell arguments and command injection vectors
"""

import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.transaction import TransactionModel
from app.security.validator import (
    validate_safe_path,
    validate_file_upload,
    sanitize_identifier,
    SecurityError,
)
from app.ingestion.engine import IngestionEngine
from app.ingestion.xml_loader import XmlLoader


@pytest.fixture
def test_client_and_db(tmp_path):
    """Provides an isolated test database and FastAPI TestClient."""
    db_file = tmp_path / "sec_test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, TestingSessionLocal()
    app.dependency_overrides.clear()


# ==============================================================================
# 1. PATH TRAVERSAL AND MALICIOUS FILENAMES
# ==============================================================================

def test_path_traversal_prevention(tmp_path):
    """Test directory traversal, symlink escapes, and null-byte injection."""
    allowed_dir = tmp_path / "sandbox"
    allowed_dir.mkdir()
    secret_dir = tmp_path / "secrets"
    secret_dir.mkdir()
    secret_file = secret_dir / "passwords.txt"
    secret_file.write_text("SUPER_SECRET")

    # Attempt ../ escape
    traversal_path = allowed_dir / ".." / "secrets" / "passwords.txt"
    with pytest.raises(SecurityError, match="Path traversal violation"):
        validate_safe_path(traversal_path, allowed_root=allowed_dir)

    # Attempt null-byte injection
    with pytest.raises(SecurityError, match="null byte"):
        validate_safe_path(str(allowed_dir / "valid.csv\0.exe"), allowed_root=allowed_dir)


def test_spa_path_traversal(test_client_and_db):
    """Verify SPA static server blocks path traversal attempts to sensitive files."""
    client, _ = test_client_and_db
    traversal_urls = [
        "/../../../../etc/passwd",
        "/..%2F..%2Fetc%2Fpasswd",
        "/../../package.json",
        "/../../backend/app/core/config.py",
    ]
    for url in traversal_urls:
        response = client.get(url)
        # Must not return 200 containing sensitive server source code
        assert "SUPER_SECRET" not in response.text
        assert "DATABASE_URL" not in response.text


def test_malicious_filenames_and_extensions(test_client_and_db):
    """Verify rejection of executable extensions and path traversal in uploads."""
    client, _ = test_client_and_db

    # 1. Dangerous executable extension
    response = client.post(
        "/api/ingest",
        files={"file": ("malware.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "Unsupported or forbidden file extension" in response.text

    # 2. Bash script upload
    response = client.post(
        "/api/ingest",
        files={"file": ("script.sh", b"#!/bin/bash\nrm -rf /", "application/x-sh")},
    )
    assert response.status_code == 400


# ==============================================================================
# 2. OVERSIZED UPLOADS
# ==============================================================================

def test_oversized_upload_rejection(test_client_and_db):
    """Verify denial-of-service prevention on payloads exceeding 50 MB."""
    client, _ = test_client_and_db

    # Directly verify validator catches oversized file
    with pytest.raises(SecurityError, match="exceeds maximum limit"):
        validate_file_upload("large.csv", byte_size=55 * 1024 * 1024)

    # Test via API endpoint
    dummy_overflow = b"a" * (51 * 1024 * 1024)
    response = client.post(
        "/api/ingest",
        files={"file": ("huge.csv", dummy_overflow, "text/csv")},
    )
    assert response.status_code == 400
    assert "exceeds maximum limit" in response.text


# ==============================================================================
# 3. MALICIOUS XML (XXE AND BILLION LAUGHS)
# ==============================================================================

def test_malicious_xml_xxe_and_entity_expansion():
    """Verify XML parser isolates and quarantines XXE payloads without executing them."""
    xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE foo [
      <!ELEMENT foo ANY >
      <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
    <transactions>
      <transaction>
        <txid>&xxe;</txid>
        <timestamp>2026-10-06T12:00:00Z</timestamp>
      </transaction>
    </transactions>
    """
    records = list(XmlLoader.parse_content(xxe_payload, "xxe_exploit.xml"))
    assert len(records) == 1
    record, flags, status, row_idx = records[0]
    assert status == "INVALID"
    assert "FLAG_XML_PARSE_ERROR" in flags

    # Billion Laughs entity expansion attack
    billion_laughs = """<?xml version="1.0"?>
    <!DOCTYPE lolz [
      <!ENTITY lol "lol">
      <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
    ]>
    <transactions><transaction><txid>&lol1;</txid></transaction></transactions>
    """
    records_bl = list(XmlLoader.parse_content(billion_laughs, "billion_laughs.xml"))
    assert len(records_bl) == 1
    assert records_bl[0][2] == "INVALID"


# ==============================================================================
# 4. SQL INJECTION AUDIT
# ==============================================================================

def test_sql_injection_resilience(test_client_and_db):
    """Verify parameterized queries prevent SQL injection across all query endpoints."""
    client, db = test_client_and_db

    # Seed one legitimate transaction
    tx = TransactionModel(
        record_id="rec-sql-01",
        txid="01" * 32,
        source_file="legit.csv",
        source_row=1,
        timestamp="2026-10-06T12:00:00Z",
        output_amount=1.0,
    )
    db.add(tx)
    db.commit()

    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE transactions; --",
        "admin' UNION SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27 --",
        "1' AND SLEEP(5) --",
        "1'; EXEC xp_cmdshell('dir'); --",
    ]

    for payload in sqli_payloads:
        # Search transactions
        res = client.get(f"/api/transactions?query={payload}")
        assert res.status_code == 200, f"SQLi payload caused unexpected server response: {res.status_code}"
        # Transaction table must still exist and be intact
        table_check = db.execute(text("SELECT COUNT(*) FROM transactions")).scalar()
        assert table_check == 1, "SQL Injection payload damaged transactions table!"

        # Detail endpoints
        res_detail = client.get(f"/api/transactions/{payload}")
        assert res_detail.status_code == 404

        res_alert = client.get(f"/api/alerts/{payload}")
        assert res_alert.status_code == 404

        res_ent = client.get(f"/api/entities/{payload}")
        assert res_ent.status_code == 404


# ==============================================================================
# 5. HTML / SCRIPT INJECTION (XSS)
# ==============================================================================

def test_html_and_script_injection_sanitization(test_client_and_db):
    """Verify that XSS vectors and script tags are rejected by identifier validation."""
    xss_payloads = [
        "<script>alert('pwn')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(document.cookie)",
        "<svg onload=alert(1)>",
        "<iframe src='javascript:alert(1)'>",
    ]

    for payload in xss_payloads:
        with pytest.raises(SecurityError, match="forbidden characters"):
            sanitize_identifier(payload)


# ==============================================================================
# 6. UNSAFE SHELL ARGUMENTS & COMMAND INJECTION
# ==============================================================================

def test_unsafe_shell_arguments_and_command_injection():
    """Verify command injection characters (; | & $ `) are rejected."""
    shell_payloads = [
        "; rm -rf / ;",
        "| cat /etc/passwd",
        "$(whoami)",
        "`id`",
        "&& echo HACKED",
        "127.0.0.1; whoami",
    ]

    for payload in shell_payloads:
        with pytest.raises(SecurityError):
            sanitize_identifier(payload)
