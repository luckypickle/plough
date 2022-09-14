from typing import Optional,List

from pydantic import BaseModel
import datetime

# Shared properties
class InviteBase(BaseModel):
    user_id: Optional[int] = None
    phone: Optional[str] = None
    invite_code: Optional[str] = None
    register_time: Optional[datetime.datetime] = None
    first_order_time: Optional[datetime.datetime] = None
# Properties to receive via API on creation
class InviteCreate(InviteBase):
    prev_invite: Optional[int] = None
    prev_prev_invite: Optional[int] = None
    pass


# Properties to receive via API on update
class InviteUpdate(InviteBase):
    prev_invite:Optional[int] = None
    prev_prev_invite:Optional[int] = None
    current_level:Optional[int] = None

class InviteInDBBase(InviteBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class InviteForInfo(InviteBase):
    level: Optional[int] = None
    invited_count: Optional[int] = None
    invited_place_order_count: Optional[int] = None
    prev_user_phone: Optional[str] = None
    total_amount: Optional[int] = None
    uncollect_amount: Optional[int] = None
# Additional properties to return via API
class InvitedUserDetail(InviteBase):
    status: Optional[int] = 1
class InvitedDetailUsers(BaseModel):
    total: int = 0
    invited_users: List[InvitedUserDetail]
class InviteOrder(BaseModel):
    phone:Optional[str]=None
    prev_phone:Optional[str]=None
    prev_prev_phone:Optional[str]=None
    order_count:Optional[int]=0
    order_amount:Optional[int]=0
    register_time:Optional[datetime.datetime]=None

class InviteOrderInfo(BaseModel):
    total:int=0
    invite_orders:List[InviteOrder]

class Invite(InviteInDBBase):
    pass

