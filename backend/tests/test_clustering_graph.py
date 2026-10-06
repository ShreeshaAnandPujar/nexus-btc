"""Unit tests for entity clustering and graph engine."""

import networkx as nx
import pytest
from app.clustering.union_find import UnionFind
from app.clustering.hdbscan_clustering import BehavioralClusterer
from app.graph.engine import ForensicGraphEngine
from app.graph.serialization import to_cytoscape_json
from app.graph.subgraph import compute_topological_metrics


def test_union_find_clustering():
    uf = UnionFind()
    # Union a, b, c
    uf.union("wallet_1", "wallet_2")
    uf.union("wallet_2", "wallet_3")

    # Union d, e
    uf.union("wallet_4", "wallet_5")

    assert uf.find("wallet_1") == uf.find("wallet_3")
    assert uf.find("wallet_1") != uf.find("wallet_4")
    assert uf.cluster_size("wallet_1") == 3
    assert uf.cluster_size("wallet_4") == 2

    clusters = uf.get_clusters()
    assert len(clusters) == 2


def test_behavioral_clustering():
    bc = BehavioralClusterer(min_cluster_size=2)
    profiles = {
        "w1": {"tx_count": 100, "vol_sent": 50.0, "vol_recv": 50.0, "avg_fee": 0.001, "reuse_rate": 0.8},
        "w2": {"tx_count": 105, "vol_sent": 52.0, "vol_recv": 49.0, "avg_fee": 0.001, "reuse_rate": 0.82},
        "w3": {"tx_count": 1, "vol_sent": 0.01, "vol_recv": 0.01, "avg_fee": 0.0001, "reuse_rate": 0.0},
        "w4": {"tx_count": 2, "vol_sent": 0.02, "vol_recv": 0.01, "avg_fee": 0.0001, "reuse_rate": 0.0},
    }
    clusters = bc.cluster_wallets(profiles)
    assert isinstance(clusters, dict)


def test_graph_serialization_cytoscape():
    g = nx.MultiDiGraph()
    g.add_node("wallet:1A1z", type="WALLET", label="1A1z", risk=10.0)
    g.add_node("tx:tx01", type="TRANSACTION", label="tx01", risk=85.0, amount=1.5)
    g.add_edge("wallet:1A1z", "tx:tx01", relationship="SPENT", amount=1.5, provenance="OBSERVED")

    resp = to_cytoscape_json(g, subgraph_type="ego", focus_id="tx:tx01")
    assert resp.node_count == 2
    assert resp.edge_count == 1
    assert resp.nodes[0].data.id in ("wallet:1A1z", "tx:tx01")
    assert resp.edges[0].data.relationship == "SPENT"


def test_topological_metrics():
    g = nx.MultiDiGraph()
    g.add_node("tx:test")
    g.add_node("wallet:w1")
    g.add_node("wallet:w2")
    g.add_edge("wallet:w1", "tx:test")
    g.add_edge("tx:test", "wallet:w2")

    metrics = compute_topological_metrics(g, "tx:test")
    assert metrics["degree_in"] == 1.0
    assert metrics["degree_out"] == 1.0
    assert metrics["degree_total"] == 2.0
