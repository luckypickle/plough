from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import pytz
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/create_or_update_divination_settings", response_model=schemas.DivinationSettingsQuery)
def create_or_update_divination_settings(
        *,
        db: Session = Depends(deps.get_db),
        entry_type: int = 0,
        show_type: int = 0,
        analysis_isClose: bool = False,
        taimingshen_isClose: bool = False,
        xingyun_isClose: bool = False,
        liuri_isClose: bool = False,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    userId,masterId = None,None
    divination_settings = None
    if isinstance(current_user, models.User):
        userId=current_user.id
        divination_settings = crud.divination_settings.get_by_user_id(db=db, user_id=userId)
    elif isinstance(current_user,models.Master):
        masterId=current_user.id
        divination_settings = crud.divination_settings.get_by_master_id(db=db, master_id=current_user.id)
    else:
        raise HTTPException(
            status_code=404,
            detail="Insufficient permissions",
        )   
    divination_settings_in = schemas.DivinationSettings(
        user_id=userId,
        master_id=masterId,        
        entry_type=entry_type,
        show_type=show_type,
        analysis_isClose=analysis_isClose,
        taimingshen_isClose=taimingshen_isClose,
        xingyun_isClose=xingyun_isClose,
        liuri_isClose=liuri_isClose
    )
    if divination_settings is None:
        crud.divination_settings.create_divination_settings(db, divination_settings=divination_settings_in)
    else:
        crud.divination_settings.update(db, db_obj=divination_settings, obj_in=divination_settings_in)
    return divination_settings_in

@router.get("/divination_settings", response_model=schemas.DivinationSettingsQuery)
def get_divination_settings(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    divination_settings=None
    if isinstance(current_user, models.User):
        divination_settings = crud.divination_settings.get_by_user_id(db=db, user_id=current_user.id)
    elif isinstance(current_user,models.Master):
        divination_settings = crud.divination_settings.get_by_master_id(db=db, master_id=current_user.id)
    else:
        raise HTTPException(
            status_code=404,
            detail="Insufficient permissions",
        )   
    if divination_settings is None:
        divination_settings=schemas.DivinationSettingsQuery()
    return divination_settings
