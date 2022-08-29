from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class MasterStatus(Enum):
    inactive: int = 0
    active: int = 1
    refused: int = 2
    freeze: int = 3


# Shared properties
class MasterBase(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None

# Properties to receive via API on creation
class MasterCreate(MasterBase):
    pass

class MasterForOrder(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    id: Optional[int] = None
    price: Optional[int] = None
    avatar: Optional[str] = None

class MasterRegister(MasterBase):
    verify_code: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None


# Properties to receive via API on update
class MasterUpdate(MasterBase):
    name: Optional[str] = None
    status: Optional[int] = None
    phone: Optional[str] = None
    rate: Optional[int] = None
    password: Optional[str] = None
    price: Optional[int] = None
    desc: Optional[str] = None


class MasterInDBBase(MasterBase):
    id: Optional[int] = None
    name: Optional[str] = None
    rate: Optional[int] = None
    order_number: Optional[int] = None
    order_amount: Optional[int] = None
    price: Optional[int] = None
    create_time: Optional[datetime] = None
    desc: Optional[str] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Master(MasterInDBBase):
    pass

class MasterQuery(BaseModel):
    total: int
    masters: List[Master]

# Additional properties stored in DB
class MasterInDB(MasterInDBBase):
    hashed_password: str
