from random import sample
from string import ascii_letters, digits
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.master import Master
from app.schemas.master import MasterCreate, MasterUpdate, MasterRegister, MasterStatus


class CRUDMaster(CRUDBase[Master, MasterCreate, MasterUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Master]:
        return db.query(Master).filter(Master.name == name).first()

    def get_by_phone(self, db: Session, *, phone: str) -> Optional[Master]:
        return db.query(Master).filter(Master.phone == phone).first()

    def get_multi_with_conditions(self, db: Session, *, status: int, skip: int = 0, limit: int = 100) -> Optional[
        Master]:
        query = db.query(Master)
        if status >= 0:
            query = query.filter(Master.status == status)
        return (
            query.count(),
            query.offset(skip).limit(limit).all()
        )

    def create(self, db: Session, *, obj_in: MasterCreate) -> Master:
        master = self.get_by_phone(obj_in.phone)
        if not master or master.status == MasterStatus.refused:
            db_obj = Master(
                hashed_password=get_password_hash("12345678"),
                name=obj_in.name,
                avatar=obj_in.avatar,
                rate=40,
                phone=obj_in.phone,
                price=0,
                status=MasterStatus.inactive.value
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            return None

    def login(self, db: Session, *, phone: str, password: str, verified: bool) -> Optional[Master]:
        master = self.get_by_phone(db, phone=phone)
        if verified or (master and verify_password(password, master.hashed_password)):
            return master
        else:
            return None

    def register(self, db: Session, *, obj_in: MasterRegister) -> Master:
        master = self.get_by_phone(db=db, phone=obj_in.phone)
        if not master or master.status == MasterStatus.refused:
            db_obj = Master(
                hashed_password=get_password_hash("12345678"),
                name=obj_in.name,
                avatar=obj_in.avatar,
                rate=40,
                phone=obj_in.phone,
                status=MasterStatus.inactive.value
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            return None

    def update(
            self, db: Session, *, db_obj: Master, obj_in: Union[MasterUpdate, Dict[str, Any]]
    ) -> Master:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def is_active(self, master: Master) -> bool:
        if hasattr(master, "status"):
            return master.status == 1
        else:
            return False


master = CRUDMaster(Master)
