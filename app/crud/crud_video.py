from typing import List, Any
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


from app.crud.base import CRUDBase
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate


class CRUDVideo(CRUDBase[Video, VideoCreate, VideoUpdate]):


    @staticmethod
    def get_all(db: Session, name:str,status:int, skip: int, limit: int):
        sql = db.query(Video)
        if name != "":
            sql=sql.filter(Video.name.like("%"+name+"%"))
        if status != -1:
            sql = sql.filter(Video.status == status)
        return (sql.count(),sql.order_by(Video.top.desc(),Video.create_time.asc()).offset(skip).limit(limit).all())



    @staticmethod
    def delete_Video(db: Session,Video_id:int,owner_id:int) ->bool:
        obj = db.query(Video).get(Video_id)
        if obj.owner_id == owner_id:
            db.delete(obj)
            db.commit()
            return True
        #super(CRUDVideo,self).remove(db,Video_id)
        return False


video = CRUDVideo(Video)
