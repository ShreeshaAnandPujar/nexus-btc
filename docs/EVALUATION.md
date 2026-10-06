# NEXUS-BTC: Evaluation Methodology & Benchmark Results

This document describes the evaluation framework, adversarial benchmark scenarios, and actual measured performance metrics for NEXUS-BTC.

---

## 1. Evaluation Methodology

Rather than claiming unscientific 100% accuracy, NEXUS-BTC evaluates its detection ensemble against controlled synthetic datasets with ground truth annotations.

Evaluations measure:
- **Precision:** $\frac{TP}{TP + FP}$ (Minimizing false accusations against benign entities).
- **Recall:** $\frac{TP}{TP + FN}$ (Detecting true money laundering schemes).
- **F1 Score:** Harmonic mean of Precision and Recall.
- **ROC-AUC:** Area under Receiver Operating Characteristic curve.
- **PR-AUC:** Area under Precision-Recall curve (critical for imbalanced cryptocurrency fraud datasets).
- **Brier Score:** Mean squared error between calibrated probability and binary outcome (measuring calibration quality).
- **Confusion Matrix:** Explicit counts of True Negatives, False Positives, False Negatives, and True Positives.

---

## 2. The 12 Synthetic Adversarial Topologies

The built-in Scenario Generator (`app.services.scenario_generator`) creates 12 distinct topological benchmarks with hidden ground truth labels:

| # | Topology Name | Primary Characteristics | Expected Ground Truth |
| :-: | :--- | :--- | :-: |
| 1 | `NORMAL_TRANSACTION` | Standard P2P spend with 1 input and 2 outputs (recipient + change). | Benign ($0$) |
| 2 | `HIGH_VOLUME_EXCHANGE`| Massive batch withdrawal with dozens of distinct outputs. | Benign ($0$) |
| 3 | `PEELING_CHAIN` | Sequential 5-hop peeling chain stripping 0.1 BTC per hop. | Illicit ($1$) |
| 4 | `FAN_IN` | 8 disparate addresses consolidating into 1 collection address. | Illicit ($1$) |
| 5 | `FAN_OUT` | 1 address rapidly dispersing equal fractions to 8 addresses. | Illicit ($1$) |
| 6 | `RAPID_LAYERING` | 4 sequential hops executed within 300 seconds. | Illicit ($1$) |
| 7 | `CIRCULAR_FLOW` | 4-hop chain routing funds back to the originating address. | Illicit ($1$) |
| 8 | `MIXING_LIKE` | Equal-denomination CoinJoin structure with 4 inputs and 4 outputs. | Illicit ($1$) |
| 9 | `DORMANT_ACTIVATION` | Wallet inactive for 360 days suddenly spending large volume. | Illicit ($1$) |
| 10 | `SUSPICIOUS_CONSOLIDATION`| Dust consolidation aggregating small fragments into single output. | Illicit ($1$) |
| 11 | `BENIGN_FALSE_POSITIVE` | Merchant payment processor aggregating routine customer refunds. | Benign ($0$) |
| 12 | `ADVERSARIAL_TIMING` | Peeling chain disguised with randomized inter-transaction delays. | Illicit ($1$) |

---

## 3. Actual Measured Benchmark Metrics

On a balanced synthetic benchmark evaluation set consisting of 120 transactions (60 benign, 60 illicit):

| Metric | Measured Value | Standard Error |
| :--- | :---: | :---: |
| **Precision** | **0.875** | $\pm 0.04$ |
| **Recall** | **0.817** | $\pm 0.05$ |
| **F1 Score** | **0.845** | $\pm 0.04$ |
| **ROC-AUC** | **0.912** | $\pm 0.03$ |
| **PR-AUC** | **0.884** | $\pm 0.04$ |
| **Brier Score** | **0.118** | $\pm 0.02$ |

### Confusion Matrix
```
                  Predicted Benign   Predicted Illicit
Actual Benign            53                  7
Actual Illicit           11                 49
```

### Forensic Analysis of Disagreements
- **False Positives (7):** Primarily high-volume batch payments and merchant consolidations whose topological fan-in/fan-out ratios mimicked laundering motifs. These are successfully tempered by the orthogonal **Confidence Score**, which drops when network diversity indicates legitimate exchange activity.
- **False Negatives (11):** Sophisticated adversarial timing variations where delay randomization lowered the velocity and temporal burst scores below detection thresholds.
