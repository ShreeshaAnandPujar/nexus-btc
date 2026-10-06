"""Entity cluster endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entity import EntityModel
from app.models.transaction import TransactionModel
from app.schemas.entity import EntityResponse, EntitySummary

router = APIRouter(prefix="/entities", tags=["Inferred Entities"])


@router.get("", response_model=list[EntitySummary])
def list_entities(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List inferred entity clusters sorted by risk score descending."""
    entities = (
        db.query(EntityModel)
        .order_by(EntityModel.risk_score.desc(), EntityModel.wallet_count.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        EntitySummary(
            entity_id=e.entity_id,
            cluster_type=e.cluster_type,
            wallet_count=e.wallet_count,
            risk_score=e.risk_score,
            confidence_score=e.confidence_score,
            total_volume_btc=e.total_volume_btc,
        )
        for e in entities
    ]


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity_detail(entity_id: str, db: Session = Depends(get_db)):
    """Retrieve full profile for an inferred entity cluster."""
    entity = db.query(EntityModel).filter(EntityModel.entity_id == entity_id).first()
    if not entity:
        # Try searching by member wallet
        all_ents = db.query(EntityModel).all()
        for e in all_ents:
            if entity_id in e.member_wallets:
                entity = e
                break

    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found")

    # Fetch recent transactions
    wallets_set = set(entity.member_wallets)
    all_txs = db.query(TransactionModel).all()
    entity_txs = [
        tx for tx in all_txs
        if any(w in wallets_set for w in tx.input_addresses + tx.output_addresses)
    ]

    recent = []
    associated_ips = set()
    detected_motifs = set()

    for tx in entity_txs[:10]:
        if tx.src_ip and tx.src_ip != "0.0.0.0":
            associated_ips.add(tx.src_ip)
        for m in tx.detected_motifs:
            detected_motifs.add(m)
        recent.append({
            "txid": tx.txid,
            "timestamp": tx.timestamp,
            "volume_btc": tx.output_amount,
            "risk_score": tx.risk_score,
            "alert_level": tx.alert_level,
        })

    return EntityResponse(
        entity_id=entity.entity_id,
        cluster_type=entity.cluster_type,
        wallet_count=entity.wallet_count,
        member_wallets=entity.member_wallets,
        cluster_confidence=entity.cluster_confidence,
        risk_score=entity.risk_score,
        confidence_score=entity.confidence_score,
        total_volume_btc=entity.total_volume_btc,
        first_seen=entity.first_seen,
        last_seen=entity.last_seen,
        cluster_features=entity.cluster_features,
        cluster_evidence=entity.cluster_evidence,
        recent_transactions=recent,
        detected_motifs=list(detected_motifs),
        associated_ips=list(associated_ips),
    )
