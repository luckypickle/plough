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


@router.get("/rewards_info",response_model=Any)
def reward_list(
    *,
    user_id:str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
)->Any:
    """
    Get invited user reward info
    """
    ret = schemas.RewardDetailInfos(total=0, reward_details=[])
    total,rewards = crud.reward.get_reward_list(db,user_id=user_id,skip=skip,limit=limit)
    if total == 0:
        return ret
    ret.total = total
    for reward_obj in rewards:
        if reward_obj.prev_user_id == user_id:
            invited_user = crud.user.get(db,id=reward_obj.user_id)
            if invited_user is None:
                continue
            ret.reward_details.append(schemas.RewardDetail(
                invited_user=invited_user.phone,
                order_amount=reward_obj.amount,
                reward_amount=reward_obj.prev_amount,
                order_time=reward_obj.order_time,
                prev_prev_level=0
            ))
        elif reward_obj.prev_prev_user_id == user_id:
            invited_user = crud.user.get(db, id=reward_obj.user_id)
            prev_invited_user =crud.user.get(db, id=reward_obj.prev_user_id)
            if invited_user is None or prev_invited_user is None:
                continue
            ret.reward_details.append(schemas.RewardDetail(
                invited_user=invited_user.phone,
                prev_invited_user = prev_invited_user.phone,
                order_amount=reward_obj.amount,
                reward_amount=reward_obj.prev_prev_amount,
                order_time=reward_obj.order_time,
                prev_prev_level=1
            ))
    return ret