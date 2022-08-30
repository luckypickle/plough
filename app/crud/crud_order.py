import time
from typing import List
from random import sample
from string import ascii_letters, digits

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate, OrderUpdateDivination, OrderStatus


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    @staticmethod
    def create_with_owner(
        db: Session, *, obj_in: OrderCreate, owner_id: int
    ) -> Order:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Order()
        for k, v in obj_in_data.items():
            setattr(db_obj, k, v)
        db_obj.owner_id = owner_id,
        db_obj.arrange_status = 0,
        db_obj.status = OrderStatus.init.value,
        db_obj.order_number = ''.join(sample(ascii_letters + digits, 16))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def updateDivination(db: Session, *, db_obj: Order, obj_in: OrderUpdateDivination) -> Order:
        db_obj.divination = obj_in.divination
        # db_obj.status = OrderStatus.checked
        db_obj.arrange_status = 1
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


    @staticmethod
    def get_summary(db: Session, role: int, role_id: int):
        if role == 0:  # superuser
            orders = db.query(Order).all()
        elif role == 1:  # user
            orders = db.query(Order).filter(Order.owner_id == role_id).all()
        elif role == 2:  # master
            orders = db.query(Order).filter(Order.master_id == role_id).all()
        else:
            orders = []
        return len(orders)

    def get_multi_with_condition(
            self, db: Session, *,
            role_id: int,
            role: int = 0,
            status: int = -1,
            skip: int = 0, limit: int = 100
    ) -> (int, List[Order]):
        query = db.query(self.model)
        conditions = []
        if role == 1:
            conditions.append(Order.owner_id == role_id)
        elif role == 2:
            conditions.append(Order.master_id == role_id)
        if status >= 0:
            conditions.append(Order.status == status)
        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
        )

    def get_open_orders(
            self, db: Session, *,
            skip: int = 0, limit: int = 100
    ) -> (int, List[Order]):
        query = db.query(self.model)
        conditions = []
        conditions.append(Order.is_open==1)
        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
        )


order = CRUDOrder(Order)
