from typing import Optional
from sqlalchemy import DateTime

from pydantic import BaseModel


# Shared properties
class MeihuaBase(BaseModel):
    owner_id: Optional[int] = None
    cause: Optional[str] = None
    way: Optional[int] = 1
    shanggua: Optional[int] = 0
    xiagua: Optional[int] = 0
    dongyao: Optional[int] = 0
    pic: Optional[str] = None


# Properties to receive via API on creation
class MeihuaCreate(MeihuaBase):
    pass

# Properties to receive via API on update
class MeihuaUpdate(MeihuaBase):
   pass

class MeihuaQuery(MeihuaBase):
    id: Optional[int] = None
    result: Optional[str] = None
    create_time: Optional[str] = "None"

class MeihuaInDBBase(MeihuaBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    class Config:
        orm_mode = True
    
# Additional properties to return via API
class Meihua(MeihuaInDBBase):
    pass
