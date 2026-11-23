"""Prompt template routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import prompt_template
from app.schemas import PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateOut

router = APIRouter()


@router.post("", response_model=PromptTemplateOut, status_code=201)
async def create_prompt_template(obj_in: PromptTemplateCreate, db: AsyncSession = Depends(get_db)):
    return await prompt_template.create(db, obj_in=obj_in)


@router.get("", response_model=List[PromptTemplateOut])
async def list_prompt_templates(
    agent_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if agent_type:
        return await prompt_template.get_by_agent_type(db, agent_type=agent_type, skip=skip, limit=limit)
    return await prompt_template.get_multi(db, skip=skip, limit=limit)


@router.get("/{template_id}", response_model=PromptTemplateOut)
async def get_prompt_template(template_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await prompt_template.get(db, id=template_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return db_obj


@router.put("/{template_id}", response_model=PromptTemplateOut)
async def update_prompt_template(
    template_id: str, obj_in: PromptTemplateUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await prompt_template.get(db, id=template_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return await prompt_template.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{template_id}", response_model=dict)
async def delete_prompt_template(template_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await prompt_template.remove(db, id=template_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return {"message": "Prompt template deleted"}
