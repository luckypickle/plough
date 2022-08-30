from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentStatus


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def get_by_order_id(self, db: Session, order_id: int) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.order_id == order_id).first()

    def get_by_master_id(self, db: Session, master_id: int, skip: int = 0, limit: int = 100) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.master_id == master_id).all()

    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> Optional[Comment]:
        return db.query(Comment).filter(Comment.user_id == user_id).all()

    def create(self, db: Session, *, obj_in: CommentCreate, master_id: int, user_id: int) -> Comment:
        comment = self.get_by_order_id(db=db, order_id=obj_in.order_id)
        if not comment or master.status == CommentStatus.removed.value:
            db_obj = Comment(
                order_id=obj_in.order_id,
                content=obj_in.content,
                rate=obj_in.rate,
                master_id=master_id,
                user_id=user_id,
                status=CommentStatus.init.value
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            return None

    def update_by_id(self, db: Session, *, obj_in: CommentUpdate, comment_id: int) -> Comment:
        c = self.get(db=db, id=comment_id)
        if c:
            c.status = obj_in.status
            db.add(c)
            db.commit()
            db.refresh(c)
            return c
        else:
            return None


comment = CRUDComment(Comment)
