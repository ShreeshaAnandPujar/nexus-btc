"""Unified Correlation Engine for NEXUS-BTC."""

from app.correlation.geo_asn import GeoEnricher, GeoResult
from app.correlation.probabilistic import ProbabilisticCorrelator, CorrelationEvidence


class CorrelationEngine:
    """Orchestrates network geo-enrichment and probabilistic on-chain correlation."""

    def __init__(self):
        self.geo_enricher = GeoEnricher()
        self.correlator = ProbabilisticCorrelator()

    def enrich_ip(self, ip_str: str | None) -> GeoResult:
        return self.geo_enricher.lookup(ip_str)

    def correlate_transaction(
        self,
        tx_timestamp: str,
        src_ip: str | None,
        net_timestamp: str | None = None,
        ip_observation_count: int = 1,
        cluster_ips: list[str] | None = None,
        asn: int = 0,
        country: str = "UNKNOWN",
    ) -> CorrelationEvidence:
        # If country or ASN not set, attempt geo lookup
        if (country == "UNKNOWN" or asn == 0) and src_ip:
            geo_res = self.geo_enricher.lookup(src_ip)
            if geo_res.available:
                country = geo_res.country
                asn = geo_res.asn

        return self.correlator.correlate(
            tx_timestamp=tx_timestamp,
            net_timestamp=net_timestamp,
            ip_observation_count=ip_observation_count,
            cluster_observed_ips=cluster_ips,
            target_ip=src_ip or "0.0.0.0",
            asn=asn,
            country=country,
        )

    def close(self):
        self.geo_enricher.close()
