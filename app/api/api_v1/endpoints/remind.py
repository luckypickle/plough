import pytz
import sxtwl
from typing import Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.im_utils import pushMsg
from app.api.util import get_next_birthday


router = APIRouter()

@router.post("/create_remind_birthday")
def create_remind_birthday(
        *,
        db: Session = Depends(deps.get_db),
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        sex: int = 1,
        location: str = '',
        label: str = '',
        remind_days:str = '0',
        remind_type:int = 1,
        remind_calendar:int = 1,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get remind_birthday and save to database.
    """
    remind_birthday = schemas.RemindBirthdayCreate(
        owner_id=current_user.id,
        name=name,
        birthday=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
        sex=sex,
        location=location,
        label=label,
        remind_days=remind_days,
        remind_type=remind_type,
        remind_calendar=remind_calendar
    )
    remindBirthday = crud.remind_birthday.create_remind_birthday(db, remindBirthday = remind_birthday)
    return remindBirthday

@router.put("/remind_birthday/{id}")
def update_remind_birthday(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        sex: int = 1,
        location: str = '',
        label: str = '',
        remind_days:str = '0',
        remind_type:int = 1,
        remind_calendar:int = 1,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an remind_birthday.(only user)
    """
    remind_birthday = crud.remind_birthday.get(db, id=id)
    if not remind_birthday:
        raise HTTPException(
            status_code=404,
            detail="No remindBirthday exists for the current user",
        )
    if(remind_birthday.owner_id != current_user.id):
        raise HTTPException(
            status_code=404,
            detail="The current remindBirthday does not belong to this user",
        ) 
    remind_birthday_in = schemas.RemindBirthdayUpdate(
        owner_id=current_user.id,
        name=name,
        birthday=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
        sex=sex,
        location=location,
        label=label,
        remind_days=remind_days,
        remind_type=remind_type,
        remind_calendar=remind_calendar
    )
    remindBirthday = crud.remind_birthday.update(db, db_obj=remind_birthday, obj_in=remind_birthday_in)
    return remindBirthday

@router.get("/remind_birthdays", response_model=List[schemas.RemindBirthdayQuery])
def get_remind_birthdays(
        db: Session = Depends(deps.get_db),
        name: str = '',
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    remind_birthdays = crud.remind_birthday.get_multi_by_owner(db, owner_id=current_user.id, name=name)
    rets = []
    nowTime= datetime.today()
    for r in remind_birthdays:
        birthday = datetime.strptime(r.birthday,"%Y-%m-%d %H:%M:%S")
        nextBirthday = get_next_birthday(nowTime,birthday,r.remind_calendar)
        rets.append(schemas.RemindBirthdayQuery(
            id=r.id,
            name=r.name,
            birthday=r.birthday,
            sex=r.sex,
            location=r.location,
            label=r.label,
            owner_id=r.owner_id,
            remind_days=r.remind_days,
            remind_type=r.remind_type,
            remind_calendar=r.remind_calendar,
            days=(nextBirthday-nowTime).days+1
        ))
    return rets

@router.delete('/remind_birthday')
def delete_remind_birthday( remind_birthday_id:int ,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    res = crud.remind_birthday.delete_remind_birthday(db=db,id=remind_birthday_id,owner_id=current_user.id)
    if res:
        return "success"
    else:
        return "failed"

@router.post("/create_remind_day")
def create_remind_day(
        *,
        db: Session = Depends(deps.get_db),
        title: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        name: str = '',
        content: str = '',
        remind_days:str = '0',
        remind_type:int = 1,
        remind_calendar:int = 1,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get remind_day and save to database.
    """
    remind_day = schemas.RemindDayCreate(
        owner_id=current_user.id,
        name=name,
        day_time=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
        title=title,
        content=content,
        remind_days=remind_days,
        remind_type=remind_type,
        remind_calendar=remind_calendar
    )
    remindDay = crud.remind_day.create_remind_day(db, remindDay=remind_day)
    return remindDay

@router.put("/remind_day/{id}")
def update_remind_day(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        title: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        name: str = '',
        content: str = '',
        remind_days:str = '0',
        remind_type:int = 1,
        remind_calendar:int = 1,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an remind_day.(only user)
    """
    remind_day = crud.remind_day.get(db, id=id)
    if not remind_day:
        raise HTTPException(
            status_code=404,
            detail="No remindDay exists for the current user",
        )
    if(remind_day.owner_id != current_user.id):
        raise HTTPException(
            status_code=404,
            detail="The current remindDay does not belong to this user",
        ) 
    remind_day_in = schemas.RemindDayUpdate(
        owner_id=current_user.id,
        name=name,
        day_time=f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00",
        title=title,
        content=content,
        remind_days=remind_days,
        remind_type=remind_type,
        remind_calendar=remind_calendar
    )
    remindDay = crud.remind_day.update(db, db_obj=remind_day, obj_in=remind_day_in)
    return remindDay

@router.get("/remind_days", response_model=List[schemas.RemindBirthdayQuery])
def get_remind_days(
        db: Session = Depends(deps.get_db),
        title: str = '',
        current_user: models.User = Depends(deps.get_current_active_user)
) -> List[schemas.RemindBirthdayQuery]:
    remind_days = crud.remind_day.get_multi_by_owner(db, owner_id=current_user.id, title=title)
    rets = []
    nowTime= datetime.today()
    for r in remind_days:
        dayTime = datetime.strptime(r.day_time,"%Y-%m-%d %H:%M:%S")
        nextDayTime = get_next_birthday(nowTime,dayTime,r.remind_calendar)
        rets.append(schemas.RemindDayQuery(
            id=r.id,
            name=r.name,
            title=r.title,
            day_time=r.day_time,
            content=r.content,
            owner_id=r.owner_id,
            remind_days=r.remind_days,
            remind_type=r.remind_type,
            remind_calendar=r.remind_calendar,
            days=(nextDayTime-nowTime).days+1
        ))
    return rets

@router.delete('/remind_day')
def delete_remind_day( remind_day_id:int ,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    res = crud.remind_day.delete_remind_day(db=db,id=remind_day_id,owner_id=current_user.id)
    if res:
        return "success"
    else:
        return "failed"

@router.get('/remind')
def remind(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    nowTime= datetime.today()
    remind_in = {"remind_time":nowTime}
    remind_birthdays = crud.remind_birthday.get_multi_by_owner(db, owner_id=current_user.id, name='')
    for r in remind_birthdays:
        if r.remind_days == "-1":
            continue
        birthday = datetime.strptime(r.birthday,"%Y-%m-%d %H:%M:%S")
        if r.remind_time is not None:
            #公历当天已提醒           
            if nowTime.month == r.remind_time.month and nowTime.day == r.remind_time.day:
                print('公历当天已提醒')
                continue   
            #该提醒为不重复提醒 
            if r.remind_type == 0 and (nowTime-datetime(year = r.remind_time.year, month = r.remind_time.month, day = r.remind_time.day)).days>30:
                continue        
        if r.remind_calendar == 1:   
            isRun = nowTime.year%4==0 and nowTime.year%100 != 0 or nowTime.year % 400==0
            if birthday.month == 2 and birthday.day == 29 and not isRun:
                continue
            birthday= datetime(year = nowTime.year, month = birthday.month, day = birthday.day)
        else:
            birthdayLunar = sxtwl.fromSolar(birthday.year,birthday.month,birthday.day)
            nowTimeLunar = sxtwl.fromSolar(nowTime.year,nowTime.month,nowTime.day)
            nowBirthdayLunar = sxtwl.fromLunar(nowTimeLunar.getLunarYear(),birthdayLunar.getLunarMonth(),birthdayLunar.getLunarDay())
            #生日为农历大月最后一天
            if birthdayLunar.getLunarDay()==30 and nowBirthdayLunar.getLunarDay()!=30:
                continue
            birthday = datetime(year = nowBirthdayLunar.getSolarYear(),month = nowBirthdayLunar.getSolarMonth(),day = nowBirthdayLunar.getSolarDay())
        days = str(r.remind_days).split(";")
        days.remove('')
        for day in days:
            remindTime = birthday + timedelta(days = -int(day))  

            if remindTime.month == nowTime.month and remindTime.day == nowTime.day:
                crud.remind_birthday.update(db, db_obj=r, obj_in=remind_in)
                pushMsg("生日提醒:" + r.name + "还有" + day +"天生日", "user_" + str(current_user.id))
    remind_days = crud.remind_day.get_multi_by_owner(db, owner_id=current_user.id, title='')
    for r in remind_days:
        if r.remind_days == "-1":
            continue
        birthday = datetime.strptime(r.day_time,"%Y-%m-%d %H:%M:%S")
        if r.remind_time is not None:
            #公历当天已提醒           
            if nowTime.month == r.remind_time.month and nowTime.day == r.remind_time.day:
                print('公历当天已提醒')
                continue   
            #该提醒为不重复提醒 
            if r.remind_type == 0 and (nowTime-datetime(year = r.remind_time.year, month = r.remind_time.month, day = r.remind_time.day)).days>30:
                continue        
        if r.remind_calendar == 1:   
            isRun = nowTime.year%4==0 and nowTime.year%100 != 0 or nowTime.year % 400==0
            if birthday.month == 2 and birthday.day == 29 and not isRun:
                continue
            birthday= datetime(year = nowTime.year, month = birthday.month, day = birthday.day)
        else:
            birthdayLunar = sxtwl.fromSolar(birthday.year,birthday.month,birthday.day)
            nowTimeLunar = sxtwl.fromSolar(nowTime.year,nowTime.month,nowTime.day)
            nowBirthdayLunar = sxtwl.fromLunar(nowTimeLunar.getLunarYear(),birthdayLunar.getLunarMonth(),birthdayLunar.getLunarDay())
            #生日为农历大月最后一天
            if birthdayLunar.getLunarDay()==30 and nowBirthdayLunar.getLunarDay()!=30:
                continue
            birthday = datetime(year = nowBirthdayLunar.getSolarYear(),month = nowBirthdayLunar.getSolarMonth(),day = nowBirthdayLunar.getSolarDay())
        days = str(r.remind_days).split(";")
        if days[-1]=='':
            days.remove('')
        for day in days:
            remindTime = birthday + timedelta(days = -int(day))  
            if remindTime.month == nowTime.month and remindTime.day == nowTime.day:
                crud.remind_birthday.update(db, db_obj=r, obj_in=remind_in)
                print("纪念日提醒:" + r.title + "还有" + day +"天", "user_" + str(current_user.id))
                pushMsg("纪念日提醒:" + r.title + "还有" + day +"天", "user_" + str(current_user.id))

    return "success"