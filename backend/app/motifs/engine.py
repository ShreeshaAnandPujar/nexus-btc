"""Unified Motif Engine orchestrating all laundering topology detectors."""

from typing import Any
import networkx as nx
from app.models.transaction import TransactionModel
from app.motifs.base import MotifEvidence
from app.motifs.peeling_chain import PeelingChainDetector
from app.motifs.coinjoin import CoinJoinDetector
from app.motifs.fan_in_out import FanInOutDetector
from app.motifs.rapid_layering import RapidLayeringDetector
from app.motifs.circular_flow import CircularFlowDetector, DormantActivationDetector


class MotifEngine:
    """Detects all 9 non-negotiable Bitcoin money-laundering structural motifs."""

    def __init__(self):
        self.peeling_detector = PeelingChainDetector()
        self.coinjoin_detector = CoinJoinDetector()
        self.fan_detector = FanInOutDetector()
        self.layering_detector = RapidLayeringDetector()
        self.circular_detector = CircularFlowDetector()
        self.dormant_detector = DormantActivationDetector()

    def scan_transaction(
        self,
        tx: TransactionModel,
        wallet_history: dict[str, list[str]] | None = None,
    ) -> list[MotifEvidence]:
        """Scan an individual transaction for point motifs."""
        motifs: list[MotifEvidence] = []

        # 1. Peeling chain
        peel = self.peeling_detector.detect_transaction(tx)
        if peel:
            motifs.append(peel)

        # 2. CoinJoin / Mixing-like
        mix = self.coinjoin_detector.detect_transaction(tx)
        if mix:
            motifs.append(mix)

        # 3. Fan-in / Fan-out / Consolidation / Rapid-split
        fan_motifs = self.fan_detector.detect_transaction(tx)
        motifs.extend(fan_motifs)

        # 4. Dormant activation
        dormant = self.dormant_detector.detect_transaction(tx, wallet_history)
        motifs.extend(dormant)

        return motifs

    def scan_all(
        self,
        transactions: list[TransactionModel],
        g: nx.MultiDiGraph | None = None,
    ) -> dict[str, list[MotifEvidence]]:
        """
        Scan full transaction set and graph for both point and topological motifs.
        Returns mapping: {txid: [MotifEvidence, ...]}
        """
        results: dict[str, list[MotifEvidence]] = {}

        # Build wallet history map for dormancy detection
        wallet_history: dict[str, list[str]] = {}
        for tx in transactions:
            for w in tx.input_addresses:
                wallet_history.setdefault(w, []).append(tx.timestamp)

        # Run point detectors
        for tx in transactions:
            tx_motifs = self.scan_transaction(tx, wallet_history)
            if tx_motifs:
                results[tx.txid] = tx_motifs

        # Run chain detectors (Rapid layering)
        layer_motifs = self.layering_detector.detect(transactions)
        for m in layer_motifs:
            for txid in m.transactions:
                results.setdefault(txid, []).append(m)

        # Run cycle detectors (Circular flow)
        if g is not None:
            circ_motifs = self.circular_detector.detect(g)
            # Annotate affected transactions
            for cm in circ_motifs:
                results.setdefault("GLOBAL_CYCLE", []).append(cm)

        return results
