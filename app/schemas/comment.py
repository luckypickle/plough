from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CommentStatus(Enum):
    init: int = 0
    checked: int = 1
    removed: int = 2


# Shared properties
class CommentBase(BaseModel):
    order_id: Optional[int] = None
    content: Optional[str] = None
    rate: Optional[int] = None


# Properties to receive via API on creation
class CommentCreate(CommentBase):
    pass


# Properties to receive via API on update
class CommentUpdate(CommentBase):
    status: Optional[int] = None


class CommentInDBBase(CommentBase):
    id: Optional[int] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Comment(CommentInDBBase):
    pass


# Additional properties stored in DB
class CommentInDB(CommentInDBBase):
    pass
