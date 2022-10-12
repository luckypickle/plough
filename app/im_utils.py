# -- coding: utf-8 --
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
import requests

#settings: AppSettings = get_app_settings()

#url_base = settings.IM_URL
url_base="http://134.175.102.61:18080"

def register_account(avatar,fortune,mobile,nickName):
    try:

        url = url_base+"/api/custom/add"

        querystring = {"avatar": avatar, "fortune": fortune, "mobile": str(mobile), "nickName": str(nickName)}

        response = requests.request("POST", url, params=querystring)

        data = response.json()
        return data["code"] == 200
    except Exception as ex:
        print(ex)
        return False


if __name__ == "__main__":
    res =register_account("https://wuxingyanyi-1254113200.cos.ap-shanghai.myqcloud.com/07ad11ef4ad91101cdb7caed890a1ed6.jpg",0,15601598786,15601598786)
    print(res)