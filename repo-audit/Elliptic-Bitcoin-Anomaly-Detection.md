# Repository Audit: Elliptic-Bitcoin-Anomaly-Detection

## 1. Executive Summary & Purpose
- **Repository Name**: Elliptic-Bitcoin-Anomaly-Detection
- **Source**: `https://github.com/Sajjad-Shahali/Elliptic-Bitcoin-Anomaly-Detection.git`
- **Author**: Sajjad Shahali (Thesis / Academic Research Project s340464, 2025-2026)
- **Stated Purpose**: State-of-the-art anomaly detection and illicit transaction identification on the Elliptic Bitcoin dataset using classical ML, graph representation learning, deep generative autoencoders (VAE/DOMINANT), and calibrated ensembles.
- **Scope & Role in NEXUS-BTC**: Serves as the **scientific cornerstone** for AI/ML design in NEXUS-BTC:
  1. Probability calibration via Platt scaling and isotonic regression (preventing uncalibrated overconfident scores).
  2. Structural graph features (OddBall ego-net law, clustering coefficients, average neighbour degrees).
  3. Supervised and unsupervised model definitions (Random Forest, Isolation Forest, LOF).
  4. SHAP explainability methodology and temporal split validation.
  *(Note: No license is attached; all concepts and algorithms must be cleanly reimplemented).*

---

## 2. Technical Profile & Inventory (24-Dimension Analysis)

| # | Dimension | Assessment |
|---|-----------|------------|
| 1 | **Language** | Python 3.10 - 3.12 |
| 2 | **Framework** | Scikit-Learn 1.9, LightGBM, PyTorch 2.11, PyG (`torch_geometric`), Optuna, NetworkX, Joblib |
| 3 | **Backend Architecture** | None. Academic experimentation harness, evaluation scripts (`scripts/`), and model pipelines (`src/`) |
| 4 | **Frontend Architecture** | None. Comprehensive academic figures, LaTeX presentations, and PDF research reports |
| 5 | **Database / Storage** | Flat CSVs + 20+ serialised model weights (`.joblib` and `.pt` checkpoint files in `models/`) |
| 6 | **Data Schema** | Elliptic dataset schema: 165 features, transaction IDs, time steps 1-49, classes (1=Illicit, 2=Licit) |
| 7 | **ML Models** | Comprehensive suite: LightGBM, Gradient Boosting, Random Forest, Isolation Forest, Local Outlier Factor (LOF), One-Class SVM, VAE, Autoencoder, LSTM-AE, DOMINANT (Deep Graph AE), GraphSAGE, GAT, and Soft-Voting Ensembles |
| 8 | **Graph Algorithms** | Ego-net density extraction, OddBall power-law outlier metrics, clustering coefficients (`nx.clustering`), average neighbour degree, temporal rolling features |
| 9 | **Anomaly Detection** | Multimodal: Unsupervised reconstruction loss (Autoencoders/DOMINANT), contamination isolation (IsolationForest), density estimation (LOF) |
| 10 | **Clustering Methods** | Latent-space clustering via VAE / Autoencoders |
| 11 | **Laundering Detection Logic** | Heuristic structural anomaly rules + pseudo-label propagation across temporal transaction graphs |
| 12 | **Tracing Algorithms** | None |
| 13 | **Explainability** | **SHAP TreeExplainer** on tree ensembles (`scripts/shap_gbm.py`), GNNExplainer analysis, and deterministic model feature ablation |
| 14 | **API Integrations** | `kagglehub` (for initial automated dataset pull) |
| 15 | **Network Dependencies** | None during offline model inference |
| 16 | **Config / Environment** | `config.py` with root and data directory configurations |
| 17 | **Docker Dependencies** | None |
| 18 | **OS Assumptions** | Cross-platform |
| 19 | **Runtime Version** | Python >= 3.10 |
| 20 | **Test Coverage** | 0% formal pytest suites; extensive empirical benchmarking scripts across 40+ model variants |
| 21 | **License** | **NONE** (No LICENSE file provided in repository) |
| 22 | **Code Quality** | **Exceptional scientific quality**: Rigorous temporal evaluation splits (steps 1-34 train, 35-49 test), strict avoidance of temporal data leakage, Brier score calibration, Optuna hyperparameter tuning |
| 23 | **Reusable Components** | Probability calibration logic (`scripts/probability_calibration.py`); OddBall/ego-net structural formulas (`scripts/structural_graph_features.py`); SHAP explainability pipeline; optimal threshold tuning (`f1_optimal_threshold`) |
| 24 | **Dangerous / Incompatible** | Absence of open-source license; massive pre-trained binary checkpoints (>500MB); fragile PyTorch Geometric dependencies |

---

## 3. Component Deep Dive

### Strongest Components
1. **Probability Calibration Engine (`scripts/probability_calibration.py`)**:
   - Uses Platt scaling (logistic calibration) and Isotonic Regression fit on validation steps to transform raw, overconfident classifier outputs into statistically calibrated probabilities ( \in [0, 1]$).
   - Evaluates probability reliability via Brier score loss ( = rac{1}{N} \sum (p_i - y_i)^2$).
2. **Structural Ego-Net & OddBall Features (`scripts/structural_graph_features.py`)**:
   - Computes neighbourhood density and power-law deviations (OddBall law) directly from topology, capturing graph anomalies without requiring node attributes.
3. **SHAP Tree Explainability Pipeline (`scripts/shap_gbm.py`)**:
   - Computes exact Shapley values for Gradient Boosted trees, outputting feature contribution rankings per individual transaction.
4. **F1-Optimal Threshold Finder (`src/autoencoder.py`)**:
   - Automatically sweeps decision thresholds on validation data to maximise F1-score on severe class imbalances, rather than defaulting to an arbitrary 0.5 threshold.

### Weakest Components
1. **No Operational Application**: No REST API, no database ingestion pipeline, no interactive user interface.
2. **Heavy PyTorch Overhead**: Multiple deep architectures (DOMINANT, LSTM-AE, GAT) require substantial RAM and specialized GPU environments, making them ill-suited for a student evaluation laptop without GPU.

---

## 4. Reusable vs. Incompatible Modules

### Reusable (Conceptually / Algorithmically Reimplemented)
- **Platt Scaling & Isotonic Calibration**: Reimplement in NEXUS-BTC's `ml/calibration.py` using Scikit-Learn.
- **OddBall & Ego-Net Features**: Reimplement in pure NetworkX for NEXUS-BTC's topological feature engine.
- **SHAP Waterfall Logic**: Integrate directly with Scikit-Learn Random Forest in NEXUS-BTC's explainability module.
- **Threshold Optimization**: Reimplement in NEXUS-BTC's evaluation suite.

### Incompatible / Excluded
- Pre-trained `.pt` binary weights (unlicensed, opaque).
- Monolithic LaTeX and presentation documents.
- Direct source code copying.

---

## 5. Dependencies & Version Constraints
- `scikit-learn >= 1.3`, `lightgbm >= 4.0`, `networkx >= 3.0`, `joblib >= 1.3`, `shap >= 0.44`, `optuna >= 3.5`
- Optional: `torch >= 2.1`, `torch_geometric >= 2.5`

---

## 6. License & Provenance Analysis
- **License Status**: Absent (All Rights Reserved by default).
- **Provenance**: Authored by Sajjad Shahali as part of an academic thesis.
- **Resolution**: Adhere strictly to Phase 2: **DO NOT copy the source code or binary model checkpoints**. Use all methodologies, mathematical formulations, and validation principles as **conceptual inspiration** and implement them natively in NEXUS-BTC.

---

## 7. Integration Risks & Mitigation
- **Risk 1: Deep Learning Failure during Evaluation**: GNN/DOMINANT models crash on student machines lacking CUDA.
  - *Mitigation*: NEXUS-BTC designates Random Forest + Isolation Forest + Platt Calibration as the primary zero-dependency ML tier. PyG models are purely optional.
- **Risk 2: Model Overconfidence**: Uncalibrated models produce false 99% risk scores.
  - *Mitigation*: Adopt the repository's Platt scaling and Brier score calibration pipeline to guarantee realistic, calibrated probabilities.

---

## 8. Final Recommendation
**STATUS: ESSENTIAL SCIENTIFIC REFERENCE (REIMPLEMENT ALGORITHMS)**
Translate the probability calibration, OddBall graph feature equations, optimal threshold tuning, and SHAP explainability pipelines into NEXUS-BTC's native Python ML engine.
