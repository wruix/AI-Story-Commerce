"""Performance metric routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import performance_metric, publishing_record as publishing_record_crud
from app.schemas import PerformanceMetricCreate, PerformanceMetricUpdate, PerformanceMetricOut

router = APIRouter()


@router.post("", response_model=PerformanceMetricOut, status_code=201)
async def create_performance_metric(obj_in: PerformanceMetricCreate, db: AsyncSession = Depends(get_db)):
    db_record = await publishing_record_crud.get(db, id=obj_in.publishing_record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Publishing record not found")
    return await performance_metric.create(db, obj_in=obj_in)


@router.get("", response_model=List[PerformanceMetricOut])
async def list_performance_metrics(
    publishing_record_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if publishing_record_id:
        return await performance_metric.get_by_publishing_record(
            db, publishing_record_id=publishing_record_id, skip=skip, limit=limit
        )
    return await performance_metric.get_multi(db, skip=skip, limit=limit)


@router.get("/{metric_id}", response_model=PerformanceMetricOut)
async def get_performance_metric(metric_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await performance_metric.get(db, id=metric_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Performance metric not found")
    return db_obj


@router.put("/{metric_id}", response_model=PerformanceMetricOut)
async def update_performance_metric(
    metric_id: str, obj_in: PerformanceMetricUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await performance_metric.get(db, id=metric_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Performance metric not found")
    return await performance_metric.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{metric_id}", response_model=dict)
async def delete_performance_metric(metric_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await performance_metric.remove(db, id=metric_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Performance metric not found")
    return {"message": "Performance metric deleted"}
