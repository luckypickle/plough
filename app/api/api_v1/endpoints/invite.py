import datetime
from typing import Any, List,Optional
import json
import pytz
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from app import crud, models, schemas, utils
from app.api import deps
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.utils import send_new_account_email
from app.bazi import BaZi
import time
router = APIRouter()

tz = pytz.timezone('Asia/Shanghai')
@router.post("/invite_info", response_model=schemas.InviteForInfo)
def get_invite_info(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
)->schemas.InviteForInfo:
    """
    Get invite info
    """
    invite_info = crud.invite.get_invite_info(db, user_id=current_user.id)
    outof_bind = 0
    register_time = int(time.mktime(current_user.create_time.timetuple()))
    if time.time() > register_time + 24 * 3600:
        outof_bind = 1
    if invite_info is None:
        invite_code = utils.generate_invite_code()
        if current_user.phone is None:
            phone = current_user.email
        else:
            phone = current_user.phone
        invite_obj = schemas.InviteCreate(
            user_id=current_user.id,
            phone=phone,
            invite_code=invite_code,
            register_time=current_user.create_time.astimezone(tz)
        )
        crud.invite.create(db, obj_in=invite_obj)
        ret_obj = schemas.InviteForInfo(
            user_id=current_user.id,
            phone=phone,
            invite_code=invite_code,
            level=0,
            invited_count=0,
            invited_place_order_count=0,
            prev_user_phone="",
            total_amount=0,
            uncollect_amount=0,
            register_time=current_user.create_time.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
            outof_bind_time=outof_bind
        )
    else:
        prev_user = crud.user.get(db, id=invite_info.prev_invite)
        prev_phone = ""
        if prev_user is not None:
            if prev_user.phone is None:
                prev_phone = prev_user.email
            else:
                prev_phone = prev_user.phone
        total_amount = crud.reward.get_first_total_reward(db,user_id=current_user.id)+ crud.reward.get_second_total_reward(db,user_id=current_user.id)
        temp_phone = invite_info.phone
        if invite_info.phone is None or invite_info.phone == "":
            user_obj = crud.user.get(db, id=invite_info.user_id)
            temp_phone = user_obj.email
        ret_obj = schemas.InviteForInfo(
            user_id= invite_info.user_id,
            phone= temp_phone,
            invite_code=invite_info.invite_code,
            level=invite_info.current_level,
            invited_count=crud.invite.get_prev_count(db, user_id=invite_info.user_id, status=1)+crud.invite.get_prev_count(db, user_id=invite_info.user_id, status=2),
            invited_place_order_count=crud.invite.get_prev_count(db,user_id=invite_info.user_id,status=2),
            prev_user_phone=prev_phone,
            total_amount=total_amount,
            uncollect_amount=total_amount-crud.withdraw.get_withdraw_amount(db,user_id=current_user.id),
            outof_bind_time=outof_bind
        )
        if invite_info.phone is None or invite_info.phone == "":
            crud.invite.update(db,db_obj=invite_info,obj_in={"phone":temp_phone})
    return ret_obj

@router.get("/invite_url",response_model=Any)
def get_invite_url(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
)->Any:
    """
    Get my invite url
    """
    invite_code = crud.invite.get_invite_code(db,user_id=current_user.id)
    if invite_code == "" or invite_code is None:
        raise HTTPException(
            status_code=400,
            detail="Don`t have invite code",
        )
    return {
        'invite_url':'wwww.lol.com/'+invite_code,
    }
@router.get("/invite_poster",response_model=Any)
def get_invite_poster(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
)->Any:
    """
    Get my invite poster
    """
    invite_code = crud.invite.get_invite_code(db, user_id=current_user.id)
    if invite_code == "" or invite_code is None:
        raise HTTPException(
            status_code=400,
            detail="Don`t have invite code",
        )
    return {
        'invite_poster':'i`m photo '+invite_code,
    }
@router.post("/bind_invite_code",response_model=Any)
def bind_invite_code(
    *,
    invite_code:str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
)->Any:
    """
    Bind invite code
    """
    user_invite_obj = crud.invite.get_invite_info(db, user_id=current_user.id)
    if user_invite_obj is None:
        raise HTTPException(
            status_code=400,
            detail="Should get invite info first",
        )
    register_time = int(time.mktime(current_user.create_time.timetuple()))
    if time.time() > register_time+24*3600:
        raise HTTPException(
            status_code=400,
            detail="Out of bind time",
        )
    if user_invite_obj.invite_code == invite_code:
        raise HTTPException(
            status_code=400,
            detail="Cant bind youself",
        )
    inviter = crud.invite.get_invite_user(db,invite_code=invite_code)
    if inviter is None:
        raise HTTPException(
            status_code=400,
            detail="Invite code is not exist",
        )

    prev_inviter = crud.invite.get_invite_user(db, invite_code=inviter.invite_code)
    prev_prev_user_id = None
    if prev_inviter is not None:
        prev_prev_user_id=prev_inviter.prev_invite
        if user_invite_obj.invite_code == prev_inviter.invite_code or prev_inviter.prev_invite == user_invite_obj.user_id\
                or prev_inviter.prev_prev_invite == user_invite_obj.user_id:
            raise HTTPException(
                status_code=400,
                detail="Invite cant be a circle",
            )
    update_obj = schemas.InviteUpdate(
        prev_invite=inviter.user_id,
        prev_prev_invite=prev_prev_user_id
    )
    crud.invite.update(db, db_obj=user_invite_obj, obj_in=update_obj)


    return {
        'success': True
    }
@router.get("/invite_users_info",response_model=Any)
def invite_users(
    *,
    phone:str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
)->Any:
    """
    Get invited users info
    """
    user_obj = crud.user.get_by_phone(db,phone=phone)
    if user_obj is None:
        raise HTTPException(
            status_code=400,
            detail="User`s phone doesnt exist",
        )
    ret = schemas.InvitedDetailUsers(total=0,invited_count=0,invited_order_count=0, invited_users=[])
    invited_count, invited_users = crud.invite.get_invited_users(db, user_id=user_obj.id, skip=skip, limit=limit)
    if invited_count == 0:
        return ret
    ret.total = invited_count

    for invited_user_obj in invited_users:
        order_time = None
        if invited_user_obj.first_order_time is not None:
            order_time = invited_user_obj.first_order_time.strftime("%Y-%m-%d %H:%M:%S")
        register_time = (invited_user_obj.register_time+datetime.timedelta(hours=8)).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
        temp_phone = invited_user_obj.phone
        if invited_user_obj.phone is None or invited_user_obj.phone == "":
            user_obj = crud.user.get(db,id=invited_user_obj.user_id)
            temp_phone = user_obj.email
        ret.invited_users.append(schemas.InvitedUserDetail(
            user_id=invited_user_obj.user_id,
            phone=temp_phone,
            register_time=register_time,
            first_order_time=order_time,
            status=invited_user_obj.order_status,
        ))
        if invited_user_obj.phone is None or invited_user_obj.phone == "":
            crud.invite.update(db,db_obj=invited_user_obj,obj_in={"phone":temp_phone})

    ret.invited_count = crud.invite.get_prev_count(db, user_id=user_obj.id, status=1)+crud.invite.get_prev_count(db, user_id=user_obj.id, status=2)
    ret.invited_order_count = crud.invite.get_prev_count(db, user_id=user_obj.id, status=2)
    return ret
@router.get("/invite_order_infos",response_model=Any)
def invite_order_info(
    *,
    phone:str = None,
    prev_phone:str=None,
    prev_prev_phone:str=None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
)->Any:
    """
    Get invited users order info
    """
    user_id = None
    prev_user_id=None
    prev_prev_user_id=None

    if phone is not None and phone != "":
        user_obj = crud.user.get_by_phone(db,phone=phone)
        if user_obj is None:
            raise HTTPException(
                status_code=400,
                detail="User`s phone doesnt exist",
            )
        user_id = user_obj.id
    if prev_phone is not None and prev_phone != "":
        prev_user_obj = crud.user.get_by_phone(db, phone=prev_phone)
        if prev_user_obj is None:
            raise HTTPException(
                status_code=400,
                detail="User`s prev phone doesnt exist",
            )
        prev_user_id= prev_user_obj.id
    if prev_prev_phone is not None and prev_prev_phone != "":
        prev_prev_user_obj = crud.user.get_by_phone(db, phone=prev_prev_phone)
        if prev_prev_user_obj is None:
            raise HTTPException(
                status_code=400,
                detail="User`s prev phone doesnt exist",
            )
        prev_prev_user_id=prev_prev_user_obj.id
    ret = schemas.InviteOrderInfo(total=0, invite_orders=[])
    invited_count, invited_users = crud.invite.get_invited_users_with_condition(db, user_id=user_id,
                                                                                prev_user_id=prev_user_id,
                                                                                prev_prev_user_id=prev_prev_user_id,
                                                                                skip=skip,
                                                                                limit=limit)
    if invited_count == 0:
        return ret
    ret.total = invited_count
    for invited_user_obj in invited_users:
        prev_phone = None
        prev_prev_phone = None
        if invited_user_obj.prev_invite is not None:
            prev_user = crud.user.get(db,id=invited_user_obj.prev_invite)
            if prev_user is not None:
                if prev_user.phone is None:
                    prev_phone = prev_user.email
                else:
                    prev_phone = prev_user.phone
        if invited_user_obj.prev_invite is not None:
            prev_prev_user = crud.user.get(db,id=invited_user_obj.prev_prev_invite)
            if prev_prev_user is not None:
                if prev_prev_user.phone is None:
                    prev_prev_phone = prev_prev_user.email
                else:
                    prev_prev_phone = prev_prev_user.phone
        ret.invite_orders.append(schemas.InviteOrder(
            phone=invited_user_obj.phone,
            register_time=invited_user_obj.register_time.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
            prev_phone=prev_phone,
            prev_prev_phone=prev_prev_phone,
            order_count=crud.order.get_order_count(db,user_id=invited_user_obj.user_id),
            order_amount=crud.order.get_order_amount(db,user_id=invited_user_obj.user_id)
        ))
    return ret
