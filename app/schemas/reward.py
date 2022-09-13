from typing import Optional

from pydantic import BaseModel


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


# Additional properties to return via API
class Reward(RewardInDBBase):
    pass

