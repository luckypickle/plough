from typing import Optional,List

from pydantic import BaseModel, EmailStr


# Shared properties
class BillBase(BaseModel):
    id: Optional[int] = 0
    master_id: Optional[int] = 0
    value: Optional[int] = None
    bill_date: Optional[str] = None
    status: Optional[int] = 0



# Properties to receive via API on creation
class BillCreate(BillBase):
    pass

class BillQuery(BillBase):
    master_name: Optional[str] = None

class BillList(BaseModel):
    total: Optional[int]=0
    bills: List[BillQuery]



# Properties to receive via API on update
class BillUpdate(BaseModel):
    id: Optional[int] = 0
    status: Optional[int] = 0


