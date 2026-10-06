"""Unit tests for forensic security constraints."""

import pytest
from pathlib import Path
from app.security import (
    validate_safe_path,
    validate_file_upload,
    sanitize_identifier,
    SecurityError,
)


def test_validate_safe_path(tmp_path):
    sub = tmp_path / "data" / "allowed"
    sub.mkdir(parents=True)
    valid_file = sub / "test.csv"
    valid_file.write_text("dummy")

    # Valid relative path inside root
    resolved = validate_safe_path(valid_file, allowed_root=tmp_path)
    assert resolved == valid_file.resolve()

    # Traversal escape outside root
    with pytest.raises(SecurityError, match="Path traversal violation"):
        validate_safe_path("/etc/passwd", allowed_root=tmp_path)


def test_validate_file_upload():
    # Valid file upload
    validate_file_upload("transactions.csv", byte_size=1024)

    # Invalid extension
    with pytest.raises(SecurityError, match="Unsupported or forbidden"):
        validate_file_upload("malware.exe", byte_size=1024)

    # Size exceeds limit
    with pytest.raises(SecurityError, match="exceeds maximum limit"):
        validate_file_upload("huge.json", byte_size=60_000_000, max_bytes=50_000_000)


def test_sanitize_identifier():
    assert sanitize_identifier("txid_12345abcdef") == "txid_12345abcdef"
    assert sanitize_identifier("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa") == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    assert sanitize_identifier("192.168.1.1:8333") == "192.168.1.1:8333"

    with pytest.raises(SecurityError):
        sanitize_identifier("txid; rm -rf /")

    with pytest.raises(SecurityError):
        sanitize_identifier("<script>alert(1)</script>")
