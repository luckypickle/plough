import pytz
import json
import sxtwl
from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.api.util import get_next_birthday
from app.bazi.meihua import get_meihua



router = APIRouter()

@router.post("/create_meihua",response_model=schemas.MeihuaQuery)
def create_meihua(
        *,
        db: Session = Depends(deps.get_db),
        cause: str,
        way: int = 1,
        shanggua: int = 10,
        xiagua: int = 10,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> schemas.MeihuaQuery:
    """
    Get meihua and save to database.
    """
    nowTime= datetime.now()
    if way==1:
        nowTimeLunar = sxtwl.fromSolar(nowTime.year,nowTime.month,nowTime.day)
        yGZ = nowTimeLunar.getYearGZ()
        hGZ = nowTimeLunar.getHourGZ(nowTime.hour)
        if nowTimeLunar.hasJieQi():
            jd = nowTimeLunar.getJieQiJD()
            jieqi_t = sxtwl.JD2DD(jd)
            if jieqi_t.h > int(nowTime.hour) or (jieqi_t.h==nowTime.hour and jieqi_t.m>= nowTime.minute):
                tmp_day = nowTimeLunar.before(1)
                yGZ = tmp_day.getYearGZ()
        year = yGZ.dz+1
        month = nowTimeLunar.getLunarMonth()
        day = nowTimeLunar.getLunarDay()
        hour = hGZ.dz+1
        dongyao = (year+month+day+hour)%6
        shanggua = (year+month+day)%8
        xiagua = (year+month+day+hour)%8
    elif way==2:
        dongyao = (int(shanggua)+int(xiagua)) %6
        shanggua = int(shanggua)%8
        xiagua = int(xiagua)%8
    else:
        raise HTTPException(
            status_code=404,
            detail="There is currently no such way available",
        )
    meihua = schemas.MeihuaCreate(
        owner_id=current_user.id,
        cause=cause,
        way=way,
        shanggua=shanggua,
        xiagua=xiagua,
        dongyao=dongyao
    )
    result = get_meihua(shanggua,xiagua,dongyao)
    meihua = crud.meihua.create_meihua(db, meihua = meihua)
    if meihua:
        meihua.create_time = nowTime,
        db.add(meihua),
        db.commit()
        db.refresh(meihua)
    print(str(meihua.create_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")))
    meihua = schemas.MeihuaQuery(
        id=meihua.id,
        owner_id=meihua.owner_id,
        cause=meihua.cause,
        way=meihua.way,
        shanggua=meihua.shanggua,
        xiagua=meihua.xiagua,
        dongyao=meihua.dongyao,
        create_time=meihua.create_time.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        result=json.dumps(result),
    )
    return meihua

@router.post("/meihua")
def meihua(
        *,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    nowTimeLunar = sxtwl.fromSolar(year,month,day)
    yGZ = nowTimeLunar.getYearGZ()
    hGZ = nowTimeLunar.getHourGZ(hour)
    if nowTimeLunar.hasJieQi():
        jd = nowTimeLunar.getJieQiJD()
        jieqi_t = sxtwl.JD2DD(jd)
        if jieqi_t.h > int(hour) or (jieqi_t.h==hour and jieqi_t.m>= minute):
            tmp_day = nowTimeLunar.before(1)
            yGZ = tmp_day.getYearGZ()
    year = yGZ.dz+1
    month = nowTimeLunar.getLunarMonth()
    day = nowTimeLunar.getLunarDay()
    hour = hGZ.dz+1
    dongyao = (year+month+day+hour)%6
    shanggua = (year+month+day)%8
    xiagua = (year+month+day+hour)%8
    result = get_meihua(shanggua,xiagua,dongyao)
    return json.dumps(result)

@router.put("/meihua/{id}")
def update_meihua(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        pic: str,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an meihua.(only user)
    """
    meihua = crud.meihua.get(db, id=id)
    if not meihua:
        raise HTTPException(
            status_code=404,
            detail="No meihua exists for the current user",
        )
    if(meihua.owner_id != current_user.id):
        raise HTTPException(
            status_code=404,
            detail="The current meihua does not belong to this user",
        ) 
    meihua_in = {"pic":pic}
    meihua = crud.meihua.update(db, db_obj=meihua, obj_in=meihua_in)
    return meihua

@router.get("/meihuas", response_model=List[schemas.MeihuaQuery])
def get_meihuas(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    meihuas = crud.meihua.get_multi_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    rets = []
    for meihua in meihuas:
        result = get_meihua(meihua.shanggua,meihua.xiagua,meihua.dongyao)
        rets.append(schemas.MeihuaQuery(
            id=meihua.id,
            owner_id=meihua.owner_id,
            cause=meihua.cause,
            way=meihua.way,
            shanggua=meihua.shanggua,
            xiagua=meihua.xiagua,
            dongyao=meihua.dongyao,
            create_time=meihua.create_time.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            result=json.dumps(result),
            pic=meihua.pic,
        ))
    return rets
