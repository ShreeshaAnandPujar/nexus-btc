"""Value-Aware Best-First Forward and Backward Fund Tracer."""

import heapq
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.transaction import TransactionModel
from app.models.entity import EntityModel
from app.schemas.trace import TraceRequest, TraceResponse, TracePath, TraceHop, EndpointType
from app.tracing.classifier import EndpointClassifier


class BestFirstFundTracer:
    """Explores money flow branches in descending order of BTC transfer value."""

    def __init__(self, db: Session | None = None):
        self._db = db
        self.classifier = EndpointClassifier()

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def trace(self, req: TraceRequest) -> TraceResponse:
        start_time = time.time()
        start_wallets = self._resolve_start_wallets(req.start_type, req.start_identifier)

        if not start_wallets:
            return TraceResponse(
                target=req.start_identifier,
                target_type=req.start_type,
                paths_explored=0,
                nodes_visited=0,
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                ranked_paths=[],
                endpoints_summary={},
            )

        # Index transactions by input address for fast forward lookup
        all_txs = self.db.query(TransactionModel).all()
        tx_by_input: dict[str, list[TransactionModel]] = {}
        for tx in all_txs:
            for w in tx.input_addresses:
                if w and w != "COINBASE":
                    tx_by_input.setdefault(w, []).append(tx)

        # Priority Queue: (-amount, current_wallet, [TraceHop], visited_set)
        pq: list[tuple[float, str, list[TraceHop], list[str]]] = []

        # Seed the queue
        if req.start_type.lower() == "txid":
            seed_tx = self.db.query(TransactionModel).filter(TransactionModel.txid == req.start_identifier).first()
            if seed_tx:
                in_w = seed_tx.input_addresses[0] if seed_tx.input_addresses else "COINBASE"
                for idx, out_w in enumerate(seed_tx.output_addresses):
                    amt = seed_tx.output_amounts[idx] if idx < len(seed_tx.output_amounts) else 0.0
                    hop = TraceHop(
                        hop_index=1,
                        txid=seed_tx.txid,
                        from_wallet=in_w,
                        to_wallet=out_w,
                        amount_btc=amt,
                        timestamp=seed_tx.timestamp,
                        hop_risk=seed_tx.risk_score,
                    )
                    heapq.heappush(pq, (-amt, out_w, [hop], [in_w, out_w]))
        else:
            for w in start_wallets:
                outgoing = tx_by_input.get(w, [])
                for tx in outgoing:
                    for idx, out_w in enumerate(tx.output_addresses):
                        amt = tx.output_amounts[idx] if idx < len(tx.output_amounts) else 0.0
                        hop = TraceHop(
                            hop_index=1,
                            txid=tx.txid,
                            from_wallet=w,
                            to_wallet=out_w,
                            amount_btc=amt,
                            timestamp=tx.timestamp,
                            hop_risk=tx.risk_score,
                        )
                        heapq.heappush(pq, (-amt, out_w, [hop], [w, out_w]))

        completed_paths: list[TracePath] = []
        visited_nodes: set[str] = set(start_wallets)
        paths_explored = 0

        # Initial reference volume
        initial_vol = max([abs(p[0]) for p in pq]) if pq else 1.0
        min_threshold = initial_vol * req.min_value_ratio

        # Prune initial dust entries below threshold
        pq = [item for item in pq if -item[0] >= min_threshold]
        heapq.heapify(pq)

        while pq and len(visited_nodes) < req.max_nodes:
            neg_amt, current_w, hops, path_wallets = heapq.heappop(pq)
            amt = -neg_amt
            visited_nodes.add(current_w)
            paths_explored += 1

            # Termination checks
            if len(hops) >= req.max_hops:
                endpoint = self.classifier.classify_endpoint(
                    current_w, tx_by_input.get(current_w, []), horizon_reached=True
                )
                completed_paths.append(self._create_path(hops, endpoint))
                continue

            outgoing = tx_by_input.get(current_w, [])
            if not outgoing:
                # Dormant UTXO
                endpoint = self.classifier.classify_endpoint(
                    current_w, [], horizon_reached=False
                )
                completed_paths.append(self._create_path(hops, endpoint))
                continue

            # Branch forward
            branched = False
            for tx in outgoing:
                for idx, next_w in enumerate(tx.output_addresses):
                    next_amt = tx.output_amounts[idx] if idx < len(tx.output_amounts) else 0.0

                    if next_amt < min_threshold:
                        continue  # Prune negligible value dust

                    is_cycle = next_w in path_wallets
                    next_hop = TraceHop(
                        hop_index=len(hops) + 1,
                        txid=tx.txid,
                        from_wallet=current_w,
                        to_wallet=next_w,
                        amount_btc=next_amt,
                        timestamp=tx.timestamp,
                        hop_risk=tx.risk_score,
                    )
                    new_hops = hops + [next_hop]

                    if is_cycle:
                        endpoint = "CYCLE"
                        completed_paths.append(self._create_path(new_hops, endpoint))
                        branched = True
                        continue

                    heapq.heappush(pq, (-next_amt, next_w, new_hops, path_wallets + [next_w]))
                    branched = True

            if not branched:
                endpoint = self.classifier.classify_endpoint(current_w, outgoing)
                completed_paths.append(self._create_path(hops, endpoint))

        # Sort paths by total traced BTC descending
        completed_paths.sort(key=lambda p: p.total_btc_traced, reverse=True)
        top_paths = completed_paths[:15]

        # Summarize endpoints
        summary: dict[str, int] = {}
        for p in completed_paths:
            summary[p.endpoint_type] = summary.get(p.endpoint_type, 0) + 1

        exec_ms = round((time.time() - start_time) * 1000, 2)
        return TraceResponse(
            target=req.start_identifier,
            target_type=req.start_type,
            paths_explored=paths_explored,
            nodes_visited=len(visited_nodes),
            execution_time_ms=exec_ms,
            ranked_paths=top_paths,
            endpoints_summary=summary,
        )

    def _resolve_start_wallets(self, start_type: str, identifier: str) -> list[str]:
        if start_type == "wallet":
            return [identifier]
        if start_type == "txid":
            tx = self.db.query(TransactionModel).filter(TransactionModel.txid == identifier).first()
            if tx:
                return [w for w in tx.output_addresses if w]
            return []
        if start_type == "entity":
            ent = self.db.query(EntityModel).filter(EntityModel.entity_id == identifier).first()
            if ent:
                return ent.member_wallets
        return [identifier]

    def _create_path(self, hops: list[TraceHop], endpoint: EndpointType) -> TracePath:
        import uuid
        tot_btc = hops[0].amount_btc if hops else 0.0
        last_w = hops[-1].to_wallet if hops else "UNKNOWN"
        cum_risk = round(sum(h.hop_risk for h in hops) / len(hops), 2) if hops else 0.0

        # Duration
        duration_s = 0.0
        if len(hops) > 1:
            try:
                from datetime import datetime
                t0 = datetime.fromisoformat(hops[0].timestamp.replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(hops[-1].timestamp.replace("Z", "+00:00"))
                duration_s = abs((t1 - t0).total_seconds())
            except Exception:
                pass

        return TracePath(
            path_id=f"PATH-{uuid.uuid4().hex[:8].upper()}",
            hops=hops,
            total_btc_traced=round(tot_btc, 8),
            endpoint_wallet=last_w,
            endpoint_type=endpoint,
            path_length=len(hops),
            duration_seconds=duration_s,
            cumulative_risk=cum_risk,
        )
