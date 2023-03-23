# -- coding: utf-8 --
from sqlalchemy.orm import Session
from app import crud, models, schemas
import time
from datetime import datetime, timedelta
import sxtwl

def make_return(code,memo):
    return {'code': code, 'result': memo}

cache_master_rate={}
cache_master_rate_time=0
cache_master_rate_refresh_interval=900
def load_master_rate(db:Session):
    global cache_master_rate_time, cache_master_rate
    if int(time.time())-cache_master_rate_time<cache_master_rate_refresh_interval:
        return
    rates = {}
    counts ={}

    res = crud.comment.get_all(db,type=0,limit=100000)
    for one_data in res:
        if one_data.rate is None:
            continue
        if int(one_data.rate)<1:
            continue
        rate = int(one_data.rate)
        master_id = one_data.master_id
        if str(master_id) in rates:
            rates[str(master_id)]+=rate
            counts[str(master_id)]+=1
        else:
            rates[str(master_id)] = rate
            counts[str(master_id)] = 1
    cache_master_rate = {}
    for k,v in rates.items():
        cache_master_rate[k] = "%.1f"%(float(v)/counts[k])
    cache_master_rate_time = int(time.time())


def get_avg_rate(master_id):
    if str(master_id) not in cache_master_rate:
        return 0
    else:
        return cache_master_rate[str(master_id)]

def get_next_birthday(nowTime,birthday,remind_calendar):
    if remind_calendar == 1:   
        nextYear = nowTime.year
        if nowTime.month>birthday.month or (nowTime.month == birthday.month and nowTime.day > birthday.day):
            nextYear += 1
        isRun = nextYear%4==0 and nextYear%100 != 0 or nextYear % 400==0
        if birthday.month == 2 and birthday.day == 29 and not isRun:
            while not isRun:
                nextYear += 1
                isRun = nextYear%4==0 and nextYear%100 != 0 or nextYear % 400==0
        return datetime(year = nextYear, month = birthday.month, day = birthday.day)
    else:
        birthdayLunar = sxtwl.fromSolar(birthday.year,birthday.month,birthday.day)
        nowTimeLunar = sxtwl.fromSolar(nowTime.year,nowTime.month,nowTime.day)
        nextYear = nowTimeLunar.getLunarYear()
        if nowTimeLunar.getLunarMonth() > birthdayLunar.getLunarMonth() :
            nextYear += 1
        elif  nowTimeLunar.getLunarMonth() == birthdayLunar.getLunarMonth() and nowTimeLunar.getLunarDay() > birthdayLunar.getLunarDay() :
            nextYear += 1
        elif nowTimeLunar.getLunarMonth() == birthdayLunar.getLunarMonth() and nowTimeLunar.isLunarLeap() and not birthdayLunar.isLunarLeap():
            nextYear += 1
        #当年当月是闰月的算闰月生日 之后的闰月不算
        if nowTimeLunar.isLunarLeap() and nextYear == nowTimeLunar.getLunarYear() and birthdayLunar.getLunarYear() == nowTimeLunar.getLunarYear():
            nowBirthdayLunar = sxtwl.fromLunar(nextYear,birthdayLunar.getLunarMonth(),birthdayLunar.getLunarDay(),isRun=True)
        elif nowTimeLunar.isLunarLeap() and nextYear == nowTimeLunar.getLunarYear():
            nowBirthdayLunar = sxtwl.fromLunar(nextYear+1,birthdayLunar.getLunarMonth(),birthdayLunar.getLunarDay())
        else:
            nowBirthdayLunar = sxtwl.fromLunar(nextYear,birthdayLunar.getLunarMonth(),birthdayLunar.getLunarDay())
        #生日为农历大月最后一天
        leap = birthdayLunar.getLunarDay()==30 and nowBirthdayLunar.getLunarDay()!=30
        while leap:
            nextYear += 1
            nowBirthdayLunar = sxtwl.fromLunar(nextYear,birthdayLunar.getLunarMonth(),birthdayLunar.getLunarDay())
            leap = birthdayLunar.getLunarDay()==30 and nowBirthdayLunar.getLunarDay()!=30
        return datetime(year = nowBirthdayLunar.getSolarYear(),month = nowBirthdayLunar.getSolarMonth(),day = nowBirthdayLunar.getSolarDay())
    

