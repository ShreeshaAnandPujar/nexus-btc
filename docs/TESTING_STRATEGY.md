# Testing Strategy & Quality Assurance: NEXUS-BTC

## 1. Testing Philosophy
NEXUS-BTC enforces a multi-layer verification strategy to ensure forensic reliability, numerical precision, and zero-crash fault tolerance during academic demonstrations.

---

## 2. Test Suite Hierarchy

```
tests/
├── unit/
│   ├── test_schema_validation.py     # Ingestion schema, regex, script types
│   ├── test_defensive_ingest.py      # Missing fields, malformed amounts, null IPs
│   ├── test_union_find.py            # Co-spend address clustering correctness
│   └── test_enrichment.py            # Offline MaxMind GeoIP fallback behaviour
├── graph/
│   ├── test_graph_builder.py         # NetworkX node & edge creation invariants
│   ├── test_peeling_detector.py      # Peeling chain detection precision & recall
│   ├── test_coinjoin_detector.py     # CoinJoin sliding window tolerance matching
│   └── test_fund_tracer.py           # Best-first fund tracing & stop reason classification
├── ml/
│   ├── test_feature_extractor.py     # Multi-view feature vector dimensions & bounds
│   ├── test_model_inference.py       # Scikit-Learn inference & threshold bounds
│   ├── test_calibration.py           # Platt scaling probability bounds [0, 1]
│   └── test_shap_attributions.py     # Sum of SHAP attributions equals model delta
├── api/
│   ├── test_ingest_endpoints.py      # POST /api/ingest file uploads
│   ├── test_alert_endpoints.py       # GET /api/alerts filtering & sorting
│   └── test_trace_endpoints.py       # GET /api/trace path responses
└── e2e/
    └── test_offline_pipeline_e2e.py  # End-to-end ingest -> motif -> ML -> alert pipeline
```

---

## 3. Key Verification Invariants

1. **Ingestion Idempotency**: Ingesting the same transaction batch twice produces identical database state and flags duplicates without raising primary key collisions.
2. **Graceful Degradation**: Running ingestion with an empty or missing GeoIP database sets `country="UNKNOWN"` and `asn=0` with zero exceptions.
3. **Forensic Trace Bounds**: Best-first fund tracing strictly respects `max_hops` and `max_nodes`, guaranteeing loop termination on cyclic transaction paths.
4. **SHAP Attribution Honesty**: For every alert, the sum of baseline value plus all feature SHAP attributions exactly matches the model's raw output.
