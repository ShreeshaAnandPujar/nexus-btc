"""Entity Resolution and Clustering Engine combining Common-Input heuristic and HDBSCAN."""

import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.database import SessionLocal
from app.models.transaction import TransactionModel
from app.models.entity import EntityModel
from app.clustering.union_find import UnionFind
from app.clustering.hdbscan_clustering import BehavioralClusterer


class EntityClusteringEngine:
    """Forensic entity clustering engine enforcing non-legal identity attribution."""

    def __init__(self, db: Session | None = None):
        self._db = db
        self.behavioral_clusterer = BehavioralClusterer()

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def run_clustering(self) -> dict[str, Any]:
        """Execute complete entity clustering pipeline over stored transactions."""
        logger.info("Initiating Common-Input entity clustering...")
        uf = UnionFind()
        wallet_stats: dict[str, dict[str, float]] = {}
        wallet_timestamps: dict[str, list[str]] = {}

        transactions = self.db.query(TransactionModel).all()

        for tx in transactions:
            inputs = tx.input_addresses
            outputs = tx.output_addresses
            in_amts = tx.input_amounts
            out_amts = tx.output_amounts

            # 1. Multi-input Common-Input Heuristic
            valid_inputs = [w for w in inputs if w and w != "COINBASE"]
            if len(valid_inputs) > 1:
                base = valid_inputs[0]
                for other in valid_inputs[1:]:
                    uf.union(base, other)
            elif len(valid_inputs) == 1:
                # Register single input in UnionFind
                uf.find(valid_inputs[0])

            # Gather behavioral statistics
            for idx, w in enumerate(inputs):
                if w and w != "COINBASE":
                    amt = in_amts[idx] if idx < len(in_amts) else 0.0
                    stats = wallet_stats.setdefault(
                        w, {"tx_count": 0, "vol_sent": 0.0, "vol_recv": 0.0, "avg_fee": 0.0, "reuse_rate": 0.0}
                    )
                    stats["tx_count"] += 1
                    stats["vol_sent"] += amt
                    stats["avg_fee"] = (stats["avg_fee"] + tx.fee) / 2.0
                    wallet_timestamps.setdefault(w, []).append(tx.timestamp)

            for idx, w in enumerate(outputs):
                if w:
                    amt = out_amts[idx] if idx < len(out_amts) else 0.0
                    stats = wallet_stats.setdefault(
                        w, {"tx_count": 0, "vol_sent": 0.0, "vol_recv": 0.0, "avg_fee": 0.0, "reuse_rate": 0.0}
                    )
                    stats["tx_count"] += 1
                    stats["vol_recv"] += amt
                    wallet_timestamps.setdefault(w, []).append(tx.timestamp)

        # Build clusters
        ci_clusters = uf.get_clusters()
        logger.info(f"Generated {len(ci_clusters)} common-input clusters")

        wallet_to_entity: dict[str, str] = {}
        entity_records: list[EntityModel] = []

        # Remove existing entities to prevent stale state
        self.db.query(EntityModel).delete()

        for root, member_wallets in ci_clusters.items():
            # Generate deterministic entity id
            sorted_wallets = sorted(member_wallets)
            ent_hash = hashlib.sha256("::".join(sorted_wallets).encode()).hexdigest()[:12]
            entity_id = f"ENT-CI-{ent_hash.upper()}"

            for w in member_wallets:
                wallet_to_entity[w] = entity_id

            # Aggregates
            total_vol = sum(
                wallet_stats.get(w, {}).get("vol_sent", 0.0) + wallet_stats.get(w, {}).get("vol_recv", 0.0)
                for w in member_wallets
            )
            all_ts = [ts for w in member_wallets for ts in wallet_timestamps.get(w, [])]
            first_seen = min(all_ts) if all_ts else None
            last_seen = max(all_ts) if all_ts else None

            confidence = 0.95 if len(member_wallets) > 1 else 0.70
            evidence = [
                f"Multi-input co-spending detected across {len(member_wallets)} wallet addresses",
                "Deterministic Common Input Ownership Heuristic applied",
            ] if len(member_wallets) > 1 else ["Single wallet singleton cluster"]

            ent_record = EntityModel(
                entity_id=entity_id,
                cluster_type="common_input" if len(member_wallets) > 1 else "singleton",
                wallet_count=len(member_wallets),
                member_wallets_json=json.dumps(member_wallets),
                cluster_confidence=confidence,
                risk_score=0.0,  # Will be enriched by risk engine
                confidence_score=confidence * 100.0,
                cluster_features_json=json.dumps({
                    "total_volume_btc": round(total_vol, 8),
                    "co_spent_input_count": len(member_wallets),
                }),
                cluster_evidence_json=json.dumps(evidence),
                first_seen=first_seen,
                last_seen=last_seen,
                total_volume_btc=round(total_vol, 8),
            )
            entity_records.append(ent_record)

        # Batch insert entities
        self.db.bulk_save_objects(entity_records)

        # Annotate transactions with entity_id
        for tx in transactions:
            first_input = next((w for w in tx.input_addresses if w and w != "COINBASE"), None)
            if first_input and first_input in wallet_to_entity:
                tx.entity_id = wallet_to_entity[first_input]
            elif tx.output_addresses and tx.output_addresses[0] in wallet_to_entity:
                tx.entity_id = wallet_to_entity[tx.output_addresses[0]]

        self.db.commit()

        return {
            "entities_created": len(entity_records),
            "multi_wallet_clusters": sum(1 for e in entity_records if e.wallet_count > 1),
            "wallets_indexed": len(wallet_to_entity),
        }

    def get_entity_for_wallet(self, wallet_address: str) -> EntityModel | None:
        """Find entity containing the specified wallet."""
        entities = self.db.query(EntityModel).all()
        for e in entities:
            if wallet_address in e.member_wallets:
                return e
        return None
