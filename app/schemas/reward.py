from typing import Optional,List

from pydantic import BaseModel
import datetime

# Shared properties
class RewardBase(BaseModel):
    order_id: Optional[int] = None

# Properties to receive via API on creation
class RewardCreate(RewardBase):
    pass


# Properties to receive via API on update
class RewardUpdate(RewardBase):
    pass

class RewardInDBBase(RewardBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class RewardDetail(RewardBase):
    invited_user:Optional[str] = None
    prev_invited_user: Optional[str] = None
    order_amount:Optional[int] = None
    reward_amount:Optional[int] = None
    order_time: Optional[datetime.datetime] = None
    prev_prev_level:Optional[int] = None
class RewardDetailInfos(RewardBase):
    total: int = 0
    reward_details: List[RewardDetail]
# Additional properties to return via API
class Reward(RewardInDBBase):
    pass

