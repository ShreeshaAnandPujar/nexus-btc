"""Unified Ingestion Engine coordinating multi-format loaders, quarantine, and persistence."""

import json
import time
import uuid
from pathlib import Path
from typing import Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.logging import logger
from app.models.transaction import TransactionModel, GraphEdgeModel
from app.schemas.canonical import CanonicalTransaction, IngestResult
from app.ingestion.detector import detect_format
from app.ingestion.csv_loader import CsvLoader
from app.ingestion.json_loader import JsonLoader
from app.ingestion.xml_loader import XmlLoader
from app.ingestion.quarantine import QuarantineManager


class IngestionEngine:
    """Enterprise-grade ingestion orchestrator for NEXUS-BTC."""

    def __init__(self, db: Session | None = None):
        self.db_provided = db is not None
        self._db = db
        self.quarantine = QuarantineManager()
        init_db()

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def close(self):
        if not self.db_provided and self._db is not None:
            self._db.close()
            self._db = None

    def ingest_content(
        self,
        content: str | bytes,
        source_name: str = "upload.csv",
        format_hint: str | None = None,
    ) -> IngestResult:
        """Ingest raw string or bytes payload with auto-detection."""
        start_time = time.time()
        ingestion_id = str(uuid.uuid4())
        detected = format_hint or detect_format(content, source_name)

        logger.info(f"Beginning ingestion [{ingestion_id}]: format={detected}, source={source_name}")

        if detected == "json":
            generator = JsonLoader.parse_content(content, source_name)
        elif detected == "xml":
            generator = XmlLoader.parse_content(content, source_name)
        else:
            generator = CsvLoader.parse_content(content, source_name)

        return self._process_stream(generator, source_name, ingestion_id, start_time)

    def ingest_file(self, file_path: Path | str) -> IngestResult:
        """Ingest a file from the local file system."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        start_time = time.time()
        ingestion_id = str(uuid.uuid4())
        detected = detect_format(b"", path.name)

        logger.info(f"Ingesting local file [{ingestion_id}]: {path.name} (detected {detected})")

        if detected == "json":
            generator = JsonLoader.parse_file(path)
        elif detected == "xml":
            generator = XmlLoader.parse_file(path)
        else:
            generator = CsvLoader.parse_file(path)

        return self._process_stream(generator, str(path), ingestion_id, start_time)

    def _process_stream(
        self,
        generator,
        source_name: str,
        ingestion_id: str,
        start_time: float,
    ) -> IngestResult:
        records_read = 0
        records_valid = 0
        records_invalid = 0
        duplicates = 0
        normalization_warnings = 0
        last_quarantine_path: str | None = None

        seen_txids_batch: set[str] = set()
        transactions_to_save: list[TransactionModel] = []
        edges_to_save: list[GraphEdgeModel] = []

        # Query existing txids from db for deduplication
        existing_txids = set(
            row[0] for row in self.db.query(TransactionModel.txid).all()
        )

        for record_dict, flags, status, row_idx in generator:
            records_read += 1

            if status == "INVALID":
                records_invalid += 1
                q_path = self.quarantine.quarantine_record(
                    raw_record=record_dict,
                    source_file=source_name,
                    source_row=row_idx,
                    error_reason=";".join(flags),
                    ingestion_id=ingestion_id,
                )
                last_quarantine_path = str(q_path)
                continue

            if flags:
                normalization_warnings += len(flags)

            txid = record_dict.get("txid", "")

            # Deduplication
            if txid in seen_txids_batch or txid in existing_txids:
                duplicates += 1
                continue

            seen_txids_batch.add(txid)
            records_valid += 1

            # Prepare DB Model
            tx_model = TransactionModel(
                record_id=str(uuid.uuid4()),
                source_file=source_name,
                source_row=row_idx,
                validation_status=status,
                data_quality_flags_json=json.dumps(flags),
                timestamp=record_dict["timestamp"],
                txid=txid,
                src_ip=record_dict.get("src_ip"),
                dst_ip=record_dict.get("dst_ip"),
                src_port=record_dict.get("src_port", 8333),
                dst_port=record_dict.get("dst_port", 8333),
                country=record_dict.get("country", "UNKNOWN"),
                asn=record_dict.get("asn", 0),
                input_addresses_json=json.dumps(record_dict.get("input_addresses", [])),
                output_addresses_json=json.dumps(record_dict.get("output_addresses", [])),
                input_amounts_json=json.dumps(record_dict.get("input_amounts", [])),
                output_amounts_json=json.dumps(record_dict.get("output_amounts", [])),
                input_amount=record_dict.get("input_amount", 0.0),
                output_amount=record_dict.get("output_amount", 0.0),
                fee=record_dict.get("fee", 0.0),
                script_type=record_dict.get("script_type", "UNKNOWN"),
            )
            transactions_to_save.append(tx_model)

            # Build Graph Edges for edge cache
            in_addrs = record_dict.get("input_addresses", [])
            out_addrs = record_dict.get("output_addresses", [])
            out_amts = record_dict.get("output_amounts", [])

            # Wallet-to-Wallet edges through transaction
            for src_addr in in_addrs:
                if not src_addr:
                    continue
                for dst_idx, dst_addr in enumerate(out_addrs):
                    if not dst_addr:
                        continue
                    amt = out_amts[dst_idx] if dst_idx < len(out_amts) else 0.0
                    edge_id = f"{txid[:16]}_{src_addr[:8]}_{dst_addr[:8]}"
                    edges_to_save.append(
                        GraphEdgeModel(
                            edge_id=edge_id,
                            txid=txid,
                            source=src_addr,
                            target=dst_addr,
                            relationship_type="TRANSFERRED",
                            amount=amt,
                            timestamp=record_dict["timestamp"],
                            confidence=1.0,
                            provenance="OBSERVED",
                        )
                    )

            # Batch commit to prevent high memory usage
            if len(transactions_to_save) >= settings.BATCH_SIZE:
                self.db.bulk_save_objects(transactions_to_save)
                self.db.bulk_save_objects(edges_to_save)
                self.db.commit()
                transactions_to_save.clear()
                edges_to_save.clear()

        # Flush remaining
        if transactions_to_save:
            self.db.bulk_save_objects(transactions_to_save)
            if edges_to_save:
                self.db.bulk_save_objects(edges_to_save)
            self.db.commit()

        exec_time = round(time.time() - start_time, 4)
        logger.info(
            f"Ingestion [{ingestion_id}] finished in {exec_time}s: read={records_read}, valid={records_valid}, "
            f"invalid={records_invalid}, duplicates={duplicates}"
        )

        return IngestResult(
            ingestion_id=ingestion_id,
            source_file=source_name,
            records_read=records_read,
            records_valid=records_valid,
            records_invalid=records_invalid,
            duplicates=duplicates,
            normalization_warnings=normalization_warnings,
            quarantined_path=last_quarantine_path,
            execution_time_seconds=exec_time,
            status="COMPLETED" if records_invalid == 0 else "PARTIAL_SUCCESS",
            message=f"Successfully processed {records_valid} records ({records_invalid} quarantined, {duplicates} duplicates)",
        )
