from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UploadHistoryBase(BaseModel):
    file_name: Optional[str] = None
    url: Optional[str] = None



# Properties to receive via API on creation
class UploadHistoryCreate(UploadHistoryBase):
    status: Optional[int] = 0


# Properties to receive via API on update
class UploadHistoryUpdate(UploadHistoryBase):
    pass


class UploadHistoryInDBBase(UploadHistoryBase):
    id: Optional[int] = None
    create_time: Optional[str] = None


    class Config:
        orm_mode = True


# Additional properties to return via API
class UploadHistory(UploadHistoryInDBBase):
    pass

class FileType(BaseModel):
    file_type:str