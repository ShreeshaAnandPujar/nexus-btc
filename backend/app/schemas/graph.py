"""Cytoscape graph schemas for forensic visual canvas."""

from pydantic import BaseModel, Field
from typing import Any


class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    type: str  # WALLET, TRANSACTION, IP, ENTITY, ASN, COUNTRY
    risk: float = 0.0
    confidence: float = 1.0
    amount: float = 0.0
    cluster_id: str | None = None
    sublabel: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData


class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    relationship: str  # OBSERVED, SPENT, CREATED, TRANSFERRED, CLUSTERED_AS, ASSOCIATED_WITH, LOCATED_IN
    amount: float = 0.0
    timestamp: str | None = None
    confidence: float = 1.0
    provenance: str = "OBSERVED"  # OBSERVED, INFERRED, PROBABILISTIC


class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData


class GraphResponse(BaseModel):
    nodes: list[CytoscapeNode] = Field(default_factory=list)
    edges: list[CytoscapeEdge] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    subgraph_type: str = "global"  # ego, cluster, motif, global
    focus_id: str | None = None
