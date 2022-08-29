from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class VersionBase(BaseModel):
    product: Optional[str] = None
    vstr: Optional[str] = None
    desc: Optional[str] = None
    memo: Optional[str] = None
    url: Optional[str] = None

# Properties to receive via API on creation
class VersionCreate(VersionBase):
    status: Optional[int] = None

# Properties to receive via API on update
class VersionUpdate(VersionBase):
    release_time: Optional[int] = None
    status: Optional[int] = None

class VersionInDBBase(VersionBase):
    id: Optional[int] = None
    status: Optional[int] = None
    release_time: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Version(VersionInDBBase):
    pass

