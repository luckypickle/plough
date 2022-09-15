from typing import Optional,List

from pydantic import BaseModel
import datetime

# Shared properties
class WithdrawBase(BaseModel):
    pass


# Properties to receive via API on creation
class WithdrawCreate(WithdrawBase):
    pay_name:Optional[str]= None
    pay_card_num:Optional[str]= None
    pay_amount : Optional[int] = None
    pay_status:Optional[int]=0
    user_id: Optional[int] = None
    phone:Optional[str] = None
    create_user_time:Optional[datetime.datetime] = None


# Properties to receive via API on update
class WithdrawUpdate(WithdrawBase):
    pay_status: Optional[int] = 0

class WithdrawInDBBase(WithdrawBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True
class WithdrawInfo(WithdrawCreate):
    phone:Optional[str]=None
    register_time:Optional[datetime.datetime]=None
    id:Optional[int]=None
    order_time:Optional[datetime.datetime]=None
class WithdrawItems(BaseModel):
    total:Optional[int] = 0
    items:List[WithdrawInfo]

# Additional properties to return via API
class Withdraw(WithdrawInDBBase):
    pass

