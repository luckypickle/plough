from typing import Optional

from pydantic import BaseModel


# Shared properties
class WithdrawBase(BaseModel):
    user_id: Optional[int] = None

# Properties to receive via API on creation
class WithdrawCreate(WithdrawBase):
    pay_name:Optional[str]= None
    pay_card_num:Optional[str]= None
    pay_amount : Optional[int] = None
    status:Optional[int]=0


# Properties to receive via API on update
class WithdrawUpdate(WithdrawBase):
    pass

class WithdrawInDBBase(WithdrawBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Withdraw(WithdrawInDBBase):
    pass

