import time
import uuid
import random
from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.mpcode import MPCode
from app.models.order import Order
from app.schemas.user import UserCreate, UserUpdate, UserSummary


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_summary(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[UserSummary]:
        query = db.query(func.count(Order.id), func.sum(Order.amount), User.phone, User.create_time, User.id) \
            .join(Order, Order.owner_id == User.id, isouter=True) \
            .filter(User.is_superuser == False) \
            .group_by(User.phone, User.create_time, User.id)
        ret_obj = []
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        for i in users:
            ret_obj.append(UserSummary(
                id=i.id,
                phone=i.phone,
                create_time=str(i.create_time),
                order_count=i[0],
                order_amount=i[1] if i[1] else 0
            ))
        return (total, ret_obj)

    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone).first()

    def login_or_register(self, db: Session, *, phone: str, verify_code: str) -> Optional[User]:
        user = self.get_by_phone(db, phone=phone)
        valid_mpcode = False
        now = int(time.time())
        mpcode = db.query(MPCode).filter(
            MPCode.phone == phone,
            MPCode.expire_time >= now,
            MPCode.status == 0).first()
        if mpcode and mpcode.code == verify_code:
            valid_mpcode = True
        if not user and valid_mpcode:
            return self.create(db, obj_in=UserCreate(phone=phone))
        elif valid_mpcode or verify_password(verify_code, user.hashed_password):
            return user
        else:
            return None

    def create_superuser(self, db: Session, *, obj_in: UserCreate) -> User:
        rand_password = ''.join(random.sample('1234567890abcdefghijklmnopqrstufwxyz', 8))
        db_obj = User(
            hashed_password=get_password_hash(rand_password),
            user_name=str(uuid.uuid4()),
            full_name="",
            is_superuser=True,
            phone=obj_in.phone,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        rand_password = ''.join(random.sample('1234567890abcdefghijklmnopqrstufwxyz', 8))
        db_obj = User(
            hashed_password=get_password_hash(rand_password),
            user_name=str(uuid.uuid4()),
            is_superuser=False,
            phone=obj_in.phone
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    # login with phone
    def authenticate(self, db: Session, *, user_name: str, password: str) -> Optional[User]:
        user = self.get_by_phone(db, phone=user_name)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        if not isinstance(user, User):
            return False
        else:
            return user.is_active

    def is_superuser(self, user: User) -> bool:
        if hasattr(user, "is_superuser"):
            return user.is_superuser
        else:
            return False


user = CRUDUser(User)
