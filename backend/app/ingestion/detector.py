"""Format sniffer for automatic detection of CSV, JSON, and XML."""

from pathlib import Path


def detect_format(content: str | bytes, filename: str = "") -> str:
    """Detect whether input is 'csv', 'json', or 'xml' based on suffix and content sniffing."""
    suffix = Path(filename).suffix.lower()
    if suffix in [".csv", ".tsv"]:
        return "csv"
    if suffix == ".json":
        return "json"
    if suffix == ".xml":
        return "xml"

    # Content sniffing
    text = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else str(content)
    text_stripped = text.strip()

    if text_stripped.startswith("<") and text_stripped.endswith(">"):
        return "xml"
    if (text_stripped.startswith("{") and text_stripped.endswith("}")) or (
        text_stripped.startswith("[") and text_stripped.endswith("]")
    ):
        return "json"
    if "," in text_stripped or "\t" in text_stripped:
        return "csv"

    # Default fallback
    return "csv"
