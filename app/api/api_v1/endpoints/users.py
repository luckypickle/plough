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
from app.bazi.bazi import  convert_lunar_to_solar

router = APIRouter()


@router.get("/list")
def read_users(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    total, users = crud.user.get_user_summary(db, skip=skip, limit=limit)
    return {
        "total": total,
        "users": users
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
        user_name: str = Body(None),
        email: EmailStr = Body(None),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = crud.user.get_by_name(db, name=user_name)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = schemas.UserCreate(
        password=password,
        email=email,
        user_name=user_name,
        phone=phone)
    user = crud.user.create(db, obj_in=user_in)
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
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get divination and save to database.
    """
    bazi = BaZi(year, month, day, hour, sex,lunar,run,minute)
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
        divination=json.dumps(divination)
    )
    crud.history.create_owner_divination(db, history=history)
    return divination


@router.get("/history", response_model=List[schemas.History])
def get_history(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get divination history.
    """
    history = crud.history.get_multi_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    rets = []
    for h in history:
        rets.append(schemas.History(
            id=h.id,
            name=h.name,
            birthday=h.birthday,
            sex=h.sex,
            location=h.location,
            divination=h.divination,
            create_time=h.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
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
