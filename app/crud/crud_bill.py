from typing import List, Any,Optional
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillUpdate


class CRUDBill(CRUDBase[Bill, BillCreate, BillUpdate]):
    @staticmethod
    def get_by_id(db: Session, *, id: int) -> Optional[Bill]:
        return db.query(Bill).filter(Bill.id == id).first()
    @staticmethod
    def get_all_by_date(db: Session,date:str, skip:int,limit:int) -> (int,List[Bill]):
        sql = db.query(Bill).filter(Bill.bill_date==date)
        return (sql.count(),sql.offset(skip).limit(limit).all())

    @staticmethod
    def get_by_bill_date_master_id(db:Session,master_id:int,bill_date:str)-> Optional[Bill]:
        return db.query(Bill).filter(Bill.master_id == master_id,Bill.bill_date == bill_date).first()
    @staticmethod
    def get_paid_amount_by_master_id(db:Session,master_id:int)-> Optional[Bill]:
        return db.query(func.sum(Bill.value)).filter(Bill.master_id==master_id,Bill.status==1).scalar()


    @staticmethod
    def create_bill(db: Session,bill:BillCreate):

        pass

    @staticmethod
    def update_or_create(db:Session,bill:BillCreate):
        billObj = CRUDBill.get_by_id(db,id=bill.id)
        if billObj is None:
            obj_in_data = jsonable_encoder(bill)
            db_obj = Bill()
            for k, v in obj_in_data.items():
                setattr(db_obj, k, v)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return billObj


    # @staticmethod
    # def get_multi_by_owner(db: Session, owner_id: int, skip: int, limit: int) -> History:
    #     return db.query(History) \
    #         .filter(History.owner_id == owner_id, History.status == 0) \
    #         .order_by(History.id.desc()) \
    #         .offset(skip).limit(limit) \
    #         .all()
    #
    # def create_owner_divination(self, db: Session, history: HistoryCreate) -> Any:
    #     total = db.query(History).filter(History.owner_id == history.owner_id, History.status == 0).count()
    #     if total >= 100:
    #         first_history = db.query(History) \
    #             .filter(History.owner_id == history.owner_id, History.status == 0) \
    #             .order_by(History.id).first()
    #         if first_history:
    #             db.query(History).filter(History.id == first_history.id).delete()
    #     self.create(db, obj_in=history)


bill = CRUDBill(Bill)
