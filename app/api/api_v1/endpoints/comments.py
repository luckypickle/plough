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


@router.get("/query_by_order", response_model=schemas.Comment)
def read_comment_by_order(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comment by order.
    """
    comment = crud.comment.get_by_order_id(db, order_id=order_id)
    if comment is not None:
        comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
    return comment


@router.get("/query_by_master", response_model=schemas.CommentQuery)
def read_comment_by_master(
        master_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comment by master.
    """
    (total_rate,total,comments) = crud.comment.get_by_master_id(db, master_id=master_id, skip=skip, limit=limit)
    ret_obj = schemas.CommentQuery(rate="",total=0, comments=[])
    if total_rate is None:
        total_rate=0
    if total==0:
        ret_obj.rate="0"
    else:
        ret_obj.rate = "%.2f"%(float(total_rate)/total)
    ret_obj.total=total
    for one_com in comments:
        #create_time = one_com.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        #print(one_com.create_time)
        create_time = one_com.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret_obj.comments.append(schemas.Comment(
            id=one_com.id,
            status=one_com.status,
            order_id=one_com.order_id,
            content=one_com.content,
            rate=one_com.rate,
            create_time=create_time
        ))

    return ret_obj


@router.get("/query_by_user", response_model=List[schemas.Comment])
def read_comment_by_master(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comment by user.
    """
    comments = crud.comment.get_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    ret = []
    for one_comm in comments:
        one_comm.create_time=one_comm.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret.append(one_comm)
    return ret

@router.get("/list",response_model=List[schemas.Comment])
def get_list(
        startTime:Optional[int],
        endTime:Optional[int],
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
        settings: AppSettings = Depends(get_app_settings)) -> Any:
    '''
    super user get all comments
    '''

    comments = crud.comment.get_all(db,  skip=skip, limit=limit)
    ret = []
    for one_comm in comments:
        one_comm.create_time = one_comm.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret.append(one_comm)
    return ret



@router.post("/create", response_model=schemas.Comment)
def create_comment(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.CommentCreate,
        current_user: models.User = Depends(deps.get_current_active_user),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new comment.
    """
    order = crud.order.get(db, id=obj_in.order_id)
    if not order:
        raise HTTPException(
            status_code=403,
            detail="Order not found",
        )
    if current_user.id != order.owner_id:
        raise HTTPException(
            status_code=403,
            detail="User is not order owner",
        )

    comment = crud.comment.create(db, obj_in=obj_in, master_id=order.master_id, user_id=order.owner_id)
    if comment is not  None:
        order = crud.order.get(db, id=obj_in.order_id)
        order_in={"comment_rate":obj_in.rate}
        crud.order.update(db=db, db_obj=order, obj_in=order_in)
        comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        comment = schemas.Comment()
    #crud.order.updateOrderRate(db, order_id=order.id, rate=obj_in.rate)
    return comment



@router.put("/{comment_id}", response_model=schemas.Comment)
def update_comment_by_id(
        *,
        db: Session = Depends(deps.get_db),
        comment_id: int,
        obj_in: schemas.CommentUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a master. (superuser only)
    """
    order = crud.order.get(db, id=obj_in.order_id)
    if not order:
        raise HTTPException(
            status_code=403,
            detail="Order not found",
        )
    comment = crud.comment.update_by_id(db=db, obj_in=obj_in, comment_id=comment_id)
    if comment is not None:
        comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
    return comment
