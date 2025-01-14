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
from app.bazi.bazi import get_bazi_by_birthday, get_dianpan_divination
from app.models.user import User
from app.models.master import Master
from app.im_utils import disable_chat,recovery_chat,pushMsg
router = APIRouter()
import app.im_utils
def isTestPay():
    return False

@router.get("/", response_model=schemas.OrderQuery)
def read_orders(
        db: Session = Depends(deps.get_db),
        order_number: str = "",
        name: str = "",
        user_account:str = "",
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
            user_phone=user_account,
            master_name=master_name,
            product_id=product_id,
            arrange_status=arrange_status,
            order_min_amount=order_min_amount,
            order_max_amount=order_max_amount, role=0, role_id=current_user.id, status=status,
                                                            skip=skip, limit=limit)
    else:
        total, orders = crud.order.get_multi_with_condition_by_user(db, role=1, role_id=current_user.id, status=status,
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
            memo=memo,
            isNorth=o.isNorth,
            beat_info=o.beat_info

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
        sizhu = None
        birthday = datetime.datetime.strptime(o.birthday,"%Y-%m-%d %H:%M")
        if birthday is not None:
            sizhu = get_bazi_by_birthday(birthday.year,birthday.month,birthday.day,birthday.hour,birthday.minute)

        for one_com in comments:
            print(one_com)
            create_time = one_com[0].create_time.strftime("%Y-%m-%d %H:%M:%S")
            if one_com[0].user_id==1:
                user_name="匿名评论"
            else:
                user_name = one_com[1][:3]+"****"+one_com[1][-4:] if one_com[1] is not None else one_com[2]
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
        fav  = crud.favority.get_by_user_id_order_id(db,current_user.id,o.id)
        isFavorite = False
        favoriteId = None  
        if fav is not None:
            isFavorite = True
            favoriteId = fav.id
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
            interact_comment_list=comment_ret,
            sizhu=sizhu,
            isNorth=o.isNorth,
            beat_info=o.beat_info,
            isFavorite=isFavorite,
            favorite_id=favoriteId
        ))
    return ret_obj




@router.get("/openOrderById", response_model=schemas.OpenOrder)
def read_orders(
        db: Session = Depends(deps.get_db),
        id: int = 0,
        # current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve open orders [all user].
    """
    util.load_master_rate(db)
    o = crud.order.get(db,id=id)
    util.load_master_rate(db)
    o = crud.order.get(db, id=id)
    if o.is_open != 1:
        raise HTTPException(status_code=404, detail="Order not found")
    # FIXME, not check count
    products = crud.product.get_multi(db=db)
    for p in products:
        if p.id == o.product_id:
            product = p.name

    create_time = o.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    pay_time = o.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    _, comments = crud.comment.get_interact_by_order_id_full_data(db, o.id, type=1, limit=3)
    comment_ret = []
    sizhu = None
    birthday = datetime.datetime.strptime(o.birthday, "%Y-%m-%d %H:%M")
    if birthday is not None:
        sizhu = get_bazi_by_birthday(birthday.year, birthday.month, birthday.day, birthday.hour, birthday.minute)

    for one_com in comments:
        print(one_com)
        create_time = one_com[0].create_time.strftime("%Y-%m-%d %H:%M:%S")
        user_name = one_com[1][:3] + "****" + one_com[1][-4:] if one_com[1] is not None else one_com[2]
        comment_ret.append(schemas.InteractComment(
            id=one_com[0].id,
            status=one_com[0].status,
            order_id=one_com[0].order_id,
            content=one_com[0].content,
            create_time=create_time,
            user_name=user_name
        ))
    comment = crud.comment.get_by_order_id(db, o.id, type=0)
    if comment is not None:
        comment.create_time = comment.create_time.strftime("%Y-%m-%d %H:%M:%S")

    ret_obj = schemas.OpenOrder(
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
        isNorth=o.isNorth,
        sizhu=sizhu,
        beat_info=o.beat_info
    )
    return ret_obj



@router.get('/user_arrange_order', response_model=schemas.OrderQuery)
def get_user_arramge_order(
        db: Session = Depends(deps.get_db),
        id:int = -1,
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_user),
):
    if isinstance(current_user, User):
        #user
        if crud.user.is_active(current_user):
            total,orders = crud.order.get_arrange_orders(db,current_user.id,id,skip,limit)
        else:
            total = 0
            orders = []
    elif isinstance(current_user,Master):
        #master
        if crud.master.is_active(current_user):
            total, orders = crud.order.get_arrange_orders(db, id, current_user.id, skip, limit)
        else:
            total = 0
            orders = []

    ret_obj = schemas.OrderQuery(total=0, orders=[])
    ret_obj.total = total
    products = crud.product.get_multi(db=db)
    for o in orders:
        for p in products:
            if p.id == o.product_id:
                product = p.name

        create_time = o.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        pay_time = o.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

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
            owner_email=o.owner.email,
            owner_phone=o.owner.phone,
            pic1=pic1,
            pic2=pic2,
            pic3=pic3,
            memo=memo,
            isNorth=o.isNorth,
            beat_info=o.beat_info
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
            user_name = one_com[1][:3]+"****"+one_com[1][-4:] if one_com[1] is not None else one_com[2]
            comment_ret.append(schemas.InteractComment(
                id=one_com[0].id,
                status=one_com[0].status,
                order_id=one_com[0].order_id,
                content=one_com[0].content,
                create_time=create_time,
                user_name=user_name
            ))
        birthday = datetime.datetime.strptime(o[0].birthday, "%Y-%m-%d %H:%M")
        sizhu=None
        if birthday is not None:
            sizhu = get_bazi_by_birthday(birthday.year, birthday.month, birthday.day, birthday.hour, birthday.minute)

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
            interact_comment_list=comment_ret,
            sizhu=sizhu,
            isNorth=o[0].isNorth,
            beat_info=o[0].beat_info
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
    ret_obj = schemas.MasterOrderQuery(total=0,total_reward=0.0, orders=[],count_rate="",amount_rate="")
    ret_obj.total = total
    if total_reward is not None:
        ret_obj.total_reward= total_reward/100
    count_rate,amount_rate = crud.order.get_master_order_rate(db,current_master.id)
    ret_obj.count_rate = count_rate
    ret_obj.amount_rate = amount_rate
    for o in orders:
        for p in products:
            if p.id == o.product_id:
                product = p.name
        create_time = o.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        pay_time = o.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        count = crud.folder_order.get_count_by_master_and_order(db=db, master_id=current_master.id,order_id=o.id)
        isFolder = False
        if(count > 0):
            isFolder = True
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
            isNorth=o.isNorth,
            beat_info=o.beat_info,
            isFolder=isFolder
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
            fav = crud.favority.create_user_favorite(db,schemas.FavoriteCreate(
                user_id=current_user.id,
                order_id=order_id,
                status=0
            ))

            return util.make_return(0,fav.id)
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
def update_free_order_status(db, order_id):
    order = crud.order.get(db=db, id=order_id)
    if order:
        order.status = 1
        order.pay_time = datetime.datetime.now(),
        db.add(order),
        db.commit()
        db.refresh(order)
        pushMsg("您有新的排盘订单，请尽快查看", "master_" + str(order.master_id))
        recovery_chat(order.master_id, order.owner_id,order.memo)
    order = crud.order.get(db=db, id=order_id)
    if order is not None and order.status == 1:
        if order.status == 1:
            invite_obj = crud.invite.get_invite_info(db, user_id=order.owner_id)
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
            prev_invite_obj = crud.invite.get_invite_info(db, user_id=invite_obj.prev_invite)
            if prev_invite_obj is not None:
                prev_invite_obj.current_level = get_user_level(
                    crud.invite.get_prev_count(db, user_id=invite_obj.prev_invite))
                db.add(prev_invite_obj),
                db.commit()
                db.refresh(prev_invite_obj)
                if prev_invite_obj.current_level is None:
                    prev_obj_level = 0
                else:
                    prev_obj_level = prev_invite_obj.current_level
                prev_amount = get_reward_amount(prev_obj_level, order.amount, False)
                prev_prev_invite_obj = crud.invite.get_invite_info(db, user_id=invite_obj.prev_prev_invite)
                if prev_prev_invite_obj is not None:
                    if prev_prev_invite_obj.current_level is None:
                        prev_prev_obj_level = 0
                    else:
                        prev_prev_obj_level = prev_prev_invite_obj.current_level
                    prev_prev_amount = get_reward_amount(prev_prev_obj_level, order.amount, True)
                reward_obj = models.Reward(
                    order_id=order.id,
                    user_id=order.owner_id,
                    order_amount=order.amount,
                    prev_user_id=invite_obj.prev_invite,
                    prev_prev_user_id=invite_obj.prev_prev_invite,
                    prev_amount=prev_amount,
                    prev_prev_amount=prev_prev_amount,
                    order_time=order.pay_time
                )
                crud.reward.create(db, obj_in=reward_obj)
def update_order_status(db, wxpay, order_id, out_trade_no, mchid): 
    logging.info(f"轮询订单order_id：{order_id}状态开始")
    for i in range(36):
        if isTestPay():
            order = crud.order.get(db=db, id=order_id)
            if order:
                order.status = 1
                order.pay_time = datetime.datetime.now(),
                db.add(order),
                db.commit()
                db.refresh(order)
                pushMsg("您有新的排盘订单，请尽快查看","master_"+str(order.master_id))
                recovery_chat(order.master_id,order.owner_id,order.memo)
            break
        else:
            ret = wxpay.query(out_trade_no=out_trade_no, mchid=mchid)
            ret_json = json.loads(ret[1])
            print(ret_json["trade_state"])
            if ret_json["trade_state"] == "SUCCESS":
                logging.info(f"订单order_id：{order_id}支付成功")
                order = crud.order.get(db=db, id=order_id)
                if order:
                    order.status = 1
                    order.pay_time = datetime.datetime.now()
                    product = crud.product.get(db=db, id=order.product_id)
                    if product is not None and product.name == "点盘":
                        birthday = datetime.datetime.strptime(str(order.birthday).split(":")[0], "%Y-%m-%d %H")
                        divination = get_dianpan_divination(birthday.year, birthday.month, birthday.day, birthday.hour, order.sex)
                        order.arrange_status = 1
                        order.divination = divination
                    db.add(order),
                    db.commit()
                    db.refresh(order)
                    pushMsg("您有新的排盘订单，请尽快查看", "master_" + str(order.master_id))
                    recovery_chat(order.master_id, order.owner_id,order.memo)
                break
            elif i == 35:
                code, message = wxpay.close(
                        out_trade_no=out_trade_no
                    )
                logging.info(f"订单order_id：{order_id},超时关闭code: {code},message:{message}")
        time.sleep(5)
    logging.info(f"轮询订单order_id：{order_id}状态结束")
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
        trade_type: str = "app",
        current_user: models.User = Depends(deps.get_current_active_user),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new order.
    """
    master = crud.master.get(db=db, id=order_in.master_id)
    if not master:
        raise HTTPException(status_code=404, detail="Master not found")
    print(order_in.product_id)
    product = crud.product.get(db=db, id=order_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    price = crud.masterProduct.get_master_product_price_by_id(db, master.id,order_in.product_id)
    if price is None:
        order_in.amount = master.price
    else:
        order_in.amount = price.price

    order_in.shareRate = master.rate
    if product.name == '点盘':
        limit_time = 1668047054
        obj = crud.order.get_order_by_time(db,time=limit_time, user_id=current_user.id, product_id=order_in.product_id)
        if obj is not None:
            raise HTTPException(status_code=404, detail="您已经下过点盘")

    order = crud.order.create_with_owner(db=db, obj_in=order_in, owner_id=current_user.id)
    with open(settings.PRIVATE_KEY, "r") as f:
        pkey = f.read()
    wechatpay_type=WeChatPayType.APP 
    if trade_type == "native":
        wechatpay_type=WeChatPayType.NATIVE 
    wxpay = WeChatPay(
        wechatpay_type=wechatpay_type,
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
        code_url = None
        prepay_id = None
        paysign = None
        timearray = time.strptime(order_in.create_time, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timearray))
        noncestr = ''.join(sample(ascii_letters + digits, 8))
        package = 'Sign=WXPay'
        if trade_type == "native":
            code_url = result.get('code_url')
            logging.info(f"二维码支付code_url: {code_url},orderId:{order.id}")
        else:
            prepay_id = result.get('prepay_id')
            paysign = wxpay.sign([settings.APPID, str(timestamp), noncestr, prepay_id])
            logging.info(f"App支付prepay_id: {prepay_id},orderId:{order.id}")
        task.add_task(update_order_status, db, wxpay, order.id, order.order_number, settings.MCHID)
        return {'code': 0, 'result': {
            'ordernumber': order.order_number,
            'appid': settings.APPID,
            'partnerid': settings.MCHID,
            'prepayid': prepay_id,
            'codeurl': code_url,
            'package': package,
            'nonceStr': noncestr,
            'timestamp': timestamp,
            'price': order.amount,
            'sign': paysign
        }}
    else:
        return {'code': -1, 'result': {'reason': result.get('code')}}

@router.get("/getOrderPay")
def get_order_pay(
        *,
        db: Session = Depends(deps.get_db),
        ordernumber: str,
        trade_type: str = "app",
        current_user: models.User = Depends(deps.get_current_active_user),
        settings: AppSettings = Depends(get_app_settings)

) -> Any:
    with open(settings.PRIVATE_KEY, "r") as f:
        pkey = f.read()
    wechatpay_type=WeChatPayType.APP 
    if trade_type == "native":
        wechatpay_type=WeChatPayType.NATIVE 
    wxpay = WeChatPay(
        wechatpay_type=wechatpay_type,
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
    ret = wxpay.query(out_trade_no=ordernumber, mchid=settings.MCHID)
    ret_json = json.loads(ret[1])
    print(ret_json["trade_state"])
    if ret_json["trade_state"] == "SUCCESS":
        return {'code': 0, 'result': {
            'trade_state': ret_json["trade_state"],
            'trade_state_desc': ret_json["trade_state_desc"]
        }}
    else:
        return {'code': -1, 'result': {
            'trade_state': ret_json["trade_state"],
            'trade_state_desc': ret_json["trade_state_desc"]
        }}

@router.get("/offOrderInfo", response_model=Any)
def get_off_order_info(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    user_exist_dot_order,dot_product_id = crud.order.get_user_type_order(db, user_id=current_user.id,name='点盘')
    user_exist_free_order,free_product_id = crud.order.get_user_type_order(db, user_id=current_user.id,name='免费排盘')
    if user_exist_dot_order is None or user_exist_free_order is None:
        raise HTTPException(status_code=400, detail="Don't exist product yet")
    invite_count = crud.invite.get_prev_count(db, user_id=current_user.id, status=2)
    if (not user_exist_dot_order) and user_exist_free_order:
        raise HTTPException(status_code=400, detail="Order State error")
    limit_time = 1668047054
    obj = crud.order.get_order_by_time(db, time=limit_time, user_id=current_user.id, product_id=dot_product_id)   
    recent_dot_order_info = {}
    if obj is not None:
        user_recent_dot_order = True
        if user_exist_dot_order and (not user_exist_free_order) and obj.arrange_status == 3:
            create_time = obj.create_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            pay_time = obj.pay_time.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            recent_dot_order_info = schemas.Order(
                id=obj.id,
                product_id=obj.product_id,
                product='点盘',
                order_number=obj.order_number,
                name=obj.name,
                sex=obj.sex,
                birthday=obj.birthday,
                location=obj.location,
                amount=obj.amount,
                shareRate=obj.shareRate,
                owner_id=obj.owner_id,
                master_id=obj.master_id,
                divination=obj.divination,
                reason=obj.reason,
                create_time=create_time,
                pay_time=pay_time,
                arrange_status=obj.arrange_status,
                status=obj.status,
                master=obj.master.name,
                master_avatar=obj.master.avatar,
                owner=obj.owner.user_name,
                is_open=obj.is_open,
                comment_rate=obj.comment_rate,
                owner_email= obj.owner.email,
                owner_phone= obj.owner.phone,
                # pic1=pic1,
                # pic2=pic2,
                # pic3=pic3,
                # memo=memo,
                isNorth=obj.isNorth,
                beat_info=obj.beat_info
            )
    else:
        user_recent_dot_order = False
    return {'exist_dot_order': user_exist_dot_order,
            'exist_free_order': user_exist_free_order,
            'exist_recent_dot_order':user_recent_dot_order,
            'recent_dot_order_info':recent_dot_order_info,
            'free_product_id':free_product_id,
            'invite_count': invite_count}

@router.post('create_free_order')
def create_free_order(
        *,
        task: BackgroundTasks,
        db: Session = Depends(deps.get_db),
        order_in: schemas.OrderCreate,
        trade_type: str = "app",
        current_user: models.User = Depends(deps.get_current_active_user),
        settings: AppSettings = Depends(get_app_settings)
) -> Any:
    """
    Create new free order.
    """
    master = crud.master.get(db=db, id=order_in.master_id)
    if not master:
        raise HTTPException(status_code=404, detail="Master not found")
    product = crud.product.get(db=db, id=order_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    user_exist_free_order, free_product_id = crud.order.get_user_type_order(db, user_id=current_user.id,name='免费排盘')
    if user_exist_free_order:
        raise HTTPException(status_code=404, detail="Cant place free order again")
    if product.name != '免费排盘':
        raise HTTPException(status_code=404, detail="Cant use this to place order")
    invite_count = crud.invite.get_prev_count(db, user_id=current_user.id, status=2)
    if isTestPay():
        invite_count = 12
    order_in.amount = (100 - min(100, 10*invite_count))*100
    order_in.shareRate = master.rate
    order = crud.order.create_with_owner(db=db, obj_in=order_in, owner_id=current_user.id)
    if order_in.amount != 0:
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
            code_url = None
            prepay_id = None
            paysign = None
            timearray = time.strptime(order_in.create_time, "%Y-%m-%d %H:%M:%S")
            timestamp = int(time.mktime(timearray))
            noncestr = ''.join(sample(ascii_letters + digits, 8))
            package = 'Sign=WXPay'
            
            if trade_type == "native":
                code_url = result.get('code_url')
                logging.info(f"二维码支付code_url: {code_url},orderId:{order.id}")
            else:
                prepay_id = result.get('prepay_id')
                paysign = wxpay.sign([settings.APPID, str(timestamp), noncestr, prepay_id])
                logging.info(f"App支付prepay_id: {prepay_id},orderId:{order.id}")
            task.add_task(update_order_status, db, wxpay, order.id, order.order_number, settings.MCHID)
            return {'code': 0, 'result': {
                'ordernumber': order.order_number,
                'appid': settings.APPID,
                'partnerid': settings.MCHID,
                'prepayid': prepay_id,
                'codeurl': code_url,
                'package': package,
                'nonceStr': noncestr,
                'timestamp': timestamp,
                'price': order.amount,
                'sign': paysign
            }}
        else:
            return {'code': -1, 'result': {'reason': result.get('code')}}
    else:
        timearray = time.strptime(order_in.create_time, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timearray))
        task.add_task(update_free_order_status, db,  order.id)
        return {'code': 0, 'result': {
            'ordernumber': order.order_number,
            'appid': settings.APPID,
            'partnerid': settings.MCHID,
            'prepayid': '',
            'package': '',
            'nonceStr': '',
            'timestamp': timestamp,
            'price': order.amount,
            'sign': ''
        }}

@router.get("/get_master_by_order_id",response_model=schemas.Master)
def get_master_by_order_id(
        order_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
)->schemas.Master:
    return crud.order.get_master_by_order_id(db,order_id=order_id)
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
    if order.arrange_status ==3:
        count = crud.order.get_pending_order_count(db,order.master_id,order.owner_id)
        if count ==0:
            disable_chat(order.master_id,order.owner_id)
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
        comment_rate=order.comment_rate,
        isNorth=order.isNorth,
        beat_info=order.beat_info
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
        comment_rate=order.comment_rate,
        isNorth=order.isNorth,
        beat_info=order.beat_info
    )


