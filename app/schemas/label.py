from typing import Optional

from pydantic import BaseModel


# Shared properties
class LabelBase(BaseModel):
    label_name: Optional[str] = None
    user_id: Optional[int] = None


# Properties to receive via API on creation
class LabelCreate(LabelBase):
    label_type: Optional[int] = 0


# Properties to receive via API on update
class LabelUpdate(LabelBase):
    pass

class LabelQuery(LabelBase):
    id: Optional[int] = None

class LabelInDBBase(LabelBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    label_type: Optional[int] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class Label(LabelInDBBase):
    pass
