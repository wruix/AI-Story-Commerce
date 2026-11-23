"""Story idea routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import story_idea, product as product_crud
from app.schemas import StoryIdeaCreate, StoryIdeaUpdate, StoryIdeaOut

router = APIRouter()


@router.post("", response_model=StoryIdeaOut, status_code=201)
async def create_story_idea(obj_in: StoryIdeaCreate, db: AsyncSession = Depends(get_db)):
    db_product = await product_crud.get(db, id=obj_in.product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await story_idea.create(db, obj_in=obj_in)


@router.get("", response_model=List[StoryIdeaOut])
async def list_story_ideas(
    product_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if product_id:
        return await story_idea.get_by_product(db, product_id=product_id, skip=skip, limit=limit)
    return await story_idea.get_multi(db, skip=skip, limit=limit)


@router.get("/{story_idea_id}", response_model=StoryIdeaOut)
async def get_story_idea(story_idea_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await story_idea.get(db, id=story_idea_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Story idea not found")
    return db_obj


@router.put("/{story_idea_id}", response_model=StoryIdeaOut)
async def update_story_idea(
    story_idea_id: str, obj_in: StoryIdeaUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await story_idea.get(db, id=story_idea_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Story idea not found")
    return await story_idea.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{story_idea_id}", response_model=dict)
async def delete_story_idea(story_idea_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await story_idea.remove(db, id=story_idea_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Story idea not found")
    return {"message": "Story idea deleted"}
