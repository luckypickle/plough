from typing import Generator, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import get_app_settings
from app.db.session import SessionLocal

settings = get_app_settings()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_prefix}/login/access-token",
    scopes={
        "user": "Read information about the current user.",
        "master": "Read information about the current master."}
)


# master_oauth2 = OAuth2PasswordBearer(
#     tokenUrl=f"{settings.api_prefix}/login/master-token"
# )


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
        security_scopes: SecurityScopes,
        db: Session = Depends(get_db),
        token: str = Depends(reusable_oauth2)
) -> Any:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key.get_secret_value(), algorithms=[security.ALGORITHM]
        )
        token_scopes = payload.get("scopes", [])
        entity_id = payload.get("sub")
        if entity_id is None:
            raise credentials_exception
        token_data = schemas.TokenPayload(scopes=token_scopes, sub=entity_id)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if "master" in token_data.scopes:
        entity = crud.master.get(db, id=token_data.sub)
    else:
        entity = crud.user.get(db, id=token_data.sub)
    if not entity:
        raise HTTPException(status_code=404, detail="User not found")
    return entity


def get_current_active_master(
        current_master: models.Master = Depends(get_current_user),
) -> models.Master:
    if not crud.master.is_active(current_master):
        raise HTTPException(status_code=400, detail="Inactive master")
    return current_master


def get_current_active_user(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
