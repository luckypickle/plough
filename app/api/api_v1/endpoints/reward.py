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
    user_id:int,
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
                order_amount=reward_obj.order_amount,
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
                order_amount=reward_obj.order_amount,
                reward_amount=reward_obj.prev_prev_amount,
                order_time=reward_obj.order_time,
                prev_prev_level=1
            ))
    return ret
@router.get("/total_infos",response_model=Any)
def total_info(
    *,
    phone:str=None,
    son_phone:str=None,
    grand_son_phone:str=None,
    level:int=0,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
)->Any:
    """
    get reward info
    level = 0 全部 1下级 2下下级
    """
    user_id = None
    son_user_id = None
    grand_son_user_id = None
    if level == 1 and (grand_son_phone != "" and grand_son_phone is not None):
        raise HTTPException(
            status_code=400,
            detail="Search condition error",
        )

    if phone is not None and phone != "":
        user_obj = crud.user.get_by_phone(db, phone=phone)
        if user_obj is None:
            raise HTTPException(
                status_code=400,
                detail="User`s phone doesnt exist",
            )
        user_id = user_obj.id
    if son_phone is not None and son_phone != "":
        son_user_obj = crud.user.get_by_phone(db, phone=son_phone)
        if son_user_obj is None:
            raise HTTPException(
                status_code=400,
                detail="User`s son phone doesnt exist",
            )
        son_user_id = son_user_obj.id
    if grand_son_phone is not None and grand_son_phone != "":
        grand_son_user_obj = crud.user.get_by_phone(db, phone=grand_son_phone)
        if grand_son_user_obj is None:
            raise HTTPException(
                status_code=400,
                detail="User`s grand son phone doesnt exist",
            )
        grand_son_user_id = grand_son_user_obj.id

    ret = schemas.RewardInfos(total=0, item=[])
    total,rewards = crud.reward.get_reward_list_condition(db,user_id=user_id,son_user_id=son_user_id,
                                                          grand_son_user_id=grand_son_user_id,level=level,skip=skip,limit=limit)

    if total == 0:
        return ret
    ret.total = total
    for reward_obj in rewards:
        if user_id is not None:
            if level == 1:
                user_obj = crud.user.get(db,id=reward_obj.user_id)
                prev_obj = crud.user.get(db,id=reward_obj.prev_user_id)
                ret.item.append(schemas.RewardInfo(
                    user_phone=prev_obj.phone,
                    register_time=prev_obj.create_time,
                    son_phone=user_obj.phone,
                    son_order_amout=reward_obj.order_amount,
                    order_time=reward_obj.order_time,
                    son_reward_amount=reward_obj.prev_amount,
                    order_level=1
                ))
            elif level == 2:
                user_obj = crud.user.get(db, id=reward_obj.user_id)
                prev_prev_obj = crud.user.get(db, id=reward_obj.prev_prev_user_id)
                ret.item.append(schemas.RewardInfo(
                    user_phone=prev_prev_obj.phone,
                    register_time=prev_prev_obj.create_time,
                    grand_son_phone=user_obj.phone,
                    grand_son_order_amount=reward_obj.order_amount,
                    grand_son_reward_amount=reward_obj.prev_prev_amount,
                    order_time=reward_obj.order_time,
                    order_level=2
                ))
            else:
                user_obj = crud.user.get(db, id=reward_obj.user_id)
                prev_obj = crud.user.get(db, id=reward_obj.prev_user_id)
                prev_prev_obj = crud.user.get(db, id=reward_obj.prev_prev_user_id)
                if prev_obj.id == user_id:
                    ret.item.append(schemas.RewardInfo(
                        user_phone=prev_obj.phone,
                        register_time=prev_obj.create_time,
                        son_phone=user_obj.phone,
                        son_order_amout=reward_obj.order_amount,
                        order_time=reward_obj.order_time,
                        son_reward_amount=reward_obj.prev_amount,
                        order_level=1
                    ))
                else:
                    ret.item.append(schemas.RewardInfo(
                        user_phone=prev_prev_obj.phone,
                        register_time=prev_prev_obj.create_time,
                        grand_son_phone=user_obj.phone,
                        grand_son_order_amount=reward_obj.order_amount,
                        grand_son_reward_amount=reward_obj.prev_prev_amount,
                        order_time=reward_obj.order_time,
                        order_level=2
                    ))
        else:
            if level == 1:
                user_obj = crud.user.get(db, id=reward_obj.user_id)
                prev_obj = crud.user.get(db, id=reward_obj.prev_user_id)
                ret.item.append(schemas.RewardInfo(
                    user_phone=prev_obj.phone,
                    register_time=prev_obj.create_time,
                    son_phone=user_obj.phone,
                    son_order_amout=reward_obj.order_amount,
                    order_time=reward_obj.order_time,
                    son_reward_amount=reward_obj.prev_amount,
                    order_level=1
                ))
            elif level == 2:
                user_obj = crud.user.get(db, id=reward_obj.user_id)
                prev_prev_obj = crud.user.get(db, id=reward_obj.prev_prev_user_id)
                ret.item.append(schemas.RewardInfo(
                    user_phone=prev_prev_obj.phone,
                    register_time=prev_prev_obj.create_time,
                    grand_son_phone=user_obj.phone,
                    grand_son_order_amount=reward_obj.order_amount,
                    grand_son_reward_amount=reward_obj.prev_prev_amount,
                    order_time=reward_obj.order_time,
                    order_level=2
                ))
            else:
                user_obj = crud.user.get(db, id=reward_obj.user_id)
                prev_obj = crud.user.get(db, id=reward_obj.prev_user_id)
                prev_prev_obj = crud.user.get(db, id=reward_obj.prev_prev_user_id)
                if grand_son_user_id is not None:
                    ret.item.append(schemas.RewardInfo(
                        user_phone=prev_prev_obj.phone,
                        register_time=prev_prev_obj.create_time,
                        grand_son_phone=user_obj.phone,
                        grand_son_order_amount=reward_obj.order_amount,
                        grand_son_reward_amount=reward_obj.prev_prev_amount,
                        order_time=reward_obj.order_time,
                        order_level=2
                    ))
                else:
                    if son_user_id is not None:
                        ret.item.append(schemas.RewardInfo(
                            user_phone=prev_obj.phone,
                            register_time=prev_obj.create_time,
                            son_phone=user_obj.phone,
                            son_order_amout=reward_obj.order_amount,
                            order_time=reward_obj.order_time,
                            son_reward_amount=reward_obj.prev_amount,
                            order_level=1
                        ))
                    else:
                        if prev_prev_obj is not None:
                            ret.item.append(schemas.RewardInfo(
                                user_phone=prev_prev_obj.phone,
                                register_time=prev_prev_obj.create_time,
                                son_phone=user_obj.phone,
                                son_order_amout=reward_obj.order_amount,
                                order_time=reward_obj.order_time,
                                son_reward_amount=reward_obj.prev_amount,
                                grand_son_phone=user_obj.phone,
                                grand_son_order_amount=reward_obj.order_amount,
                                grand_son_reward_amount=reward_obj.prev_prev_amount,
                                order_level=2
                            ))
                        else:
                            ret.item.append(schemas.RewardInfo(
                                user_phone=prev_obj.phone,
                                register_time=prev_obj.create_time,
                                son_phone=user_obj.phone,
                                son_order_amout=reward_obj.order_amount,
                                order_time=reward_obj.order_time,
                                son_reward_amount=reward_obj.prev_amount,
                                order_level=1
                            ))
    return ret
