"""Risk and Confidence Fusion Engine with Evidence Chain Builder."""

from typing import Any
from app.models.transaction import TransactionModel
from app.models.alert import AlertModel
from app.motifs.base import MotifEvidence
from app.risk.scoring import RiskScoringEngine
from app.risk.confidence import ConfidenceScoringEngine
from app.schemas.alert import EvidenceChainStep


class RiskEngine:
    """Orchestrates risk scoring, confidence computation, and evidence chain assembly."""

    def __init__(self):
        self.risk_scorer = RiskScoringEngine()
        self.confidence_scorer = ConfidenceScoringEngine()

    def evaluate_transaction(
        self,
        tx: TransactionModel,
        anomaly_scores: dict[str, float],
        motifs: list[MotifEvidence],
        correlation_evidence: dict[str, Any],
        graph_density: float = 0.0,
        graph_degree: float = 0.0,
    ) -> tuple[float, float, str, list[EvidenceChainStep]]:
        """
        Evaluate transaction risk, confidence, severity, and evidence chain.
        Returns: (risk_score, confidence_score, severity, evidence_chain)
        """
        anomaly_combined = anomaly_scores.get("combined_anomaly_score", 0.0)
        net_score = correlation_evidence.get("association_score", 50.0)
        net_conf = correlation_evidence.get("association_confidence", 50.0)
        disagreement = anomaly_scores.get("model_disagreement", 0.0)

        # 1. Compute Risk Score
        risk_score, severity, motif_contrib = self.risk_scorer.compute_risk(
            anomaly_score=anomaly_combined,
            motifs=motifs,
            network_score=net_score,
            graph_density=graph_density,
            graph_degree=graph_degree,
        )

        # 2. Compute Confidence Score
        # Completeness ratio
        is_valid_ip = tx.src_ip not in ("0.0.0.0", "UNKNOWN", "")
        has_geo = tx.country not in ("UNKNOWN", "")
        has_asn = (tx.asn or 0) > 0
        comp_ratio = sum([is_valid_ip, has_geo, has_asn]) / 3.0

        confidence_score = self.confidence_scorer.compute_confidence(
            data_completeness_ratio=comp_ratio,
            correlation_confidence=net_conf,
            model_disagreement=disagreement,
            has_motifs=len(motifs) > 0,
            graph_degree=graph_degree,
        )

        # 3. Assemble Forensic Evidence Chain
        chain: list[EvidenceChainStep] = []
        step_idx = 1

        # Step 1: Network Observation
        if tx.src_ip and tx.src_ip != "0.0.0.0":
            chain.append(
                EvidenceChainStep(
                    step_number=step_idx,
                    step_type="NETWORK_OBSERVATION",
                    identifier=tx.src_ip,
                    description=f"Broadcast packet observed from IP {tx.src_ip} (ASN {tx.asn}, Country {tx.country})",
                    relationship="probabilistic",
                    confidence=round(net_conf / 100.0, 2),
                    metadata={"asn": tx.asn, "country": tx.country, "port": tx.src_port},
                )
            )
            step_idx += 1

        # Step 2: Transaction Broadcast
        chain.append(
            EvidenceChainStep(
                step_number=step_idx,
                step_type="TRANSACTION",
                identifier=tx.txid,
                description=f"Transaction {tx.txid[:12]}... recorded with {tx.output_amount:.4f} BTC volume and fee {tx.fee:.6f} BTC",
                relationship="observed",
                confidence=1.0,
                metadata={"volume_btc": tx.output_amount, "timestamp": tx.timestamp},
            )
        )
        step_idx += 1

        # Step 3: Input Wallets
        in_sample = tx.input_addresses[:3]
        chain.append(
            EvidenceChainStep(
                step_number=step_idx,
                step_type="INPUT_WALLET",
                identifier=", ".join(in_sample),
                description=f"Fund origin from {len(tx.input_addresses)} input UTXO address(es)",
                relationship="observed",
                confidence=1.0,
                metadata={"input_count": len(tx.input_addresses)},
            )
        )
        step_idx += 1

        # Step 4: Output Wallets
        out_sample = tx.output_addresses[:3]
        chain.append(
            EvidenceChainStep(
                step_number=step_idx,
                step_type="OUTPUT_WALLET",
                identifier=", ".join(out_sample),
                description=f"Funds transferred to {len(tx.output_addresses)} destination output(s)",
                relationship="observed",
                confidence=1.0,
                metadata={"output_count": len(tx.output_addresses)},
            )
        )
        step_idx += 1

        # Step 5: Entity Cluster
        if tx.entity_id:
            chain.append(
                EvidenceChainStep(
                    step_number=step_idx,
                    step_type="ENTITY",
                    identifier=tx.entity_id,
                    description=f"Wallet belongs to inferred entity cluster {tx.entity_id}",
                    relationship="inferred",
                    confidence=0.90,
                    metadata={"entity_id": tx.entity_id},
                )
            )
            step_idx += 1

        # Step 6: Laundering Motif
        if motifs:
            primary_m = motifs[0]
            chain.append(
                EvidenceChainStep(
                    step_number=step_idx,
                    step_type="MOTIF",
                    identifier=primary_m.motif_type,
                    description=f"Structural laundering topology identified: {primary_m.summary}",
                    relationship="inferred",
                    confidence=primary_m.confidence,
                    metadata=primary_m.details,
                )
            )

        return risk_score, confidence_score, severity, chain
