"""Unit tests for laundering motifs, fund tracing, and explainability."""

import json
import numpy as np
import pytest
from app.models.transaction import TransactionModel
from app.motifs.peeling_chain import PeelingChainDetector
from app.motifs.coinjoin import CoinJoinDetector
from app.motifs.fan_in_out import FanInOutDetector
from app.tracing.classifier import EndpointClassifier
from app.correlation.probabilistic import ProbabilisticCorrelator
from app.correlation.geo_asn import GeoEnricher
from app.explainability.counterfactual import CounterfactualEngine
from app.explainability.shap_explainer import ShapExplainer
from app.features.engine import FEATURE_COLUMNS


def test_peeling_chain_detection():
    detector = PeelingChainDetector()
    tx = TransactionModel(
        record_id="rec_1",
        source_file="test.csv",
        txid="0" * 64,
        timestamp="2026-03-01T12:00:00Z",
        input_addresses_json=json.dumps(["wallet_origin"]),
        output_addresses_json=json.dumps(["wallet_peeled", "wallet_change"]),
        input_amounts_json=json.dumps([10.0]),
        output_amounts_json=json.dumps([0.3, 9.699]),  # 3% peel, 97% change
        input_amount=10.0,
        output_amount=9.999,
        fee=0.001,
    )
    res = detector.detect_transaction(tx)
    assert res is not None
    assert res.motif_type == "PEELING_CHAIN"
    assert res.confidence >= 0.80


def test_coinjoin_detection():
    detector = CoinJoinDetector()
    tx = TransactionModel(
        record_id="rec_2",
        source_file="test.csv",
        txid="1" * 64,
        timestamp="2026-03-01T12:00:00Z",
        input_addresses_json=json.dumps(["in1", "in2", "in3", "in4"]),
        output_addresses_json=json.dumps(["out1", "out2", "out3", "change"]),
        input_amounts_json=json.dumps([0.11, 0.12, 0.11, 0.13]),
        output_amounts_json=json.dumps([0.10, 0.10, 0.10, 0.169]),  # 3 equal 0.10 outputs
        input_amount=0.47,
        output_amount=0.469,
        fee=0.001,
    )
    res = detector.detect_transaction(tx)
    assert res is not None
    assert res.motif_type == "MIXING_LIKE"


def test_fan_in_and_fan_out():
    detector = FanInOutDetector()
    # Fan in
    tx_fan_in = TransactionModel(
        record_id="rec_3",
        source_file="test.csv",
        txid="2" * 64,
        timestamp="2026-03-01T12:00:00Z",
        input_addresses_json=json.dumps(["in1", "in2", "in3", "in4", "in5"]),
        output_addresses_json=json.dumps(["dest1"]),
        input_amounts_json=json.dumps([1.0] * 5),
        output_amounts_json=json.dumps([4.999]),
        input_amount=5.0,
        output_amount=4.999,
        fee=0.001,
    )
    motifs = detector.detect_transaction(tx_fan_in)
    assert any(m.motif_type in ("FAN_IN", "CONSOLIDATION") for m in motifs)

    # Fan out
    tx_fan_out = TransactionModel(
        record_id="rec_4",
        source_file="test.csv",
        txid="3" * 64,
        timestamp="2026-03-01T12:00:00Z",
        input_addresses_json=json.dumps(["in1"]),
        output_addresses_json=json.dumps([f"out{i}" for i in range(8)]),
        input_amounts_json=json.dumps([8.0]),
        output_amounts_json=json.dumps([0.999] * 8),
        input_amount=8.0,
        output_amount=7.992,
        fee=0.008,
    )
    motifs_out = detector.detect_transaction(tx_fan_out)
    assert any(m.motif_type in ("FAN_OUT", "RAPID_SPLIT") for m in motifs_out)


def test_probabilistic_correlation():
    correlator = ProbabilisticCorrelator()
    res = correlator.correlate(
        tx_timestamp="2026-03-01T12:00:00Z",
        net_timestamp="2026-03-01T12:00:01Z",  # 1s delta
        ip_observation_count=5,
        target_ip="198.51.100.1",
        asn=13335,
        country="US",
    )
    assert res.association_score >= 70.0
    assert res.association_confidence >= 70.0
    assert len(res.association_reasons) >= 3


def test_geoip_graceful_degradation():
    enricher = GeoEnricher(db_path=None)
    res = enricher.lookup("1.1.1.1")
    assert res.available is False
    assert "Geo enrichment unavailable" in res.status_message
    assert res.country == "UNKNOWN"


def test_counterfactual_engine():
    from app.motifs.base import MotifEvidence
    m = MotifEvidence(motif_type="PEELING_CHAIN", confidence=0.90)
    cf_results = CounterfactualEngine.generate_counterfactuals(
        original_risk=92.0,
        motifs=[m],
        tx_volume_btc=5.0,
        fan_ratio=0.1,
    )
    assert len(cf_results) >= 1
    # Check that delta is negative (risk reduced)
    assert cf_results[0].delta < 0
    assert cf_results[0].new_risk < 92.0


def test_shap_deterministic_fallback():
    explainer = ShapExplainer(tree_estimator=None)
    x_vec = np.array([5.0, 0.001, 2.0, 5.0, 2.5, 0.4, 0.0, 7.0, 2.5, 0.2, 0.1, 10.0, 1.0, 1.0])
    attributions = explainer.explain_sample(x_vec, base_value=18.0, final_risk=80.0)
    assert len(attributions) == len(FEATURE_COLUMNS)
    assert attributions[0].contribution != 0.0
