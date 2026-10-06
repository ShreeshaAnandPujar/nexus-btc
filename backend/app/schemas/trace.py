"""Schemas for Value-Aware Best-First Fund Tracing."""

from pydantic import BaseModel, Field
from typing import Literal

EndpointType = Literal["SERVICE", "DORMANT", "MIXER_LIKE", "HORIZON", "CYCLE", "UNKNOWN"]


class TraceRequest(BaseModel):
    start_type: Literal["wallet", "txid", "entity"]
    start_identifier: str
    direction: Literal["forward", "backward"] = "forward"
    max_hops: int = 10
    max_nodes: int = 100
    min_value_ratio: float = 0.01  # Terminate branch below 1% of initial volume


class TraceHop(BaseModel):
    hop_index: int
    txid: str
    from_wallet: str
    to_wallet: str
    amount_btc: float
    timestamp: str
    hop_risk: float
    stop_reason: EndpointType | None = None


class TracePath(BaseModel):
    path_id: str
    hops: list[TraceHop]
    total_btc_traced: float
    endpoint_wallet: str
    endpoint_type: EndpointType
    path_length: int
    duration_seconds: float
    cumulative_risk: float


class TraceResponse(BaseModel):
    target: str
    target_type: str
    paths_explored: int
    nodes_visited: int
    execution_time_ms: float
    ranked_paths: list[TracePath]
    endpoints_summary: dict[str, int]
