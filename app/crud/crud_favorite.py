from typing import List, Any
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteUpdate


class CRUDFavorite(CRUDBase[Favorite, FavoriteCreate, FavoriteUpdate]):
    # @staticmethod
    # def get_count_by_owner(db: Session, owner_id: int) -> int:
    #     return db.query(Favorite).filter(History.owner_id == owner_id, History.status == 0).count()


    @staticmethod
    def get_multi_by_owner(db: Session, user_id: int, skip: int, limit: int) -> Favorite:
        return db.query(Favorite) \
            .filter(Favorite.user_id == user_id, Favorite.status == 0) \
            .order_by(Favorite.id.desc()) \
            .offset(skip).limit(limit) \
            .all()

    def create_user_favorite(self, db: Session, favorite: FavoriteCreate) -> Any:
        self.create(db, obj_in=favorite)

    @staticmethod
    def delete_favorite(db: Session,favorite_id:int,user_id:int) ->bool:
        obj = db.query(Favorite).get(favorite_id)
        if obj.user_id == user_id:
            db.delete(obj)
            db.commit()
            return True
        #super(CRUDHistory,self).remove(db,history_id)
        return False


favority = CRUDFavorite(Favorite)
