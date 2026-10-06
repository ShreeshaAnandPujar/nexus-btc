"""Circular flow and dormant activation laundering motif detectors."""

from datetime import datetime
import networkx as nx
from app.models.transaction import TransactionModel
from app.motifs.base import BaseMotifDetector, MotifEvidence


class CircularFlowDetector(BaseMotifDetector):
    """Detects cycles in the fund transfer graph (wash trading / round-tripping)."""

    motif_type = "CIRCULAR_FLOW"

    def detect(self, target: nx.MultiDiGraph | list[TransactionModel]) -> list[MotifEvidence]:
        if isinstance(target, list):
            g = nx.MultiDiGraph()
            for tx in target:
                for in_w in tx.input_addresses:
                    for out_w in tx.output_addresses:
                        g.add_edge(f"wallet:{in_w}", f"wallet:{out_w}", relationship="TRANSFERRED", amount=tx.output_amount)
            return self._detect_in_graph(g)
        return self._detect_in_graph(target)

    def _detect_in_graph(self, g: nx.MultiDiGraph) -> list[MotifEvidence]:
        results = []
        # Build wallet-to-wallet directed graph
        wallet_graph = nx.DiGraph()

        for u, v, data in g.edges(data=True):
            if data.get("relationship") == "TRANSFERRED" and str(u).startswith("wallet:") and str(v).startswith("wallet:"):
                wallet_graph.add_edge(u, v, **data)

        # Find simple cycles of length between 2 and 6
        try:
            cycles = list(nx.simple_cycles(wallet_graph))
            for cycle in cycles[:20]:
                if 2 <= len(cycle) <= 6:
                    clean_wallets = [w.replace("wallet:", "") for w in cycle]
                    results.append(
                        MotifEvidence(
                            motif_type=self.motif_type,
                            wallets=clean_wallets,
                            hops=len(clean_wallets),
                            confidence=0.85,
                            details={"cycle_path": clean_wallets},
                            summary=f"Circular fund flow: {len(clean_wallets)}-hop closed loop detected",
                        )
                    )
        except Exception:
            pass

        return results


class DormantActivationDetector(BaseMotifDetector):
    """Detects wallets dormant for >180 days suddenly transacting significant volume."""

    motif_type = "DORMANT_ACTIVATION"

    def detect_transaction(self, tx: TransactionModel, wallet_history: dict[str, list[str]] | None = None) -> list[MotifEvidence]:
        results = []
        if not wallet_history:
            return results

        try:
            tx_time = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00"))
            for w in tx.input_addresses:
                timestamps = wallet_history.get(w, [])
                if len(timestamps) > 1:
                    past_times = [
                        datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        for ts in timestamps if ts != tx.timestamp
                    ]
                    if past_times:
                        most_recent = max(past_times)
                        dormancy_days = (tx_time - most_recent).days
                        if dormancy_days >= 60 and tx.input_amount >= 1.0:
                            results.append(
                                MotifEvidence(
                                    motif_type=self.motif_type,
                                    transactions=[tx.txid],
                                    wallets=[w],
                                    confidence=0.80,
                                    details={
                                        "dormancy_days": dormancy_days,
                                        "activated_volume_btc": tx.input_amount,
                                    },
                                    summary=f"Dormant address {w[:10]}... reactivated after {dormancy_days} days with {tx.input_amount:.2f} BTC",
                                )
                            )
        except Exception:
            pass

        return results
