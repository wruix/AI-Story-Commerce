"""Compliance review routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import compliance_review, advertisement as advertisement_crud
from app.schemas import ComplianceReviewCreate, ComplianceReviewUpdate, ComplianceReviewOut

router = APIRouter()


@router.post("", response_model=ComplianceReviewOut, status_code=201)
async def create_compliance_review(obj_in: ComplianceReviewCreate, db: AsyncSession = Depends(get_db)):
    db_ad = await advertisement_crud.get(db, id=obj_in.advertisement_id)
    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return await compliance_review.create(db, obj_in=obj_in)


@router.get("", response_model=List[ComplianceReviewOut])
async def list_compliance_reviews(
    advertisement_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if advertisement_id:
        return await compliance_review.get_by_advertisement(db, advertisement_id=advertisement_id, skip=skip, limit=limit)
    return await compliance_review.get_multi(db, skip=skip, limit=limit)


@router.get("/{review_id}", response_model=ComplianceReviewOut)
async def get_compliance_review(review_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await compliance_review.get(db, id=review_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Compliance review not found")
    return db_obj


@router.put("/{review_id}", response_model=ComplianceReviewOut)
async def update_compliance_review(
    review_id: str, obj_in: ComplianceReviewUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await compliance_review.get(db, id=review_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Compliance review not found")
    return await compliance_review.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{review_id}", response_model=dict)
async def delete_compliance_review(review_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await compliance_review.remove(db, id=review_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Compliance review not found")
    return {"message": "Compliance review deleted"}
