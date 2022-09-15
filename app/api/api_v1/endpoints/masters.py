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
    masters = crud.master.get_multi(db, skip=skip, limit=limit)
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
        status: int = -1,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve masters. (superuser only)
    """
    total, masters = crud.master.get_multi_with_conditions(db=db, status=status, skip=skip, limit=limit)
    ret_obj = schemas.MasterQuery(
        total=total,
        masters=masters
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
                avg_rate = util.cache_master_rate[str(one_data.id)],
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


@router.get("/me", response_model=schemas.Master)
def read_master_me(
        db: Session = Depends(deps.get_db),
        current_master: models.Master = Depends(deps.get_current_active_master),
) -> Any:
    """
    Get current master.
    """
    return current_master


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
    data_in = schemas.MasterRegister(
        verify_code=verify_code,
        name=name,
        avatar=avatar,
        phone=phone,
        email=email)
    master = crud.master.register(db, obj_in=data_in)
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
