"""Forensic graph endpoints for Cytoscape.js canvas."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.graph.engine import ForensicGraphEngine
from app.graph.serialization import to_cytoscape_json
from app.schemas.graph import GraphResponse

router = APIRouter(prefix="/graph", tags=["Forensic Graph Canvas"])


@router.get("", response_model=GraphResponse)
def get_global_graph(
    max_nodes: int = Query(100, ge=10, le=300),
    db: Session = Depends(get_db),
):
    """Retrieve global or sampled transaction graph payload formatted for Cytoscape.js."""
    engine = ForensicGraphEngine(db=db)
    engine.build_from_database(max_records=max_nodes * 2)
    return to_cytoscape_json(engine.graph, subgraph_type="global", max_nodes=max_nodes)


@router.get("/{identifier}", response_model=GraphResponse)
def get_ego_graph(
    identifier: str,
    radius: int = Query(2, ge=1, le=4),
    max_nodes: int = Query(80, ge=10, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve induced ego-subgraph centered around a specific entity, wallet, or TXID."""
    engine = ForensicGraphEngine(db=db)
    engine.build_from_database(max_records=1000)
    subgraph = engine.get_ego_subgraph(target_id=identifier, radius=radius, max_nodes=max_nodes)
    return to_cytoscape_json(subgraph, subgraph_type="ego", focus_id=identifier, max_nodes=max_nodes)
