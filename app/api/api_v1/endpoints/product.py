import logging
import json
import time
from random import sample
from string import ascii_letters, digits
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings

router = APIRouter()


@router.get("/list", response_model=List[schemas.ProductForOrder])
def read_product(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve products.
    """
    products = crud.product.get_multi_by_sort(db, skip=skip, limit=limit)
    ret_obj = []
    for p in products:
        if p.status !=1:
            continue
        ret_obj.append(schemas.ProductForOrder(
            id=p.id,
            name=p.name,
            desc=p.desc
        ))
    return ret_obj
@router.get("/listWithPrice", response_model=List[schemas.ProductForOrderPrice])
def read_product(
        db: Session = Depends(deps.get_db),
        master_id:int =-1,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve products.
    """
    products = crud.product.get_multi_by_sort(db, skip=skip, limit=limit)
    prices = crud.masterProduct.get_master_product_price(db,master_id)
    master = crud.master.get(db,master_id)
    if not crud.user.is_superuser(current_user):
        if master is None or master.status!=1:
            raise HTTPException(status_code=400, detail="The master id not in this system.",)
    ret_obj = []
    cache_p = {}
    if master.price is None:

        normal_price = 0
    else:
        normal_price = int(master.price)
    for r in prices:
        cache_p[str(r.product_id)] = r.price
    for p in products:
        if p.status !=1:
            continue
        if str(p.id) in cache_p:
            tmp_price = cache_p[str(p.id)]
        else:
            tmp_price = normal_price

        ret_obj.append(schemas.ProductForOrderPrice(
            id=p.id,
            name=p.name,
            desc=p.desc,
            price=tmp_price
        ))
    return ret_obj


@router.get("/info", response_model=List[schemas.Product])
def read_product(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve products (admin only).
    """
    products = crud.product.get_multi_by_sort(db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=schemas.Product)
def create_product(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.ProductCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new product. (superuser only)
    """
    product = crud.master.get_by_name(db, name=obj_in.name)
    if product:
        raise HTTPException(
            status_code=400,
            detail="The product with this name already exists in the system.",
        )
    product = crud.product.create(db, obj_in=obj_in)
    return product


@router.put("/{id}", response_model=schemas.Product)
def update_product(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        obj_in: schemas.ProductUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an product.
    """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = crud.product.update(db=db, db_obj=product, obj_in=obj_in)
    return product

