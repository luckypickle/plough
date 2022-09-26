from typing import Any, List,Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.bazi import BaZi
import pytz
router = APIRouter()


@router.get("/",response_model=schemas.VideoQuery)
def read_video_list(name:str="",status:int =-1,skip:int=0,limit:int=100,
                    db: Session = Depends(deps.get_db),
                    current_user: models.User = Depends(deps.get_current_active_user)):
    """
    read all video list.
    """
    count,videos = crud.video.get_all(db,name,status,skip,limit)
    ret_obj =schemas.VideoQuery(total=0,videos=[])
    ret_obj.total = count
    for o in videos:
        create_time = o.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret_obj.videos.append(schemas.Video(
            id=o.id,
            create_time=create_time,
            name=o.name,
            video_url=o.video_url,
            surface_plot_url=o.surface_plot_url,
            status=o.status,
            top=o.top,
        ))
    return ret_obj




@router.post("/create", response_model=schemas.Video)
def create_comment(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.VideoCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new video.(only super user)
    """

    video = crud.video.create(db, obj_in=obj_in)
    if video is not None:
        video.create_time = video.create_time.strftime("%Y-%m-%d %H:%M:%S")
    return video



@router.put("/{video_id}", response_model=schemas.Video)
def update_comment_by_id(
        *,
        db: Session = Depends(deps.get_db),
        video_id: int,
        obj_in: schemas.VideoUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a video. (superuser only)
    """
    obj = crud.video.get(db,id=video_id)
    if obj is None:
        return HTTPException(status_code=400, detail="video id not exist.")
    video = crud.video.update(db=db,db_obj=obj, obj_in=obj_in)

    if video is not None:
        video.create_time = video.create_time.strftime("%Y-%m-%d %H:%M:%S")
    return video
