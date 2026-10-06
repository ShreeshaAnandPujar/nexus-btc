"""HDBSCAN behavioral wallet clustering."""

import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler
from app.core.logging import logger


class BehavioralClusterer:
    """Groups wallets by behavioral similarity vectors using HDBSCAN."""

    def __init__(self, min_cluster_size: int = 2):
        self.min_cluster_size = min_cluster_size

    def cluster_wallets(
        self, wallet_profiles: dict[str, dict[str, float]]
    ) -> dict[str, list[str]]:
        """
        Group wallet addresses based on behavioral feature vectors.
        wallet_profiles: {wallet_address: {tx_count, vol_sent, vol_recv, avg_fee, reuse_rate}}
        Returns: {cluster_id: [wallet_address, ...]}
        """
        wallets = list(wallet_profiles.keys())
        if len(wallets) < self.min_cluster_size:
            return {}

        feature_keys = ["tx_count", "vol_sent", "vol_recv", "avg_fee", "reuse_rate"]
        matrix = []
        for w in wallets:
            prof = wallet_profiles[w]
            vec = [float(prof.get(k, 0.0)) for k in feature_keys]
            matrix.append(vec)

        X = np.array(matrix, dtype=np.float64)
        if np.all(X == X[0, :]):
            # Identical features, no dispersion
            return {}

        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            clusterer = HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=1,
                metric="euclidean",
            )
            labels = clusterer.fit_predict(X_scaled)

            clusters: dict[str, list[str]] = {}
            for idx, label in enumerate(labels):
                if label != -1:  # -1 is noise
                    cid = f"ENT-BEH-{label:04d}"
                    if cid not in clusters:
                        clusters[cid] = []
                    clusters[cid].append(wallets[idx])

            return clusters
        except Exception as e:
            logger.warning(f"HDBSCAN clustering failed: {e}")
            return {}
