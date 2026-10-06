"""Fan-in, Fan-out, Consolidation, and Rapid-split motif detectors."""

from app.models.transaction import TransactionModel
from app.motifs.base import BaseMotifDetector, MotifEvidence


class FanInOutDetector(BaseMotifDetector):
    """Detects multi-input consolidation (FAN_IN) and dispersion (FAN_OUT / RAPID_SPLIT)."""

    def detect_transaction(self, tx: TransactionModel) -> list[MotifEvidence]:
        results: list[MotifEvidence] = []
        in_count = len(tx.input_addresses)
        out_count = len(tx.output_addresses)

        # 1. FAN_IN / CONSOLIDATION (many inputs -> 1 or 2 outputs)
        if in_count >= 4 and out_count <= 2:
            conf = min(0.95, 0.70 + (in_count * 0.02))
            results.append(
                MotifEvidence(
                    motif_type="FAN_IN",
                    transactions=[tx.txid],
                    wallets=list(set(tx.input_addresses + tx.output_addresses)),
                    hops=1,
                    value_preservation=round(tx.output_amount / (tx.input_amount + 1e-8), 4),
                    confidence=conf,
                    details={
                        "input_count": in_count,
                        "output_count": out_count,
                        "total_consolidated_btc": tx.output_amount,
                    },
                    summary=f"FAN_IN: Consolidated {in_count} UTXOs into {out_count} output(s)",
                )
            )
            if out_count == 1:
                results.append(
                    MotifEvidence(
                        motif_type="CONSOLIDATION",
                        transactions=[tx.txid],
                        wallets=list(set(tx.input_addresses + tx.output_addresses)),
                        hops=1,
                        value_preservation=round(tx.output_amount / (tx.input_amount + 1e-8), 4),
                        confidence=conf,
                        details={
                            "input_count": in_count,
                            "output_count": out_count,
                            "total_consolidated_btc": tx.output_amount,
                        },
                        summary=f"CONSOLIDATION: Aggregated {in_count} inputs into single output",
                    )
                )

        # 2. FAN_OUT / RAPID_SPLIT (1 or 2 inputs -> many outputs)
        if in_count <= 2 and out_count >= 5:
            conf = min(0.95, 0.70 + (out_count * 0.02))
            results.append(
                MotifEvidence(
                    motif_type="FAN_OUT",
                    transactions=[tx.txid],
                    wallets=list(set(tx.input_addresses + tx.output_addresses)),
                    hops=1,
                    value_preservation=round(tx.output_amount / (tx.input_amount + 1e-8), 4),
                    confidence=conf,
                    details={
                        "input_count": in_count,
                        "output_count": out_count,
                        "total_dispersed_btc": tx.output_amount,
                    },
                    summary=f"FAN_OUT: Dispersed {in_count} input(s) into {out_count} recipient outputs",
                )
            )
            if out_count >= 8:
                results.append(
                    MotifEvidence(
                        motif_type="RAPID_SPLIT",
                        transactions=[tx.txid],
                        wallets=list(set(tx.input_addresses + tx.output_addresses)),
                        hops=1,
                        value_preservation=round(tx.output_amount / (tx.input_amount + 1e-8), 4),
                        confidence=conf,
                        details={
                            "input_count": in_count,
                            "output_count": out_count,
                            "total_dispersed_btc": tx.output_amount,
                        },
                        summary=f"RAPID_SPLIT: Split funds across {out_count} outputs in single transaction",
                    )
                )

        return results

    def detect(self, transactions: list[TransactionModel]) -> list[MotifEvidence]:
        results: list[MotifEvidence] = []
        for tx in transactions:
            results.extend(self.detect_transaction(tx))
        return results
