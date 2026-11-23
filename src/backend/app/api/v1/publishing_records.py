"""Publishing record routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import publishing_record, advertisement as advertisement_crud
from app.schemas import PublishingRecordCreate, PublishingRecordUpdate, PublishingRecordOut

router = APIRouter()


@router.post("", response_model=PublishingRecordOut, status_code=201)
async def create_publishing_record(obj_in: PublishingRecordCreate, db: AsyncSession = Depends(get_db)):
    db_ad = await advertisement_crud.get(db, id=obj_in.advertisement_id)
    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return await publishing_record.create(db, obj_in=obj_in)


@router.get("", response_model=List[PublishingRecordOut])
async def list_publishing_records(
    advertisement_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if advertisement_id:
        return await publishing_record.get_by_advertisement(
            db, advertisement_id=advertisement_id, skip=skip, limit=limit
        )
    return await publishing_record.get_multi(db, skip=skip, limit=limit)


@router.get("/{record_id}", response_model=PublishingRecordOut)
async def get_publishing_record(record_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await publishing_record.get(db, id=record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Publishing record not found")
    return db_obj


@router.put("/{record_id}", response_model=PublishingRecordOut)
async def update_publishing_record(
    record_id: str, obj_in: PublishingRecordUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await publishing_record.get(db, id=record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Publishing record not found")
    return await publishing_record.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{record_id}", response_model=dict)
async def delete_publishing_record(record_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await publishing_record.remove(db, id=record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Publishing record not found")
    return {"message": "Publishing record deleted"}
