"""Graph topological feature calculations."""

from typing import Any
import networkx as nx
from app.models.transaction import TransactionModel
from app.graph.subgraph import compute_topological_metrics


def extract_graph_features(tx: TransactionModel, g: nx.MultiDiGraph) -> dict[str, dict[str, Any]]:
    """Extract graph structural and ego-net metrics for a transaction."""
    tx_node_id = f"tx:{tx.txid}"
    metrics = compute_topological_metrics(g, tx_node_id)

    # In-degree, Out-degree, Ego density
    tot_deg = metrics["degree_total"]
    fan_ratio = metrics["fan_ratio"]
    density = metrics["ego_density"]
    clustering = metrics["clustering_coef"]

    return {
        "graph_degree_total": {
            "name": "graph_degree_total",
            "value": float(tot_deg),
            "normalized": min(1.0, round(tot_deg / 50.0, 4)),
            "source": "graph",
            "description": "Total directed degree in transaction graph",
        },
        "graph_fan_ratio": {
            "name": "graph_fan_ratio",
            "value": float(fan_ratio),
            "normalized": min(1.0, round(fan_ratio / 10.0, 4)),
            "source": "graph",
            "description": "Ratio of outgoing to incoming edges in ego-subgraph",
        },
        "graph_ego_density": {
            "name": "graph_ego_density",
            "value": float(density),
            "normalized": float(density),
            "source": "graph",
            "description": "Edge density among 1-hop topological neighbors",
        },
        "graph_clustering_coefficient": {
            "name": "graph_clustering_coefficient",
            "value": float(clustering),
            "normalized": float(clustering),
            "source": "graph",
            "description": "Local clustering coefficient of transaction node",
        },
    }
