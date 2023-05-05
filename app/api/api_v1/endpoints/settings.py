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
        entry_type: int = None,
        show_type: int = None,
        analysis_isClose: bool = None,
        taimingshen_isClose: bool = None,
        xingyun_isClose: bool = None,
        liuri_isClose: bool = None,
        early_isClose: bool = None,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    divination_settings_in = {}
    if entry_type is not None:
        divination_settings_in["entry_type"]=entry_type
    if show_type is not None:
        divination_settings_in["show_type"]=show_type
    if analysis_isClose is not None:
        divination_settings_in["analysis_isClose"]=analysis_isClose
    if taimingshen_isClose is not None:
        divination_settings_in["taimingshen_isClose"]=taimingshen_isClose
    if xingyun_isClose is not None:
        divination_settings_in["xingyun_isClose"]=xingyun_isClose
    if liuri_isClose is not None:
        divination_settings_in["liuri_isClose"]=liuri_isClose
    if early_isClose is not None:
        divination_settings_in["early_isClose"]=early_isClose
    divination_settings = None
    if isinstance(current_user, models.User):
        divination_settings_in["user_id"]=current_user.id
        divination_settings = crud.divination_settings.get_by_user_id(db=db, user_id=current_user.id)
    elif isinstance(current_user,models.Master):
        divination_settings_in["master_id"]=current_user.id
        divination_settings = crud.divination_settings.get_by_master_id(db=db, master_id=current_user.id)
    else:
        raise HTTPException(
            status_code=404,
            detail="Insufficient permissions",
        )   
    if divination_settings is None:
        divination_settings = crud.divination_settings.create(db, obj_in=divination_settings_in)
    else:
        divination_settings = crud.divination_settings.update(db, db_obj=divination_settings, obj_in=divination_settings_in)
    return divination_settings

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
