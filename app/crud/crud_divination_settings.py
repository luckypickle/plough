from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.divination_settings import DivinationSettings
from app.schemas.divination_settings import DivinationSettingsCreate, DivinationSettingsUpdate


class CRUDDivinationSettings(CRUDBase[DivinationSettings, DivinationSettingsCreate, DivinationSettingsUpdate]):

    def create_divination_settings(self, db: Session, divination_settings: DivinationSettingsCreate) -> Any:
        self.create(db, obj_in=divination_settings)

    @staticmethod
    def get_by_user_id(db:Session,user_id:int) -> DivinationSettings:
        return db.query(DivinationSettings).filter(DivinationSettings.user_id==user_id).first()

    @staticmethod
    def get_by_master_id(db:Session,master_id:int) -> DivinationSettings:
        return db.query(DivinationSettings).filter(DivinationSettings.master_id==master_id).first()

divination_settings = CRUDDivinationSettings(DivinationSettings)
