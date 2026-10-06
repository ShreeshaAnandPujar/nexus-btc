"""Temporal burst and velocity anomaly detector."""

from datetime import datetime
import numpy as np
from app.models.transaction import TransactionModel


class TemporalBurstDetector:
    """Detects transaction frequency surges, burst clusters, and rapid inter-arrival timing."""

    @staticmethod
    def detect_bursts(transactions: list[TransactionModel]) -> dict[str, float]:
        """
        Evaluate temporal burst anomaly score [0-100] per transaction.
        Returns: {txid: burst_score}
        """
        if len(transactions) < 2:
            return {tx.txid: 0.0 for tx in transactions}

        sorted_txs = sorted(transactions, key=lambda t: t.timestamp)
        scores: dict[str, float] = {}

        timestamps = []
        for tx in sorted_txs:
            try:
                dt = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00"))
                timestamps.append((dt.timestamp(), tx.txid, tx.output_amount))
            except Exception:
                timestamps.append((0.0, tx.txid, tx.output_amount))

        for idx, (t, txid, vol) in enumerate(timestamps):
            # Window of 5 minutes (300s)
            window_count = 0
            window_vol = 0.0
            for t_other, _, v_other in timestamps:
                if 0 <= (t - t_other) <= 300:
                    window_count += 1
                    window_vol += v_other

            # Compute score based on surge
            burst_score = 0.0
            if window_count >= 10:
                burst_score += 50.0
            elif window_count >= 5:
                burst_score += 25.0

            if window_vol >= 50.0:
                burst_score += 40.0
            elif window_vol >= 10.0:
                burst_score += 20.0

            scores[txid] = min(100.0, round(burst_score, 2))

        return scores
