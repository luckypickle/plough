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
        # current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve comment by order.
    """
    comment = crud.comment.get_by_order_id(db, order_id=order_id,type=0)
    if comment is not None:
        comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
    return comment


@router.get("/interact_comment_by_order", response_model=schemas.InteractCommentQuery)
def read_interact_comment_by_order(
        order_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        # current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve interact comment by order.
    """
    ( total, comments) = crud.comment.get_interact_by_order_id_full_data(db, order_id=order_id,type=1,skip=skip,limit=limit)
    ret_obj = schemas.InteractCommentQuery(rate="", total=0, comments=[])

    ret_obj.total = total
    for one_com in comments:
        # create_time = one_com.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        # print(one_com.create_time)
        create_time = one_com[0].create_time.strftime("%Y-%m-%d %H:%M:%S")
        if one_com.user_id==1:
            user_name="匿名用户"
        else:
            user_name = one_com[1][:3]+"****"+one_com[1][-4:] if one_com[1] is not None else one_com[2]
        ret_obj.comments.append(schemas.InteractComment(
            id=one_com[0].id,
            status=one_com[0].status,
            order_id=one_com[0].order_id,
            content=one_com[0].content,
            create_time=create_time,
            user_name=user_name
        ))

    return ret_obj



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
    (total_rate,total,comments) = crud.comment.get_by_master_id(db, master_id=master_id,type=0, skip=skip, limit=limit)
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

@router.get("/list",response_model=schemas.CommentListQuery)
def get_list(
        phone:str="",
        master_name:str = "",
        startTime:int =0,
        endTime:int=999999999,
        type:int=-1,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
        settings: AppSettings = Depends(get_app_settings)) -> Any:
    '''
    super user get all comments
    '''

    total,comments = crud.comment.get_all_merge_order(db, phone_or_email=phone,master_name=master_name,start_time=startTime,end_time=endTime,type=type, skip=skip, limit=limit)
    ret = schemas.CommentListQuery(total=0,comments=[])
    ret.total=total
    for one_comm in comments:
        # print(one_comm.create_time)
        # print(one_comm[8])
        if one_comm.phone is None:
            phone = one_comm.email
        else:
            phone = one_comm.phone
        create_time = one_comm.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret.comments.append(schemas.CommentFullData(
            create_time=create_time,
            user_id=phone,
        master_name=one_comm.master_name,
        product_name=one_comm.product_name,
            id=one_comm.id,
        status=one_comm.status,
            rate=one_comm.rate,
            content=one_comm.content,
            order_id=one_comm.order_id,
            type=one_comm.type
                                                    ))
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

    if obj_in.type==0 and current_user.id != order.owner_id:
        raise HTTPException(
            status_code=403,
            detail="User is not order owner",
        )

    comment = crud.comment.create(db, obj_in=obj_in, master_id=order.master_id, user_id=current_user.id)
    if comment is not  None and obj_in.type !=1:
        order = crud.order.get(db, id=obj_in.order_id)
        order_in={"comment_rate":obj_in.rate}
        crud.order.update(db=db, db_obj=order, obj_in=order_in)
        comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        comment = schemas.Comment()
    #crud.order.updateOrderRate(db, order_id=order.id, rate=obj_in.rate)
    return comment

@router.post("/createInteract", response_model=schemas.Comment)
def create_comment(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.CommentCreate,

        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new comment.
    """
    if obj_in.type!=1:
        raise HTTPException(
            status_code=403,
            detail="only support interact comment",
        )
    order = crud.order.get(db, id=obj_in.order_id)
    if not order:
        raise HTTPException(
            status_code=403,
            detail="Order not found",
        )

    comment = crud.comment.create(db, obj_in=obj_in, master_id=order.master_id, user_id=1)
    if comment is not  None:
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
    # order = crud.order.get(db, id=obj_in.order_id)
    # if not order:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Order not found",
    #     )
    comment = crud.comment.update_by_id(db=db, obj_in=obj_in, comment_id=comment_id)
    if obj_in.status==1 and comment is not None:
        order = crud.order.get(db, id=comment.order_id)
        order_in = {"comment_rate": 0}
        crud.order.update(db=db, db_obj=order, obj_in=order_in)
    if comment is not None:
        comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
    return comment
