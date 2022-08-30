from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class MPCodeBase(BaseModel):
    phone: Optional[str] = None
    code: Optional[str] = None
    request_time: Optional[int] = None
    expire_time: Optional[int] = None
    status: Optional[int] = None


# Properties to receive via API on creation
class MPCodeCreate(MPCodeBase):
    pass


# Properties to receive via API on update
class MPCodeUpdate(MPCodeBase):
    pass


class MPCodeInDBBase(MPCodeBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class MPCode(MPCodeInDBBase):
    pass


# Additional properties stored in DB
class MPCodeInDB(MPCodeInDBBase):
    pass
