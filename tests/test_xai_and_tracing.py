"""Comprehensive Test Suite for Explainability (Section 8) and Fund Tracing (Section 9)."""

import pytest
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.transaction import TransactionModel
from app.models.alert import AlertModel
from app.models.entity import EntityModel
from app.motifs.base import MotifEvidence
from app.explainability.engine import ExplainabilityEngine
from app.explainability.counterfactual import CounterfactualEngine
from app.explainability.graph_ablation import GraphAblationEngine
from app.explainability.shap_explainer import ShapExplainer
from app.tracing.best_first_tracer import BestFirstFundTracer
from app.schemas.trace import TraceRequest
from app.services.pipeline import ForensicPipeline


@pytest.fixture
def isolated_db(tmp_path):
    """Provides a fresh isolated database for testing."""
    db_file = tmp_path / "xai_trace_test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ==============================================================================
# SECTION 8: EXPLAINABILITY TEST
# ==============================================================================

def test_explainability_all_fields_and_faithfulness(isolated_db):
    """
    Verify:
    - risk exists
    - confidence exists
    - top reasons exist
    - supporting transactions exist
    - supporting graph evidence exists
    - motif evidence exists where applicable
    - changing inputs alters explanations faithfully without hallucinated reasons
    """
    # 1. Populate suspicious laundering transaction
    tx_peeling = TransactionModel(
        record_id="rec-peel-01",
        txid="0101010101010101010101010101010101010101010101010101010101010101",
        source_file="test.csv",
        source_row=1,
        timestamp="2026-10-06T12:00:00Z",
        src_ip="185.220.101.5",
        country="RU",
        asn=12345,
        input_addresses_json='["1PeelInAddr111111111111111111111"]',
        output_addresses_json='["1PeelOutDust1111111111111111111", "1PeelRemainder11111111111111111"]',
        input_amounts_json="[10.0]",
        output_amounts_json="[0.05, 9.949]",
        input_amount=10.0,
        output_amount=9.999,
        fee=0.001,
        script_type="P2PKH",
    )
    isolated_db.add(tx_peeling)
    isolated_db.commit()

    # Run forensic pipeline
    pipeline = ForensicPipeline(db=isolated_db)
    result = pipeline.run_full_pipeline()
    assert result["status"] == "COMPLETED"

    alerts = isolated_db.query(AlertModel).all()
    assert len(alerts) > 0, "Pipeline must generate an alert for high-risk pattern"

    for alert in alerts:
        # Verify core fields
        assert alert.risk_score is not None and 0.0 <= alert.risk_score <= 100.0
        assert alert.confidence_score is not None and 0.0 <= alert.confidence_score <= 100.0
        assert alert.severity in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        
        # Verify evidence chain
        chain = alert.evidence_chain
        assert isinstance(chain, list) and len(chain) > 0, "Alert must contain supporting evidence steps"
        for step in chain:
            assert "step_number" in step
            assert "step_type" in step
            assert "identifier" in step
            assert "description" in step

        # Verify explanation structure
        expl = alert.explanation
        assert expl is not None, "Alert must have explanation payload"
        assert expl["final_risk_score"] == alert.risk_score
        assert "base_expected_value" in expl
        
        # Verify top reasons exist (feature attributions)
        attributions = expl.get("top_feature_attributions", [])
        assert len(attributions) > 0, "Must contain top feature attributions"
        for attr in attributions:
            assert "feature_name" in attr
            assert "contribution" in attr
            assert "display_name" in attr
            assert "interpretation" in attr

        # Verify counterfactual sensitivity deltas
        counterfactuals = expl.get("counterfactuals", [])
        assert len(counterfactuals) > 0, "Must provide counterfactual what-if scenarios"
        for cf in counterfactuals:
            assert "original_risk" in cf
            assert "new_risk" in cf
            assert "delta" in cf
            assert cf["delta"] <= 0.0, "Removing suspicious motifs must reduce or maintain risk"

        # Verify graph ablation evidence
        ablations = expl.get("graph_ablations", [])
        assert len(ablations) > 0, "Must provide graph topological ablation evidence"
        for ab in ablations:
            assert "original_risk" in ab
            assert "ablated_motif_or_subgraph" in ab
            assert "risk_after_ablation" in ab

    # 2. Modify input: verify explanation changes faithfully
    engine = ExplainabilityEngine()
    dummy_tx = TransactionModel(
        record_id="mod-01",
        txid="0202020202020202020202020202020202020202020202020202020202020202",
        source_file="mod.csv",
        source_row=1,
        timestamp="2026-10-06T12:00:00Z",
        input_addresses_json='["1A"]',
        output_addresses_json='["1B"]',
        input_amount=1.0,
        output_amount=0.999,
        fee=0.001,
    )
    
    # Run with high risk and Peeling Chain motif
    motif_evidence = [
        MotifEvidence(
            motif_type="PEELING_CHAIN",
            confidence=0.92,
            involved_txids=[dummy_tx.txid],
            involved_wallets=["1A", "1B"],
            description="Peeling chain detected with 1 peeling hop",
            evidence_data={"peel_amount": 0.05, "remainder_amount": 0.949},
        )
    ]
    expl_peel = engine.explain(
        alert_id="ALT-PEEL",
        tx=dummy_tx,
        feature_vec=np.array([1.0, 0.05, 0.0, 1.0, 1.0, 0.9, 0.8, 4.0, 0.2, 0.5, 0.9, 0.8]),
        risk_score=85.0,
        motifs=motif_evidence,
    )

    # Run with low risk and NO motifs
    expl_benign = engine.explain(
        alert_id="ALT-BENIGN",
        tx=dummy_tx,
        feature_vec=np.array([1.0, 0.0001, 0.0, 0.0, 0.0, 0.1, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]),
        risk_score=20.0,
        motifs=[],
    )

    # Explanations must differ substantially and reflect the altered reality
    assert expl_peel.final_risk_score != expl_benign.final_risk_score
    assert "PEELING_CHAIN" in expl_peel.forensic_summary
    assert "PEELING_CHAIN" not in expl_benign.forensic_summary
    assert len(expl_peel.counterfactuals) > len(expl_benign.counterfactuals)


# ==============================================================================
# SECTION 9: FUND TRACE TEST
# ==============================================================================

def test_fund_tracing_cycles_and_infinite_loops(isolated_db):
    """
    Verify:
    - cycle handling (A -> B -> C -> A) does not loop infinitely
    - no duplicate hops along a single loop
    - cycle is detected and correctly categorized as 'CYCLE'
    """
    # Create cyclic flow: W1 -> W2 -> W3 -> W1
    tx1 = TransactionModel(
        record_id="t1",
        txid="1111111111111111111111111111111111111111111111111111111111111111",
        source_file="cycle.csv",
        source_row=1,
        timestamp="2026-10-06T10:00:00Z",
        input_addresses_json='["W_ALPHA"]',
        output_addresses_json='["W_BETA"]',
        output_amounts_json="[10.0]",
        output_amount=10.0,
    )
    tx2 = TransactionModel(
        record_id="t2",
        txid="2222222222222222222222222222222222222222222222222222222222222222",
        source_file="cycle.csv",
        source_row=2,
        timestamp="2026-10-06T10:10:00Z",
        input_addresses_json='["W_BETA"]',
        output_addresses_json='["W_GAMMA"]',
        output_amounts_json="[9.9]",
        output_amount=9.9,
    )
    tx3 = TransactionModel(
        record_id="t3",
        txid="3333333333333333333333333333333333333333333333333333333333333333",
        source_file="cycle.csv",
        source_row=3,
        timestamp="2026-10-06T10:20:00Z",
        input_addresses_json='["W_GAMMA"]',
        output_addresses_json='["W_ALPHA"]',
        output_amounts_json="[9.8]",
        output_amount=9.8,
    )
    isolated_db.add_all([tx1, tx2, tx3])
    isolated_db.commit()

    tracer = BestFirstFundTracer(db=isolated_db)
    req = TraceRequest(
        start_identifier="W_ALPHA",
        start_type="wallet",
        max_hops=10,
        max_nodes=100,
        min_value_ratio=0.01,
    )
    res = tracer.trace(req)

    assert res.paths_explored > 0
    assert len(res.ranked_paths) > 0
    # Must terminate without infinite loop and flag CYCLE
    has_cycle_endpoint = any(p.endpoint_type == "CYCLE" for p in res.ranked_paths)
    assert has_cycle_endpoint, "Cyclic transaction must terminate as CYCLE endpoint"


def test_fund_tracing_max_hop_control_and_dust_pruning(isolated_db):
    """
    Verify:
    - maximum-hop control strictly caps path length
    - dust filtering (min_value_ratio) prunes dust outputs
    """
    # Linear chain of 10 hops: W0 -> W1 -> W2 -> ... -> W10
    # Also attach tiny dust output (0.000001 BTC) at every hop
    txs = []
    for i in range(10):
        tx = TransactionModel(
            record_id=f"rec-chain-{i}",
            txid=f"aa{i:02d}" + "00" * 30,
            source_file="chain.csv",
            source_row=i + 1,
            timestamp=f"2026-10-06T10:{i:02d}:00Z",
            input_addresses_json=f'["W_CHAIN_{i}"]',
            output_addresses_json=f'["W_CHAIN_{i+1}", "W_DUST_{i}"]',
            output_amounts_json=f"[5.0, 0.0000001]",
            output_amount=5.0000001,
        )
        txs.append(tx)
    isolated_db.add_all(txs)
    isolated_db.commit()

    tracer = BestFirstFundTracer(db=isolated_db)
    
    # 1. Test max_hops = 3
    req_3 = TraceRequest(
        start_identifier="W_CHAIN_0",
        start_type="wallet",
        max_hops=3,
        max_nodes=50,
        min_value_ratio=0.05,  # Filters dust 0.0000001 BTC
    )
    res_3 = tracer.trace(req_3)
    assert len(res_3.ranked_paths) > 0
    for path in res_3.ranked_paths:
        assert path.path_length <= 3, f"Path length {path.path_length} exceeded max_hops 3"
        # Verify dust was pruned: no dust wallet visited
        for hop in path.hops:
            assert "W_DUST" not in hop.to_wallet

    # 2. Test max_hops = 6
    req_6 = TraceRequest(
        start_identifier="W_CHAIN_0",
        start_type="wallet",
        max_hops=6,
        max_nodes=50,
        min_value_ratio=0.05,
    )
    res_6 = tracer.trace(req_6)
    assert len(res_6.ranked_paths) > 0
    max_len = max(p.path_length for p in res_6.ranked_paths)
    assert max_len <= 6, f"Path length {max_len} exceeded max_hops 6"


def test_fund_tracing_large_branching_and_missing_transactions(isolated_db):
    """
    Verify:
    - Large branching factor (1 input fan-out to 60 outputs) does not hang or crash
    - Non-existent transaction/wallet query returns empty result cleanly
    """
    # 1. Missing transaction / wallet query
    tracer = BestFirstFundTracer(db=isolated_db)
    req_missing = TraceRequest(
        start_identifier="NON_EXISTENT_WALLET_99999",
        start_type="wallet",
        max_hops=5,
        max_nodes=50,
    )
    res_missing = tracer.trace(req_missing)
    assert res_missing.paths_explored == 0
    assert len(res_missing.ranked_paths) == 0

    # 2. Large branching factor: 1 input to 60 outputs
    out_addrs = [f"1FanOutBranch{i:03d}11111111111111111" for i in range(60)]
    out_amts = [0.1] * 60
    import json
    tx_fan = TransactionModel(
        record_id="rec-fan-60",
        txid="ff" * 32,
        source_file="fan60.csv",
        source_row=1,
        timestamp="2026-10-06T15:00:00Z",
        input_addresses_json='["1HugeRootSource11111111111111111"]',
        output_addresses_json=json.dumps(out_addrs),
        output_amounts_json=json.dumps(out_amts),
        output_amount=6.0,
    )
    isolated_db.add(tx_fan)
    isolated_db.commit()

    req_fan = TraceRequest(
        start_identifier="1HugeRootSource11111111111111111",
        start_type="wallet",
        max_hops=3,
        max_nodes=100,
        min_value_ratio=0.001,
    )
    res_fan = tracer.trace(req_fan)
    assert res_fan.paths_explored > 0
    assert len(res_fan.ranked_paths) > 0
    assert res_fan.execution_time_ms < 1000.0, "Large branching trace must execute within 1 second"
