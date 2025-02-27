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
from app.bazi.bazi import  convert_lunar_to_solar,get_wuxing_by_selectyear,get_wuxing_ganzhi
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

@router.get("/aaa", response_model=schemas.User)
def read_user_me(
        db: Session = Depends(deps.get_db)) -> Any:
    for i in range(1459,1558):
        user = crud.user.get(db, id=i)
        print(i)
    # register_account(get_read_url("3bf8616fe6c23c0c465527ec80397b24.png"), 0, "user_"+str(user.id), user.phone)




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
    divination_settings = crud.divination_settings.get_by_user_id(db=db, user_id=current_user.id)
    if divination_settings is None:
        divination_settings=schemas.DivinationSettingsQuery()
    bazi = BaZi(year, month, day, hour, sex, minute=minute, early_isOpen=divination_settings.early_isOpen, wuxing_time_isOpen=divination_settings.wuxing_time_isOpen, location=location)
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
        label_id:int = None,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get divination and save to database.
    """
    divination_settings = crud.divination_settings.get_by_user_id(db=db, user_id=current_user.id)
    if divination_settings is None:
        divination_settings=schemas.DivinationSettingsQuery()
    bazi = BaZi(year, month, day, hour, sex, minute=minute, early_isOpen=divination_settings.early_isOpen, wuxing_time_isOpen=divination_settings.wuxing_time_isOpen, location=location)
    beatInfo = None
    if(selectyear > 0):
        beatInfo = get_wuxing_by_selectyear(selectyear)
    divination = bazi.get_detail()
    total = crud.history.get_count_by_owner(db, current_user.id)
    if lunar==1:
        year,month,day = convert_lunar_to_solar(year,month,day,run)
    index = 0
    if name == '':
        index = crud.history.get_index_by_owner(db, current_user.id) + 1
        name = "案例"+str(index)
    history = schemas.HistoryCreate(
        owner_id=current_user.id,
        name=name,
        birthday=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
        sex=sex,
        location=location,
        status=0,
        divination=json.dumps(divination),
        isNorth=is_north,
        beat_info=json.dumps(beatInfo),
        label_id=label_id,
        history_index=index
    )
    history = crud.history.create_owner_divination(db, history=history)
    divination['beat_info'] = json.dumps(beatInfo)
    divination['id'] = history.id
    divination['name'] = history.name
    return divination
   

@router.post("/history", response_model=List[schemas.HistoryQuery])
def get_history(
        *,
        skip: int = 0,
        limit: int = 100,
        top: int = 0,
        user_name: str ="",
        label_name: str ="",
        wuxing: str ="",
        sex: int = -1,
        gans: list = Body([]),
        zhis: list = Body([]),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get divination history.
    """
    history = crud.history.get_multi_by_owner(db=db, owner_id=current_user.id, top=top, skip=skip, limit=limit)
    rets = []
    for h in history:
        labelName="默认"
        if(h.label_id is not None):
            label=crud.label.get(db, id=h.label_id)
            if(label is not None):
                labelName=label.label_name
        divination = json.loads(h.divination)
        if user_name != "":
            if h.name.find(user_name)==-1 and labelName.find(user_name) == -1:
                continue
        if label_name != "":
            if labelName != label_name:
                continue
        if sex >= 0 and sex !=h.sex:
            continue
        if wuxing != "":
            ganzhi = get_wuxing_ganzhi(wuxing)
            if ganzhi.find(divination["sizhu"]["gans"][4]) == -1:
                continue   
        if len(gans) > 0:
            if not set(gans).issubset(divination["sizhu"]["gans"]):
                continue
        if len(zhis) > 0:
            if not set(zhis).issubset(divination["sizhu"]["zhis"]):
                continue
        tz = pytz.timezone('Asia/Shanghai')
        rets.append(schemas.HistoryQuery(
            id=h.id,
            name=h.name,
            birthday=h.birthday,
            sex=h.sex,
            location=h.location,
            divination=h.divination,
            create_time=(h.create_time+datetime.timedelta(hours=8)).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
            isNorth=h.isNorth,
            beat_info=h.beat_info,
            label_id=h.label_id,
            label_name=labelName,
            like_str=h.like_str,
            dislike_str=h.dislike_str,
            pattern=h.pattern
        ))
    return rets

@router.put("/history/{id}", response_model=Any)
def update_history(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
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
        label_id:int = None,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an history.
    """
    divination_settings = crud.divination_settings.get_by_user_id(db=db, user_id=current_user.id)
    if divination_settings is None:
        divination_settings=schemas.DivinationSettingsQuery()
    bazi = BaZi(year, month, day, hour, sex, minute=minute, early_isOpen=divination_settings.early_isOpen, wuxing_time_isOpen=divination_settings.wuxing_time_isOpen, location=location)
    beatInfo = None
    if(selectyear > 0):
        beatInfo = get_wuxing_by_selectyear(selectyear)
    divination = bazi.get_detail()
    if lunar==1:
        year,month,day = convert_lunar_to_solar(year,month,day,run)
    history = crud.history.get(db, id=id)
    if not history:
        raise HTTPException(
            status_code=404,
            detail="No history exists for the current user",
        )
    if(history.owner_id != current_user.id):
        raise HTTPException(
            status_code=404,
            detail="The current history does not belong to this user",
        ) 
    index = history.history_index
    if name == '':
        index = crud.history.get_index_by_owner(db, current_user.id) + 1
        name = "案例"+str(index)
    history_in = schemas.HistoryUpdate(
        owner_id=current_user.id,
        name=name,
        birthday=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
        sex=sex,
        location=location,
        divination=json.dumps(divination),
        isNorth=is_north,
        beat_info=json.dumps(beatInfo),
        label_id=label_id,
        history_index = index
    )
    history = crud.history.update(db, db_obj=history, obj_in=history_in)

    divination['beat_info'] = json.dumps(beatInfo)
    divination['id'] = id
    divination['name'] = history.name
    return divination

@router.put("/addTopHistory/{id}", response_model=Any)
def add_top_history(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    history = crud.history.get(db, id=id)
    if not history:
        raise HTTPException(
            status_code=404,
            detail="No history exists for the current user",
        )
    if(history.owner_id != current_user.id):
        raise HTTPException(
            status_code=404,
            detail="The current history does not belong to this user",
        ) 
    if(history.top == 1):
        raise HTTPException(
            status_code=404,
            detail="The current history has been set to the top",
        ) 
    history_in = {"top":1, "top_time":datetime.datetime.now()}
    history = crud.history.update(db, db_obj=history, obj_in=history_in)
    return "success"

@router.put("/cancelTopHistory/{id}", response_model=Any)
def cancel_top_history(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    history = crud.history.get(db, id=id)
    if not history:
        raise HTTPException(
            status_code=404,
            detail="No history exists for the current user",
        )
    if(history.owner_id != current_user.id):
        raise HTTPException(
            status_code=404,
            detail="The current history does not belong to this user",
        ) 
    if(history.top == 0):
        raise HTTPException(
            status_code=404,
            detail="The current history has been set to the cancel top",
        ) 
    history_in = {"top":0, "top_time":None}
    history = crud.history.update(db, db_obj=history, obj_in=history_in)
    return "success"

@router.put("/historyNote/{id}", response_model=Any)
def update_history_note(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        like_str: str = '',
        dislike_str: str = '',
        pattern: str = '',
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an historyNote.
    """
    history = crud.history.get(db, id=id)
    if not history:
        raise HTTPException(
            status_code=404,
            detail="No history exists for the current user",
        )
    if(history.owner_id != current_user.id):
        raise HTTPException(
            status_code=404,
            detail="The current history does not belong to this user",
        ) 
    history_in={"like_str":like_str,"dislike_str":dislike_str,"pattern":pattern}
    history = crud.history.update(db, db_obj=history, obj_in=history_in)
    return history

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


@router.post("/createLabel")
def create_label(
        *,
        db: Session = Depends(deps.get_db),
        label_name: str = '',
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new Label.(only user)
    """
    count = crud.label.get_count_by_user_and_name(db=db, user_id=current_user.id,label_name=label_name)
    if(count > 0):
        raise HTTPException(
            status_code=400,
            detail="label name already exists",
        )   
    label = schemas.Label(
        label_name=label_name,
        label_type=1,
        user_id=current_user.id
    )
    label = crud.label.create(db=db, obj_in=label)
    return label


@router.get("/labels", response_model=List[schemas.LabelQuery])
def get_labels(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get labels by user.
    """
    labels = crud.label.get_multi_by_user(db=db, user_id=current_user.id)
    rets = []
    for h in labels:
        rets.append(schemas.LabelQuery(
            id=h.id,
            label_name=h.label_name,
            user_id=h.user_id
        ))
    return rets

@router.delete('/label')
def delete_label(label_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)):
    res=crud.label.delete_label(db=db,label_id=label_id,user_id=current_user.id)
    if res:
        return "success"
    else:
        return "failed"

@router.post("/createHistoryEvent")
def create_history_event(
        *,
        db: Session = Depends(deps.get_db),
        history_id: int,
        event_type: str,
        year: int,
        year_gz: str,
        content: str = '',
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new Event.(only user)
    """
    event = schemas.HistoryEvent(
        history_id=history_id,
        event_type=event_type,
        year=year,
        year_gz=year_gz,
        content=content,
    )
    event = crud.history_event.create(db=db, obj_in=event)
    return event

@router.put("/event/{id}")
def update_event(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        event_type: str,
        year: int,
        year_gz: str,
        content: str = '',
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an event.(only user)
    """
    event = crud.history_event.get(db, id=id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="No event exists",
        )
    history = crud.history.get(db, id=event.history_id)
    if history is None:
        raise HTTPException(
            status_code=404,
            detail="No history exists",
        )
    if current_user.id != history.owner_id:
        raise HTTPException(
            status_code=404,
            detail="The event does not belong to the user",
        )
    event_in = schemas.HistoryEventUpdate(
        history_id=event.history_id,
        event_type=event_type,
        year=year,
        year_gz=year_gz,
        content=content
    )
    event = crud.history_event.update(db, db_obj=event, obj_in=event_in)
    return event

@router.get("/events")
def get_events(
        *,
        db: Session = Depends(deps.get_db),
        history_id: int,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get events by user.
    """
    events = crud.history_event.get_multi_by_history(db=db, history_id=history_id)
    return events

@router.delete('/event')
def delete_event(event_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)):
    event=crud.history_event.get(db, id=event_id)
    if event is None:
        return "failed"
    history = crud.history.get(db, id=event.history_id)
    if history is None:
        return "failed"
    if current_user.id != history.owner_id:
        return "failed"    
    res=crud.history_event.delete_history_event(db=db,id=event_id)
    if res:
        return "success"
    else:
        return "failed"

@router.post("/createHistoryCombine")
def create_history_combine(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.HistoryCombineCreate,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new HistoryCombine.(only user)
    """
    obj_in.owner_id = current_user.id
    history_combine = crud.history_combine.create(db=db, obj_in=obj_in)
    return history_combine

@router.get("/combines")
def get_history_combines(
        *,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get HistoryCombines by user.
    """
    combines = crud.history_combine.get_multi_by_owner(db=db, owner_id=current_user.id,skip=skip,limit=limit)
    rets = []
    tz = pytz.timezone('Asia/Shanghai')
    for combine in combines:
        rets.append(schemas.HistoryCombineQuery(
            id=combine.id,
            owner_id=combine.owner_id,
            name1=combine.name1,
            birthday1=combine.birthday1,
            sex1=combine.sex1,
            location1=combine.location1,
            divination1=combine.divination1,
            isNorth1=combine.isNorth1,
            name2=combine.name2,
            birthday2=combine.birthday2,
            sex2=combine.sex2,
            location2=combine.location2,
            divination2=combine.divination2,
            isNorth2=combine.isNorth2,
            create_time=(combine.create_time+datetime.timedelta(hours=8)).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
        ))
    return rets

@router.delete('/combine')
def delete_history_combine(id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)):
    res=crud.history_combine.delete_history_combine(db=db,history_combine_id=id,owner_id=current_user.id)
    if res:
        return "success"
    else:
        return "failed"

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
