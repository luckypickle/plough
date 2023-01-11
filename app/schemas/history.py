from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class HistoryBase(BaseModel):
    owner_id: Optional[int] = None
    name: Optional[str] = None
    birthday: Optional[str] = None
    sex: Optional[int] = 1
    location: Optional[str] = ''
    divination: Optional[str] = ''
    isNorth:Optional[bool]=True


# Properties to receive via API on creation
class HistoryCreate(HistoryBase):
    status: Optional[int] = 0


# Properties to receive via API on update
class HistoryUpdate(HistoryBase):
    pass


class HistoryInDBBase(HistoryBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class History(HistoryInDBBase):
    pass
