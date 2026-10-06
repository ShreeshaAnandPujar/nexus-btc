# NEXUS-BTC: Digital Forensics & Money Laundering Motif Detection

NEXUS-BTC incorporates digital forensics methodologies aligned with investigative standards of law enforcement and intelligence organizations.

---

## 1. The 9 Laundering Motif Detectors

NEXUS-BTC implements deterministic algorithmic detectors for 9 classical Bitcoin obfuscation and laundering topologies:

| Motif | Topology Description | Detection Algorithm & Thresholds |
| :--- | :--- | :--- |
| **PEELING_CHAIN** | Sequential chain of transactions where a large UTXO peels off small expenditure amounts while passing the bulk remainder to fresh change addresses. | $\ge 3$ consecutive hops; 1 large change output ($>80\%$) + 1 small peel output ($<20\%$); high value preservation ($>0.85$). |
| **MIXING_LIKE / COINJOIN** | Equalized output distributions designed to obscure UTXO linkage across multiple uncoordinated participants. | $\ge 3$ inputs, $\ge 3$ outputs; $\ge 60\%$ of outputs share identical or near-identical BTC denominations (within $0.0001$ BTC). |
| **FAN_IN** | Consolidation of funds from many dispersed wallet addresses into one or two central collection wallets. | In/Out address ratio $\ge 4.0$; input count $\ge 4$; single or dual output targets. |
| **FAN_OUT** | Rapid dispersal of concentrated funds into a multitude of small downstream wallets. | Output count $\ge 5$; In/Out ratio $\le 0.25$; output amounts evenly partitioned. |
| **RAPID_LAYERING** | Fast multi-hop movement of funds across several intermediaries within short timeframes. | $\ge 3$ sequential hops occurring in $< 900$ seconds ($15$ minutes) aggregate duration. |
| **CIRCULAR_FLOW** | Funds cycle through multiple intermediary wallets before returning to the originating entity or cluster. | Cycle detection in NetworkX directed subgraph; start wallet appears downstream within $\le 6$ hops. |
| **DORMANT_ACTIVATION**| Sudden high-volume movement from a wallet that has remained inactive for an extended period. | Inactive dormancy period $\ge 180$ days ($4320$ hours) followed by sudden high-value expenditure. |
| **CONSOLIDATION** | Aggregation of numerous small dust outputs into a significant single spend, often preparatory to exchange liquidation. | Input count $\ge 8$ with low average input balance ($<0.05$ BTC) aggregating into single high output. |
| **RAPID_SPLIT** | Branching split where an incoming sum is divided into distinct fractions within a single block interval. | $\ge 3$ outputs generated within $< 60$ seconds of prior parent confirmation. |

---

## 2. Entity Clustering Heuristics

Addresses are aggregated into probable behavioral clusters using two complementary techniques:

### 2.1 Common-Input Clustering (Disjoint Set Union)
Based on the Nakamoto Satoshi co-spending heuristic:
> *If multiple Bitcoin addresses appear as inputs in the same non-CoinJoin transaction, they are presumed to be controlled by the same wallet software holding the corresponding private keys.*

NEXUS-BTC implements this using an optimal **Disjoint Set Union (Union-Find)** data structure with path compression and union-by-rank, ensuring near-linear $\mathcal{O}(N \cdot \alpha(N))$ clustering efficiency.

### 2.2 HDBSCAN Behavioral Clustering
For addresses that do not co-spend directly but exhibit matching behavioral signatures (e.g., identical fee-rate preferences, synchronized broadcast schedules, and matching script types), HDBSCAN groups addresses into density-based clusters without requiring predefined cluster counts.

---

## 3. Value-Aware Best-First Fund Tracing

Rather than naive breadth-first search (which explodes exponentially on Bitcoin's directed transaction graph), NEXUS-BTC employs a **value-aware best-first search** priority queue:

$$\text{Priority}(hop) = -\text{Amount}_{\text{BTC}}$$

### Algorithmic Parameters
- `start_type`: `txid`, `wallet`, or `entity`.
- `max_hops`: Maximum exploration depth (default: 4–6 hops).
- `max_nodes`: Node ceiling to prevent unbounded execution (default: 50–100).
- `min_value_ratio`: Pruning threshold discarding dust below a fraction of the root volume (default: $0.01$).

### Semantic Endpoint Classifications
Each traced path terminates at a classified endpoint:
- **`SERVICE`:** Known institutional custodian, payment processor, or exchange (based on local clustering and high counterparty diversity).
- **`DORMANT`:** Unspent UTXO that has not moved downstream in the available ledger data.
- **`MIXER_LIKE`:** Multi-party equalized denomination transaction where coin history is severed.
- **`HORIZON`:** Maximum hop or node threshold reached without encountering a terminal wallet.
- **`CYCLE`:** Path looped back to a previously visited wallet.
- **`UNKNOWN`:** Unclassified address.

---

## 4. Forensic Caveats & Legal Disclaimer

1. **Network Observation vs. Physical Identity:** An IP address associated with a Bitcoin transaction broadcast represents a *network relay node or broadcaster observed in the P2P swarm*. In peer-to-peer protocols like Bitcoin, transaction propagation involves gossip diffusion (BIP 152 / Erlay), meaning the observed broadcaster is frequently an intermediary relay rather than the wallet owner.
2. **Behavioral Clusters vs. Legal Entities:** An inferred entity cluster reflects *shared algorithmic wallet behavior*, not a verified legal individual or corporate organization.
