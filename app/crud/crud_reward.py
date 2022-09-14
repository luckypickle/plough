from typing import Optional,List
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func,or_

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
        conditions.append(Reward.prev_user_id == user_id)
        conditions.append(Reward.prev_prev_user_id == user_id)
        query = query.filter(or_(*conditions))
        return (
            query.count(),
            query.order_by(Reward.order_time.desc()).offset(skip).limit(limit).all()
        )
    def get_reward_list_condition(
            self, db: Session, *,
            user_id:int,
            son_user_id:int,
            grand_son_user_id:int,
            level:int,
            skip: int = 0, limit: int = 100
    ) -> (int, List[Reward]):
        query = db.query(self.model)
        conditions = []
        if user_id is not None:
            if level == 1:
                conditions.append(Reward.prev_user_id == user_id)
                if son_user_id is not None:
                    conditions.append(Reward.user_id == son_user_id)
            elif level == 2:
                conditions.append(Reward.prev_prev_user_id == user_id)
                if son_user_id is not None:
                    conditions.append(Reward.prev_user_id == son_user_id)
                if grand_son_user_id is not None:
                    conditions.append(Reward.user_id == grand_son_user_id)
            else:
                if grand_son_user_id is not None:
                    conditions.append(Reward.prev_prev_user_id == user_id)
                    conditions.append(Reward.user_id == grand_son_user_id)
                    if son_user_id is not None:
                        conditions.append(Reward.prev_user_id == son_user_id)
                else:
                    if son_user_id is not None:
                        conditions.append((Reward.prev_user_id == user_id and Reward.user_id == son_user_id)
                                          or(Reward.prev_prev_user_id == user_id and Reward.prev_user_id == son_user_id))
                    else:
                         conditions.append(Reward.prev_user_id == user_id or Reward.prev_prev_user_id == user_id)
        else:
            if level == 1:
                if son_user_id is not None:
                    conditions.append(Reward.user_id == son_user_id)
            elif level == 2:
                conditions.append(Reward.prev_prev_user_id != 0)
                if son_user_id is not None:
                    conditions.append(Reward.prev_user_id == son_user_id)
                if grand_son_user_id is not None:
                    conditions.append(Reward.user_id == grand_son_user_id)
            else:
                if grand_son_user_id is not None:
                    conditions.append(Reward.user_id == grand_son_user_id)
                    if son_user_id is not None:
                        conditions.append(Reward.prev_user_id == son_user_id)
                else:
                    if son_user_id is not None:
                        conditions.append(Reward.user_id == son_user_id or Reward.prev_user_id == son_user_id)
        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(Reward.order_time.desc()).offset(skip).limit(limit).all()
        )
    def get_first_total_reward(self, db: Session, *,
            user_id:int)->int:
        total =db.query(func.sum(Reward.prev_amount)).filter(Reward.prev_user_id == user_id).scalar()
        if total is None:
            total =0
        print('first total is ',total)
        return total
    def get_second_total_reward(self, db: Session, *,
            user_id:int)->int:
        total = db.query(func.sum(Reward.prev_prev_amount)).filter(Reward.prev_prev_user_id == user_id).scalar()
        if total is None:
            total =0
        print('Second total is ', total)
        return total

reward = CRUDReward(Reward)
