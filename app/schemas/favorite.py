from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class FavoriteBase(BaseModel):
    user_id: Optional[int] = None
    order_id: Optional[str] = None



# Properties to receive via API on creation
class FavoriteCreate(FavoriteBase):
    status: Optional[int] = 0


# Properties to receive via API on update
class FavoriteUpdate(FavoriteBase):
    status: Optional[int] = 0


class FavoriteInDBBase(FavoriteBase):
    id: Optional[int] = None
    create_time: Optional[str] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Favorite(FavoriteInDBBase):
    pass
