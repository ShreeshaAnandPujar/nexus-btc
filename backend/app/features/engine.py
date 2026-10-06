"""Unified Feature Engineering Engine providing multi-view representations."""

from typing import Any
import numpy as np
import networkx as nx
from app.models.transaction import TransactionModel
from app.features.transaction_view import extract_transaction_features
from app.features.graph_view import extract_graph_features
from app.features.network_view import extract_network_features

FEATURE_COLUMNS = [
    "tx_total_volume_btc",
    "tx_fee_ratio",
    "tx_input_count",
    "tx_output_count",
    "tx_fan_ratio",
    "tx_output_gini",
    "tx_address_reuse",
    "graph_degree_total",
    "graph_fan_ratio",
    "graph_ego_density",
    "graph_clustering_coefficient",
    "net_ip_frequency",
    "net_telemetry_completeness",
    "net_asn_present",
]


class FeatureEngine:
    """Computes and normalizes multi-view behavioral and structural features."""

    def __init__(self):
        self.feature_columns = FEATURE_COLUMNS

    def extract_all_features(
        self,
        tx: TransactionModel,
        g: nx.MultiDiGraph | None = None,
        ip_freq_map: dict[str, int] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Extract all multi-view features with rich forensic metadata."""
        if g is None:
            g = nx.MultiDiGraph()

        tx_feats = extract_transaction_features(tx)
        graph_feats = extract_graph_features(tx, g)
        net_feats = extract_network_features(tx, ip_freq_map)

        all_feats = {}
        all_feats.update(tx_feats)
        all_feats.update(graph_feats)
        all_feats.update(net_feats)
        return all_feats

    def extract_vector(
        self,
        tx: TransactionModel,
        g: nx.MultiDiGraph | None = None,
        ip_freq_map: dict[str, int] | None = None,
    ) -> np.ndarray:
        """Extract standardized 1D float array for ML model consumption."""
        feat_dict = self.extract_all_features(tx, g, ip_freq_map)
        vec = []
        for col in self.feature_columns:
            if col in feat_dict:
                vec.append(float(feat_dict[col]["value"]))
            else:
                vec.append(0.0)
        return np.array(vec, dtype=np.float64)
