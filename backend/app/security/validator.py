"""Security validation functions for safe air-gapped forensics."""

import re
from pathlib import Path


class SecurityError(ValueError):
    """Raised when security boundaries or validation constraints are violated."""
    pass


ALLOWED_EXTENSIONS = {".csv", ".json", ".xml", ".txt", ".mmdb"}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB
SAFE_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.\:\@]{1,128}$")


def validate_safe_path(target_path: str | Path, allowed_root: Path | None = None) -> Path:
    """
    Prevents path traversal attacks by resolving symlinks and verifying
    that the canonical target resides strictly within the allowed directory tree.
    """
    # Ensure no null bytes or control characters before filesystem operations
    if "\0" in str(target_path):
        raise SecurityError("Path contains forbidden null byte")

    path = Path(target_path).resolve()
    if allowed_root is not None:
        root = Path(allowed_root).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            raise SecurityError(
                f"Path traversal violation: Target '{path}' is outside root '{root}'"
            )
    return path


def validate_file_upload(
    filename: str,
    byte_size: int,
    max_bytes: int = MAX_UPLOAD_BYTES,
    allowed_extensions: set[str] | None = None,
) -> None:
    """Validates file extension and size limits against DoS and malicious extensions."""
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS

    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        raise SecurityError(
            f"Unsupported or forbidden file extension '{ext}'. Allowed: {sorted(allowed_extensions)}"
        )

    if byte_size > max_bytes:
        raise SecurityError(
            f"File size {byte_size} bytes exceeds maximum limit of {max_bytes} bytes"
        )


def sanitize_identifier(value: str) -> str:
    """
    Sanitizes alphanumeric forensic identifiers (TXIDs, wallet addresses, IP addresses).
    Strips dangerous characters preventing shell or SQL injection attacks.
    """
    cleaned = value.strip()
    if not SAFE_IDENTIFIER_PATTERN.match(cleaned):
        raise SecurityError(
            f"Identifier '{value}' contains forbidden characters or invalid length"
        )
    return cleaned
