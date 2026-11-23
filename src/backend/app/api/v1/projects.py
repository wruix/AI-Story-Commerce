"""Project routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import project
from app.schemas import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter()


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(obj_in: ProjectCreate, db: AsyncSession = Depends(get_db)):
    db_obj = await project.get_by_name(db, name=obj_in.name)
    if db_obj:
        raise HTTPException(status_code=400, detail="Project with this name already exists")
    return await project.create(db, obj_in=obj_in)


@router.get("", response_model=List[ProjectOut])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    return await project.get_multi(db, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await project.get(db, id=project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_obj


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str, obj_in: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await project.get(db, id=project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return await project.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await project.remove(db, id=project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}
