import logging
import json
import time
import datetime
from random import sample
from string import ascii_letters, digits
from typing import Any, List

import pytz
from fastapi import APIRouter, Depends, HTTPException
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from wechatpayv3 import WeChatPay, WeChatPayType

from app import crud, models, schemas
from app.api import deps
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.api import util

router = APIRouter()
def isTestPay():
    return False

@router.get("/", response_model=schemas.OrderQuery)
def read_orders(
        db: Session = Depends(deps.get_db),
        order_number: str = "",
        name: str = "",
        master_name:str = "",
        product_id:int = -1,
        arrange_status:int = -1,
        order_min_amount:int = 0,
        order_max_amount:int = 999999999,
        status: int = -1,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve orders (User & SuperUser).
    """
    is_super = False
    if crud.user.is_superuser(current_user):
        is_super = True
        total, orders = crud.order.get_multi_with_condition(db, order_number=order_number,
            name=name,
            master_name=master_name,
            product_id=product_id,
            arrange_status=arrange_status,
            order_min_amount=order_min_amount,
            order_max_amount=order_max_amount, role=0, role_id=current_user.id, status=status,
                                                            skip=skip, limit=limit)
    else:
        total, orders = crud.order.get_multi_with_condition(db, role=1, role_id=current_user.id, status=status,
                                                            skip=skip, limit=limit)
    # FIXME, not check count
    ret_obj = schemas.OrderQuery(total=0, orders=[])
    ret_obj.total = total
    products = crud.product.get_multi(db=db)
    for o in orders:
        for p in products:
            if p.id == o.product_id:
                product = p.name

        create_time = o.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        pay_time = o.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        if is_super:
            pic1 = o.pic1
            pic2 = o.pic2
            pic3 = o.pic3
            memo = o.memo
        else:
            pic1 = None
            pic2 = None
            pic3 = None
            memo = None
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
            is_open=o.is_open,
            comment_rate=o.comment_rate,
            owner_email= o.owner.email,
            owner_phone= o.owner.phone,
            pic1=pic1,
            pic2=pic2,
            pic3=pic3,
            memo=memo

        ))
    return ret_obj



@router.get("/openOrders", response_model=schemas.OpenOrderQuery)
def read_orders(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve open orders [all user].
    """
    util.load_master_rate(db)
    total, orders = crud.order.get_open_orders(db,skip=skip, limit=limit)
    # FIXME, not check count
    ret_obj = schemas.OrderQuery(total=0, orders=[])
    ret_obj.total = total
    products = crud.product.get_multi(db=db)
    for o in orders:
        for p in products:
            if p.id == o.product_id:
                product = p.name

        create_time = o.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        pay_time = o.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        _,comments = crud.comment.get_interact_by_order_id_full_data(db,o.id,type=1,limit=3)
        comment_ret = []
        for one_com in comments:
            print(one_com)
            create_time = one_com[0].create_time.strftime("%Y-%m-%d %H:%M:%S")
            user_name = one_com[1] if one_com[1] is not None else one_com[2]
            comment_ret.append(schemas.InteractComment(
                id=one_com[0].id,
                status=one_com[0].status,
                order_id=one_com[0].order_id,
                content=one_com[0].content,
                create_time=create_time,
                user_name=user_name
            ))
        comment = crud.comment.get_by_order_id(db,o.id,type=0)
        if comment is not None:
            comment.create_time  = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret_obj.orders.append(schemas.OpenOrder(
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
            is_open=o.is_open,
            comment_rate=o.comment_rate,
            master_rate=util.get_avg_rate(o.master_id),
            comment=comment,
            interact_comment_list=comment_ret
        ))
    return ret_obj


@router.get('/openOrders/favorite', response_model=schemas.FavOrderQuery)
def read_orders_by_favorite(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve open orders [all user].
    """
    util.load_master_rate(db)
    total, orders = crud.order.get_favorite_open_orders(db,user_id=current_user.id,skip=skip, limit=limit)
    print(orders)
    # FIXME, not check count
    ret_obj = schemas.FavOrderQuery(total=0, orders=[])
    ret_obj.total = total
    products = crud.product.get_multi(db=db)
    for o in orders:
        print(o[0])
        for p in products:
            if p.id == o[0].product_id:
                product = p.name

        create_time = o[0].create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        pay_time = o[0].pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        _, comments = crud.comment.get_interact_by_order_id_full_data(db, o[0].id, limit=3)
        comment_ret = []
        for one_com in comments:
            create_time = one_com[0].create_time.strftime("%Y-%m-%d %H:%M:%S")
            user_name = one_com[1] if one_com[1] is not None else one_com[2]
            comment_ret.append(schemas.InteractComment(
                id=one_com[0].id,
                status=one_com[0].status,
                order_id=one_com[0].order_id,
                content=one_com[0].content,
                create_time=create_time,
                user_name=user_name
            ))
        comment = crud.comment.get_by_order_id(db, o[0].id, type=0)
        if comment is not None:
            comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret_obj.orders.append(schemas.FavOrder(
            id=o[0].id,
            product_id=o[0].product_id,
            product=product,
            order_number=o[0].order_number,
            name=o[0].name,
            sex=o[0].sex,
            birthday=o[0].birthday,
            location=o[0].location,
            amount=o[0].amount,
            shareRate=o[0].shareRate,
            owner_id=o[0].owner_id,
            master_id=o[0].master_id,
            divination=o[0].divination,
            reason=o[0].reason,
            create_time=create_time,
            pay_time=pay_time,
            arrange_status=o[0].arrange_status,
            status=o[0].status,
            master=o[2],
            master_avatar=o[3],
            owner=o[4],
            is_open=o[0].is_open,
            comment_rate=o[0].comment_rate,
            favorite_id=o[1],
            master_rate=util.get_avg_rate(o[0].master_id),
            comment=comment,
            interact_comment_list=comment_ret
        ))
    return ret_obj


@router.get("/master", response_model=schemas.MasterOrderQuery)
def read_orders_master(
        db: Session = Depends(deps.get_db),
        status: int = -1,
        skip: int = 0,
        limit: int = 100,
        current_master: models.Master = Depends(deps.get_current_active_master),
) -> Any:
    """
    Retrieve orders (Master).
    """
    total,total_reward, orders = crud.order.get_multi_and_sum_with_condition(
        db=db, role=2, role_id=current_master.id, status=status, skip=skip, limit=limit
    )
    # FIXME, not check count
    products = crud.product.get_multi(db=db)
    ret_obj = schemas.MasterOrderQuery(total=0,total_reward=0.0, orders=[])
    ret_obj.total = total
    if total_reward is not None:
        ret_obj.total_reward= total_reward/100
    for o in orders:
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
            comment_rate=o.comment_rate
        ))
    return ret_obj

def get_user_level(registed_count):
    print('registed count is ',registed_count)
    if registed_count == 0:
        return 0
    elif registed_count <3and registed_count > 0:
        return 1
    elif registed_count<5and registed_count >= 3:
        return 2
    elif registed_count < 10and registed_count >= 5:
        return 3
    elif registed_count>=10:
        return 4


@router.post('/orderFavorite')
def set_order_favorite( db: Session = Depends(deps.get_db),
        order_id:int=0,
        current_user: models.User = Depends(deps.get_current_user),):
    order = crud.order.get(db,order_id)
    if order is not None:
        if order.is_open==1:
            fav  = crud.favority.get_by_user_id_order_id(db,current_user.id,order_id)
            if fav is not None:
                return util.make_return(-1, "already favorite")
            crud.favority.create_user_favorite(db,schemas.FavoriteCreate(
                user_id=current_user.id,
                order_id=order_id,
                status=0
            ))

            return util.make_return(0,"success")
        else:
            return util.make_return(-1, "not open")
    else:
        return util.make_return(-1, "order id error")


@router.get('/orderPic',response_model=schemas.OrderPic)
def get_order_pic(db: Session = Depends(deps.get_db),
                  order_id:int=0,
                current_user: models.User = Depends(deps.get_current_user),):
    res = crud.order.get(db, order_id)
    if crud.user.is_active(current_user):
        if res.owner_id==current_user.id:
            return schemas.OrderPic(pic1=res.pic1,pic2=res.pic2,pic3=res.pic3,memo=res.memo)

    if crud.master.is_active(current_user):
        if res.master_id ==current_user.id:
            return schemas.OrderPic(pic1=res.pic1, pic2=res.pic2, pic3=res.pic3,memo=res.memo)
    return schemas.OrderPic()



@router.delete('/orderFavorite')
def delete_order_favorite( db: Session = Depends(deps.get_db),
        favorite_id:int=0,
        current_user: models.User = Depends(deps.get_current_user),):
    res = crud.favority.delete_favorite(db,favorite_id,current_user.id)

    return "success"

def get_user_level(registed_count):
    if registed_count == 0:
        return 0
    elif registed_count <3and registed_count > 0:
        return 1
    elif registed_count<5and registed_count >= 3:
        return 2
    elif registed_count < 10and registed_count >= 5:
        return 3
    elif registed_count>=10:
        return 4

def get_reward_amount(level,amount,prev):
    level_percent=[0,8,10,12,15]
    level_prev_percent=[0,2,3,4,5]
    if prev:
        return int(amount*level_prev_percent[level]//100)
    else:
        return int(amount*level_percent[level]//100)
def update_order_status(db, wxpay, order_id, out_trade_no, mchid):
    for i in range(12):
        if isTestPay():
            order = crud.order.get(db=db, id=order_id)
            if order:
                order.status = 1
                order.pay_time = datetime.datetime.now(),
                db.add(order),
                db.commit()
                db.refresh(order)
            break
        else:
            ret = wxpay.query(out_trade_no=out_trade_no, mchid=mchid)
            ret_json = json.loads(ret[1])
            print(ret_json["trade_state"])
            if ret_json["trade_state"] != "NOTPAY":
                order = crud.order.get(db=db, id=order_id)
                if order:
                    order.status = 1
                    order.pay_time = datetime.datetime.now(),
                    db.add(order),
                    db.commit()
                    db.refresh(order)
                break
        time.sleep(5)
    order = crud.order.get(db=db, id=order_id)
    if order is not None and order.status == 1:
        if order.status == 1:
            invite_obj = crud.invite.get_invite_info(db,user_id=order.owner_id)
            if invite_obj is None:
                return
            if invite_obj.order_status == 1:
                invite_obj.order_status = 2
                invite_obj.first_order_time = order.pay_time
                db.add(invite_obj),
                db.commit()
                db.refresh(invite_obj)
            prev_amount = 0
            prev_prev_amount = 0
            prev_invite_obj = crud.invite.get_invite_info(db,user_id=invite_obj.prev_invite)
            if prev_invite_obj is not None:
                prev_invite_obj.current_level = get_user_level(crud.invite.get_prev_count(db,user_id=invite_obj.prev_invite))
                db.add(prev_invite_obj),
                db.commit()
                db.refresh(prev_invite_obj)
                if prev_invite_obj.current_level is None:
                    prev_obj_level = 0
                else:
                    prev_obj_level = prev_invite_obj.current_level
                prev_amount = get_reward_amount(prev_obj_level,order.amount,False)
                prev_prev_invite_obj = crud.invite.get_invite_info(db,user_id=invite_obj.prev_prev_invite)
                if prev_prev_invite_obj is not None:
                    if prev_prev_invite_obj.current_level is None:
                        prev_prev_obj_level = 0
                    else:
                        prev_prev_obj_level = prev_prev_invite_obj.current_level
                    prev_prev_amount = get_reward_amount(prev_prev_obj_level, order.amount, True)
                reward_obj = models.Reward(
                    order_id=order.id,
                    user_id = order.owner_id,
                    order_amount=order.amount,
                    prev_user_id=invite_obj.prev_invite,
                    prev_prev_user_id=invite_obj.prev_prev_invite,
                    prev_amount = prev_amount,
                    prev_prev_amount = prev_prev_amount,
                    order_time = order.pay_time
                )
                crud.reward.create(db,obj_in=reward_obj)

@router.post("/")
def create_order(
        *,
        task: BackgroundTasks,
        db: Session = Depends(deps.get_db),
        order_in: schemas.OrderCreate,
        current_user: models.User = Depends(deps.get_current_active_user),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new order.
    """
    master = crud.master.get(db=db, id=order_in.master_id)
    if not master:
        raise HTTPException(status_code=404, detail="Master not found")
    product = crud.product.get(db=db, id=order_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    price = crud.masterProduct.get_master_product_price_by_id(db, master.id,order_in.product_id)
    if price is None:
        order_in.amount = master.price
    else:
        order_in.amount = price.price



    order_in.shareRate = master.rate
    order = crud.order.create_with_owner(db=db, obj_in=order_in, owner_id=current_user.id)
    with open(settings.PRIVATE_KEY, "r") as f:
        pkey = f.read()
    wxpay = WeChatPay(
        wechatpay_type=WeChatPayType.APP,
        mchid=settings.MCHID,
        private_key=pkey,
        cert_serial_no=settings.CERT_SERIAL_NO,
        apiv3_key=settings.APIV3_KEY,
        appid=settings.APPID,
        notify_url=settings.NOTIFY_URL,
        cert_dir=settings.CERT_DIR,
        logger=None,
        partner_mode=settings.PARTNER_MODE,
        proxy=None)
    if isTestPay():
        code=200
        message=json.dumps({'prepay_id':'123456665878'})
    else:
        code, message = wxpay.pay(
            description=product.name,
            out_trade_no=order.order_number,
            amount={'total': order.amount}
        )
    result = json.loads(message)
    if code in range(200, 300):

        prepay_id = result.get('prepay_id')
        timearray = time.strptime(order_in.create_time, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timearray))
        noncestr = ''.join(sample(ascii_letters + digits, 8))
        package = 'Sign=WXPay'
        paysign = wxpay.sign([settings.APPID, str(timestamp), noncestr, prepay_id])
        task.add_task(update_order_status, db, wxpay, order.id, order.order_number, settings.MCHID)
        return {'code': 0, 'result': {
            'ordernumber': order.order_number,
            'appid': settings.APPID,
            'partnerid': settings.MCHID,
            'prepayid': prepay_id,
            'package': package,
            'nonceStr': noncestr,
            'timestamp': timestamp,
            'price': order.amount,
            'sign': paysign
        }}
    else:
        return {'code': -1, 'result': {'reason': result.get('code')}}


@router.put("/{id}", response_model=schemas.OrderUpdate)
def update_order(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        order_in: schemas.OrderUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an order (superuser).
    """
    order = crud.order.get(db=db, id=id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # if not crud.user.is_superuser(current_user) and (order.owner_id != current_user.id):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    order = crud.order.update(db=db, db_obj=order, obj_in=order_in)
    return schemas.OrderUpdate(
        product_id=order.product_id,
        name=order.name,
        sex=order.sex,
        birthday=order.birthday,
        location=order.location,
        master_id=order.master_id,
        amount=order.amount,
        reason=order.reason,
        arrange_status=order.arrange_status,
        status=order.status
    )


@router.put("/master/{id}", response_model=schemas.Order)
def master_update_order(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        order_in: schemas.OrderUpdateDivination,
        current_master: models.User = Depends(deps.get_current_active_master),
) -> Any:
    """
    Update an order by master.
    """
    order = crud.order.get(db=db, id=id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.master_id != current_master.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if order.status != schemas.order.OrderStatus.checked.value:
        raise HTTPException(status_code=400, detail="Not need divination")
    order = crud.order.updateDivination(db=db, db_obj=order, obj_in=order_in)
    product = crud.product.get(db=db, id=order.product_id)
    x = order.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    p = order.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    return schemas.Order(
        id=order.id,
        product_id=order.product_id,
        product=product.name,
        order_number=order.order_number,
        name=order.name,
        sex=order.sex,
        birthday=order.birthday,
        location=order.location,
        amount=order.amount,
        shareRate=order.shareRate,
        owner_id=order.owner_id,
        master_id=order.master_id,
        divination=order.divination,
        reason=order.reason,
        create_time=x,
        pay_time=p,
        status=order.status,
        arrange_status=order.arrange_status,
        master=order.master.name,
        master_avatar=order.master.avatar,
        owner=order.owner.user_name,
        comment_rate=order.comment_rate
    )


@router.get("/{id}", response_model=schemas.Order)
def read_order_by_id(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get order by ID.
    """
    order = crud.order.get(db=db, id=id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not crud.user.is_superuser(current_user) and (order.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    # FIXME, not check count
    products = crud.product.get_multi(db=db)
    product = None
    for p in products:
        if p.id == order.product_id:
            product = p.name
    create_time = order.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    pay_time = order.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    return schemas.Order(
        id=order.id,
        product_id=order.product_id,
        product=product,
        order_number=order.order_number,
        name=order.name,
        sex=order.sex,
        birthday=order.birthday,
        location=order.location,
        amount=order.amount,
        shareRate=order.shareRate,
        owner_id=order.owner_id,
        master_id=order.master_id,
        divination=order.divination,
        reason=order.reason,
        create_time=create_time,
        pay_time=pay_time,
        status=order.status,
        arrange_status=order.arrange_status,
        master=order.master.name,
        master_avatar=order.master.avatar,
        owner=order.owner.user_name,
        comment_rate=order.comment_rate
    )
