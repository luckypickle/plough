from typing import Optional, List
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.invite import Invite
from app.schemas.invite import InviteCreate, InviteUpdate, InviteForInfo


class CRUDInvite(CRUDBase[Invite, InviteCreate, InviteUpdate]):
    @staticmethod
    def get_by_id(self, db: Session, *, id: int) -> Optional[Invite]:
        return db.query(Invite).filter(Invite.id == id).first()

    @staticmethod
    def get_invite_info(
            db: Session, *,
            user_id: int
    ) -> (Optional[Invite]):
        return db.query(Invite).filter(Invite.user_id == user_id).first()
    @staticmethod
    def get_invite_code(
            db:Session,*,
            user_id:int
    )->(Optional[str]):
        row = db.query(Invite.invite_code).filter(Invite.user_id == user_id).first()
        return row.invite_code
    @staticmethod
    def get_invite_user(
            db:Session,*,
            invite_code:str
    )->(Optional[Invite]):
        return db.query(Invite).filter(Invite.invite_code == invite_code).first()

    def get_invited_users(
            self, db: Session, *,
            user_id:int,
            skip: int = 0, limit: int = 100
    ) -> (int, List[Invite]):
        query = db.query(self.model)
        conditions = []
        conditions.append(Invite.prev_invite == user_id)
        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(Invite.register_time.desc()).offset(skip).limit(limit).all()
        )
    def get_prev_count(self,db: Session, *,
            user_id: int)->int:
        pass
    def get_prev_prev_count(selfdb: Session, *,
            user_id: int)->int:
        pass
invite = CRUDInvite(Invite)
