from typing import Optional,List
from pydantic import BaseModel


# Shared properties
class FolderOrderBase(BaseModel):
    order_id: Optional[int] = None
    folder_id: Optional[int] = None
    master_id: Optional[int] = None

# Properties to receive via API on creation
class FolderOrderCreate(FolderOrderBase):
    status: Optional[int] = 0

class FolderOrderIds(BaseModel):
    ids: List[int]

# Properties to receive via API on update
class FolderOrderUpdate(FolderOrderBase):
    pass

class FolderOrderInDBBase(FolderOrderBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class FolderOrder(FolderOrderInDBBase):
    pass
