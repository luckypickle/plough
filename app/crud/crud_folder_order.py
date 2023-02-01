from typing import List,Optional,Any

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.folder_order import FolderOrder
from app.schemas.folder_order import FolderOrderCreate, FolderOrderUpdate

class CRUDFolderOrder(CRUDBase[FolderOrder, FolderOrderCreate, FolderOrderUpdate]):

    @staticmethod
    def get_count_by_master_and_order(db: Session, master_id: int, order_id: int) -> int:
        return db.query(FolderOrder) \
            .filter(FolderOrder.master_id == master_id, FolderOrder.order_id == order_id, FolderOrder.status == 0) \
            .count()
    
    @staticmethod
    def get_count_by_folder(db: Session, folder_id: int) -> int:
        return db.query(FolderOrder) \
            .filter(FolderOrder.folder_id == folder_id, FolderOrder.status == 0) \
            .count()

    def create_folder_order(self, db: Session, folderOrder: FolderOrderCreate) -> Any:
        self.create(db, obj_in=folderOrder)
    
    def get_multi_with_conditions(
            self, db: Session, *,
            folder_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> (int, List[FolderOrder]):
        query = db.query(self.model)
        query = query.filter(FolderOrder.folder_id==folder_id, FolderOrder.status == 0)
        return (
            query.count(),
            query.order_by(FolderOrder.create_time.desc()).offset(skip).limit(limit).all()
            )

    @staticmethod
    def delete_folder_order(db: Session,id:int,master_id:int) ->bool:
        obj = db.query(FolderOrder).get(id)
        if obj is None:
            return False
        if obj.master_id == master_id:
            db.delete(obj)
            db.commit()
            return True
        return False

        
    @staticmethod
    def delete_folder_orders(db: Session,folder_id:int) ->bool:
        objs = db.query(FolderOrder) \
            .filter(FolderOrder.folder_id == folder_id, FolderOrder.status == 0) \
                .all()
        for obj in objs:
            db.delete(obj)
        db.commit()
        return True

folder_order = CRUDFolderOrder(FolderOrder)
