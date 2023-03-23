from typing import Optional

from pydantic import BaseModel


# Shared properties
class RemindDayBase(BaseModel):
    owner_id: Optional[int] = None
    title: Optional[str] = None
    name: Optional[str] = None
    day_time: Optional[str] = None
    content: Optional[str] = None
    remind_days: Optional[str] = '0'
    remind_type: Optional[int] = 1
    remind_calendar: Optional[int] = 1

# Properties to receive via API on creation
class RemindDayCreate(RemindDayBase):
    pass


# Properties to receive via API on update
class RemindDayUpdate(RemindDayBase):
   pass

class RemindDayQuery(RemindDayBase):
    id: Optional[int] = None
    days: Optional[int] = 0

class RemindDayInDBBase(RemindDayBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    class Config:
        orm_mode = True
    
# Additional properties to return via API
class RemindDay(RemindDayInDBBase):
    pass
