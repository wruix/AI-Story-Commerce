"""Product routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import product, project as project_crud
from app.schemas import ProductCreate, ProductUpdate, ProductOut

router = APIRouter()


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(obj_in: ProductCreate, db: AsyncSession = Depends(get_db)):
    db_project = await project_crud.get(db, id=obj_in.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await product.create(db, obj_in=obj_in)


@router.get("", response_model=List[ProductOut])
async def list_products(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if project_id:
        return await product.get_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return await product.get_multi(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await product.get(db, id=product_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_obj


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: str, obj_in: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await product.get(db, id=product_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return await product.update(db, db_obj=db_obj, obj_in=obj_in)


@router.delete("/{product_id}", response_model=dict)
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    db_obj = await product.remove(db, id=product_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
