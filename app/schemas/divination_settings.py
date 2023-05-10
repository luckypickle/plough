from typing import Optional

from pydantic import BaseModel

# Shared properties
class DivinationSettingsBase(BaseModel):
    user_id: Optional[int] = None
    master_id: Optional[int] = None
    entry_type: Optional[int] = 0
    show_type: Optional[int] = 0
    analysis_isClose:Optional[bool]=False
    taimingshen_isClose:Optional[bool]=False
    xingyun_isClose:Optional[bool]=False
    liuri_isClose:Optional[bool]=True
    early_isOpen:Optional[bool]=False
    wuxing_time_isOpen:Optional[bool]=False
# Properties to receive via API on creation
class DivinationSettingsCreate(DivinationSettingsBase):
    pass

# Properties to receive via API on update
class DivinationSettingsUpdate(DivinationSettingsBase):
    pass

class DivinationSettingsQuery(DivinationSettingsBase):
    class Config:
        orm_mode = True

class DivinationSettingsInDBBase(DivinationSettingsBase):
    id: Optional[int] = None
    create_time: Optional[str] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class DivinationSettings(DivinationSettingsInDBBase):
    pass
