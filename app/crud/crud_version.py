from typing import Optional
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.version import Version
from app.schemas.version import VersionUpdate, VersionCreate


class CRUDVersion(CRUDBase[Version, VersionCreate, VersionUpdate]):
    def get_by_product(self, db: Session, *, product: str) -> Optional[Version]:
        return db.query(Version) \
            .filter(Version.product == product) \
            .order_by(Version.release_time.desc()) \
            .first()

    def release_version(self, db: Session, *, obj_in: VersionCreate) -> Optional[Version]:
        db_obj = Version(
            vstr=obj_in.vstr,
            product=obj_in.product,
            desc=obj_in.desc,
            memo=obj_in.memo,
            url=obj_in.url,
            release_time=int(time.time()),
            status=int(obj_in.status)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

version = CRUDVersion(Version)
