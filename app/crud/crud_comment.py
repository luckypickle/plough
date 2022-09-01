from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.crud.crud_master import CRUDMaster
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentStatus
from app.models.order import Order
from app.models.user import User
from app.models.master import Master
from app.models.product import Product


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    @staticmethod
    def get_by_order_id(db: Session, order_id: int) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.status == 0).filter(Comment.order_id == order_id).first()

    @staticmethod
    def get(db: Session, id: int) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.status == 0).filter(Comment.id == id).first()

    @staticmethod
    def get_by_master_id(db: Session, master_id: int, skip: int = 0, limit: int = 100) -> (int, int, Optional[Comment]):
        sql = db.query(Comment).filter(Comment.master_id == master_id)
        sum_sql = db.query(func.sum(Comment.rate)).filter(Comment.master_id == master_id)

        return (sum_sql.scalar(), sql.count(), sql.offset(skip).limit(limit).all())

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.status == 0).filter(Comment.user_id == user_id).offset(skip).limit(
            limit).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.status == 0).order_by(Comment.id.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_merge_order(db: Session, skip: int = 0, limit: int = 100) -> (int, Optional[Comment]):
        sql = db.query(Comment.id, Comment.order_id, Comment.status, Comment.master_id, Comment.rate, Comment.content,
                       Comment.user_id,
                       Comment.create_time, User.phone, Master.name.label('master_name'),
                       Product.name.label('product_name')).filter(Comment.order_id == Order.id). \
            filter(Order.product_id == Product.id).filter(Order.owner_id == User.id).filter(
            Order.master_id == Master.id). \
            filter(Comment.status == 0)

        return (sql.count(), sql.order_by(Comment.id.asc()).offset(skip).limit(limit).all())

    @staticmethod
    def create(db: Session, *, obj_in: CommentCreate, master_id: int, user_id: int) -> Optional[Comment]:
        comment = CRUDComment.get_by_order_id(db=db, order_id=obj_in.order_id)
        master = CRUDMaster.get_by_id(db=db, id=master_id)

        if not comment or master.status == CommentStatus.removed.value:
            db_obj = Comment()
            db_obj.order_id = obj_in.order_id
            db_obj.content = obj_in.content
            db_obj.rate = obj_in.rate
            db_obj.master_id = master_id
            db_obj.user_id = user_id
            db_obj.status = CommentStatus.init.value
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            return None

    @staticmethod
    def update_by_id(db: Session, *, obj_in: CommentUpdate, comment_id: int) -> Optional[Comment]:
        c = CRUDComment.get(db=db, id=comment_id)
        if c:
            c.status = obj_in.status
            db.add(c)
            db.commit()
            db.refresh(c)
            return c
        else:
            return None


comment = CRUDComment(Comment)
