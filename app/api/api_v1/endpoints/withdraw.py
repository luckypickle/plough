from typing import Any, List
import json
import pytz
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.utils import send_new_account_email
from app.bazi import BaZi

router = APIRouter()

@router.post("/withdraw_money",response_model=Any)
def withdraw_money(
    *,
    amount:str,
    real_name:str,
    card_num:str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
)->Any:
    """
    Withdraw money
    """
    withdraw_obj = schemas.WithdrawCreate(
        user_id=current_user.id,
        pay_name=real_name,
        pay_card_num=card_num,
        pay_amount=amount,
        status=0
    )
    crud.withdraw.create(db,obj_in=withdraw_obj)
    return ""