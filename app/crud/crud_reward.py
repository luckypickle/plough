from typing import Optional,List
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.crud.base import CRUDBase
from app.models.reward import Reward
from app.schemas.reward import RewardCreate, RewardUpdate


class CRUDReward(CRUDBase[Reward, RewardCreate, RewardUpdate]):
    @staticmethod
    def get_by_id(self, db: Session, *, id: int) -> Optional[Reward]:
        return db.query(Reward).filter(Reward.id == id).first()
    def get_reward_list(
            self, db: Session, *,
            user_id:int,
            skip: int = 0, limit: int = 100
    ) -> (int, List[Reward]):
        query = db.query(self.model)
        conditions = []
        conditions.append(Reward.prev_user_id == user_id or Reward.prev_prev_user_id == user_id)
        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(Reward.order_time.desc()).offset(skip).limit(limit).all()
        )
    def get_first_total_reward(self, db: Session, *,
            user_id:int)->int:
        return db.query(func.sum(Reward.prev_amount)).filter(Reward.prev_user_id == user_id).scalar()
    def get_second_total_reward(self, db: Session, *,
            user_id:int)->int:
        return db.query(func.sum(Reward.prev_prev_amount)).filter(Reward.prev_prev_user_id == user_id).scalar()

reward = CRUDReward(Reward)
