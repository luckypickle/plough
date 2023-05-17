from typing import List,Any

from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate

class CRUDCharacter(CRUDBase[Character, CharacterCreate, CharacterUpdate]):

    def create_character(self, db: Session, character: CharacterCreate) -> Any:
        return self.create(db, obj_in=character)

    def get_one_by_char(self, db: Session, owner_id: int,chars: str) -> Character:
        return db.query(Character).filter(Character.owner_id == owner_id,Character.chars == chars).first()

    def get_multi_by_owner(
            self, db: Session, *,
            owner_id: int,
            skip: int, 
            limit: int
    ) -> List[Character]:
        return db.query(Character) \
            .filter(Character.owner_id == owner_id) \
            .order_by(Character.update_time.desc()) \
            .offset(skip).limit(limit) \
            .all()

    @staticmethod
    def delete_character(db: Session,id:int,owner_id:int) ->bool:
        obj = db.query(Character).get(id)
        if obj is None:
            return False
        if obj.owner_id == owner_id:
            db.delete(obj)
            db.commit()
            return True
        return False

character = CRUDCharacter(Character)