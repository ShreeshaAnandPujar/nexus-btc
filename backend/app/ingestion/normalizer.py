"""Defensive normalizer transforming heterogeneous raw dicts into CanonicalTransaction."""

import ipaddress
import json
import re
from datetime import datetime, timezone
from typing import Any

_POSTGRES_ARRAY_RE = re.compile(r"^\{([^\}]*)\}$")
_HEX_64_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def parse_array_field(val: Any) -> list[str]:
    """Parse list-like string in postgres ({a,b}), JSON ([a,b]), or delimited (a;b|c) syntax."""
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        items = []
        for x in val:
            if isinstance(x, dict):
                addr = x.get("address") or x.get("addr") or x.get("wallet")
                if addr:
                    items.append(str(addr).strip())
            elif x is not None and str(x).strip():
                items.append(str(x).strip().strip('"\''))
        return items

    s = str(val).strip()
    if not s or s.lower() in ("none", "null", "{}"):
        return []

    # Check postgres array syntax {addr1,addr2}
    pg_match = _POSTGRES_ARRAY_RE.match(s)
    if pg_match:
        inner = pg_match.group(1).strip()
        if not inner:
            return []
        parts = []
        for part in re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", inner):
            clean = part.strip().strip('"\'')
            if clean:
                parts.append(clean)
        return parts

    # Check JSON array
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                items = []
                for x in parsed:
                    if isinstance(x, dict):
                        addr = x.get("address") or x.get("addr") or x.get("wallet")
                        if addr:
                            items.append(str(addr).strip())
                    elif x is not None and str(x).strip():
                        items.append(str(x).strip().strip('"\''))
                return items
        except json.JSONDecodeError:
            pass

    # Delimited by semicolon, pipe, or comma
    for delim in [";", "|", ","]:
        if delim in s:
            parts = [p.strip().strip('"\'') for p in s.split(delim)]
            return [p for p in parts if p]

    return [s.strip('"\'')]


def parse_float_array(val: Any) -> tuple[list[float], bool]:
    """Parse list of floats from heterogeneous string representations. Returns (amounts, has_negative)."""
    has_negative = False
    if val is None:
        return [], False

    if isinstance(val, (list, tuple)):
        results = []
        for x in val:
            if isinstance(x, dict):
                amt = x.get("amount_btc") or x.get("amount") or x.get("value") or 0.0
                try:
                    f = float(amt)
                    if f < 0:
                        has_negative = True
                    results.append(max(0.0, round(f, 8)))
                except Exception:
                    results.append(0.0)
            else:
                try:
                    amt = float(x)
                    if amt < 0:
                        has_negative = True
                    results.append(max(0.0, round(amt, 8)))
                except Exception:
                    results.append(0.0)
        return results, has_negative

    raw_strs = parse_array_field(val)
    results = []
    for item in raw_strs:
        try:
            amt = float(item)
            if amt < 0:
                has_negative = True
            results.append(max(0.0, round(amt, 8)))
        except (ValueError, TypeError):
            results.append(0.0)
    return results, has_negative


def normalize_ip(ip_str: Any) -> tuple[str, bool]:
    """Validate IP address; returns (normalized_ip, is_valid)."""
    if not ip_str or str(ip_str).strip().lower() in ("none", "null", ""):
        return "0.0.0.0", False
    s = str(ip_str).strip()
    try:
        ipaddress.ip_address(s)
        return s, True
    except ValueError:
        return "0.0.0.0", False


def normalize_port(port_val: Any, default: int = 8333) -> int:
    """Normalize network port to integer between 0 and 65535."""
    try:
        p = int(port_val)
        if 0 <= p <= 65535:
            return p
        return default
    except (ValueError, TypeError):
        return default


def normalize_raw_record(
    raw: dict[str, Any], source_file: str, source_row: int
) -> tuple[dict[str, Any], list[str], str]:
    """
    Defensively normalize raw record dictionary.
    Returns: (canonical_dict, quality_flags, validation_status)
    If critical integrity constraints fail, returns (raw, flags, 'INVALID') for quarantine.
    """
    flags: list[str] = []
    status: str = "VALID"

    # 1. Validate TXID
    raw_txid = raw.get("txid") or raw.get("transaction_id") or raw.get("tx_hash")
    if not raw_txid or not isinstance(raw_txid, str):
        flags.append("FLAG_TXID_MISSING")
        return raw, flags, "INVALID"

    txid = str(raw_txid).strip().lower()
    if not _HEX_64_RE.match(txid):
        flags.append("FLAG_TXID_MALFORMED")
        return raw, flags, "INVALID"

    # 2. Check for invalid array types (e.g. integer instead of array/string)
    for fld in ("inputs", "input_addresses", "outputs", "output_addresses"):
        val = raw.get(fld)
        if val is not None and isinstance(val, (int, float, bool)):
            flags.append(f"FLAG_{fld.upper()}_TYPE_ERROR")
            return raw, flags, "INVALID"

    # 3. Extract and Validate Amounts
    raw_in_amt = raw.get("input_amount") or raw.get("input_value")
    raw_out_amt = raw.get("output_amount") or raw.get("output_value")
    if raw_in_amt is not None:
        try:
            if float(raw_in_amt) < 0:
                flags.append("FLAG_NEGATIVE_AMOUNT")
                return raw, flags, "INVALID"
        except (ValueError, TypeError):
            flags.append("FLAG_AMOUNT_PARSE_ERROR")
            return raw, flags, "INVALID"

    if raw_out_amt is not None:
        try:
            if float(raw_out_amt) < 0:
                flags.append("FLAG_NEGATIVE_AMOUNT")
                return raw, flags, "INVALID"
        except (ValueError, TypeError):
            flags.append("FLAG_AMOUNT_PARSE_ERROR")
            return raw, flags, "INVALID"

    # 4. Extract and Validate Timestamp
    ts_raw = raw.get("ts") or raw.get("timestamp") or raw.get("time") or raw.get("datetime")
    timestamp = datetime.now(timezone.utc).isoformat()
    if ts_raw:
        ts_str = str(ts_raw).strip()
        try:
            if ts_str.endswith("Z"):
                ts_str_clean = ts_str[:-1] + "+00:00"
            else:
                ts_str_clean = ts_str
            dt = datetime.fromisoformat(ts_str_clean)
            timestamp = dt.isoformat()
        except Exception:
            flags.append("FLAG_TIMESTAMP_INVALID")
            return raw, flags, "INVALID"
    else:
        flags.append("FLAG_TIMESTAMP_MISSING")
        status = "REPAIRED"

    # 5. Network Telemetry
    src_ip, src_valid = normalize_ip(raw.get("src_ip") or raw.get("source_ip") or raw.get("source_ips"))
    if not src_valid:
        flags.append("FLAG_SRC_IP_MALFORMED")
    dst_ip, dst_valid = normalize_ip(raw.get("dst_ip") or raw.get("destination_ip") or raw.get("destination_ips"))
    if not dst_valid:
        flags.append("FLAG_DST_IP_MALFORMED")

    src_port = normalize_port(raw.get("src_port") or raw.get("source_port") or raw.get("source_ports"), 8333)
    dst_port = normalize_port(raw.get("dst_port") or raw.get("destination_port") or raw.get("destination_ports"), 8333)

    # 6. Addresses & Amounts Arrays
    input_addresses = parse_array_field(raw.get("input_addresses") or raw.get("inputs") or raw.get("from_addresses"))
    output_addresses = parse_array_field(raw.get("output_addresses") or raw.get("outputs") or raw.get("to_addresses"))

    input_amounts, in_neg = parse_float_array(raw.get("input_amounts") or raw.get("input_values") or raw.get("inputs"))
    output_amounts, out_neg = parse_float_array(raw.get("output_amounts") or raw.get("output_values") or raw.get("outputs"))

    if in_neg or out_neg:
        flags.append("FLAG_NEGATIVE_AMOUNT")
        return raw, flags, "INVALID"

    if not input_addresses:
        input_addresses = ["COINBASE"]
        if not input_amounts:
            fallback_amt = float(raw_in_amt) if raw_in_amt is not None else sum(output_amounts)
            input_amounts = [fallback_amt]
        flags.append("FLAG_COINBASE_TX")

    if not output_addresses:
        flags.append("FLAG_EMPTY_OUTPUTS")
        status = "WARNING"
        output_addresses = ["UNKNOWN_OUTPUT"]
        output_amounts = [0.0]

    # Align array lengths
    if len(input_amounts) < len(input_addresses):
        input_amounts.extend([0.0] * (len(input_addresses) - len(input_amounts)))
    elif len(input_amounts) > len(input_addresses):
        input_amounts = input_amounts[:len(input_addresses)]

    if len(output_amounts) < len(output_addresses):
        output_amounts.extend([0.0] * (len(output_addresses) - len(output_amounts)))
    elif len(output_amounts) > len(output_addresses):
        output_amounts = output_amounts[:len(output_addresses)]

    # Totals and fee
    tot_in = round(float(raw_in_amt), 8) if raw_in_amt is not None else round(sum(input_amounts), 8)
    tot_out = round(float(raw_out_amt), 8) if raw_out_amt is not None else round(sum(output_amounts), 8)

    fee_val = raw.get("fee")
    if fee_val is not None:
        try:
            fee = max(0.0, round(float(fee_val), 8))
        except (ValueError, TypeError):
            fee = max(0.0, round(tot_in - tot_out, 8))
            flags.append("FLAG_FEE_CALCULATED")
    else:
        fee = max(0.0, round(tot_in - tot_out, 8))

    # Script type
    script_raw = str(raw.get("script_type") or raw.get("script_types") or "UNKNOWN").strip().upper()
    valid_scripts = {"P2PK", "P2PKH", "P2SH", "P2WPKH", "P2TR"}
    script_type = script_raw if script_raw in valid_scripts else "UNKNOWN"
    if script_type == "UNKNOWN":
        flags.append("FLAG_SCRIPT_UNKNOWN")

    # Geolocation / ASN
    country = str(raw.get("geo_country") or raw.get("country") or "UNKNOWN").strip().upper()
    if not country or len(country) > 4:
        country = "UNKNOWN"
        flags.append("FLAG_GEO_MISSING")

    try:
        asn = int(raw.get("asn") or 0)
    except (ValueError, TypeError):
        asn = 0
        flags.append("FLAG_ASN_MISSING")

    canonical = {
        "source_file": source_file,
        "source_row": source_row,
        "validation_status": status,
        "data_quality_flags": flags,
        "timestamp": timestamp,
        "txid": txid,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "input_addresses": input_addresses,
        "output_addresses": output_addresses,
        "input_amounts": input_amounts,
        "output_amounts": output_amounts,
        "input_amount": tot_in,
        "output_amount": tot_out,
        "fee": fee,
        "script_type": script_type,
        "country": country,
        "asn": asn,
    }

    return canonical, flags, status
