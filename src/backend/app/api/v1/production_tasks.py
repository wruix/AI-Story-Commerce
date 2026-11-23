"""Production task routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import production_task, storyboard as storyboard_crud
from app.schemas import ProductionTaskCreate, ProductionTaskUpdate, ProductionTaskOut

router = APIRouter()


@router.post("", response_model=ProductionTaskOut, status_code=201)
async def create_production_task(obj_in: ProductionTaskCreate, db: AsyncSession = Depends(get_db)):
    if obj_in.storyboard_id:
        db_storyboard = await storyboard_crud.get(db, id=obj_in.storyboard_id)
        if not db_storyboard:
            raise HTTPException(status_code=404, detail="Storyboard not found")
    return await production_task.create(db, obj_in=obj_in)


@router.get("", response_model=List[ProductionTaskOut])
async def list_production_tasks(
    storyboard_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if storyboard_id:
        return await production_task.get_by_storyboard(db, storyboard_id=storyboard_id, skip=skip, limit=limit)
    return await production_task.get_multi(db, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=ProductionTaskOut)
async def get_production_task(task_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await production_task.get(db, id=task_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Production task not found")
    return db_obj


@router.put("/{task_id}", response_model=ProductionTaskOut)
async def update_production_task(
    task_id: str, obj_in: ProductionTaskUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await production_task.get(db, id=task_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Production task not found")
    return await production_task.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{task_id}", response_model=dict)
async def delete_production_task(task_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await production_task.remove(db, id=task_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Production task not found")
    return {"message": "Production task deleted"}
