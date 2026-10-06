"""Stress testing graph engine, Cytoscape serialization, and traversal bounds."""

import time
import random
import networkx as nx
import pytest
from app.graph.engine import ForensicGraphEngine
from app.graph.serialization import to_cytoscape_json
from app.graph.subgraph import extract_ego_subgraph


def test_graph_stress_1000_nodes_10000_edges():
    """Generates a dense heterogeneous graph (1,000 nodes, 10,000 edges) and benchmarks operations."""
    G = nx.MultiDiGraph()

    # 1. Create 1,000 nodes across node types
    node_types = ["WALLET", "TRANSACTION", "ENTITY", "IP", "ASN", "COUNTRY"]
    for i in range(1000):
        ntype = node_types[i % len(node_types)]
        G.add_node(
            f"node_{i}",
            type=ntype,
            risk=random.uniform(0, 100),
            amount=random.uniform(0.01, 50.0),
        )

    # 2. Add 10,000 edges
    edge_types = ["SPENT", "CREATED", "TRANSFERRED", "OBSERVED", "CLUSTERED_AS"]
    random.seed(42)
    for _ in range(10000):
        u = f"node_{random.randint(0, 999)}"
        v = f"node_{random.randint(0, 999)}"
        etype = random.choice(edge_types)
        G.add_edge(
            u,
            v,
            relationship=etype,
            amount=random.uniform(0.001, 10.0),
            confidence=random.uniform(0.5, 1.0),
        )

    assert G.number_of_nodes() == 1000
    assert G.number_of_edges() == 10000

    # Benchmark: Cytoscape Serialization
    t0 = time.time()
    response = to_cytoscape_json(G, max_nodes=500)
    serialization_time = time.time() - t0
    assert serialization_time < 0.5  # Must serialize within 500ms
    assert len(response.nodes) <= 500
    assert response.edge_count >= 0

    # Benchmark: Centrality and PageRank Computation
    t0 = time.time()
    pagerank = nx.pagerank(G, max_iter=50, weight=None)
    pr_time = time.time() - t0
    assert pr_time < 1.0  # Must calculate PageRank within 1 second
    assert len(pagerank) == 1000

    # Benchmark: Dense Ego Subgraph Extraction
    t0 = time.time()
    hub_node = "node_0"
    ego = extract_ego_subgraph(G, hub_node, radius=2, max_nodes=100)
    ego_time = time.time() - t0
    assert ego_time < 0.1  # Must extract within 100ms
    assert ego.number_of_nodes() <= 100


def test_graph_stress_5000_nodes_scaling():
    """Larger scale test: 5,000 nodes with cyclic clusters to detect recursion/leak issues."""
    G = nx.MultiDiGraph()
    for i in range(5000):
        G.add_node(f"n_{i}", node_type="WALLET", risk_score=float(i % 100))

    # Dense ring and cross-cluster edges
    for i in range(5000):
        G.add_edge(f"n_{i}", f"n_{(i + 1) % 5000}", relationship_type="TRANSFERRED", amount_btc=1.0)
        if i % 10 == 0:
            # Hub cross links
            G.add_edge(f"n_{i}", f"n_{(i * 7) % 5000}", relationship_type="SPENT", amount_btc=5.0)

    assert G.number_of_nodes() == 5000
    assert G.number_of_edges() >= 5500

    # Verify no infinite loop or recursion in bounded ego traversal
    ego = extract_ego_subgraph(G, "n_0", radius=3, max_nodes=150)
    assert ego.number_of_nodes() <= 150
