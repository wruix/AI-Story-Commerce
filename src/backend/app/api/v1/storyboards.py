"""Storyboard routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import storyboard, script as script_crud
from app.schemas import StoryboardCreate, StoryboardUpdate, StoryboardOut

router = APIRouter()


@router.post("", response_model=StoryboardOut, status_code=201)
async def create_storyboard(obj_in: StoryboardCreate, db: AsyncSession = Depends(get_db)):
    db_script = await script_crud.get(db, id=obj_in.script_id)
    if not db_script:
        raise HTTPException(status_code=404, detail="Script not found")
    return await storyboard.create(db, obj_in=obj_in)


@router.get("", response_model=List[StoryboardOut])
async def list_storyboards(
    script_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if script_id:
        return await storyboard.get_by_script(db, script_id=script_id, skip=skip, limit=limit)
    return await storyboard.get_multi(db, skip=skip, limit=limit)


@router.get("/{storyboard_id}", response_model=StoryboardOut)
async def get_storyboard(storyboard_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await storyboard.get(db, id=storyboard_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    return db_obj


@router.put("/{storyboard_id}", response_model=StoryboardOut)
async def update_storyboard(
    storyboard_id: str, obj_in: StoryboardUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await storyboard.get(db, id=storyboard_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    return await storyboard.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{storyboard_id}", response_model=dict)
async def delete_storyboard(storyboard_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await storyboard.remove(db, id=storyboard_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    return {"message": "Storyboard deleted"}
