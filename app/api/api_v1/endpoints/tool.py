import pytz
import json
import sxtwl
from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.bazi.char import get_char_wuxing

router = APIRouter()

@router.post("/character",response_model=schemas.CharacterQuery)
def character(
        *,
        db: Session = Depends(deps.get_db),
        chars: str,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> schemas.CharacterQuery:
    """
    Get character and save to database.
    """
    if len(chars)>5:
        raise HTTPException(
            status_code=404,
            detail="chars length cannot exceed 5",
        )
    character = crud.character.get_one_by_char(db, owner_id=current_user.id, chars=chars)
    chars_wuxing = ""

    if character is None:
        for c in chars:
            chars_wuxing += str(get_char_wuxing(c))
        character = schemas.CharacterCreate(
            owner_id=current_user.id,
            chars=chars,
            chars_wuxing=chars_wuxing
        )
        character = crud.character.create_character(db, character = character)
    else :
        nowTime= datetime.now()
        character_in = {"create_time":nowTime}
        character = crud.meihua.update(db, db_obj=character, obj_in=character_in)

    character = schemas.CharacterQuery(
        id=character.id,
        owner_id=character.owner_id,
        chars=character.chars,
        chars_wuxing=character.chars_wuxing,
    )
    return character

@router.get("/characters", response_model=List[schemas.CharacterQuery])
def get_characters(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    characters = crud.character.get_multi_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    rets = []
    for character in characters:
        rets.append(schemas.CharacterQuery(
            id=character.id,
            owner_id=character.owner_id,
            chars=character.chars,
            chars_wuxing=character.chars_wuxing,
        ))
    return rets

@router.delete('/character')
def delete_character(id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    res=crud.character.delete_character(db=db,id=id,owner_id=current_user.id)
    if res:
        return "success"
    else:
        return "failed"