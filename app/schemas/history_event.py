from typing import Optional,List
from pydantic import BaseModel


# Shared properties
class HistoryEventBase(BaseModel):
    history_id: Optional[int] = None
    event_type: Optional[str] = None
    year: Optional[int] = None
    year_gz: Optional[str] = None
    content: Optional[str] = None

# Properties to receive via API on creation
class HistoryEventCreate(HistoryEventBase):
    pass

# Properties to receive via API on update
class HistoryEventUpdate(HistoryEventBase):
    pass

class HistoryEventInDBBase(HistoryEventBase):
    id: Optional[int] = None
    create_time: Optional[str] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class HistoryEvent(HistoryEventInDBBase):
    pass
