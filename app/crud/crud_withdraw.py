from typing import Optional
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.withdraw import Withdraw
from app.schemas.withdraw import WithdrawCreate, WithdrawUpdate


class CRUDWithdraw(CRUDBase[Withdraw, WithdrawCreate, WithdrawUpdate]):
    @staticmethod
    def get_by_id(self, db: Session, *, id: int) -> Optional[Withdraw]:
        return db.query(Withdraw).filter(Withdraw.id == id).first()


withdraw = CRUDWithdraw(Withdraw)
