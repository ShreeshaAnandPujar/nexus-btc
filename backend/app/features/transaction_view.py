"""Transaction behavioral feature calculations."""

import math
from typing import Any
from app.models.transaction import TransactionModel


def calculate_gini(values: list[float]) -> float:
    """Calculate Gini coefficient of value distribution (0 = perfectly equal, 1 = concentrated)."""
    if not values or len(values) < 2:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cum_sum = 0.0
    for i, v in enumerate(sorted_vals, 1):
        cum_sum += i * v
    tot = sum(sorted_vals)
    if tot == 0.0:
        return 0.0
    return round((2.0 * cum_sum) / (n * tot) - (n + 1.0) / n, 4)


def extract_transaction_features(tx: TransactionModel) -> dict[str, dict[str, Any]]:
    """Extract all transaction behavioral features with metadata."""
    in_addrs = tx.input_addresses
    out_addrs = tx.output_addresses
    in_amts = tx.input_amounts
    out_amts = tx.output_amounts

    in_count = len(in_addrs)
    out_count = len(out_addrs)
    tot_in = tx.input_amount
    tot_out = tx.output_amount
    fee = tx.fee

    fee_ratio = fee / (tot_in + 1e-8)
    io_val_ratio = tot_out / (tot_in + 1e-8)
    fan_ratio = out_count / (in_count + 1e-8)
    gini = calculate_gini(out_amts)

    # Address reuse count
    overlap = len(set(in_addrs).intersection(set(out_addrs)))

    return {
        "tx_total_volume_btc": {
            "name": "tx_total_volume_btc",
            "value": round(tot_out, 6),
            "normalized": round(math.log1p(tot_out) / 10.0, 4),
            "source": "transaction",
            "description": "Total BTC transferred across all outputs",
        },
        "tx_fee_ratio": {
            "name": "tx_fee_ratio",
            "value": round(fee_ratio, 6),
            "normalized": min(1.0, round(fee_ratio * 100.0, 4)),
            "source": "transaction",
            "description": "Ratio of miner fee to total input volume",
        },
        "tx_input_count": {
            "name": "tx_input_count",
            "value": float(in_count),
            "normalized": min(1.0, round(in_count / 50.0, 4)),
            "source": "transaction",
            "description": "Number of input UTXO addresses",
        },
        "tx_output_count": {
            "name": "tx_output_count",
            "value": float(out_count),
            "normalized": min(1.0, round(out_count / 50.0, 4)),
            "source": "transaction",
            "description": "Number of output destination addresses",
        },
        "tx_fan_ratio": {
            "name": "tx_fan_ratio",
            "value": round(fan_ratio, 4),
            "normalized": min(1.0, round(fan_ratio / 10.0, 4)),
            "source": "transaction",
            "description": "Ratio of output count to input count",
        },
        "tx_output_gini": {
            "name": "tx_output_gini",
            "value": round(gini, 4),
            "normalized": round(gini, 4),
            "source": "transaction",
            "description": "Gini inequality coefficient across output values",
        },
        "tx_address_reuse": {
            "name": "tx_address_reuse",
            "value": float(overlap),
            "normalized": 1.0 if overlap > 0 else 0.0,
            "source": "transaction",
            "description": "Direct overlap between input addresses and output addresses",
        },
    }
