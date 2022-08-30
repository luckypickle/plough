from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.bazi import BaZi

router = APIRouter()


@router.get("/query_by_order", response_model=schemas.Comment)
def read_comment_by_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comment by order.
    """
    comment = crud.comment.get_by_order_id(db, order_id=order_id)
    return comment


@router.get("/query_by_master", response_model=List[schemas.Comment])
def read_comment_by_master(
        master_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comment by master.
    """
    comments = crud.comment.get_by_master_id(db, master_id=master_id, skip=skip, limit=limit)
    return comments


@router.get("/query_by_user", response_model=List[schemas.Comment])
def read_comment_by_master(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comment by user.
    """
    comments = crud.comment.get_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    return comments


@router.post("/", response_model=schemas.Comment)
def create_comment(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.CommentCreate,
        current_user: models.User = Depends(deps.get_current_active_user),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new comment.
    """
    order = crud.order.get(db, id=obj_in.order_id)
    if not order:
        raise HTTPException(
            status_code=403,
            detail="Order not found",
        )
    if current_user.id != order.owner_id:
        raise HTTPException(
            status_code=403,
            detail="User is not order owner",
        )
    comment = crud.comment.create(db, obj_in=obj_in, master_id=order.master_id, user_id=order.owner_id)
    return comment


@router.put("/{comment_id}", response_model=schemas.Comment)
def update_comment_by_id(
        *,
        db: Session = Depends(deps.get_db),
        comment_id: int,
        obj_in: schemas.CommentUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a master. (superuser only)
    """
    order = crud.order.get(db, id=obj_in.order_id)
    if not order:
        raise HTTPException(
            status_code=403,
            detail="Order not found",
        )
    comment = crud.comment.update_by_id(db=db, obj_in=obj_in, comment_id=comment_id)
    return comment
