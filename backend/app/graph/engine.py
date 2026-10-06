"""In-memory heterogeneous forensic graph engine powered by NetworkX."""

import json
from typing import Any
import networkx as nx
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.database import SessionLocal
from app.models.transaction import TransactionModel
from app.models.entity import EntityModel


class ForensicGraphEngine:
    """Heterogeneous in-memory directed graph representing blockchain and network topologies."""

    def __init__(self, db: Session | None = None):
        self._db = db
        self.graph = nx.MultiDiGraph()

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def clear(self):
        self.graph.clear()

    def build_from_database(self, max_records: int = 5000) -> int:
        """Populate heterogeneous graph from SQLite database."""
        self.clear()
        transactions = self.db.query(TransactionModel).limit(max_records).all()
        entities = self.db.query(EntityModel).all()

        # 1. Add Entities
        for ent in entities:
            ent_node_id = f"ent:{ent.entity_id}"
            self.graph.add_node(
                ent_node_id,
                label=ent.entity_id,
                type="ENTITY",
                risk=ent.risk_score,
                confidence=ent.confidence_score / 100.0,
                cluster_type=ent.cluster_type,
                wallet_count=ent.wallet_count,
            )
            for w in ent.member_wallets:
                w_node_id = f"wallet:{w}"
                if not self.graph.has_node(w_node_id):
                    self.graph.add_node(w_node_id, label=w, type="WALLET", risk=0.0)
                self.graph.add_edge(
                    w_node_id,
                    ent_node_id,
                    relationship="CLUSTERED_AS",
                    confidence=ent.cluster_confidence,
                    provenance="INFERRED",
                    amount=0.0,
                )

        # 2. Add Transactions and Telemetry
        for tx in transactions:
            tx_node_id = f"tx:{tx.txid}"
            self.graph.add_node(
                tx_node_id,
                label=f"{tx.txid[:8]}...{tx.txid[-6:]}",
                full_txid=tx.txid,
                type="TRANSACTION",
                risk=tx.risk_score,
                confidence=tx.confidence_score / 100.0 if tx.confidence_score else 1.0,
                amount=tx.output_amount,
                fee=tx.fee,
                timestamp=tx.timestamp,
                alert_level=tx.alert_level,
            )

            # Network Telemetry: IP, ASN, Country
            if tx.src_ip and tx.src_ip != "0.0.0.0":
                ip_node_id = f"ip:{tx.src_ip}"
                if not self.graph.has_node(ip_node_id):
                    self.graph.add_node(ip_node_id, label=tx.src_ip, type="IP", risk=0.0)
                self.graph.add_edge(
                    ip_node_id,
                    tx_node_id,
                    relationship="OBSERVED",
                    timestamp=tx.timestamp,
                    confidence=0.85,
                    provenance="OBSERVED",
                    amount=0.0,
                )

                if tx.country and tx.country != "UNKNOWN":
                    c_node_id = f"country:{tx.country}"
                    if not self.graph.has_node(c_node_id):
                        self.graph.add_node(c_node_id, label=tx.country, type="COUNTRY")
                    self.graph.add_edge(
                        ip_node_id,
                        c_node_id,
                        relationship="LOCATED_IN",
                        provenance="INFERRED",
                        confidence=0.90,
                        amount=0.0,
                    )

                if tx.asn and tx.asn > 0:
                    asn_node_id = f"asn:{tx.asn}"
                    if not self.graph.has_node(asn_node_id):
                        self.graph.add_node(asn_node_id, label=f"AS{tx.asn}", type="ASN")
                    self.graph.add_edge(
                        ip_node_id,
                        asn_node_id,
                        relationship="BELONGS_TO_ASN",
                        provenance="INFERRED",
                        confidence=0.95,
                        amount=0.0,
                    )

            # Inputs (Wallet SPENT to TX)
            for idx, in_addr in enumerate(tx.input_addresses):
                if in_addr and in_addr != "COINBASE":
                    w_node_id = f"wallet:{in_addr}"
                    if not self.graph.has_node(w_node_id):
                        self.graph.add_node(w_node_id, label=in_addr, type="WALLET", risk=0.0)
                    amt = tx.input_amounts[idx] if idx < len(tx.input_amounts) else 0.0
                    self.graph.add_edge(
                        w_node_id,
                        tx_node_id,
                        relationship="SPENT",
                        amount=amt,
                        timestamp=tx.timestamp,
                        confidence=1.0,
                        provenance="OBSERVED",
                    )

            # Outputs (TX CREATED to Wallet)
            for idx, out_addr in enumerate(tx.output_addresses):
                if out_addr:
                    w_node_id = f"wallet:{out_addr}"
                    if not self.graph.has_node(w_node_id):
                        self.graph.add_node(w_node_id, label=out_addr, type="WALLET", risk=0.0)
                    amt = tx.output_amounts[idx] if idx < len(tx.output_amounts) else 0.0
                    self.graph.add_edge(
                        tx_node_id,
                        w_node_id,
                        relationship="CREATED",
                        amount=amt,
                        timestamp=tx.timestamp,
                        confidence=1.0,
                        provenance="OBSERVED",
                    )

        logger.info(
            f"Forensic Graph initialized: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )
        return self.graph.number_of_nodes()

    def get_ego_subgraph(self, target_id: str, radius: int = 2, max_nodes: int = 80) -> nx.MultiDiGraph:
        """Extract ego-network subgraph around specified target node."""
        clean_target = target_id
        if not self.graph.has_node(clean_target):
            # Check prefixes
            for prefix in ["tx:", "wallet:", "ent:", "ip:"]:
                cand = f"{prefix}{target_id}"
                if self.graph.has_node(cand):
                    clean_target = cand
                    break

        if not self.graph.has_node(clean_target):
            # Return empty or fallback
            return nx.MultiDiGraph()

        # Ego graph traversal
        visited = {clean_target}
        current_frontier = {clean_target}

        for _ in range(radius):
            next_frontier = set()
            for node in current_frontier:
                neighbors = set(self.graph.predecessors(node)).union(self.graph.successors(node))
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.add(neighbor)
                        if len(visited) >= max_nodes:
                            break
                if len(visited) >= max_nodes:
                    break
            current_frontier = next_frontier
            if len(visited) >= max_nodes:
                break

        return self.graph.subgraph(visited).copy()
