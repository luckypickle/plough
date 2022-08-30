from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.crud.crud_master import CRUDMaster
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentStatus


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    @staticmethod
    def get_by_order_id(db: Session, order_id: int) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.order_id == order_id).first()

    @staticmethod
    def get_by_master_id(db: Session, master_id: int, skip: int = 0, limit: int = 100) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.master_id == master_id).all()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.user_id == user_id).all()

    @staticmethod
    def create(db: Session, *, obj_in: CommentCreate, master_id: int, user_id: int) -> Optional[Comment]:
        comment = CRUDComment.get_by_order_id(db=db, order_id=obj_in.order_id)
        master = CRUDMaster.get_by_id(db=db, id=master_id)
        if not comment or master.status == int(CommentStatus.removed):
            db_obj = Comment()
            db_obj.order_id = obj_in.order_id,
            db_obj.content = obj_in.content,
            db_obj.rate = obj_in.rate,
            db_obj.master_id = master_id,
            db_obj.user_id = user_id,
            db_obj.status = int(CommentStatus.init)
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
