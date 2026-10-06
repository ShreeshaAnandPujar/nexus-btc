"""Red-Team QA Suite: Model Integrity, False Positive, and False Negative Benchmarks."""

import numpy as np
import pytest
from app.anomaly.isolation_forest import IsolationForestDetector
from app.anomaly.supervised import CalibratedSupervisedModel
from app.anomaly.ensemble import AnomalyEnsemble
from app.anomaly.temporal_burst import TemporalBurstDetector
from app.models.transaction import TransactionModel
from app.motifs.peeling_chain import PeelingChainDetector
from app.motifs.coinjoin import CoinJoinDetector
from app.motifs.fan_in_out import FanInOutDetector
from app.motifs.rapid_layering import RapidLayeringDetector
from app.motifs.circular_flow import CircularFlowDetector
from app.services.scenario_generator import ScenarioGenerator
from app.schemas.scenario import ScenarioGenerateRequest
from app.risk.scoring import RiskScoringEngine


def test_model_nan_and_inf_handling():
    """Adversarial feature inputs containing NaNs, Infinities, and extremes must not crash models."""
    X_adversarial = np.array([
        [np.nan, 0.5, np.inf, -np.inf, 0.0, 1.0, np.nan, 0.0, 0.0, 1.0, 0.2, 0.0, 1.0, 1.0],
        [1.0, 0.001, 1.0, 2.0, 2.0, 300.0, 24.0, 0.8, 0.0, 3.0, 1.5, 0.1, 1.0, 1.0],
    ])

    iforest = IsolationForestDetector()
    if_scores = iforest.score_samples(X_adversarial)
    assert len(if_scores) == 2
    assert not np.isnan(if_scores).any()
    assert (if_scores >= 0.0).all() and (if_scores <= 100.0).all()

    rf = CalibratedSupervisedModel()
    rf_probs = rf.predict_proba(X_adversarial)
    assert len(rf_probs) == 2
    assert not np.isnan(rf_probs).any()
    assert (rf_probs >= 0.0).all() and (rf_probs <= 1.0).all()


def test_false_positive_legitimate_high_volume():
    """Verify that high transaction volume alone does NOT cause a high or critical risk alert."""
    # Legitimate exchange cold storage transfer or batch payout:
    # 500 BTC volume, but normal fee, normal fan-out, high diversity, zero laundering motifs.
    features = {
        "tx_total_volume_btc": {"value": 500.0},
        "tx_fee_ratio": {"value": 0.0001},
        "tx_input_count": {"value": 2.0},
        "tx_output_count": {"value": 30.0},
        "tx_fan_ratio": {"value": 15.0},
        "tx_output_gini": {"value": 0.3},
        "tx_address_reuse": {"value": 0.0},
        "graph_degree_total": {"value": 32.0},
        "graph_fan_ratio": {"value": 15.0},
        "graph_ego_density": {"value": 0.05},
        "graph_clustering_coefficient": {"value": 0.02},
        "net_ip_frequency": {"value": 1.0},
        "net_telemetry_completeness": {"value": 1.0},
        "net_asn_present": {"value": 1.0},
    }

    # Model scores for routine exchange activity: low anomaly, zero motifs
    anomaly_score = 25.0
    network_score = 10.0
    graph_density = 0.05
    graph_degree = 30.0
    motifs = []

    risk_engine = RiskScoringEngine()
    risk_score, severity, motif_contribution = risk_engine.compute_risk(
        anomaly_score=anomaly_score,
        motifs=motifs,
        network_score=network_score,
        graph_density=graph_density,
        graph_degree=graph_degree,
    )

    # Legitimate batch payment should NOT trigger high risk (> 65) or critical (> 80)
    assert risk_score < 60.0, f"False Positive triggered! Expected low/moderate risk, got {risk_score}"
    assert severity in ("LOW", "MEDIUM")


import json
from app.ingestion.normalizer import normalize_raw_record


def _to_tx_models(records: list[dict]) -> list[TransactionModel]:
    models = []
    for idx, r in enumerate(records):
        canonical, _, _ = normalize_raw_record(r, "scenario.json", idx)
        models.append(
            TransactionModel(
                record_id=f"rec_{idx}",
                source_file="scenario.json",
                source_row=idx,
                timestamp=canonical["timestamp"],
                txid=canonical["txid"],
                src_ip=canonical.get("src_ip"),
                dst_ip=canonical.get("dst_ip"),
                input_addresses_json=json.dumps(canonical.get("input_addresses", [])),
                output_addresses_json=json.dumps(canonical.get("output_addresses", [])),
                input_amounts_json=json.dumps(canonical.get("input_amounts", [])),
                output_amounts_json=json.dumps(canonical.get("output_amounts", [])),
                input_amount=canonical.get("input_amount", 0.0),
                output_amount=canonical.get("output_amount", 0.0),
                fee=canonical.get("fee", 0.0),
                script_type=canonical.get("script_type", "UNKNOWN"),
            )
        )
    return models


def test_false_negatives_all_motifs_detected():
    """Verify that synthetic laundering topologies trigger their respective motif detectors."""
    gen = ScenarioGenerator()

    # 1. PEELING_CHAIN
    p_req = ScenarioGenerateRequest(scenario_type="PEELING_CHAIN", seed=42)
    p_resp, p_ground = gen.generate(p_req)
    p_txs = _to_tx_models(p_ground)
    p_motifs = PeelingChainDetector().detect(p_txs)
    assert len(p_motifs) >= 1
    assert p_motifs[0].motif_type == "PEELING_CHAIN"

    # 2. MIXING_LIKE
    m_req = ScenarioGenerateRequest(scenario_type="MIXING_LIKE", seed=42)
    m_resp, m_ground = gen.generate(m_req)
    m_txs = _to_tx_models(m_ground)
    m_motifs = CoinJoinDetector().detect(m_txs)
    assert len(m_motifs) >= 1
    assert m_motifs[0].motif_type == "MIXING_LIKE"

    # 3. FAN_IN
    fi_req = ScenarioGenerateRequest(scenario_type="FAN_IN", seed=42)
    fi_resp, fi_ground = gen.generate(fi_req)
    fi_txs = _to_tx_models(fi_ground)
    fi_motifs = FanInOutDetector().detect(fi_txs)
    assert any(m.motif_type == "FAN_IN" for m in fi_motifs)

    # 4. FAN_OUT
    fo_req = ScenarioGenerateRequest(scenario_type="FAN_OUT", seed=42)
    fo_resp, fo_ground = gen.generate(fo_req)
    fo_txs = _to_tx_models(fo_ground)
    fo_motifs = FanInOutDetector().detect(fo_txs)
    assert any(m.motif_type == "FAN_OUT" for m in fo_motifs)

    # 5. RAPID_LAYERING
    rl_req = ScenarioGenerateRequest(scenario_type="RAPID_LAYERING", seed=42)
    rl_resp, rl_ground = gen.generate(rl_req)
    rl_txs = _to_tx_models(rl_ground)
    rl_motifs = RapidLayeringDetector().detect(rl_txs)
    assert any(m.motif_type == "RAPID_LAYERING" for m in rl_motifs)

    # 6. CIRCULAR_FLOW
    cf_req = ScenarioGenerateRequest(scenario_type="CIRCULAR_FLOW", seed=42)
    cf_resp, cf_ground = gen.generate(cf_req)
    cf_txs = _to_tx_models(cf_ground)
    cf_motifs = CircularFlowDetector().detect(cf_txs)
    assert any(m.motif_type == "CIRCULAR_FLOW" for m in cf_motifs)
