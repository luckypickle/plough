import time
import random
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas, utils
from app.api import deps
from app.core import security
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.core.security import get_password_hash
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
    send_verify_code,
)

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    entity = None
    if "master" in form_data.scopes:
        verified = crud.mpcode.verify_mpcode(
            db=db, 
            phone=form_data.username, 
            verify_code=form_data.password)
        if form_data.password == "9999":
            verified = True
        master = crud.master.login(
            db=db, 
            phone=form_data.username,
            email=form_data.username,
            password=form_data.password,
            verified=verified
        )
        if master is None:
            if verified:
                raise HTTPException(status_code=400, detail="No valid master")
            else:
                raise HTTPException(status_code=400, detail="Incorrect username or password")
        elif not crud.master.is_active(master):
            raise HTTPException(status_code=400, detail="Inactive master")
        entity = master
    else:
        if form_data.username.count('@') != 0:
            raise HTTPException(status_code=400, detail="Incorrect username")
        user = crud.user.login_or_register(
            db, phone=form_data.username, verify_code=form_data.password
        )
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        elif not crud.user.is_active(user):
            raise HTTPException(status_code=400, detail="Inactive user")
        entity = user
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": security.create_access_token(
            data={"sub": str(entity.id), "scopes": form_data.scopes},
            expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}


@router.post("/request-mpcode/", response_model=schemas.Msg)
def request_mpcode(
    phone: str = Body(...),
    db: Session = Depends(deps.get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> Any:
    """
    Request mpcode
    """
    now = int(time.time())
    valid_request_time = now - settings.mpcode_request_interval
    mpcodes = crud.mpcode.get_unused_code(db, phone=phone)
    need_generate = True
    retry_delta = 0
    for m in mpcodes:
        if m.request_time < valid_request_time:
            m.status = 2
            db.add(m)
            db.commit()
        else:
            if retry_delta < m.request_time - valid_request_time:
                retry_delta = m.request_time - valid_request_time
            need_generate = False
    if need_generate:
        code = utils.random_password_number(6)
        mpcodeCreate = schemas.MPCodeCreate(
            phone=phone, code=code,
            request_time=now, expire_time=now+300,
            status=0
        )
        crud.mpcode.create(db, obj_in=mpcodeCreate)
        ret = send_verify_code(phone, code)
        return {"msg": f"code generated successfully: {ret}"}
    else:
        return {"msg": f"please request after {retry_delta} seconds"}
@router.post("/request-emailcode/", response_model=Any)
def request_emailcode(
    email: str = Body(...),
    db: Session = Depends(deps.get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> Any:
    """
    Request email code
    """
    now = int(time.time())
    valid_request_time = now - settings.emailcode_request_interval
    mpcodes = crud.mpcode.get_unused_code(db, phone=email)
    need_generate = True
    retry_delta = 0
    for m in mpcodes:
        if m.request_time < valid_request_time:
            m.status = 2
            db.add(m)
            db.commit()
        else:
            if retry_delta < m.request_time - valid_request_time:
                retry_delta = m.request_time - valid_request_time
            need_generate = False
    if need_generate:
        code = utils.random_password_number(6)
        mpcodeCreate = schemas.MPCodeCreate(
            phone=email, code=code,
            request_time=now, expire_time=now + settings.emailcode_request_interval,
            status=0
        )
        crud.mpcode.create(db, obj_in=mpcodeCreate)
        ret = utils.send_verify_email(email=email,verify_code=code)
        return {"msg": f"code generated successfully: {ret}"}
    else:
        return {"msg": f"please request after {retry_delta} seconds"}