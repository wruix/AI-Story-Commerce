"""Audit log routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import audit_log
from app.schemas import AuditLogCreate, AuditLogOut

router = APIRouter()


@router.post("", response_model=AuditLogOut, status_code=201)
async def create_audit_log(obj_in: AuditLogCreate, db: AsyncSession = Depends(get_db)):
    return await audit_log.create(db, obj_in=obj_in)


@router.get("", response_model=List[AuditLogOut])
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    return await audit_log.get_recent(db, skip=skip, limit=limit)


@router.get("/{log_id}", response_model=AuditLogOut)
async def get_audit_log(log_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await audit_log.get(db, id=log_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return db_obj
