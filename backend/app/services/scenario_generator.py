"""Synthetic Adversarial Scenario Generator supporting 12 forensic topologies."""

import hashlib
import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from app.core.config import settings
from app.schemas.scenario import ScenarioGenerateRequest, ScenarioGenerateResponse, ScenarioInfo


class ScenarioGenerator:
    """Generates synthetic adversarial and benign forensic scenarios with isolated ground truth."""

    SCENARIO_CATALOG: dict[str, ScenarioInfo] = {
        "NORMAL_TRANSACTION": ScenarioInfo(
            scenario_id="SCEN-01",
            scenario_type="NORMAL_TRANSACTION",
            title="Regular Consumer Payment",
            description="Typical 1-in-2-out retail transaction with standard change and fee rate.",
            expected_pattern="Standard payment distribution, low fan ratio, zero laundering motifs.",
            ground_truth_illicit=False,
            expected_motifs=[],
        ),
        "LEGITIMATE_EXCHANGE": ScenarioInfo(
            scenario_id="SCEN-02",
            scenario_type="LEGITIMATE_EXCHANGE",
            title="High-Volume Exchange Batching",
            description="Legitimate custodial exchange sweep batching multiple user withdrawals.",
            expected_pattern="High output count, enterprise ASN, consistent fee.",
            ground_truth_illicit=False,
            expected_motifs=["FAN_OUT"],
        ),
        "PEELING_CHAIN": ScenarioInfo(
            scenario_id="SCEN-03",
            scenario_type="PEELING_CHAIN",
            title="Classic Peeling Chain (7 Hops)",
            description="Sequential 1-in-2-out transactions peeling small payments while forwarding change.",
            expected_pattern="High change ratio (>=80%), low peel ratio (<=5%), sequential hops.",
            ground_truth_illicit=True,
            expected_motifs=["PEELING_CHAIN"],
        ),
        "FAN_IN": ScenarioInfo(
            scenario_id="SCEN-04",
            scenario_type="FAN_IN",
            title="Multi-Source UTXO Consolidation",
            description="Funds collected from multiple feeder addresses into single destination.",
            expected_pattern="High fan-in ratio, rapid consolidation.",
            ground_truth_illicit=True,
            expected_motifs=["FAN_IN"],
        ),
        "FAN_OUT": ScenarioInfo(
            scenario_id="SCEN-05",
            scenario_type="FAN_OUT",
            title="Rapid Layering Dispersion (Fan-Out)",
            description="Single stash wallet quickly distributing funds across numerous recipient wallets.",
            expected_pattern="High fan-out ratio, wide address dispersion.",
            ground_truth_illicit=True,
            expected_motifs=["FAN_OUT", "RAPID_SPLIT"],
        ),
        "RAPID_LAYERING": ScenarioInfo(
            scenario_id="SCEN-06",
            scenario_type="RAPID_LAYERING",
            title="High-Velocity Multi-Hop Layering",
            description="Rapid transit across multiple intermediary burner wallets with sub-minute delays.",
            expected_pattern="Short inter-block delay (<120s), rapid hop sequence.",
            ground_truth_illicit=True,
            expected_motifs=["RAPID_LAYERING"],
        ),
        "MIXING_LIKE": ScenarioInfo(
            scenario_id="SCEN-07",
            scenario_type="MIXING_LIKE",
            title="CoinJoin / Wasabi Style Mix",
            description="Multi-party coordination with equal output denominations breaking UTXO lineage.",
            expected_pattern=">=3 inputs, identical output amounts within 1% tolerance.",
            ground_truth_illicit=True,
            expected_motifs=["MIXING_LIKE"],
        ),
        "CIRCULAR_FLOW": ScenarioInfo(
            scenario_id="SCEN-08",
            scenario_type="CIRCULAR_FLOW",
            title="Circular Wash Trading Loop",
            description="Directed fund loop returning money back to originating address cluster.",
            expected_pattern="Closed directed cycle in transaction graph.",
            ground_truth_illicit=True,
            expected_motifs=["CIRCULAR_FLOW"],
        ),
        "DORMANT_ACTIVATION": ScenarioInfo(
            scenario_id="SCEN-09",
            scenario_type="DORMANT_ACTIVATION",
            title="Dormant Whale Reactivation",
            description="Long-dormant address (inactive >180 days) abruptly liquidating substantial BTC.",
            expected_pattern="Extended inactivity followed by high-magnitude spending.",
            ground_truth_illicit=True,
            expected_motifs=["DORMANT_ACTIVATION"],
        ),
        "SUSPICIOUS_CONSOLIDATION": ScenarioInfo(
            scenario_id="SCEN-10",
            scenario_type="SUSPICIOUS_CONSOLIDATION",
            title="Suspicious Smurfing Consolidation",
            description="Collection of structured sub-threshold deposits into single aggregate wallet.",
            expected_pattern="High input count, consolidation to 1 output.",
            ground_truth_illicit=True,
            expected_motifs=["CONSOLIDATION", "FAN_IN"],
        ),
        "BENIGN_FALSE_POSITIVE": ScenarioInfo(
            scenario_id="SCEN-11",
            scenario_type="BENIGN_FALSE_POSITIVE",
            title="Mining Pool Reward Distribution",
            description="High-frequency, multi-output distribution representing benign mining payout.",
            expected_pattern="Coinbase origin, regular intervals, verified pool IP.",
            ground_truth_illicit=False,
            expected_motifs=["FAN_OUT"],
        ),
        "ADVERSARIAL_TIMING_VARIATION": ScenarioInfo(
            scenario_id="SCEN-12",
            scenario_type="ADVERSARIAL_TIMING_VARIATION",
            title="Adversarial Layering with Random Timing Jitter",
            description="Layering chain with intentionally randomized delays designed to evade heuristics.",
            expected_pattern="Non-uniform delay, variable peel ratios, structured flow.",
            ground_truth_illicit=True,
            expected_motifs=["RAPID_LAYERING"],
        ),
    }

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or (settings.DATA_DIR / "scenarios")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, req: ScenarioGenerateRequest) -> tuple[ScenarioGenerateResponse, list[dict[str, Any]]]:
        random.seed(req.seed)
        scenario_meta = self.SCENARIO_CATALOG.get(req.scenario_type, self.SCENARIO_CATALOG["NORMAL_TRANSACTION"])

        generator_fn = getattr(self, f"_gen_{req.scenario_type.lower()}", self._gen_normal_transaction)
        records = generator_fn(req)

        # File paths
        filename = f"scenario_{req.scenario_type.lower()}_{req.seed}.json"
        out_path = self.output_dir / filename
        gt_path = self.output_dir / f"ground_truth_{req.scenario_type.lower()}_{req.seed}.json"

        # Save data
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

        # Save ground truth separately
        ground_truth_data = {
            "scenario_type": req.scenario_type,
            "seed": req.seed,
            "ground_truth_illicit": scenario_meta.ground_truth_illicit,
            "expected_motifs": scenario_meta.expected_motifs,
            "total_records": len(records),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(gt_path, "w", encoding="utf-8") as f:
            json.dump(ground_truth_data, f, indent=2)

        resp = ScenarioGenerateResponse(
            scenario_id=scenario_meta.scenario_id,
            scenario_type=req.scenario_type,
            record_count=len(records),
            ground_truth_label="ILLICIT" if scenario_meta.ground_truth_illicit else "BENIGN",
            expected_motifs=scenario_meta.expected_motifs,
            parameters={
                "seed": req.seed,
                "base_volume_btc": req.base_volume_btc,
                "inject_noise": req.inject_noise,
            },
            output_filepath=str(out_path),
            message=f"Generated {len(records)} transactions for scenario {scenario_meta.title}",
        )
        return resp, records

    # ------------------ Individual Scenario Generators ------------------

    def _rand_hash(self, seed_str: str) -> str:
        return hashlib.sha256(seed_str.encode()).hexdigest()

    def _gen_normal_transaction(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
        records = []
        for i in range(req.transaction_count):
            tx_time = t0 + timedelta(minutes=15 * i)
            in_amt = round(random.uniform(0.1, 2.0), 4)
            pay_amt = round(in_amt * random.uniform(0.3, 0.6), 4)
            change_amt = round(in_amt - pay_amt - 0.0001, 4)
            records.append({
                "txid": self._rand_hash(f"normal_{req.seed}_{i}"),
                "ts": tx_time.isoformat(),
                "src_ip": f"192.0.2.{10 + (i % 20)}",
                "dst_ip": "198.51.100.1",
                "src_port": 8333,
                "dst_port": 8333,
                "input_addresses": [f"1NormIn_{req.seed}_{i}"],
                "output_addresses": [f"1NormPay_{req.seed}_{i}", f"1NormChg_{req.seed}_{i}"],
                "input_amounts": [in_amt],
                "output_amounts": [pay_amt, change_amt],
                "fee": 0.0001,
                "script_type": "P2PKH",
                "country": "US",
                "asn": 13335,
            })
        return records

    def _gen_peeling_chain(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 2, 14, 0, 0, tzinfo=timezone.utc)
        records = []
        current_in = f"1PeelOrigin_{req.seed}"
        current_bal = req.base_volume_btc

        hops = max(5, min(req.transaction_count, 10))
        for hop in range(hops):
            tx_time = t0 + timedelta(minutes=8 * hop)
            peel_amt = round(current_bal * 0.04, 4)  # 4% peel
            fee = 0.0001
            change_amt = round(current_bal - peel_amt - fee, 4)
            next_in = f"1PeelChange_{req.seed}_{hop}"

            records.append({
                "txid": self._rand_hash(f"peel_{req.seed}_{hop}"),
                "ts": tx_time.isoformat(),
                "src_ip": "203.0.113.45",
                "dst_ip": "8.8.8.8",
                "src_port": 54321,
                "dst_port": 8333,
                "input_addresses": [current_in],
                "output_addresses": [f"1PeelMerchant_{req.seed}_{hop}", next_in],
                "input_amounts": [current_bal],
                "output_amounts": [peel_amt, change_amt],
                "fee": fee,
                "script_type": "P2WPKH",
                "country": "NL",
                "asn": 49544,
            })
            current_in = next_in
            current_bal = change_amt
        return records

    def _gen_mixing_like(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 3, 18, 0, 0, tzinfo=timezone.utc)
        records = []
        denom = 0.1000  # Equal denomination
        in_addrs = [f"1MixUserIn_{req.seed}_{j}" for j in range(5)]
        out_addrs = [f"1MixUserOut_{req.seed}_{j}" for j in range(5)]
        in_amts = [0.1020, 0.1015, 0.1050, 0.1018, 0.1030]
        out_amts = [denom] * 5

        records.append({
            "txid": self._rand_hash(f"coinjoin_{req.seed}_0"),
            "ts": t0.isoformat(),
            "src_ip": "198.51.100.99",
            "dst_ip": "1.1.1.1",
            "src_port": 8333,
            "dst_port": 8333,
            "input_addresses": in_addrs,
            "output_addresses": out_addrs,
            "input_amounts": in_amts,
            "output_amounts": out_amts,
            "fee": 0.0133,
            "script_type": "P2SH",
            "country": "CH",
            "asn": 559,
        })
        return records

    def _gen_fan_in(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 4, 12, 0, 0, tzinfo=timezone.utc)
        in_count = 8
        in_addrs = [f"1FanInSrc_{req.seed}_{j}" for j in range(in_count)]
        in_amts = [round(req.base_volume_btc / in_count, 4)] * in_count
        tot_out = round(sum(in_amts) - 0.0002, 4)

        return [{
            "txid": self._rand_hash(f"fanin_{req.seed}_0"),
            "ts": t0.isoformat(),
            "src_ip": "192.0.2.77",
            "dst_ip": "8.8.8.8",
            "src_port": 8333,
            "dst_port": 8333,
            "input_addresses": in_addrs,
            "output_addresses": [f"1FanInDest_{req.seed}"],
            "input_amounts": in_amts,
            "output_amounts": [tot_out],
            "fee": 0.0002,
            "script_type": "P2WPKH",
            "country": "SG",
            "asn": 4657,
        }]

    def _gen_fan_out(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 4, 13, 0, 0, tzinfo=timezone.utc)
        out_count = 10
        out_addrs = [f"1FanOutDest_{req.seed}_{j}" for j in range(out_count)]
        slice_amt = round((req.base_volume_btc - 0.0005) / out_count, 4)
        out_amts = [slice_amt] * out_count

        return [{
            "txid": self._rand_hash(f"fanout_{req.seed}_0"),
            "ts": t0.isoformat(),
            "src_ip": "192.0.2.88",
            "dst_ip": "8.8.8.8",
            "src_port": 8333,
            "dst_port": 8333,
            "input_addresses": [f"1FanOutSrc_{req.seed}"],
            "output_addresses": out_addrs,
            "input_amounts": [req.base_volume_btc],
            "output_amounts": out_amts,
            "fee": 0.0005,
            "script_type": "P2TR",
            "country": "DE",
            "asn": 3320,
        }]

    def _gen_rapid_layering(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 5, 20, 0, 0, tzinfo=timezone.utc)
        records = []
        curr_w = f"1LayerOrigin_{req.seed}"
        bal = req.base_volume_btc

        for h in range(4):
            t_hop = t0 + timedelta(seconds=45 * h)  # Rapid 45 second hops
            next_w = f"1LayerHop_{req.seed}_{h}"
            fee = 0.0002
            out_bal = round(bal - fee, 4)

            records.append({
                "txid": self._rand_hash(f"layer_{req.seed}_{h}"),
                "ts": t_hop.isoformat(),
                "src_ip": "203.0.113.90",
                "dst_ip": "8.8.8.8",
                "src_port": 8333,
                "dst_port": 8333,
                "input_addresses": [curr_w],
                "output_addresses": [next_w],
                "input_amounts": [bal],
                "output_amounts": [out_bal],
                "fee": fee,
                "script_type": "P2WPKH",
                "country": "RU",
                "asn": 12389,
            })
            curr_w = next_w
            bal = out_bal
        return records

    def _gen_circular_flow(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 6, 8, 0, 0, tzinfo=timezone.utc)
        wallets = [f"1Circle_{req.seed}_{k}" for k in range(3)]
        records = []

        for k in range(3):
            src_w = wallets[k]
            dst_w = wallets[(k + 1) % 3]
            t_tx = t0 + timedelta(minutes=10 * k)
            records.append({
                "txid": self._rand_hash(f"circ_{req.seed}_{k}"),
                "ts": t_tx.isoformat(),
                "src_ip": "198.51.100.33",
                "dst_ip": "8.8.8.8",
                "src_port": 8333,
                "dst_port": 8333,
                "input_addresses": [src_w],
                "output_addresses": [dst_w],
                "input_amounts": [5.0],
                "output_amounts": [4.999],
                "fee": 0.001,
                "script_type": "P2PKH",
                "country": "PA",
                "asn": 27775,
            })
        return records

    def _gen_dormant_activation(self, req: ScenarioGenerateRequest) -> list[dict]:
        # Old tx from 2025
        t_old = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        t_new = datetime(2026, 3, 10, 15, 0, 0, tzinfo=timezone.utc)  # >400 days later
        whale_addr = f"1DormantWhale_{req.seed}"

        tx1 = {
            "txid": self._rand_hash(f"dormant_init_{req.seed}"),
            "ts": t_old.isoformat(),
            "src_ip": "1.1.1.1",
            "dst_ip": "8.8.8.8",
            "src_port": 8333,
            "dst_port": 8333,
            "input_addresses": ["1MinerOrigin"],
            "output_addresses": [whale_addr],
            "input_amounts": [25.0],
            "output_amounts": [24.999],
            "fee": 0.001,
            "script_type": "P2PKH",
            "country": "US",
            "asn": 13335,
        }
        tx2 = {
            "txid": self._rand_hash(f"dormant_spend_{req.seed}"),
            "ts": t_new.isoformat(),
            "src_ip": "185.107.56.22",
            "dst_ip": "8.8.8.8",
            "src_port": 8333,
            "dst_port": 8333,
            "input_addresses": [whale_addr],
            "output_addresses": [f"1Liquidation_{req.seed}"],
            "input_amounts": [24.999],
            "output_amounts": [24.998],
            "fee": 0.001,
            "script_type": "P2WPKH",
            "country": "NL",
            "asn": 49544,
        }
        return [tx1, tx2]

    def _gen_legitimate_exchange(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 7, 10, 0, 0, tzinfo=timezone.utc)
        out_count = 20
        out_addrs = [f"1ExchUser_{req.seed}_{j}" for j in range(out_count)]
        out_amts = [round(random.uniform(0.01, 0.5), 4) for _ in range(out_count)]
        tot_out = sum(out_amts)

        return [{
            "txid": self._rand_hash(f"exchange_{req.seed}_0"),
            "ts": t0.isoformat(),
            "src_ip": "104.16.123.99",
            "dst_ip": "8.8.8.8",
            "src_port": 8333,
            "dst_port": 8333,
            "input_addresses": [f"1ExchangeHotWallet_{req.seed}"],
            "output_addresses": out_addrs,
            "input_amounts": [round(tot_out + 0.001, 4)],
            "output_amounts": out_amts,
            "fee": 0.001,
            "script_type": "P2WPKH",
            "country": "US",
            "asn": 13335,
        }]

    def _gen_suspicious_consolidation(self, req: ScenarioGenerateRequest) -> list[dict]:
        return self._gen_fan_in(req)

    def _gen_benign_false_positive(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 8, 12, 0, 0, tzinfo=timezone.utc)
        return [{
            "txid": self._rand_hash(f"mining_{req.seed}_0"),
            "ts": t0.isoformat(),
            "src_ip": "192.0.2.11",
            "dst_ip": "8.8.8.8",
            "src_port": 8333,
            "dst_port": 8333,
            "input_addresses": ["COINBASE"],
            "output_addresses": [f"1PoolMiner_{req.seed}_{j}" for j in range(8)],
            "input_amounts": [3.125],
            "output_amounts": [round(3.125 / 8, 4)] * 8,
            "fee": 0.0,
            "script_type": "P2WPKH",
            "country": "IS",
            "asn": 44517,
        }]

    def _gen_adversarial_timing_variation(self, req: ScenarioGenerateRequest) -> list[dict]:
        t0 = datetime(2026, 3, 9, 14, 0, 0, tzinfo=timezone.utc)
        records = []
        curr_w = f"1AdvOrigin_{req.seed}"
        bal = req.base_volume_btc

        for h in range(4):
            # Non-uniform random delay between 5 minutes and 4 hours
            delay_min = random.randint(5, 240)
            t_hop = t0 + timedelta(minutes=delay_min * (h + 1))
            next_w = f"1AdvHop_{req.seed}_{h}"
            fee = 0.0003
            out_bal = round(bal - fee, 4)

            records.append({
                "txid": self._rand_hash(f"adv_{req.seed}_{h}"),
                "ts": t_hop.isoformat(),
                "src_ip": f"198.51.100.{10 + h}",
                "dst_ip": "8.8.8.8",
                "src_port": 8333,
                "dst_port": 8333,
                "input_addresses": [curr_w],
                "output_addresses": [next_w],
                "input_amounts": [bal],
                "output_amounts": [out_bal],
                "fee": fee,
                "script_type": "P2TR",
                "country": "RO",
                "asn": 9050,
            })
            curr_w = next_w
            bal = out_bal
        return records
