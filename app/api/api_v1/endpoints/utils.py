from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException,File,Form
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
# from app.core.celery_app import celery_app
from app.utils import send_test_email
from app.bazi.citys import cal_zone
from app.bazi.bazi import getYearJieQi,get_birthday_by_bazi,cal_wuxing_color,get_bazi_by_birthday
from app.api.util import make_return
import hashlib
import os
from app.cos_utils import upload_file_to_cos,get_read_url
from app.im_utils import register_account,query_message_list,query_message_detail,recovery_chat
router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
def test_celery(
        msg: schemas.Msg,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    # celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
        email_to: EmailStr,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


@router.get("/get-latest-version", response_model=schemas.Version, status_code=201)
def get_latest_version(
        product: str,
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get latest version.
    """
    version = crud.version.get_by_product(db=db, product=product)
    return version


@router.get("/cityzone")
def get_latest_version(
        province: str,
        city: str,
        area: str,
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get latest version.
    """

    return cal_zone(province, city, area)


year_jieqi = {}


@router.get("/yearJieQi")
def get_year_jie_qi(
        year: int
) -> Any:
    if str(year) not in year_jieqi:
        ret = getYearJieQi(year)
        year_jieqi[str(year)] = ret
    else:
        ret = year_jieqi[str(year)]
    return ret
@router.get("/BirthdayByBazi")
def get_year_jie_qi(
        year: str,
        month: str,
        day:str,
        time:str
) -> Any:
    """
        get solar birthday by bazi.
    """
    ret = get_birthday_by_bazi(year,month,day,time)
    return ret

@router.get("/todayColor")
def get_today_color(year:int,month:int,day:int,hour:int,minute:int,daydelta:int=0):
    color = cal_wuxing_color(year,month,day,hour,minute,daydelta)
    return color

@router.get("/baziByBirthday")
def get_bazi_by_birthday_(year:int,month:int,day:int,hour:int,minute:int):
    """
        get bazi by solar birthday.
    """
    ret = get_bazi_by_birthday(year,month,day,hour,minute)
    return ret



@router.post("/retrieve-version/", response_model=List[schemas.Version])
def release_version(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve version.
    """
    versions = crud.version.get_multi_by_order(db=db, skip=skip, limit=limit)
    return versions


@router.post("/release-version/", response_model=schemas.Version)
def release_version(
        obj_in: schemas.VersionCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Release a new version.
    """
    version = crud.version.release_version(db=db, obj_in=obj_in)
    return version


@router.put("/{version_id}", response_model=schemas.Version)
def update_version(
        *,
        db: Session = Depends(deps.get_db),
        version_id: int,
        obj_in: schemas.VersionUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a release version.
    """
    version = crud.version.get(db, id=version_id)
    if not version:
        raise HTTPException(
            status_code=404,
            detail="The version does not exist in the system",
        )
    version_new = crud.version.update(db, db_obj=version, obj_in=obj_in)
    return version_new


@router.post("/uploadFile",response_model=Any)
async def uploadfile(file: bytes = File(),file_type:str=Form(...),
                     db: Session = Depends(deps.get_db),
current_user: models.User = Depends(deps.get_current_user),
    ):
    file_name = hashlib.md5(file).hexdigest()

    res  = crud.upload_history.get_by_file_name(db,file_name)
    if res is not None:
        #if os.path.exists("./uploadfile/"+file_name):
        return make_return(200, res.url)
        #文件已存在从数据库中查找

    else:
        with open("./uploadfile/"+file_name+"."+file_type,"wb") as fx:
            fx.write(file)
        res = upload_file_to_cos(file_name+"."+file_type)
        if res:
            #存入数据库
            url = get_read_url(file_name+"."+file_type)
            crud.upload_history.create_upload(db,schemas.UploadHistoryCreate(file_name=file_name,url=url,status=1))
            return make_return(200,url)
        else:
            return make_return(400,"upload file to cos failed,please contact admin!")

@router.get("/messageList")
def super_user_get_message_list( db: Session = Depends(deps.get_db),
                      skip:int =0,limit:int=20,master_id:str="",user_Phone:str="",
                      current_user: models.User = Depends(deps.get_current_active_superuser), ) ->Any:
    page_num = int(skip/limit+1)
    page_size = limit
    msg_data = query_message_list(page_num,page_size,master_id,user_Phone)
    if len(msg_data)==0:
        return {
            "total":0,
            "messageList":[]
        }
    return {
        "total": msg_data['total'],
        "messageList":msg_data["rows"]
    }

@router.get("/messageDetail")
def super_user_get_message_list( db: Session = Depends(deps.get_db),
                      skip:int =0,limit:int=20,friend_name:str="",user_name:str="",
                      current_user: models.User = Depends(deps.get_current_active_superuser), ) ->Any:
    page_num = int(skip/limit+1)
    page_size = limit
    msg_data = query_message_detail(page_num,page_size,friend_name,user_name)
    if len(msg_data)==0:
        return {
            "total":0,
            "messageList":[]
        }
    return {
        "total": msg_data['count'],
        "messageList":msg_data["messageList"]
    }



@router.get("/register_all_account")
def register_all_account(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    res = crud.user.get_by_im_status(db,status=0)
    for one_ret in res:
        account = "user_"+str(one_ret.id)
        if one_ret.phone == "" or one_ret.phone == None:
            phone = one_ret.email
        else:
            phone = one_ret.phone[:3] + "****" + one_ret.phone[-4:]

        res = register_account(get_read_url("3bf8616fe6c23c0c465527ec80397b24.png"),0,account,phone)
        if res :
            crud.user.update(db,db_obj=one_ret,obj_in=schemas.UserUpdate(im_status=1))
    master_res = crud.master.get_by_im_status(db,0)
    for one_ret in master_res:

        account = "master_"+str(one_ret.id)
        #phone = one_ret.phone if one_ret.phone=="" or one_ret.phone==None else one_ret.email
        if one_ret.avatar.endswith(".png"):
            res = register_account(one_ret.avatar,1,account,one_ret.name)
        else:
            res = register_account(get_read_url("3bf8616fe6c23c0c465527ec80397b24.png"), 1, account, one_ret.name)
        if res:
            crud.master.update(db,db_obj=one_ret,obj_in=schemas.MasterUpdate(im_status=1))
    return make_return(200,"success")

@router.get("/recovery_all_chat")
def register_all_account(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    res = crud.order.get_all_pending_order(db)
    for one_data in res:
        if one_data.arrange_status!=3:
            recovery_chat(one_data.master_id,one_data.owner_id)

    return make_return(200,"success")
