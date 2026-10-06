"""Rapid layering and circular flow detectors."""

from datetime import datetime
import networkx as nx
from app.models.transaction import TransactionModel
from app.motifs.base import BaseMotifDetector, MotifEvidence


class RapidLayeringDetector(BaseMotifDetector):
    """Detects rapid sequential transactions moving funds through intermediary wallets."""

    motif_type = "RAPID_LAYERING"

    def detect(self, transactions: list[TransactionModel]) -> list[MotifEvidence]:
        if len(transactions) < 2:
            return []

        # Sort by timestamp
        sorted_txs = sorted(transactions, key=lambda t: t.timestamp)
        results = []

        # Check for chains where tx_b spends from output of tx_a within 600 seconds
        for i in range(len(sorted_txs) - 1):
            tx_a = sorted_txs[i]
            tx_b = sorted_txs[i + 1]

            common = set(tx_a.output_addresses).intersection(set(tx_b.input_addresses))
            if common:
                try:
                    t_a = datetime.fromisoformat(tx_a.timestamp.replace("Z", "+00:00"))
                    t_b = datetime.fromisoformat(tx_b.timestamp.replace("Z", "+00:00"))
                    diff_sec = (t_b - t_a).total_seconds()

                    if 0 <= diff_sec <= 600:
                        results.append(
                            MotifEvidence(
                                motif_type=self.motif_type,
                                transactions=[tx_a.txid, tx_b.txid],
                                wallets=list(common),
                                hops=2,
                                duration_seconds=diff_sec,
                                value_preservation=round(tx_b.output_amount / (tx_a.input_amount + 1e-8), 4),
                                confidence=0.88,
                                details={
                                    "intermediary_wallets": list(common),
                                    "transit_delay_seconds": diff_sec,
                                },
                                summary=f"Rapid layering: {diff_sec:.0f}s transit through intermediary wallet",
                            )
                        )
                except Exception:
                    pass

        return results
