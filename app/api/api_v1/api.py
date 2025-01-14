from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    orders, login, users, 
    masters, utils, pay,
    product, comments, invite, reward, withdraw,video,folders,settings,remind,meihua,tool
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(pay.router, prefix="/pay", tags=["pay"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(masters.router, prefix="/masters", tags=["masters"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(product.router, prefix="/product", tags=["product"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(invite.router, prefix="/invite", tags=["invite"])
api_router.include_router(reward.router, prefix="/reward", tags=["reward"])
api_router.include_router(withdraw.router, prefix="/withdraw", tags=["withdraw"])
api_router.include_router(video.router, prefix="/video", tags=["video"])
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(remind.router, prefix="/remind", tags=["remind"])
api_router.include_router(meihua.router, prefix="/meihua", tags=["meihua"])
api_router.include_router(tool.router, prefix="/tool", tags=["tool"])