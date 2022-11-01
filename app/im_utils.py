# -- coding: utf-8 --
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
import requests

settings: AppSettings = get_app_settings()

url_base = settings.IM_URL
#url_base="http://134.175.102.61:18080"

def safe_post(url,querystring):
    try:
        response = requests.request("POST", url, params=querystring)
        return response.json()
    except Exception as ex:
        print(ex)
        return {"data":100,"error":str(ex)}

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


def query_message_list(page_num, page_size,teacherId,userPhone):
    url = url_base + "/api/custom/talklist"

    querystring = {"pageNum": page_num, "pageSize": page_size, "teacherId": str(teacherId), "userPhone": str(userPhone)}

    response = safe_post(url,querystring)


    data = response
    #
    # print(response.text)
    if data["code"] == 200:
        return data["data"]
    return {}

def query_message_detail(page_num,page_size,friend_name,user_name):
    url = url_base + "/api/custom/messagelist"

    querystring = {"pageNum": page_num, "pageSize": page_size, "friendname": str(friend_name ), "username": str(user_name)}

    response = safe_post(url, querystring)

    data = response
    #print(response.text)
    if data["code"] == 200:
        return data["data"]
    return {}

def recovery_chat(master_id,user_id):
    url = url_base + "/api/custom/recoveryChat"

    querystring = {"mastername": "master_"+str(master_id),
                   "username": "user_"+str(user_id)}

    response = safe_post(url, querystring)

    data = response
    # print(response.text)
    if data["code"] == 200:
        return data["msg"]
    return {}
def disable_chat(master_id,user_id):
    url = url_base + "/api/custom/disableChat"

    querystring = {"mastername": "master_"+str(master_id),
                   "username": "user_"+str(user_id)}

    response = safe_post(url, querystring)

    data = response
    # print(response.text)
    if data["code"] == 200:
        return data["msg"]
    return {}
def pushMsg(content,user_name):
    url = url_base + "/api/xinge/pushMsg"

    querystring = {"content": content,
                   "username": str(user_name)}

    response = safe_post(url, querystring)

    data = response
    # print(response.text)
    if data["code"] == 200:
        return data["msg"]
    return {}



if __name__ == "__main__":
    # res =register_account("https://wuxingyanyi-1254113200.cos.ap-shanghai.myqcloud.com/07ad11ef4ad91101cdb7caed890a1ed6.jpg",0,15601598786,15601598786)
    # print(res)
    res =query_message_list(1,10,"","")
    print(res)
    res =query_message_detail(1,10,"master_10","user_37")
    print(res)