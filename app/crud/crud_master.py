from random import sample
from string import ascii_letters, digits
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.db.base_class import Base
from app.models.master import Master
from app.schemas.master import MasterCreate, MasterUpdate, MasterRegister, MasterStatus


class CRUDMaster(CRUDBase[Master, MasterCreate, MasterUpdate]):
    @staticmethod
    def get_by_id(db: Session, *, id: int) -> Optional[Master]:
        return db.query(Master).filter(Master.id == id).first()

    @staticmethod
    def get_by_name(db: Session, *, name: str) -> Optional[Master]:
        return db.query(Master).filter(Master.name == name).first()

    @staticmethod
    def get_by_phone(db: Session, *, phone: str) -> Optional[Master]:
        return db.query(Master).filter(Master.phone == phone).first()

    @staticmethod
    def get_multi_with_conditions(db: Session, *, status: int, skip: int = 0, limit: int = 100) -> (int, Optional[
        Master]):
        query = db.query(Master)
        if status >= 0:
            query = query.filter(Master.status == status)
        return (
            query.count(),
            query.offset(skip).limit(limit).all()
        )

    def create(self, db: Session, *, obj_in: MasterCreate) -> Optional[Master]:
        master = self.get_by_phone(obj_in.phone)
        if not master or master.status == MasterStatus.refused.value:
            db_obj = Master()
            db_obj.hashed_password = get_password_hash("12345678"),
            db_obj.name = obj_in.name,
            db_obj.avatar = obj_in.avatar,
            db_obj.rate = 40,
            db_obj.phone = obj_in.phone,
            db_obj.price = 0,
            db_obj.status = MasterStatus.inactive.value
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            return None

    @staticmethod
    def login(db: Session, *, phone: str, password: str, verified: bool) -> Optional[Master]:
        master = CRUDMaster.get_by_phone(db, phone=phone)
        if verified or (master and verify_password(password, master.hashed_password)):
            return master
        else:
            return None

    @staticmethod
    def register(db: Session, *, obj_in: MasterRegister) -> Optional[Master]:
        master = CRUDMaster.get_by_phone(db=db, phone=obj_in.phone)
        if not master or master.status == MasterStatus.refused.value:
            db_obj = Master()
            db_obj.hashed_password = get_password_hash("12345678")
            db_obj.name = obj_in.name
            db_obj.avatar = obj_in.avatar
            db_obj.rate = 40
            db_obj.phone = obj_in.phone
            db_obj.status = MasterStatus.inactive.value
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            return None

    def update(
            self, db: Session, *, db_obj: Master, obj_in: Union[MasterUpdate, Dict[str, Any]]
    ) -> Base:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super(CRUDMaster,self).update(db, db_obj=db_obj, obj_in=update_data)

    @staticmethod
    def is_active(master: Master) -> bool:
        if hasattr(master, "status"):
            return master.status == 1
        else:
            return False


master = CRUDMaster(Master)
