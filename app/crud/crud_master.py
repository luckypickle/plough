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
        if phone is None or phone =="":
            return None
        return db.query(Master).filter(Master.phone == phone).first()

    @staticmethod
    def get_by_im_status(db: Session,  status: str) -> Optional[Master]:
        if status == 0:
            return db.query(Master).filter((Master.im_status == 0) | (Master.im_status == None)).all()
        return db.query(Master).filter((Master.im_status == status)).all()

    @staticmethod
    def get_by_email(db: Session, *, email: str) -> Optional[Master]:
        if email is None  or email =="":
            return None
        return db.query(Master).filter(Master.email == email).first()

    @staticmethod
    def get_multi_with_conditions(db: Session, *, status: int, name:str = "", skip: int = 0, limit: int = 100 ,is_order:int=0) -> (int, Optional[
        Master]):
        query = db.query(Master)
        if status >= 0:
            query = query.filter(Master.status == status)
        if status ==-2:
            query = query.filter(Master.status !=2)
        if name != "":
            query.filter(Master.name==name)
        if is_order==1:
            return (
                query.count(),
                query.order_by(Master.create_time.desc()).offset(skip).limit(limit).all()
            )
        return (
            query.count(),
            query.order_by(Master.sort_weight.desc()).offset(skip).limit(limit).all()
        )



    def create(self, db: Session, *, obj_in: MasterCreate) -> Optional[Master]:
        master = self.get_by_phone(obj_in.phone)
        master_email = self.get_by_email(obj_in.email)
        if (master is None and master_email is None) or master.status == MasterStatus.refused.value:
            db_obj = Master()
            db_obj.hashed_password = get_password_hash("12345678"),
            db_obj.name = obj_in.name,
            db_obj.avatar = obj_in.avatar,
            db_obj.rate = 40,
            db_obj.phone = obj_in.phone,
            db_obj.email = obj_in.email,
            db_obj.price = 0,
            db_obj.status = MasterStatus.inactive.value
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            return None

    @staticmethod
    def login(db: Session, *, phone: str, password: str,email:str, verified: bool) -> Optional[Master]:
        master = CRUDMaster.get_by_phone(db, phone=phone)
        master_email = CRUDMaster.get_by_email(db,email=email)
        if verified or(master and verify_password(password, master.hashed_password)) or (master_email and verify_password(password, master_email.hashed_password)):
            if master is not None:
                return master
            else:
                return master_email
        else:
            return None

    @staticmethod
    def register(db: Session, *, obj_in: MasterRegister) -> Optional[Master]:
        master = CRUDMaster.get_by_phone(db=db, phone=obj_in.phone)
        master_email = CRUDMaster.get_by_email(db, email=obj_in.email)
        if ((master is None or master.status == MasterStatus.refused.value) and (master_email is None or master_email.status == MasterStatus.refused.value)):
            db_obj = Master()
            db_obj.hashed_password = get_password_hash("12345678")
            db_obj.name = obj_in.name
            db_obj.avatar = obj_in.avatar
            db_obj.rate = 40
            db_obj.phone = obj_in.phone
            db_obj.email = obj_in.email
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
