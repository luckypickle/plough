from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class MasterProdcutBase(BaseModel):
    master_id:Optional[int] = None
    product_id: Optional[int] = None
    price: Optional[int] = None
    status: Optional[int] = 1



# Properties to receive via API on creation
class MasterProdcutCreate(MasterProdcutBase):
    pass


# Properties to receive via API on update
class MasterProdcutUpdate(MasterProdcutBase):
    pass


class MasterProdcutInDBBase(MasterProdcutBase):
    id: Optional[int] = None
    create_time: Optional[str] = None


    class Config:
        orm_mode = True


# Additional properties to return via API
class MasterProduct(MasterProdcutInDBBase):
    pass
