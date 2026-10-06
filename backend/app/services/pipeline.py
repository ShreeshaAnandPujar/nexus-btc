"""End-to-End Digital Forensics Pipeline for NEXUS-BTC."""

import json
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.core.logging import logger
from app.models.transaction import TransactionModel
from app.models.alert import AlertModel
from app.models.entity import EntityModel
from app.clustering.engine import EntityClusteringEngine
from app.graph.engine import ForensicGraphEngine
from app.features.engine import FeatureEngine
from app.motifs.engine import MotifEngine
from app.anomaly.ensemble import AnomalyEnsemble
from app.correlation.engine import CorrelationEngine
from app.risk.engine import RiskEngine
from app.explainability.engine import ExplainabilityEngine
from app.explainability.shap_explainer import ShapExplainer


class ForensicPipeline:
    """Master orchestrator executing the 14-stage NEXUS-BTC forensic surveillance loop."""

    def __init__(self, db: Session | None = None):
        self._db = db
        init_db()

        self.clustering_engine = EntityClusteringEngine(self.db)
        self.graph_engine = ForensicGraphEngine(self.db)
        self.feature_engine = FeatureEngine()
        self.motif_engine = MotifEngine()
        self.anomaly_ensemble = AnomalyEnsemble()
        self.correlation_engine = CorrelationEngine()
        self.risk_engine = RiskEngine()
        self.explainability_engine = ExplainabilityEngine(
            tree_estimator=self.anomaly_ensemble.supervised_rf.base_rf
        )

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def run_full_pipeline(self) -> dict:
        """Run complete analysis over all transactions currently stored in SQLite."""
        t0 = time.time()
        logger.info("Starting NEXUS-BTC forensic analysis pipeline...")

        # 1. Fetch transactions
        transactions = self.db.query(TransactionModel).all()
        if not transactions:
            logger.warning("No transactions found in database to analyze.")
            return {"status": "EMPTY", "message": "No transactions in database"}

        # 2. Entity Clustering (Common-Input Union-Find)
        cluster_summary = self.clustering_engine.run_clustering()

        # 3. Build Forensic Graph
        node_count = self.graph_engine.build_from_database()

        # 4. Extract Multi-View Feature Vectors
        ip_freq_map: dict[str, int] = {}
        for tx in transactions:
            if tx.src_ip:
                ip_freq_map[tx.src_ip] = ip_freq_map.get(tx.src_ip, 0) + 1

        feature_matrix = []
        for tx in transactions:
            vec = self.feature_engine.extract_vector(tx, self.graph_engine.graph, ip_freq_map)
            feature_matrix.append(vec)

        import numpy as np
        X = np.array(feature_matrix, dtype=np.float64)

        # 5. Detect Laundering Motifs
        all_motifs = self.motif_engine.scan_all(transactions, self.graph_engine.graph)

        # 6. Run AI Anomaly Ensemble
        ensemble_scores = self.anomaly_ensemble.infer(X, transactions)
        # Update ShapExplainer with fitted base estimator
        self.explainability_engine.shap_explainer = ShapExplainer(
            self.anomaly_ensemble.supervised_rf.base_rf
        )

        # 7. Evaluate Risk, Confidence, Evidence Chains & Generate Alerts
        # Clear existing alerts
        self.db.query(AlertModel).delete()
        alerts_created = []

        for idx, tx in enumerate(transactions):
            tx_motifs = all_motifs.get(tx.txid, [])
            anom_score_dict = ensemble_scores[idx] if idx < len(ensemble_scores) else {}

            # Network Correlation Evidence
            corr_evidence = self.correlation_engine.correlate_transaction(
                tx_timestamp=tx.timestamp,
                src_ip=tx.src_ip,
                ip_observation_count=ip_freq_map.get(tx.src_ip or "", 1),
                asn=tx.asn or 0,
                country=tx.country or "UNKNOWN",
            )

            # Risk & Confidence Fusion
            risk_score, conf_score, severity, chain = self.risk_engine.evaluate_transaction(
                tx=tx,
                anomaly_scores=anom_score_dict,
                motifs=tx_motifs,
                correlation_evidence=corr_evidence.model_dump(),
                graph_density=float(X[idx, 9]) if len(X[idx]) > 9 else 0.0,
                graph_degree=float(X[idx, 7]) if len(X[idx]) > 7 else 0.0,
            )

            # Update transaction record
            tx.risk_score = risk_score
            tx.confidence_score = conf_score
            tx.alert_level = severity
            tx.detected_motifs_json = json.dumps([m.motif_type for m in tx_motifs])

            # If severity is Medium, High, or Critical, generate Alert
            if severity in ("MEDIUM", "HIGH", "CRITICAL") or tx_motifs:
                alert_id = f"ALT-{tx.txid[:8].upper()}"
                primary_motif = tx_motifs[0].motif_type if tx_motifs else None

                # Explanations
                xai_response = self.explainability_engine.explain(
                    alert_id=alert_id,
                    tx=tx,
                    feature_vec=X[idx],
                    risk_score=risk_score,
                    motifs=tx_motifs,
                    model_scores=anom_score_dict,
                    graph_degree=float(X[idx, 7]) if len(X[idx]) > 7 else 2.0,
                )

                alert = AlertModel(
                    alert_id=alert_id,
                    txid=tx.txid,
                    entity_id=tx.entity_id,
                    risk_score=risk_score,
                    confidence_score=conf_score,
                    severity=severity,
                    primary_motif=primary_motif,
                    motifs_json=json.dumps([m.motif_type for m in tx_motifs]),
                    explanation_json=json.dumps(xai_response.model_dump()),
                    counterfactual_json=json.dumps(
                        [c.model_dump() for c in xai_response.counterfactuals]
                    ),
                    evidence_chain_json=json.dumps([s.model_dump() for s in chain]),
                    model_contributions_json=json.dumps(anom_score_dict),
                )
                alerts_created.append(alert)

        # Batch insert alerts
        if alerts_created:
            self.db.bulk_save_objects(alerts_created)

        # Enrich entities with risk scores based on member transactions
        entities = self.db.query(EntityModel).all()
        for ent in entities:
            member_txs = [
                tx for tx in transactions
                if any(w in ent.member_wallets for w in tx.input_addresses + tx.output_addresses)
            ]
            if member_txs:
                max_risk = max(tx.risk_score for tx in member_txs)
                avg_conf = sum(tx.confidence_score for tx in member_txs) / len(member_txs)
                ent.risk_score = round(max_risk, 2)
                ent.confidence_score = round(avg_conf, 2)

        self.db.commit()

        duration = round(time.time() - t0, 3)
        logger.info(
            f"Forensic Pipeline complete in {duration}s: analyzed {len(transactions)} txs, "
            f"generated {len(alerts_created)} alerts ({len([a for a in alerts_created if a.severity == 'CRITICAL'])} CRITICAL)"
        )

        return {
            "status": "COMPLETED",
            "execution_time_seconds": duration,
            "transactions_analyzed": len(transactions),
            "alerts_generated": len(alerts_created),
            "critical_alerts": len([a for a in alerts_created if a.severity == "CRITICAL"]),
            "high_alerts": len([a for a in alerts_created if a.severity == "HIGH"]),
            "entities_clustered": cluster_summary.get("entities_created", 0),
            "graph_nodes": node_count,
        }
