from typing import Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate


class CRUDFolder(CRUDBase[Folder, FolderCreate, FolderUpdate]):
    @staticmethod
    def get_count_by_master_and_name(db: Session, master_id: int, folder_name: str) -> Folder:
        return db.query(Folder) \
            .filter(Folder.master_id == master_id, Folder.folder_name == folder_name, Folder.status == 0) \
            .count()

    @staticmethod
    def get_multi_by_master(db: Session, master_id: int) -> Folder:
        return db.query(Folder) \
            .filter(Folder.master_id == master_id, Folder.status == 0) \
            .order_by(Folder.id.desc()) \
            .all()

    def create_master_folder(self, db: Session, folder: FolderCreate) -> Any:
        self.create(db, obj_in=folder)

    @staticmethod
    def delete_folder(db: Session,folder_id:int,master_id:int) ->bool:
        obj = db.query(Folder).get(folder_id)
        if obj is None:
            return False
        if obj.master_id == master_id:
            db.delete(obj)
            db.commit()
            return True
        #super(CRUDFolder,self).remove(db,history_id)
        return False

folder = CRUDFolder(Folder)
