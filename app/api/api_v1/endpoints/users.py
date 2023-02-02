import datetime
from typing import Any, List
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

from app.bazi import BaZi
from app.bazi.bazi import  convert_lunar_to_solar,get_wuxing_by_selectyear
import time
from app.cos_utils import get_read_url
from  app.im_utils import register_account

router = APIRouter()


@router.get("/list")
def read_users(
        db: Session = Depends(deps.get_db),
        user_phone: str = None,
        level :int = 5,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    user_id = None
    user_obj = crud.user.get_by_phone(db,phone=user_phone)
    if user_obj is not None:
        user_id = user_obj.id
    total, users = crud.user.get_user_summary(db, user_id=user_id,level=level,skip=skip, limit=limit)

    invite_users = []
    for user in users:
        level = 0
        if user.level is not None:
            level = user.level
        invite_users.append(schemas.InviteSummary(
            id=user.id,
            create_time=user.create_time,
            order_count=user.order_count,
            order_amount=user.order_amount,
            phone=user.phone,
            level=level,
            first_order_count=crud.invite.get_prev_count(db,user_id=user.id,status=1)+crud.invite.get_prev_count(db,user_id=user.id,status=2),
            first_order_amount=crud.reward.get_total_reward_amount(db,user_id=user.id,prev_prev_option=False),
            second_order_count=crud.invite.get_prev_prev_count(db,user_id=user.id,status=1)+crud.invite.get_prev_prev_count(db,user_id=user.id,status=2),
            second_order_amount=crud.reward.get_total_reward_amount(db,user_id=user.id,prev_prev_option=True),
            total_reward_amount=crud.reward.get_first_total_reward(db,user_id=user.id)+ crud.reward.get_second_total_reward(db,user_id=user.id),
            withdraw_reward_amount=crud.withdraw.get_withdraw_amount(db,user_id=user.id)
        ))
    return {
        "total": total,
        "users": invite_users
    }


@router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_phone(db, phone=user_in.phone)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create_superuser(db, obj_in=user_in)
    # if settings.EMAILS_ENABLED and user_in.email:
    #     send_new_account_email(
    #         email_to=user_in.email, username=user_in.email, password=user_in.password
    #     )
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        password: str = Body(None),
        full_name: str = Body(None),
        user_name: str = Body(None),
        email: EmailStr = Body(None),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if user_name is not None:
        user_in.user_name = user_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user



@router.post("/open", response_model=schemas.User)
def create_user_open(
        *,
        db: Session = Depends(deps.get_db),
        phone: str = Body(...),
        password: str = Body(...),
        invite_code:str=Body(None),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    prev_user = None
    if invite_code is not None and invite_code != "":
        prev_user = crud.invite.get_invite_user(db, invite_code=invite_code)
        if prev_user is None:
            raise HTTPException(
                status_code=403,
                detail="邀请码错误",
            )
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    valid_mpcod,user = crud.user.register(db,phone=phone,verify_code=password)
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="您已完成注册，请打开五行演义APP进行排盘批盘吧！",
        )
    phone_or_email = phone
    if phone_or_email.count("@") != 0:
        phone_or_email = phone
    else:
        phone_or_email = phone[:3] + "****" + phone[-4:]
    ret = register_account(get_read_url("3bf8616fe6c23c0c465527ec80397b24.png"), 0, "user_"+str(user.id), phone_or_email)
    if ret:
        crud.user.update(db,db_obj=user,obj_in=schemas.UserUpdate(im_status=1))
    if not valid_mpcod:
        raise HTTPException(
            status_code=400,
            detail="验证码错误",
        )
    #user = crud.user.get_by_name(db, name=user_name)
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="您已完成注册，请打开五行演义APP进行排盘批盘吧！",
        )
    '''
    user_in = schemas.UserCreate(
        password=password,
        email=email,
        user_name=user_name,
        phone=phone)
    user = crud.user.create(db, obj_in=user_in)
'''
    tz = pytz.timezone('Asia/Shanghai')
    if prev_user is not None:
        invite_code_user = utils.generate_invite_code()
        invite_obj = schemas.InviteCreate(
            user_id=user.id,
            phone=phone,
            invite_code=invite_code_user,
            register_time=user.create_time.astimezone(tz),
            prev_invite=prev_user.user_id,
            prev_prev_invite=prev_user.prev_invite
        )
        crud.invite.create(db, obj_in=invite_obj)
    else:
        invite_code_user = utils.generate_invite_code()
        invite_obj = schemas.InviteCreate(
            user_id=user.id,
            phone=phone,
            invite_code=invite_code_user,
            register_time=user.create_time.astimezone(tz)
        )
        crud.invite.create(db, obj_in=invite_obj)
    return user


@router.get("/divination", response_model=Any)
def get_divination(
        *,
        db: Session = Depends(deps.get_db),
        name: str = '',
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        sex: int = 0,
        location: str = '',
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get divination.
    """
    bazi = BaZi(year, month, day, hour, sex)
    divination = bazi.get_detail()
    return divination


# @router.get("/sizhu2year", response_model=Any)
# def get_year_from_sizhu(
#     *,
#     db: Session = Depends(deps.get_db),
#     name: str = '',
#     year: int,
#     month: int,
#     day: int,
#     hour: int,
#     minute: int = 0,
#     sex: int,
# ) -> Any:
#     """
#     Get divination.
#     """
#     bazi = BaZi(year, month, day, hour, sex)
#     divination = bazi.get_detail()
#     return divination


@router.get("/divination2", response_model=Any)
def get_saved_divination(
        *,
        db: Session = Depends(deps.get_db),
        name: str = '',
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        sex: int = 0,
        lunar:int = 0,
        run:int =0,
        location: str = '',
        is_north:bool = True,
        selectyear:int = 0,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get divination and save to database.
    """
    bazi = BaZi(year, month, day, hour, sex,lunar,run,minute)
    beatInfo = None
    if(selectyear > 0):
        beatInfo = get_wuxing_by_selectyear(selectyear)
    divination = bazi.get_detail()
    total = crud.history.get_count_by_owner(db, current_user.id)
    if lunar==1:
        year,month,day = convert_lunar_to_solar(year,month,day,run)
    history = schemas.HistoryCreate(
        owner_id=current_user.id,
        name=name,
        birthday=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
        sex=sex,
        location=location,
        status=0,
        divination=json.dumps(divination),
        isNorth=is_north,
        beat_info=beatInfo
    )
    crud.history.create_owner_divination(db, history=history)
    divination['beat_info'] = beatInfo
    return divination


@router.get("/history", response_model=List[schemas.History])
def get_history(
        skip: int = 0,
        limit: int = 100,
        user_name:str ="",
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get divination history.
    """
    history = crud.history.get_multi_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    rets = []
    for h in history:
        if user_name!="":
            if h.name.find(user_name)==-1:
                continue
        rets.append(schemas.History(
            id=h.id,
            name=h.name,
            birthday=h.birthday,
            sex=h.sex,
            location=h.location,
            divination=h.divination,
            create_time=h.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
            isNorth=h.isNorth,
            beat_info=h.beat_info
        ))
    return rets

@router.delete('/history')
def delete_history( history_id:int ,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)):

    res = crud.history.delete_history(db=db,history_id=history_id,owner_id=current_user.id)
    if res:
        return "success"
    else:
        return "failed"
@router.get("/user_statistics",response_model=Any)
def get_user_statistics(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
)-> Any:
    """
    Get user statistics info
    """
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    today_start=int(datetime.datetime(year=today.year,month=today.month,day=today.day).timestamp())
    yesterday_start = int(datetime.datetime(year=yesterday.year,month=yesterday.month,day=yesterday.day).timestamp())
    yesterday_count = crud.user.get_user_count_by_time(db,start_time=yesterday_start,end_time=today_start)
    today_count = crud.user.get_user_count_by_time(db,start_time=today_start,end_time=9999999999)
    total_count = crud.user.get_user_count_by_time(db,start_time=0,end_time=9999999999)
    order_count = crud.order.get_order_count(db,user_id=None)
    order_amount = crud.order.get_order_amount(db,user_id=None)
    return schemas.UserStatistics(
        yesterday_register=yesterday_count,
        today_register=today_count,
        total_register=total_count,
        total_order_count=order_count,
        total_payed_amount=order_amount
    )


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
        user_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
