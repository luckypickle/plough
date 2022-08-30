from typing import List
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.mpcode import MPCode
from app.schemas.mpcode import MPCodeCreate, MPCodeUpdate


class CRUDMPCode(CRUDBase[MPCode, MPCodeCreate, MPCodeUpdate]):
    # FIXME, no lock for fetching code in parallel
    def create(
            self, db: Session, *, obj_in: MPCodeCreate
    ) -> MPCode:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def verify_mpcode(self, db: Session, *, phone: str, verify_code: str) -> bool:
        now = int(time.time())
        valid_codes = db.query(MPCode).filter(MPCode.phone == phone, MPCode.status == 0).all()
        for c in valid_codes:
            if c.expire_time >= now:
                c.status = 1
                db.add(c)
                db.commit()
                db.refresh(c)
                return True
        return False

    def get_unused_code(self, db: Session, *, phone: str) -> List[MPCode]:
        return (
            db.query(self.model)
                .filter(MPCode.phone == phone, MPCode.status == 0)
                .all()
        )

    def get_by_owner_phone_request_time(
            self, db: Session, *, phone: str, request_time: int
    ) -> List[MPCode]:
        return (
            db.query(self.model)
                .filter(MPCode.phone == phone, MPCode.request_time > request_time, MPCode.status == 0)
                .all()
        )


mpcode = CRUDMPCode(MPCode)
