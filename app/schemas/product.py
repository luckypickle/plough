from typing import Optional

from pydantic import BaseModel


# Shared properties
class ProductBase(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    status: Optional[int] = None
    sort_weight: Optional[int] = None


class ProductForOrder(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None
    desc: Optional[str] = None

class ProductForOrderPrice(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None
    desc: Optional[str] = None
    price: Optional[int] = None


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass


# Properties to receive via API on update
class ProductUpdate(ProductBase):
    pass


class ProductInDBBase(ProductBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Product(ProductInDBBase):
    pass


# Additional properties stored in DB
class ProductInDB(ProductInDBBase):
    pass
