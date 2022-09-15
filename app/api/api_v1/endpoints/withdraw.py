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
    left_amount = crud.reward.get_first_total_reward(db, user_id=current_user.id) \
    + crud.reward.get_second_total_reward(db,user_id=current_user.id)\
    - crud.withdraw.get_withdraw_amount(db, user_id=current_user.id)
    if amount > left_amount:
        raise HTTPException(status_code=400, detail="Dont have enough money")
    withdraw_obj = schemas.WithdrawCreate(
        user_id=current_user.id,
        pay_name=real_name,
        pay_card_num=card_num,
        pay_amount=amount,
        pay_status=0,
        phone=current_user.phone,
        create_user_time=current_user.create_time
    )
    crud.withdraw.create(db,obj_in=withdraw_obj)
    return ""

@router.get("/withdraw_info",response_model=Any)
def withdraw_info(
    *,
    phone:str = None,
    state:int = 3,
    start_time:int=0,
    end_time:int=0,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
)->Any:
    """
    super user get withdraw orders
    等级：0-未打款,1-已打款,2-拒绝打款
    """
    user_obj = crud.user.get_by_phone(db,phone=phone)
    user_id = None
    if user_obj is not None:
        user_id = user_obj.id
    if end_time < start_time:
        raise HTTPException(status_code=400, detail="Incorrect start time")
    if start_time == 0:
        start_time = None
    ret = schemas.WithdrawItems(total=0,items=[])
    total,items = crud.withdraw.get_withdraw_items(db,user_id=user_id,state=state,start_time=start_time,end_time=end_time)
    if total == 0:
        return ret
    ret.total = total
    for withdraw_obj in items:
        ret.items.append(schemas.WithdrawInfo(
            pay_name=withdraw_obj.pay_name,
            pay_card_num=withdraw_obj.pay_card_num,
            pay_amount=withdraw_obj.pay_amount,
            pay_status=withdraw_obj.pay_status,
            register_time=withdraw_obj.create_user_time.strftime("%Y-%m-%d %H:%M:%S"),
            id=withdraw_obj.id,
            order_time=withdraw_obj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            phone=withdraw_obj.phone
        ))
    return ret
@router.post("/change_state",response_model=Any)
def change_withdraw_state(
    *,
    withdraw_id:int,
    state:int = 1,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
)->Any:
    """
    change withdraw state
    等级：0-未打款,1-已打款,2-拒绝打款
    """
    withdraw_obj = crud.withdraw.get_by_id(db,id=withdraw_id)
    if withdraw_obj is None:
        raise HTTPException(status_code=400, detail="withdraw bill is not exist")
    withdraw_update=schemas.WithdrawUpdate(
        pay_status=state
    )
    crud.withdraw.update(db,db_obj=withdraw_obj,obj_in=withdraw_update)
    return ""