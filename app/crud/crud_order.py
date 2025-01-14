import time
from typing import List,Optional,Any
from random import sample
from string import ascii_letters, digits

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func, desc,case,or_,text

from app.crud.base import CRUDBase
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate, OrderUpdateDivination, OrderStatus
from app.models.favorite import Favorite
from app.models.master import Master
from app.models.user import User
from app.models.product import Product
import datetime


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    @staticmethod
    def create_with_owner(
        db: Session, *, obj_in: OrderCreate, owner_id: int
    ) -> Order:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Order()
        for k, v in obj_in_data.items():
            setattr(db_obj, k, v)
        db_obj.owner_id = owner_id
        db_obj.arrange_status = 0
        db_obj.status = OrderStatus.init.value
        db_obj.order_number = ''.join(sample(ascii_letters + digits, 16))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_divination_order(
        db: Session, *, obj_in: OrderCreate, owner_id: int, divination:str
    ) -> Order:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Order()
        for k, v in obj_in_data.items():
            setattr(db_obj, k, v)
        db_obj.owner_id = owner_id
        db_obj.arrange_status = 1
        db_obj.divination = divination
        db_obj.status = OrderStatus.init.value
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
            order_number: str = "",
            name: str = "",
            user_phone:str= "",
            master_name: str = "",
            product_id: int = -1,
            arrange_status: int = -1,
            order_min_amount: int = 0,
            order_max_amount: int = 999999999,
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
        if order_number != "":
            conditions.append(Order.order_number == order_number)
        if name != "":
            conditions.append(Order.name == name)
        if user_phone !="":
            query = query.join(User, User.id == Order.owner_id)
            conditions.append(or_( User.phone ==user_phone , User.email==user_phone))
        if master_name != "":
            query = query.join(Master,Master.id == Order.master_id)
            conditions.append(Master.name == master_name)
        if product_id != -1:
            conditions.append(Order.product_id == product_id)
        if arrange_status >=0:
            conditions.append(Order.arrange_status == arrange_status)
        if order_min_amount !=0 :
            conditions.append(Order.amount>=order_min_amount)
        if order_max_amount != 999999999:
            conditions.append(Order.amount<=order_max_amount)

        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(case(whens=[(Order.arrange_status==1,0)] ,else_=1),Order.id.desc()).offset(skip).limit(limit).all()
        )

    def get_multi_with_condition_by_user(
            self, db: Session, *,
            role_id: int,
            order_number: str = "",
            name: str = "",
            user_phone:str= "",
            master_name: str = "",
            product_id: int = -1,
            arrange_status: int = -1,
            order_min_amount: int = 0,
            order_max_amount: int = 999999999,
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
        if order_number != "":
            conditions.append(Order.order_number == order_number)
        if name != "":
            conditions.append(Order.name == name)
        if user_phone !="":
            query = query.join(User, User.id == Order.owner_id)
            conditions.append(or_( User.phone ==user_phone , User.email==user_phone))
        if master_name != "":
            query = query.join(Master,Master.id == Order.master_id)
            conditions.append(Master.name == master_name)
        if product_id != -1:
            conditions.append(Order.product_id == product_id)
        if arrange_status >=0:
            conditions.append(Order.arrange_status == arrange_status)
        if order_min_amount !=0 :
            conditions.append(Order.amount>=order_min_amount)
        if order_max_amount != 999999999:
            conditions.append(Order.amount<=order_max_amount)

        query = query.filter(*conditions)
        return (
            query.count(),
            query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
        )

    def get_multi_and_sum_with_condition(
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
        sql = db.query(func.sum(Order.amount *func.COALESCE(Order.shareRate,0))).filter(Order.arrange_status==3).filter(*conditions)
        return (
            query.count(),
            sql.scalar(),
            query.order_by(Order.arrange_status.asc(), Order.id.desc()).offset(skip).limit(limit).all()
        )

    def get_master_order_rate(self,db: Session,master_id:int) ->(str,str):
        sql  = db.query(func.sum(Order.amount),func.count(1)).filter(Order.status==1)
        sql1  = db.query(func.sum(Order.amount),func.count(1)).filter(Order.status==1).filter(Order.master_id==master_id)
        total_res = sql.first()
        if total_res is None:
            return "0.00%", "0.00%"
        print(total_res)
        user_res = sql1.first()
        if total_res[1] ==0:
            return "0.00%","0.00%"
        if user_res[1] == 0:
            return "0.00%","0.00%"

        return ("%.2f"%(float(user_res[1])*100/ total_res[1])+"%","%.2f"%(float(user_res[0])*100/ total_res[0])+"%")


    def get_all_pending_order(self,db:Session):
        return db.query(self.model).filter(Order.status==1).filter(Order.arrange_status!=3).all()

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

    def get_all_rate_orders(self,db:Session,rate:int):
        if rate ==-1:
            sql =db.query(Order).filter(Order.comment_rate>=0)
        else:
            sql =db.query(Order).filter().filter(Order.comment_rate==rate)

        return sql.all()

    def get_first_order(self,db:Session, *,owner_id:int)->Optional[Order]:
        return db.query(Order).order_by(Order.create_time.asc()).filter(Order.owner_id == owner_id).first()

    def get_all_order_by_bill_state(self, db: Session, bill_state: int):
        sql = db.query(Order).filter(Order.bill_state==bill_state).filter(Order.status==1).filter(Order.arrange_status==3)
        if bill_state ==0:
            sql.filter(Order.bill_state==None)
        return sql.all()

    def get_order_count(self,db:Session,user_id:int):
        if user_id is None:
            return db.query(Order).filter(Order.status == 1).count()
        return db.query(Order).filter(Order.owner_id == user_id,Order.status==1).count()
    def get_order_amount(self,db:Session,user_id:int):
        if user_id is None:
            total = db.query(func.sum(Order.amount)).filter(Order.status == 1).scalar()
            if total is None:
                total = 0
            return total
        total = db.query(func.sum(Order.amount)).filter(Order.owner_id == user_id,Order.status==1).scalar()
        if total is None:
            total = 0
        return total

    def get_top_master_info(self,db:Session):
        res = db.query(func.sum(Order.amount* func.coalesce(Order.shareRate,0)/100),func.count(1),Master.name).join(Master,Order.master_id==Master.id).filter(Order.status==1).group_by(Order.master_id,Master.name).order_by(text("sum_1 desc")).limit(3).all()
        return res

    def get_order_reward_by_master(self,db:Session,master_id:int):
        total = db.query(func.sum(Order.amount*Order.shareRate/100)).filter(Order.master_id==master_id,Order.status==1).scalar()
        if total is None:
            return 0
        return total

    def get_arrange_orders(self,db:Session,user_id,master_id,skip: int = 0, limit: int = 100):
        sql = db.query(Order).filter(Order.owner_id==user_id).filter(Order.master_id==master_id).filter(Order.status==1)

        return (sql.count(),sql.order_by(Order.id.desc()).offset(skip).limit(limit).all())

    def get_pending_order_count(self,db:Session,master_id,user_id):
        sql  = db.query(Order).filter(Order.owner_id==user_id).filter(Order.master_id==master_id).filter(Order.status==1).filter(Order.arrange_status!=3)
        return sql.count()


    def get_favorite_open_orders(
            self, db: Session, *,
            user_id:int,
            skip: int = 0, limit: int = 100
    ) -> (int, List[Order]):
        subquery = db.query(Favorite.id.label('fav_id'),Favorite.order_id.label('fav_order_id')).filter(Favorite.user_id==user_id).subquery()
        #query = db.query(Order.id,Order.is_open,Order.owner_id,Order.master_id,Order.status,Order.master,Order.owner,Order.create_time,Order.product_id,Order.name
        #                 ,Order.comment_rate,Order.arrange_status,Order.amount,Order.shareRate,Order.pay_time,Order.reason,Order.channel,Order.birthday,Order.divination,Order.location,Order.order_number,Order.pay_type,Order.sex,subquery.c.fav_id)
        query = db.query(Order,subquery.c.fav_id,Master.name,Master.avatar,User.user_name).join(Master,Master.id==Order.master_id).join(User,User.id==Order.owner_id)

        conditions = []
        conditions.append(Order.is_open == 1)
        conditions.append(Order.id == subquery.c.fav_order_id)
        query = query.filter(*conditions)

        return (
            query.count(),
            query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
        )


    def get_user_type_order(self, db: Session, *,
                           user_id: int, name:str)->Any:
        product_obj = db.query(Product).filter(Product.name == name,Product.status==1).first()
        if product_obj is None:
            return None,None
        order_obj = db.query(Order).filter(Order.owner_id == user_id,
                                           Order.product_id == product_obj.id,
                                           Order.status == 1).first()
        if order_obj is None:
            return False,product_obj.id
        else:
            return True,product_obj.id


    def get_master_by_order_id(self,db: Session, * , order_id:int)->Optional[Master]:
        master_id_obj = db.query(Order.master_id).filter(Order.id == order_id).first()
        if master_id_obj is None:
            return None
        return db.query(Master).filter(Master.id == master_id_obj.master_id).first()


    def get_order_by_time(self,db:Session, *, time:int, user_id:int, product_id:int):

        return db.query(Order).filter(Order.status == 1,
                                      Order.product_id == product_id,
                                      Order.owner_id == user_id,
                                      Order.pay_time >= datetime.datetime.fromtimestamp(time)).first()

order = CRUDOrder(Order)
