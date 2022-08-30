import logging
import json
import time
from random import sample
from string import ascii_letters, digits
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from wechatpayv3 import WeChatPay, WeChatPayType

from app import crud, models, schemas
from app.api import deps
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings

router = APIRouter()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(process)s - %(levelname)s: %(message)s')
settings: AppSettings = get_app_settings()
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
    logger=logging.getLogger(__name__),
    partner_mode=settings.PARTNER_MODE,
    proxy=None)


@router.get("/wechat")
def get_prepay_id(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve prepay_id.
    """
    out_trade_no = ''.join(sample(ascii_letters + digits, 16))
    description = 'demo-description'
    amount = 1
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount}
    )
    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get('prepay_id')
        timestamp = int(time.time())
        noncestr = ''.join(sample(ascii_letters + digits, 8))
        package = 'Sign=WXPay'
        paysign = wxpay.sign([settings.APPID, str(timestamp), noncestr, prepay_id])
        return {'code': 0, 'result': {
            'appid': settings.APPID,
            'partnerid': settings.MCHID,
            'prepayid': prepay_id,
            'package': package,
            'nonceStr': noncestr,
            'timestamp': timestamp,
            'sign': paysign
        }}
    else:
        return {'code': -1, 'result': {'reason': result.get('code')}}
