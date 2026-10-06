"""Endpoint classification for fund tracing paths."""

from app.schemas.trace import EndpointType
from app.models.transaction import TransactionModel


class EndpointClassifier:
    """Classifies terminal nodes of fund tracing paths without fabricating identities."""

    @staticmethod
    def classify_endpoint(
        wallet_address: str,
        outgoing_transactions: list[TransactionModel],
        is_cycle: bool = False,
        horizon_reached: bool = False,
    ) -> EndpointType:
        if is_cycle:
            return "CYCLE"

        if horizon_reached:
            return "HORIZON"

        # If no outgoing transactions found in local storage
        if not outgoing_transactions:
            return "DORMANT"

        # Check for mixer signatures in outgoing transactions
        for tx in outgoing_transactions:
            if len(tx.input_addresses) >= 3 and len(tx.output_addresses) >= 3:
                # Check equal outputs
                out_amts = sorted([a for a in tx.output_amounts if a > 0])
                for i in range(len(out_amts) - 1):
                    denom = max(out_amts[i], out_amts[i + 1])
                    if denom > 0 and abs(out_amts[i] - out_amts[i + 1]) / denom <= 0.01:
                        return "MIXER_LIKE"

        # Check for service heuristic (massive fan-in/fan-out)
        for tx in outgoing_transactions:
            if len(tx.input_addresses) >= 20 or len(tx.output_addresses) >= 20:
                return "SERVICE"

        return "UNKNOWN"
