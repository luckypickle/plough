from typing import Optional,List
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.version import Version
from app.schemas.version import VersionUpdate, VersionCreate


class CRUDVersion(CRUDBase[Version, VersionCreate, VersionUpdate]):
    @staticmethod
    def get_by_product(db: Session, *, product: str) -> Optional[Version]:
        return db.query(Version) \
            .filter(Version.product == product) \
            .order_by(Version.release_time.desc()) \
            .first()

    @staticmethod
    def get_multi_by_order(
             db: Session, *, skip: int = 0, limit: int = 100
    ) ->  List[Version]:
        return db.query(Version).order_by(Version.release_time.desc()).offset(skip).limit(limit).all()


    @staticmethod
    def release_version(db: Session, *, obj_in: VersionCreate) -> Optional[Version]:
        db_obj = Version()
        db_obj.vstr = obj_in.vstr
        db_obj.product = obj_in.product
        db_obj.desc = obj_in.desc
        db_obj.memo = obj_in.memo
        db_obj.url = obj_in.url
        db_obj.release_time = int(time.time())
        db_obj.status = int(obj_in.status)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


version = CRUDVersion(Version)
