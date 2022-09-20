from typing import List, Any
import uuid
import time

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.upload_history import UploadHistory
from app.schemas.upload_history import UploadHistoryCreate, UploadHistoryUpdate


class CRUDUploadHistory(CRUDBase[UploadHistory, UploadHistoryCreate, UploadHistoryUpdate]):
    @staticmethod
    def get_by_file_name(db: Session, file_name: str) ->UploadHistory :
        return db.query(UploadHistory).filter(UploadHistory.file_name == file_name).first()



    def create_upload(self, db: Session, upload_history: UploadHistoryCreate) -> Any:
        self.create(db, obj_in=upload_history)



upload_history = CRUDUploadHistory(UploadHistory)
