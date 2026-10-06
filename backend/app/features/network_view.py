"""Network telemetry feature calculations."""

from typing import Any
from app.models.transaction import TransactionModel


def extract_network_features(
    tx: TransactionModel, ip_freq_map: dict[str, int] | None = None
) -> dict[str, dict[str, Any]]:
    """Extract network telemetry and IP association features."""
    ip_freq_map = ip_freq_map or {}
    src_ip = tx.src_ip or "0.0.0.0"
    freq = float(ip_freq_map.get(src_ip, 1))

    is_valid_ip = src_ip not in ("0.0.0.0", "UNKNOWN", "")
    has_asn = (tx.asn or 0) > 0
    has_geo = (tx.country or "UNKNOWN") not in ("UNKNOWN", "")

    return {
        "net_ip_frequency": {
            "name": "net_ip_frequency",
            "value": freq,
            "normalized": min(1.0, round(freq / 100.0, 4)),
            "source": "network",
            "description": "Total count of transactions observed originating from this source IP",
        },
        "net_telemetry_completeness": {
            "name": "net_telemetry_completeness",
            "value": float(sum([is_valid_ip, has_asn, has_geo])),
            "normalized": round(sum([is_valid_ip, has_asn, has_geo]) / 3.0, 4),
            "source": "network",
            "description": "Completeness score for IP, ASN, and country telemetry",
        },
        "net_asn_present": {
            "name": "net_asn_present",
            "value": 1.0 if has_asn else 0.0,
            "normalized": 1.0 if has_asn else 0.0,
            "source": "network",
            "description": "Indicator of resolved BGP Autonomous System",
        },
    }
