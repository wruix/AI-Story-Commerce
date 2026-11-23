"""Media asset routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import media_asset, storyboard as storyboard_crud
from app.schemas import MediaAssetCreate, MediaAssetUpdate, MediaAssetOut

router = APIRouter()


@router.post("", response_model=MediaAssetOut, status_code=201)
async def create_media_asset(obj_in: MediaAssetCreate, db: AsyncSession = Depends(get_db)):
    if obj_in.storyboard_id:
        db_storyboard = await storyboard_crud.get(db, id=obj_in.storyboard_id)
        if not db_storyboard:
            raise HTTPException(status_code=404, detail="Storyboard not found")
    return await media_asset.create(db, obj_in=obj_in)


@router.get("", response_model=List[MediaAssetOut])
async def list_media_assets(
    storyboard_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if storyboard_id:
        return await media_asset.get_by_storyboard(db, storyboard_id=storyboard_id, skip=skip, limit=limit)
    return await media_asset.get_multi(db, skip=skip, limit=limit)


@router.get("/{media_asset_id}", response_model=MediaAssetOut)
async def get_media_asset(media_asset_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await media_asset.get(db, id=media_asset_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return db_obj


@router.put("/{media_asset_id}", response_model=MediaAssetOut)
async def update_media_asset(
    media_asset_id: str, obj_in: MediaAssetUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await media_asset.get(db, id=media_asset_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return await media_asset.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{media_asset_id}", response_model=dict)
async def delete_media_asset(media_asset_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await media_asset.remove(db, id=media_asset_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return {"message": "Media asset deleted"}
