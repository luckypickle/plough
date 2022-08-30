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
    products = crud.product.get_multi(db, skip=skip, limit=limit)
    ret_obj = []
    for p in products:
        ret_obj.append(schemas.ProductForOrder(
            id=p.id,
            name=p.name,
            desc=p.desc
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
    products = crud.product.get_multi(db, skip=skip, limit=limit)
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
