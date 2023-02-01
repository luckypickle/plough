from typing import Optional

from pydantic import BaseModel


# Shared properties
class FolderBase(BaseModel):
    folder_name: Optional[str] = None
    master_id: Optional[int] = None


# Properties to receive via API on creation
class FolderCreate(FolderBase):
    status: Optional[int] = 0


# Properties to receive via API on update
class FolderUpdate(FolderBase):
    pass

class FolderQuery(FolderBase):
    count: int = 0

class FolderInDBBase(FolderBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class Folder(FolderInDBBase):
    pass
