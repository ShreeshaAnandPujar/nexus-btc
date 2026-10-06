"""Peeling chain laundering motif detector."""

from app.models.transaction import TransactionModel
from app.motifs.base import BaseMotifDetector, MotifEvidence


class PeelingChainDetector(BaseMotifDetector):
    """
    Detects classic Bitcoin peeling chains:
    1 input, 2 outputs: smaller peel <= 0.05 * in_val, change >= 0.80 * in_val.
    """

    motif_type = "PEELING_CHAIN"

    def detect_transaction(self, tx: TransactionModel) -> MotifEvidence | None:
        in_count = len(tx.input_addresses)
        out_count = len(tx.output_addresses)
        out_amts = tx.output_amounts
        tot_in = tx.input_amount

        if in_count == 1 and out_count == 2 and tot_in > 0 and len(out_amts) == 2:
            min_out = min(out_amts)
            max_out = max(out_amts)

            peel_ratio = min_out / tot_in
            change_ratio = max_out / tot_in

            if peel_ratio <= 0.15 and change_ratio >= 0.70:
                conf = 0.85 if (peel_ratio <= 0.05 and change_ratio >= 0.80) else 0.70
                return MotifEvidence(
                    motif_type=self.motif_type,
                    transactions=[tx.txid],
                    wallets=list(set(tx.input_addresses + tx.output_addresses)),
                    hops=1,
                    duration_seconds=0.0,
                    value_preservation=round(change_ratio, 4),
                    confidence=conf,
                    details={
                        "peeled_amount_btc": min_out,
                        "change_amount_btc": max_out,
                        "peel_ratio": round(peel_ratio, 4),
                        "change_ratio": round(change_ratio, 4),
                    },
                    summary=f"Peeling chain step: {peel_ratio*100:.1f}% peeled, {change_ratio*100:.1f}% forward change",
                )
        return None

    def detect(self, transactions: list[TransactionModel]) -> list[MotifEvidence]:
        results = []
        for tx in transactions:
            m = self.detect_transaction(tx)
            if m:
                results.append(m)
        return results

