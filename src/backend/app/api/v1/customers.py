"""Customer routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import customer
from app.schemas import CustomerCreate, CustomerUpdate, CustomerOut

router = APIRouter()


@router.post("", response_model=CustomerOut, status_code=201)
async def create_customer(obj_in: CustomerCreate, db: AsyncSession = Depends(get_db)):
    db_obj = await customer.get_by_name(db, name=obj_in.name)
    if db_obj:
        raise HTTPException(status_code=400, detail="Customer with this name already exists")
    return await customer.create(db, obj_in=obj_in)


@router.get("", response_model=List[CustomerOut])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    return await customer.get_multi(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await customer.get(db, id=customer_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_obj


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: str, obj_in: CustomerUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await customer.get(db, id=customer_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return await customer.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{customer_id}", response_model=dict)
async def delete_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await customer.remove(db, id=customer_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted"}
