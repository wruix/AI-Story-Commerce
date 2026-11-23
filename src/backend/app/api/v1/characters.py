"""Character routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import character
from app.schemas import CharacterCreate, CharacterUpdate, CharacterOut

router = APIRouter()


@router.post("", response_model=CharacterOut, status_code=201)
async def create_character(obj_in: CharacterCreate, db: AsyncSession = Depends(get_db)):
    return await character.create(db, obj_in=obj_in)


@router.get("", response_model=List[CharacterOut])
async def list_characters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    return await character.get_multi(db, skip=skip, limit=limit)


@router.get("/{character_id}", response_model=CharacterOut)
async def get_character(character_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await character.get(db, id=character_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_obj


@router.put("/{character_id}", response_model=CharacterOut)
async def update_character(
    character_id: str, obj_in: CharacterUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await character.get(db, id=character_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Character not found")
    return await character.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{character_id}", response_model=dict)
async def delete_character(character_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await character.remove(db, id=character_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"message": "Character deleted"}
