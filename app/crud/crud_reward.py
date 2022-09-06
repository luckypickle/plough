from typing import Optional
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.reward import Reward
from app.schemas.reward import RewardCreate, RewardUpdate


class CRUDReward(CRUDBase[Reward, RewardCreate, RewardUpdate]):
    @staticmethod
    def get_by_id(self, db: Session, *, id: int) -> Optional[Reward]:
        return db.query(Reward).filter(Reward.id == id).first()


reward = CRUDReward(Reward)
