"""Cytoscape.js serialization utility for forensic graphs."""

import networkx as nx
from app.schemas.graph import CytoscapeNode, CytoscapeNodeData, CytoscapeEdge, CytoscapeEdgeData, GraphResponse


def to_cytoscape_json(
    g: nx.MultiDiGraph,
    subgraph_type: str = "global",
    focus_id: str | None = None,
    max_nodes: int = 150,
) -> GraphResponse:
    """Serialize a NetworkX MultiDiGraph into Cytoscape JSON schema."""
    nodes: list[CytoscapeNode] = []
    edges: list[CytoscapeEdge] = []

    # Limit nodes to protect frontend performance
    node_list = list(g.nodes())[:max_nodes]
    selected_nodes = set(node_list)

    for node_id in node_list:
        data = g.nodes[node_id]
        node_type = data.get("type", "UNKNOWN")
        label = data.get("label", str(node_id))
        risk = float(data.get("risk", 0.0))
        confidence = float(data.get("confidence", 1.0))
        amount = float(data.get("amount", 0.0))

        nodes.append(
            CytoscapeNode(
                data=CytoscapeNodeData(
                    id=str(node_id),
                    label=str(label),
                    type=node_type,
                    risk=risk,
                    confidence=confidence,
                    amount=amount,
                    cluster_id=data.get("cluster_type"),
                    sublabel=data.get("alert_level") or data.get("timestamp"),
                    metadata={k: v for k, v in data.items() if k not in ("type", "label", "risk", "amount")},
                )
            )
        )

    for u, v, k, data in g.edges(keys=True, data=True):
        if u in selected_nodes and v in selected_nodes:
            edge_id = f"{u}_{v}_{k}"
            rel = data.get("relationship", "TRANSFERRED")
            amt = float(data.get("amount", 0.0))
            conf = float(data.get("confidence", 1.0))
            prov = data.get("provenance", "OBSERVED")
            ts = data.get("timestamp")

            edges.append(
                CytoscapeEdge(
                    data=CytoscapeEdgeData(
                        id=edge_id,
                        source=str(u),
                        target=str(v),
                        relationship=rel,
                        amount=amt,
                        timestamp=ts,
                        confidence=conf,
                        provenance=prov,
                    )
                )
            )

    return GraphResponse(
        nodes=nodes,
        edges=edges,
        node_count=len(nodes),
        edge_count=len(edges),
        subgraph_type=subgraph_type,
        focus_id=focus_id,
    )
