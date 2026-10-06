"""Transaction search and inspection endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.transaction import TransactionModel

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("")
def list_transactions(
    query: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search or list transactions with optional search by TXID, wallet, or IP."""
    db_query = db.query(TransactionModel)

    if query:
        q_clean = query.strip()
        # Check if txid prefix
        if len(q_clean) >= 8:
            db_query = db_query.filter(TransactionModel.txid.like(f"%{q_clean}%"))
        else:
            db_query = db_query.filter(
                (TransactionModel.src_ip == q_clean)
                | (TransactionModel.txid.like(f"%{q_clean}%"))
            )

    records = db_query.order_by(TransactionModel.timestamp.desc()).offset(offset).limit(limit).all()

    return [
        {
            "txid": r.txid,
            "timestamp": r.timestamp,
            "src_ip": r.src_ip,
            "country": r.country,
            "asn": r.asn,
            "input_count": len(r.input_addresses),
            "output_count": len(r.output_addresses),
            "output_amount_btc": r.output_amount,
            "fee": r.fee,
            "script_type": r.script_type,
            "risk_score": r.risk_score,
            "alert_level": r.alert_level,
            "entity_id": r.entity_id,
        }
        for r in records
    ]


@router.get("/{txid}")
def get_transaction_detail(txid: str, db: Session = Depends(get_db)):
    """Retrieve complete canonical details for a specific transaction."""
    tx = db.query(TransactionModel).filter(TransactionModel.txid == txid).first()
    if not tx:
        raise HTTPException(status_code=404, detail=f"Transaction '{txid}' not found")

    return {
        "txid": tx.txid,
        "record_id": tx.record_id,
        "source_file": tx.source_file,
        "timestamp": tx.timestamp,
        "src_ip": tx.src_ip,
        "dst_ip": tx.dst_ip,
        "src_port": tx.src_port,
        "dst_port": tx.dst_port,
        "country": tx.country,
        "asn": tx.asn,
        "input_addresses": tx.input_addresses,
        "output_addresses": tx.output_addresses,
        "input_amounts": tx.input_amounts,
        "output_amounts": tx.output_amounts,
        "input_amount": tx.input_amount,
        "output_amount": tx.output_amount,
        "fee": tx.fee,
        "script_type": tx.script_type,
        "risk_score": tx.risk_score,
        "confidence_score": tx.confidence_score,
        "alert_level": tx.alert_level,
        "entity_id": tx.entity_id,
        "detected_motifs": tx.detected_motifs,
        "data_quality_flags": tx.data_quality_flags,
    }
