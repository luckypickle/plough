from typing import Optional

from pydantic import BaseModel


# Shared properties
class RemindBirthdayBase(BaseModel):
    owner_id: Optional[int] = None
    name: Optional[str] = None
    birthday: Optional[str] = None
    sex: Optional[int] = 1
    location: Optional[str] = ''
    label: Optional[str] = ''
    remind_days: Optional[str] = '0'
    remind_type: Optional[int] = 1
    remind_calendar: Optional[int] = 1

# Properties to receive via API on creation
class RemindBirthdayCreate(RemindBirthdayBase):
    pass


# Properties to receive via API on update
class RemindBirthdayUpdate(RemindBirthdayBase):
   pass

class RemindBirthdayQuery(RemindBirthdayBase):
    id: Optional[int] = None
    days: Optional[int] = 0

class RemindBirthdayInDBBase(RemindBirthdayBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    class Config:
        orm_mode = True
    
# Additional properties to return via API
class RemindBirthday(RemindBirthdayInDBBase):
    pass
