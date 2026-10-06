"""CoinJoin and mixing-like laundering motif detector."""

from app.models.transaction import TransactionModel
from app.motifs.base import BaseMotifDetector, MotifEvidence


class CoinJoinDetector(BaseMotifDetector):
    """
    Detects CoinJoin / Wasabi / Whirlpool mixing patterns:
    >= 3 distinct inputs, >= 3 outputs, with multiple outputs matching within +-1% tolerance.
    """

    motif_type = "MIXING_LIKE"

    def detect_transaction(self, tx: TransactionModel) -> MotifEvidence | None:
        in_addrs = set(tx.input_addresses)
        out_amts = sorted([a for a in tx.output_amounts if a > 0.0])

        if len(in_addrs) >= 3 and len(out_amts) >= 3:
            # Check for equal output values within 1% relative tolerance
            equal_count = 0
            matched_val = 0.0

            for i in range(len(out_amts) - 1):
                val_a = out_amts[i]
                val_b = out_amts[i + 1]
                denom = max(val_a, val_b)
                if denom > 0 and abs(val_a - val_b) / denom <= 0.01:
                    equal_count += 1
                    matched_val = val_a

            if equal_count >= 1:
                conf = 0.90 if equal_count >= 2 else 0.75
                return MotifEvidence(
                    motif_type=self.motif_type,
                    transactions=[tx.txid],
                    wallets=list(set(tx.input_addresses + tx.output_addresses)),
                    hops=1,
                    duration_seconds=0.0,
                    value_preservation=round(sum(out_amts) / (tx.input_amount + 1e-8), 4),
                    confidence=conf,
                    details={
                        "participant_count": len(in_addrs),
                        "output_count": len(out_amts),
                        "equal_denomination_btc": matched_val,
                        "equal_count": equal_count,
                    },
                    summary=f"CoinJoin mix: {len(in_addrs)} inputs, {equal_count + 1} matching denominations ({matched_val:.4f} BTC)",
                )
        return None

    def detect(self, transactions: list[TransactionModel]) -> list[MotifEvidence]:
        results = []
        for tx in transactions:
            m = self.detect_transaction(tx)
            if m:
                results.append(m)
        return results

