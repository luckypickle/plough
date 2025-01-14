from typing import Optional

from pydantic import BaseModel


# Shared properties
class HistoryCombineBase(BaseModel):
    owner_id: Optional[int] = None
    name1: Optional[str] = None
    birthday1: Optional[str] = None
    sex1: Optional[int] = 1
    location1: Optional[str] = ''
    divination1: Optional[str] = ''
    isNorth1:Optional[bool]=True
    name2: Optional[str] = None
    birthday2: Optional[str] = None
    sex2: Optional[int] = 1
    location2: Optional[str] = ''
    divination2: Optional[str] = ''
    isNorth2:Optional[bool]=True

# Properties to receive via API on creation
class HistoryCombineCreate(HistoryCombineBase):
    pass


# Properties to receive via API on update
class HistoryCombineUpdate(HistoryCombineBase):
    pass

class HistoryCombineQuery(HistoryCombineBase):
    id: Optional[int] = None
    create_time: Optional[str] = None

class HistoryCombineInDBBase(HistoryCombineBase):
    id: Optional[int] = None
    create_time: Optional[str] = None

    class Config:
        orm_mode = True
    
# Additional properties to return via API
class HistoryCombine(HistoryCombineInDBBase):
    pass
