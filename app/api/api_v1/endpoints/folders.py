from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import pytz
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/create", response_model=schemas.Folder)
def create_folder(
        *,
        db: Session = Depends(deps.get_db),
        folder_name: str = '',
        current_master: models.Master = Depends(deps.get_current_active_master)
) -> Any:
    """
    Create new Folder.(only master)
    """
    count = crud.folder.get_count_by_master_and_name(db=db, master_id=current_master.id,folder_name=folder_name)
    if(count > 0):
        raise HTTPException(
            status_code=400,
            detail="folder name already exists",
        )   
    folder = schemas.FolderCreate(
        folder_name=folder_name,
        status=0,
        master_id=current_master.id
    )
    crud.folder.create_master_folder(db, folder=folder)
    return folder

@router.put("/folder/{id}", response_model=schemas.Folder)
def update_folder(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        folder_name: str = '',
        current_master: models.Master = Depends(deps.get_current_active_master)
) -> Any:
    """
    Update an folder.(only master)
    """
    count = crud.folder.get_count_by_master_and_name(db=db, master_id=current_master.id,folder_name=folder_name)
    if(count > 0):
        raise HTTPException(
            status_code=404,
            detail="folder name already exists",
        )   
    folder = crud.folder.get(db, id=id)
    if not folder:
        raise HTTPException(
            status_code=404,
            detail="No folder exists for the current master",
        )
    if(folder.master_id != current_master.id):
        raise HTTPException(
            status_code=404,
            detail="The current folder does not belong to this master",
        ) 
    folder_in = {"folder_name": folder_name}
    crud.folder.update(db, db_obj=folder, obj_in=folder_in)
    return folder_in

@router.get("/folders", response_model=List[schemas.FolderQuery])
def get_folders(
        db: Session = Depends(deps.get_db),
        current_master: models.Master = Depends(deps.get_current_active_master)
) -> Any:
    """
    Get folders by master.
    """
    folders = crud.folder.get_multi_by_master(db=db, master_id=current_master.id)
    rets = []
    for h in folders:
        count = crud.folder_order.get_count_by_folder(db=db, folder_id=h.id)
        rets.append(schemas.FolderQuery(
            id=h.id,
            folder_name=h.folder_name,
            master_id=h.master_id,
            count=count
        ))
    return rets

@router.delete('/folders')
def delete_folder( ids:list ,
        db: Session = Depends(deps.get_db),
        current_master: models.Master = Depends(deps.get_current_active_master)):
    for id in ids:
         #先删除关联关系
        res = crud.folder_order.delete_folder_orders(db=db,folder_id=id)
        if res:
            crud.folder.delete_folder(db=db,folder_id=id,master_id=current_master.id)
        else:
            return "failed"
    return "success" 
   
@router.post("/createFolderOrder", response_model=schemas.FolderOrder)
def create_folder(
        *,
        db: Session = Depends(deps.get_db),
        folder_id: int,
        order_id: int,
        current_master: models.Master = Depends(deps.get_current_active_master)
) -> Any:
    """
    Create new FolderOrder.(only master)
    """
    order = crud.order.get(db, id=order_id)
    if(order.master_id != current_master.id):
        raise HTTPException(
            status_code=404,
            detail="The current order does not belong to this master",
        ) 
    count = crud.folder_order.get_count_by_master_and_order(db=db, master_id=current_master.id,order_id=order_id)
    if(count > 0):
        raise HTTPException(
            status_code=404,
            detail="The current order has been collected",
        )   
    folderOrder = schemas.FolderOrderCreate(
        folder_id=folder_id,
        order_id=order_id,
        status=0,
        master_id=current_master.id
    )
    crud.folder_order.create_folder_order(db, folderOrder=folderOrder)
    return folderOrder


@router.get("/folderOrdersWithReward", response_model=schemas.MasterOrderQuery)
def read_folder_orders(
        *,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        folder_id: int,
        current_master: models.Master = Depends(deps.get_current_active_master),
) -> Any:
    """
    Retrieve orderss (Master).
    """

    total,folderOrders = crud.folder_order.get_multi_with_conditions(db=db, folder_id=folder_id, skip=skip, limit=limit)
    products = crud.product.get_multi(db=db)
    ret_obj = schemas.MasterOrderQuery(total=0,total_reward=0.0, orders=[],count_rate="",amount_rate="")
    ret_obj.total = total
    # count_rate,amount_rate = crud.order.get_master_order_rate(db,current_master.id)
    # ret_obj.count_rate = count_rate
    # ret_obj.amount_rate = amount_rate
    for f in folderOrders:
        o= crud.order.get(db, id=f.order_id)
        for p in products:
            if p.id == o.product_id:
                product = p.name
        create_time = o.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        pay_time = o.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        ret_obj.orders.append(schemas.Order(
            id=o.id,
            product_id=o.product_id,
            product=product,
            order_number=o.order_number,
            name=o.name,
            sex=o.sex,
            birthday=o.birthday,
            location=o.location,
            amount=o.amount,
            shareRate=o.shareRate,
            owner_id=o.owner_id,
            master_id=o.master_id,
            divination=o.divination,
            reason=o.reason,
            create_time=create_time,
            pay_time=pay_time,
            arrange_status=o.arrange_status,
            status=o.status,
            master=o.master.name,
            master_avatar=o.master.avatar,
            owner=o.owner.user_name,
            comment_rate=o.comment_rate,
            isNorth=o.isNorth

        ))
    return ret_obj

@router.delete('/folder_orders')
def delete_folder_order( ids:list ,
        folder_id:int ,
        db: Session = Depends(deps.get_db)):
    for id in ids:
        crud.folder_order.delete_folder_order(db=db,id=id,folder_id=folder_id)
    return "success" 




