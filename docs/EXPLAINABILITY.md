# NEXUS-BTC: Multimodal Explainability & Counterfactual Reasoning

NEXUS-BTC strictly enforces that **no alert may be generated without interpretable mathematical justification**. Investigators and courts cannot act on opaque confidence metrics; every prioritized alert provides SHAP feature attributions, counterfactual sensitivity deltas, and topological graph ablations.

---

## 1. SHAP (SHapley Additive exPlanations) Attributions

For every evaluated transaction, NEXUS-BTC executes a localized Shapley attribution pass using `shap.TreeExplainer`:

$$\text{Risk Score}(x) = \phi_0 + \sum_{j=1}^{M} \phi_j(x)$$

Where:
- $\phi_0$ is the **base expected risk** across the baseline population (e.g., $15.2$ points).
- $\phi_j(x)$ is the marginal contribution (positive or negative) of feature $j$ to the final risk score.

### Visual Presentation (SHAP Waterfall)
The interactive dashboard renders a high-contrast waterfall plot showing:
- **Red bars (+):** Features pushing risk upwards (e.g., high velocity $+18.4$, peeling chain topology $+24.1$).
- **Green/Blue bars (-):** Features pulling risk downwards (e.g., high address reuse variance $-5.2$, standard fee ratio $-3.1$).

### Deterministic Fallback Mode
In the event that the TreeExplainer cannot initialize (e.g., pure unsupervised mode with no fitted trees), NEXUS-BTC automatically activates the **Deterministic Feature Attribution Engine**, computing z-score deviations from benign feature medians. **Explanations are never fabricated.**

---

## 2. Counterfactual Sensitivity Analysis

Counterfactual analysis answers the investigator's core question:
> *"What specific behavior would need to change for this transaction to be classified as benign?"*

For each high-risk alert, the Counterfactual Engine performs localized sensitivity perturbations on key indicators:

```json
{
  "original_risk": 92.4,
  "modified_feature_name": "rapid_layering",
  "feature_removed_or_modified": "Ablated sub-minute multi-hop transaction chain",
  "new_risk": 61.2,
  "delta": -31.2,
  "interpretation": "Removing rapid layering drops risk score by 31.2 points to 61.2."
}
```

This sensitivity delta enables investigators to isolate whether an entity is flagged due to temporary network congestion or intentional obfuscation techniques.

---

## 3. Graph Topological Ablation

To evaluate the influence of graph structure independently of transaction amounts, NEXUS-BTC performs **subgraph edge ablation**:

1. Identifies connected graph structures (peel branches, fan-in hubs, circular loops).
2. Simulates the graph with candidate structures pruned.
3. Recomputes PageRank, degree centrality, and neighborhood clustering coefficients.
4. Reports the structural influence percentage:
   $$\text{Structural Influence} = \frac{\text{Risk}_{\text{original}} - \text{Risk}_{\text{ablated}}}{\text{Risk}_{\text{original}}} \times 100\%$$

---

## 4. Forensic Evidence Chain

Every alert compiles a deterministic forensic timeline:

```
[NETWORK OBSERVATION] Broadcast from IP 198.51.100.22 (AS13335, NL)
       ↓ (observed)
[TRANSACTION] TXID 7b92708a318d... (Volume: 12.5 BTC, Fee: 0.0004 BTC)
       ↓ (observed)
[INPUT WALLET] 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
       ↓ (inferred via Common-Input)
[ENTITY] ENT-4D9183B (Cluster of 4 member addresses)
       ↓ (observed)
[OUTPUT WALLET] 1BoatSLRHtKNngkdXEeobR76b53LETtpyT (0.15 BTC peel)
       ↓ (probabilistic)
[MOTIF DETECTED] PEELING_CHAIN (5 sequential hops, 91% value preservation)
```

Each link in the chain explicitly notes its epistemological status:
- **`observed`:** Verified on-chain or directly recorded in network traffic.
- **`inferred`:** Deduced through mathematical heuristics (e.g., Union-Find clustering).
- **`probabilistic`:** Estimated by machine-learning models or correlation engines.
