from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    phone: Optional[str] = None
    im_status: Optional[int] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: Optional[str] = None

    pass

# Properties to show in Admin page
class UserSummary(UserBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    order_count: Optional[int] = None
    order_amount: Optional[int] = None
    level:Optional[int] = None


# Properties to receive via API on update
class UserUpdate(UserBase):
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass
class UserStatistics(BaseModel):
    yesterday_register : Optional[int]=0
    today_register : Optional[int]=0
    total_register: Optional[int]=0
    total_order_count:Optional[int]=0
    total_payed_amount:Optional[int]=0

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
