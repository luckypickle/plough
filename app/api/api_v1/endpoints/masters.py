from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps,util
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.bazi import BaZi
from app.api.util import make_return
import base64
import hashlib
from app.cos_utils import upload_file_to_cos,get_read_url
from app.im_utils import register_account

router = APIRouter()


@router.get("/", response_model=List[schemas.MasterForOrder])
def read_masters(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve master list for placing order.
    """
    masters = crud.master.get_multi_by_sort(db, skip=skip, limit=limit)
    ret_obj = []
    for m in masters:
        if m.status == 1:
            ret_obj.append(schemas.MasterForOrder(
                name=m.name,
                desc=m.desc,
                id=m.id,
                price=m.price,
                avatar=m.avatar
            ))
    return ret_obj


@router.get("/list", response_model=schemas.MasterQuery)
def read_masters(
        db: Session = Depends(deps.get_db),
        name: str = "",
        status: int = -1,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve masters. (superuser only)
    """

    total, masters = crud.master.get_multi_with_conditions(db=db,name=name, status=status, skip=skip, limit=limit)
    ret_obj = schemas.MasterQuery(
        total=total,
        masters=masters
    )
    return ret_obj
@router.get("/listWithReward", response_model=schemas.MasterRewardQuery)
def read_masters(
        db: Session = Depends(deps.get_db),
        name: str = "",
        status: int = -1,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve masters. (superuser only)
    """
    total, masters = crud.master.get_multi_with_conditions(db=db, name=name,status=status, skip=skip, limit=limit,is_order=1)
    ret_obj = schemas.MasterRewardQuery(
        total=total,
        masters=[]
    )
    for one_data in masters:
        sum = crud.order.get_order_reward_by_master(db,one_data.id)
        ret_obj.masters.append(
            schemas.MasterReward(
                id=one_data.id,
        name= one_data.name,
        rate= one_data.rate,
        order_number=one_data.order_number,
        order_amount= one_data.order_amount,
        price= one_data.price,
        create_time= str(one_data.create_time),
        desc= one_data.desc,
        status= one_data.status,
        phone=one_data.phone,
        email= one_data.email,

        avatar= one_data.avatar,
        sort_weight=one_data.sort_weight,
                total_reward=sum,
            )
        )

    return ret_obj




@router.get("/listWithRate", response_model=schemas.MasterRateQuery)
def read_masters(
        db: Session = Depends(deps.get_db),
        status: int = -1,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve masters. (superuser only)
    """
    util.load_master_rate(db)
    total, masters = crud.master.get_multi_with_conditions(db=db, status=status, skip=skip, limit=limit)
    ret_obj = schemas.MasterRateQuery(
        total=total,
        masters=[]
    )
    for one_data in masters:
        ret_obj.masters.append(schemas.MasterForOrderRate(
                name=one_data.name,
                desc=one_data.desc,
                id=one_data.id,
                price=one_data.price,
                avatar=one_data.avatar,
                avg_rate = util.get_avg_rate(one_data.id),
            )
        )
    return ret_obj


@router.post("/", response_model=schemas.Master)
def create_master(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.MasterCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new master. (superuser only)
    """
    master = crud.master.get_by_phone(db, phone=obj_in.phone)
    if master:
        raise HTTPException(
            status_code=400,
            detail="The master with this phone already exists in the system.",
        )
    master = crud.master.create(db, obj_in=obj_in)
    return master


@router.get("/divination", response_model=Any)
def master_get_divination(
        *,
        db: Session = Depends(deps.get_db),
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        sex: int,
        current_master: models.Master = Depends(deps.get_current_active_master)
) -> Any:
    """
    Get divination.
    """
    bazi = BaZi(year, month, day, hour, sex)
    return bazi.get_detail()


@router.put("/me", response_model=schemas.Master)
def update_master_me(
        *,
        db: Session = Depends(deps.get_db),
        password: str = Body(None),
        name: str = Body(None),
        phone: str = Body(None),
        current_master: models.Master = Depends(deps.get_current_active_master),
) -> Any:
    """
    Update own master.
    """
    current_data = jsonable_encoder(current_master)
    data_in = schemas.MasterUpdate(**current_data)
    if password is not None:
        data_in.password = password
    if phone is not None:
        data_in.phone = phone
    if name is not None:
        data_in.name = name
    master = crud.master.update(db, db_obj=current_master, obj_in=data_in)
    return master



@router.get("/bills",response_model=schemas.BillList)
def get_bills(
        bill_date: str,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),) ->Any:
    '''
    get all master bill by bill date.(superuser only)
    '''

    generate_bill(db)
    total,res = crud.bill.get_all_by_date(db,date=bill_date,skip=skip,limit=limit)
    ret_data =schemas.BillList(total=total,bills=[])
    for one_data in res:
        ret_data.bills.append(schemas.BillQuery(
            id=one_data.id,
            master_id=one_data.master_id,
            master_name = one_data.master.name,
            value = one_data.value,
            bill_date = one_data.bill_date,
            status =one_data.status,
        ))

    return ret_data

@router.put("/bill")
def update_bill(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        bill_in: schemas.BillUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an bill (superuser).
    """
    bill = crud.bill.get(db=db, id=id)
    if not bill:
        raise HTTPException(status_code=404, detail="Order not found")
    # if not crud.user.is_superuser(current_user) and (order.owner_id != current_user.id):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    order = crud.bill.update(db=db, db_obj=bill, obj_in=bill_in)
    return  make_return(1,"success")

@router.put('/productPrice')
def set_product_price(db: Session = Depends(deps.get_db),
                      *,
        obj_in: schemas.MasterProdcutCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser),):

    bill = crud.masterProduct.create_price(db,obj_in)

    return make_return(1,"success")





def generate_bill(db :Session):
    all_unhandle_bill = crud.order.get_all_order_by_bill_state(db,0)
    cache_change = {}
    print(all_unhandle_bill)
    for one_data in all_unhandle_bill:
        bill_date = one_data.pay_time.strftime("%Y-%m")
        master_id = one_data.master_id
        if one_data.shareRate is None:
            shareRate = 0
        else:
            shareRate =  one_data.shareRate
        if one_data.amount is None:
            order_amount=0
        else:
            order_amount = one_data.amount
        if master_id in cache_change:
            if bill_date in cache_change[str(master_id)]:
                cache_change[str(master_id)][bill_date] += order_amount * shareRate
            else:
                cache_change[str(master_id)][bill_date] = order_amount *shareRate
        else:
            cache_change[str(master_id)] = {bill_date: order_amount * shareRate}
        crud.order.update(db,db_obj=one_data,obj_in=schemas.OrderUpdate(bill_state=1,product_id=one_data.product_id))

    for master_id,data in cache_change.items():
        for bill_date,value in data.items():
            billObj = crud.bill.get_by_bill_date_master_id(db,master_id,bill_date)
            if billObj is None:
                billObj = schemas.BillCreate(master_id=master_id,value=value,bill_date=bill_date,status=0)
            else:
                if billObj.status ==0:
                    billObj.value = billObj.value+value
            crud.bill.update_or_create(db,billObj)
    return





@router.get("/me", response_model=schemas.Master)
def read_master_me(
        db: Session = Depends(deps.get_db),
        current_master: models.Master = Depends(deps.get_current_active_master),
) -> Any:
    """
    Get current master.
    """
    return current_master


@router.get("/topMaster",response_model=schemas.TopMaster)
def get_top_masters(db: Session = Depends(deps.get_db),
        current_master: models.Master = Depends(deps.get_current_active_master),):
    res = crud.order.get_top_master_info(db)
    total, total_reward, orders = crud.order.get_multi_and_sum_with_condition(
        db=db, role=2, role_id=current_master.id, status=1, skip=0, limit=1
    )
    count_rate, amount_rate = crud.order.get_master_order_rate(db, current_master.id)
    ret_obj =  schemas.TopMaster( total_reward=0.0,paid_amount=0.0,count_rate ="0.0%",    amount_rate ="0.0%",total=0, top_detail=[])
    bill_amount = crud.bill.get_paid_amount_by_master_id(db,current_master.id)
    if total_reward is not None:
        ret_obj.total_reward = float(total_reward)/100
    if bill_amount is not None:
        ret_obj.paid_amount = float(bill_amount)/100
    ret_obj.count_rate = count_rate
    ret_obj.amount_rate = amount_rate
    ret_obj.total = total
    for one_res in res:
        ret_obj.top_detail.append(schemas.TopMasterDetail(total_reward=one_res[0],name=one_res[2],total_count=one_res[1]))


    return ret_obj



@router.post("/open", response_model=schemas.Master)
def create_master_open(
        *,
        db: Session = Depends(deps.get_db),
        phone: str = Body(...),
        email:str = Body(...),
        verify_code: str = Body(...),
        name: str = Body(None),
        avatar: str = Body(None),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new master without the need to be logged in.
    """
    if phone =="":
        phone = None
    if email == "":
        email= None
    if not settings.MASTERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open master registration is forbidden on this server",
        )
    master = crud.master.get_by_phone(db, phone=phone)
    master_email = crud.master.get_by_email(db,email=email)
    if master:
        raise HTTPException(
            status_code=400,
            detail="The master with this phone already exists in the system",
        )
    if master_email:
        raise HTTPException(
            status_code=400,
            detail="The master with this email already exists in the system",
        )
    if not crud.mpcode.verify_mpcode(db=db, phone=phone, verify_code=verify_code) and not crud.mpcode.verify_mpcode(db=db, phone=email, verify_code=verify_code):
        raise HTTPException(
            status_code=400,
            detail="Invalid verify code",
        )
    avatar_url = ""
    try:
        image_str = avatar
        image_data = base64.b64decode(image_str)
        file_name = hashlib.md5(image_data).hexdigest()

        res = crud.upload_history.get_by_file_name(db, file_name)
        if res is not None:
            # if os.path.exists("./uploadfile/"+file_name):
            avatar_url = res.url
            # 文件已存在从数据库中查找

        else:
            with open("./uploadfile/" + file_name + ".jpg" , "wb") as fx:
                fx.write(image_data)
            res = upload_file_to_cos(file_name + ".jpg")
            if res:
                # 存入数据库
                avatar_url = get_read_url(file_name + ".jpg")
                crud.upload_history.create_upload(db,
                                                  schemas.UploadHistoryCreate(file_name=file_name, url=avatar_url, status=1))
            else:
                return make_return(400, "upload file to cos failed,please contact admin!")
    except Exception as ex:
        print(ex)
        avatar_url = ""

    data_in = schemas.MasterRegister(
        verify_code=verify_code,
        name=name,
        avatar=avatar_url,
        phone=phone,
        email=email)


    data_in.im_status=1
    master = crud.master.register(db, obj_in=data_in)
    register_account(avatar_url, 1, "master_"+str(master.id), name)
    return master


@router.get("/{master_id}", response_model=schemas.Master)
def read_master_by_id(
        master_id: int,
        current_user: models.User = Depends(deps.get_current_active_superuser),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific master by id.
    """
    master = crud.master.get(db, id=master_id)
    if not master:
        raise HTTPException(
            status_code=404,
            detail="The master with this phone does not exist in the system",
        )
    return master


@router.put("/{master_id}", response_model=schemas.Master)
def update_master(
        *,
        db: Session = Depends(deps.get_db),
        master_id: int,
        obj_in: schemas.MasterUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a master. (superuser only)
    """
    master = crud.master.get(db, id=master_id)
    if not master:
        raise HTTPException(
            status_code=404,
            detail="The master with this phone does not exist in the system",
        )
    master = crud.master.update(db, db_obj=master, obj_in=obj_in)
    return master



