"""Advertisement routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import advertisement, project as project_crud
from app.schemas import AdvertisementCreate, AdvertisementUpdate, AdvertisementOut

router = APIRouter()


@router.post("", response_model=AdvertisementOut, status_code=201)
async def create_advertisement(obj_in: AdvertisementCreate, db: AsyncSession = Depends(get_db)):
    db_project = await project_crud.get(db, id=obj_in.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await advertisement.create(db, obj_in=obj_in)


@router.get("", response_model=List[AdvertisementOut])
async def list_advertisements(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if project_id:
        return await advertisement.get_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return await advertisement.get_multi(db, skip=skip, limit=limit)


@router.get("/{advertisement_id}", response_model=AdvertisementOut)
async def get_advertisement(advertisement_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await advertisement.get(db, id=advertisement_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_obj


@router.put("/{advertisement_id}", response_model=AdvertisementOut)
async def update_advertisement(
    advertisement_id: str, obj_in: AdvertisementUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await advertisement.get(db, id=advertisement_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return await advertisement.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{advertisement_id}", response_model=dict)
async def delete_advertisement(advertisement_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await advertisement.remove(db, id=advertisement_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"message": "Advertisement deleted"}
