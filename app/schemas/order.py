from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class OrderStatus(Enum):
    init: int = 0
    checked: int = 1
    done: int = 2
    cancel: int = 3


# Shared properties
class OrderBase(BaseModel):
    pass


# Properties to receive on item creation
class OrderCreate(OrderBase):
    product_id: int
    name: Optional[str]
    sex: Optional[int]
    birthday: Optional[str]
    location: Optional[str]
    master_id: Optional[int]
    amount: Optional[int]
    shareRate: Optional[int]
    create_time: Optional[str]
    pay_type: Optional[str] = "wx"


# Properties to receive on item update
class OrderUpdate(OrderCreate):
    arrange_status: Optional[int]
    reason: Optional[str]
    status: Optional[int]
    open: Optional[int]


class OrderUpdateDivination(OrderBase):
    divination: Optional[str] = None


# Properties shared by models stored in DB
class OrderInDBBase(OrderCreate):
    id: int
    order_number: str
    owner_id: int
    master_id: int
    name: Optional[str] = None
    sex: Optional[int] = None
    birthday: Optional[str] = None
    location: Optional[str] = None
    amount: Optional[int] = None
    shareRate: Optional[int] = None
    divination: Optional[str] = None
    reason: Optional[str] = None
    create_time: Optional[str] = None
    pay_time: Optional[str] = None
    arrange_status: Optional[int] = None
    status: Optional[int] = OrderStatus.init.value
    is_open: Optional[int] = 0

    class Config:
        orm_mode = True


# Properties to return to client
class Order(OrderInDBBase):
    master: Optional[str] = None
    master_avatar: Optional[str] = None
    owner: Optional[str] = None
    product: Optional[str] = None


class OrderQuery(BaseModel):
    total: int = 0
    orders: List[Order]


# Properties properties stored in DB
class OrderInDB(OrderInDBBase):
    pass
