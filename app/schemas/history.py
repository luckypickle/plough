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
    beat_info: Optional[str] = None
    label_id: Optional[int] = None

# Properties to receive via API on creation
class HistoryCreate(HistoryBase):
    status: Optional[int] = 0
    history_index: Optional[int] = 0


# Properties to receive via API on update
class HistoryUpdate(HistoryBase):
    history_index: Optional[int] = 0


class HistoryInDBBase(HistoryBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True

# Properties to receive via API on creation
class HistoryQuery(HistoryInDBBase):
    label_name: Optional[str] = None
    like_str: Optional[str] = None
    dislike_str: Optional[str] = None
    pattern: Optional[str] = None
    
# Additional properties to return via API
class History(HistoryInDBBase):
    pass
