from typing import Optional
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.crud.base import CRUDBase
from app.models.withdraw import Withdraw
from app.schemas.withdraw import WithdrawCreate, WithdrawUpdate
import datetime


class CRUDWithdraw(CRUDBase[Withdraw, WithdrawCreate, WithdrawUpdate]):
    @staticmethod
    def get_by_id( db: Session, *, id: int) -> Optional[Withdraw]:
        return db.query(Withdraw).filter(Withdraw.id == id).first()
    def get_withdraw_amount(self,db:Session,*,user_id :int):
        total = db.query(func.sum(Withdraw.pay_amount)).filter(Withdraw.user_id == user_id).scalar()
        if total is None:
            total = 0
        return total
    def get_withdraw_items(self,db:Session,*,user_id:int,state:int,start_time:int,end_time:int,skip: int = 0, limit: int = 100):
        query = db.query(self.model)
        conditions = []
        if user_id is not None:
            conditions.append(Withdraw.user_id == user_id)
        if state != 3:
            conditions.append(Withdraw.pay_status == state)
        if start_time is not None:
            conditions.append(Withdraw.create_time >= datetime.datetime.fromtimestamp(start_time))
            conditions.append(Withdraw.create_time < datetime.datetime.fromtimestamp(end_time))
        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(Withdraw.create_user_time.desc()).offset(skip).limit(limit).all()
        )

withdraw = CRUDWithdraw(Withdraw)
