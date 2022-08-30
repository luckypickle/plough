from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
# from app.core.celery_app import celery_app
from app.utils import send_test_email
from app.bazi.citys import cal_zone
from app.bazi.bazi import getYearJieQi

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
    versions = crud.version.get_multi(db=db, skip=skip, limit=limit)
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
