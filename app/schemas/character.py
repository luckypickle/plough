from typing import Optional
from sqlalchemy import DateTime

from pydantic import BaseModel
from datetime import datetime

# Shared properties
class CharacterBase(BaseModel):
    owner_id: Optional[int] = None
    chars: Optional[str] = None
    chars_wuxing: Optional[str] = None

# Properties to receive via API on creation
class CharacterCreate(CharacterBase):
    update_time: Optional[datetime] = None

# Properties to receive via API on update
class CharacterUpdate(CharacterBase):
   pass

class CharacterQuery(CharacterBase):
    id: Optional[int] = None

class CharacterInDBBase(CharacterBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    class Config:
        orm_mode = True
    
# Additional properties to return via API
class Character(CharacterInDBBase):
    pass
