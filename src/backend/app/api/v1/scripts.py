"""Script routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import script, story_idea as story_idea_crud
from app.schemas import ScriptCreate, ScriptUpdate, ScriptOut

router = APIRouter()


@router.post("", response_model=ScriptOut, status_code=201)
async def create_script(obj_in: ScriptCreate, db: AsyncSession = Depends(get_db)):
    db_idea = await story_idea_crud.get(db, id=obj_in.story_idea_id)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Story idea not found")
    return await script.create(db, obj_in=obj_in)


@router.get("", response_model=List[ScriptOut])
async def list_scripts(
    story_idea_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if story_idea_id:
        return await script.get_by_story_idea(db, story_idea_id=story_idea_id, skip=skip, limit=limit)
    return await script.get_multi(db, skip=skip, limit=limit)


@router.get("/{script_id}", response_model=ScriptOut)
async def get_script(script_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await script.get(db, id=script_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Script not found")
    return db_obj


@router.put("/{script_id}", response_model=ScriptOut)
async def update_script(
    script_id: str, obj_in: ScriptUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await script.get(db, id=script_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Script not found")
    return await script.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{script_id}", response_model=dict)
async def delete_script(script_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await script.remove(db, id=script_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Script not found")
    return {"message": "Script deleted"}
