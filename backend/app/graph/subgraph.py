"""Graph topological and ego-network feature calculations."""

import math
import networkx as nx


def compute_topological_metrics(g: nx.MultiDiGraph, node_id: str) -> dict[str, float]:
    """Compute local topological metrics for a node."""
    if not g.has_node(node_id):
        return {
            "degree_total": 0.0,
            "degree_in": 0.0,
            "degree_out": 0.0,
            "fan_ratio": 0.0,
            "clustering_coef": 0.0,
            "ego_density": 0.0,
        }

    in_deg = float(g.in_degree(node_id))
    out_deg = float(g.out_degree(node_id))
    tot_deg = in_deg + out_deg
    fan_ratio = out_deg / (in_deg + 1.0)

    # Simple undirected view for clustering
    neighbors = set(g.predecessors(node_id)).union(g.successors(node_id))
    n_neighbors = len(neighbors)

    if n_neighbors < 2:
        clustering_coef = 0.0
        ego_density = 0.0
    else:
        # Count edges between neighbors
        sub = g.subgraph(neighbors)
        actual_edges = sub.number_of_edges()
        possible_edges = n_neighbors * (n_neighbors - 1)
        ego_density = actual_edges / possible_edges if possible_edges > 0 else 0.0
        clustering_coef = min(1.0, ego_density)

    return {
        "degree_total": tot_deg,
        "degree_in": in_deg,
        "degree_out": out_deg,
        "fan_ratio": round(fan_ratio, 4),
        "clustering_coef": round(clustering_coef, 4),
        "ego_density": round(ego_density, 4),
    }


def extract_ego_subgraph(
    g: nx.MultiDiGraph, target_id: str, radius: int = 2, max_nodes: int = 80
) -> nx.MultiDiGraph:
    """Extract ego-network subgraph around specified target node bounded by max_nodes."""
    if not g.has_node(target_id):
        return nx.MultiDiGraph()

    visited = {target_id}
    current_frontier = {target_id}

    for _ in range(radius):
        next_frontier = set()
        for node in current_frontier:
            neighbors = set(g.predecessors(node)).union(g.successors(node))
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

    return g.subgraph(visited).copy()

