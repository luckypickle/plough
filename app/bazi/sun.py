from astral.sun import time_of_transit,SUN_APPARENT_RADIUS,zenith,noon
from astral import SunDirection,Observer
from datetime import date, datetime, timedelta,timezone
from typing import Dict, Optional, Tuple, Union,Any
from .ganzhi import jiazhi_map
import logging


def sunrise(
    observer: Observer,
    date: Optional[datetime.date] = None,
) -> datetime:
    tot = time_of_transit(
                observer,
                date,
                90.0 + SUN_APPARENT_RADIUS,
                SunDirection.RISING,
            )
    tot = tot+timedelta(minutes= (int(observer.longitude)) *4)
    tot_date = tot.date()
    if tot_date != date:
        if tot_date < date:
            delta = timedelta(days=1)
        else:
            delta = timedelta(days=-1)
        new_date = date + delta

        tot = time_of_transit(
            observer,
            new_date,
            90.0 + SUN_APPARENT_RADIUS,
            SunDirection.RISING,
        )
        tot = tot+timedelta(minutes= (int(observer.longitude)) *4)
    return tot

def sunset(
    observer: Observer,
    date: Optional[datetime.date] = None,
) -> datetime:
    tot = time_of_transit(
                observer,
                date,
                90.0 + SUN_APPARENT_RADIUS,
                SunDirection.SETTING,
            )
    tot = tot+timedelta(minutes= (int(observer.longitude)) *4)
    tot_date = tot.date()
    if tot_date != date:
        if tot_date < date:
            delta = timedelta(days=1)
        else:
            delta = timedelta(days=-1)
        new_date = date + delta

        tot = time_of_transit(
            observer,
            new_date,
            90.0 + SUN_APPARENT_RADIUS,
            SunDirection.SETTING,
        )
        tot = tot+timedelta(minutes= (int(observer.longitude)) *4)
    return tot


def sun(
    observer: Observer,
    date: Optional[datetime] = None,
) -> Dict[str, datetime]:
    rise = None
    set = None
    try:
        rise = sunrise(observer,date)
    except ValueError as exc:
        print("math domain error")
        logging.info(f"日出时间计算错误: {exc}")
    try:
        set = sunset(observer,date)
    except ValueError as exc:
        print("math domain error")
        logging.info(f"日落时间计算错误: {exc}")
    return {
        "sunrise": rise,
        "sunset": set,
    }

def get_dh_by_location(
    hGZ: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lng: float = 0,
    lat: float = 0,
) -> Dict[str, Any]:
    isbefore = False
    h_idx = jiazhi_map.index(hGZ)
    zi_h = 23
    zi_m = 0
    hgzs = jiazhi_map[h_idx//12*12:(h_idx//12+1)*12]
    observer = Observer(longitude=lng,latitude=lat)
    dt =datetime(year = year, month = month, day = day,hour=hour,minute=minute,tzinfo=timezone.utc)
    d_datetime = datetime(dt.year, dt.month, dt.day,tzinfo=timezone.utc)
    d = dt.date()
    if hour == 23:
        d = d + timedelta(days=1)
    s = sun(observer,d)
    s_prev = sun(observer,d + timedelta(days=-1))
    sunrise = s["sunrise"]

    sunset = s["sunset"]
    sunset_prev = s_prev["sunset"]
    # print("lat",lat)
    if sunrise is None or sunset is None or sunset_prev is None or (sunset-sunrise).total_seconds() < 720 or (sunset-sunrise).total_seconds() >24*60*60-720:

        #极夜22-2为子时 极昼为卯时
        z = zenith(observer, noon(observer, dt.date()))
        logging.info(f"极夜和极昼: {z}")
        zi_h = 22
        #极夜
        if z > 80.0:
            if 2 <= hour and hour<6:
                hGZ = hgzs[1]
            elif 6 <= hour and hour<10:
                hGZ = hgzs[2]
            elif 10 <= hour and hour<14:
                hGZ = hgzs[9]
            elif 14 <= hour and hour<18:
                hGZ = hgzs[10]
            elif 18 <= hour and hour<22:
                hGZ = hgzs[11]
            elif 22 <= hour or hour<2:
                hGZ = hgzs[0]
        else:
            #极昼
            if 2 <= hour and hour<6:
                hGZ = hgzs[4]
            elif 6 <= hour and hour<10:
                hGZ = hgzs[5]
            elif 10 <= hour and hour<14:
                hGZ = hgzs[6]
            elif 14 <= hour and hour<18:
                hGZ = hgzs[7]
            elif 18 <= hour and hour<22:
                hGZ = hgzs[8]
            elif 22 <= hour or hour<2:
                hGZ = hgzs[3]
    else :
        # 子时以0点分隔 卯时以日出时间分隔 酉时以日落时间分隔 

        logging.info("日出时间：",sunrise)
        logging.info("占卜时间：",dt)
        logging.info("日落时间：",sunset)
        if dt < sunrise:
            interval = (sunrise - d_datetime).total_seconds()/6
            logging.info("早夜八字间隔时间：",interval)
            if dt >= sunrise + timedelta(seconds = -interval):
                hGZ = hgzs[3]
            elif dt >= sunrise + timedelta(seconds = -interval*3):
                hGZ = hgzs[2]
            elif dt >= sunrise + timedelta(seconds = -interval*5):
                hGZ = hgzs[1]
            elif dt >= d_datetime:
                hGZ = hgzs[0]
            else:
                #在0点之前
                interval = (d_datetime - sunset_prev).total_seconds()/6
                zi_h = (d_datetime + timedelta(seconds = -interval)).hour
                zi_m = (d_datetime + timedelta(seconds = -interval)).minute+1
                isbefore = True
                if dt > d_datetime + timedelta(seconds = -interval):
                    hGZ = hgzs[0]
                elif dt > sunrise + timedelta(seconds = -interval*3):
                    #上一天的亥时
                    hGZ = jiazhi_map[(h_idx//12*12-1)%60]
                elif dt > sunrise + timedelta(seconds = -interval*5):
                    #上一天的戌时
                    hGZ = jiazhi_map[(h_idx//12*12-2)%60]
                else:
                    #上一天酉时 就算dt是天亮也算酉时了
                    hGZ = jiazhi_map[(h_idx//12*12-3)%60]
        elif sunrise < dt < sunset:
            interval = (sunset - sunrise).total_seconds()/12
            logging.info("白天八字间隔时间：",interval)
            if dt < sunrise + timedelta(seconds = interval):
                hGZ = hgzs[3]
            elif dt < sunrise + timedelta(seconds = interval*3):
                hGZ = hgzs[4]
            elif dt < sunrise + timedelta(seconds = interval*5):
                hGZ = hgzs[5]
            elif dt < sunrise + timedelta(seconds=interval*7):
                hGZ = hgzs[6]
            elif dt < sunrise + timedelta(seconds=interval*9):
                hGZ = hgzs[7]
            elif dt < sunrise + timedelta(seconds=interval*11):
                hGZ = hgzs[8]
            else:
                hGZ = hgzs[9]
        elif dt > sunset:
            interval = (d_datetime+ timedelta(days=1) - sunset).total_seconds()/6
            logging.info("早夜八字间隔时间：",interval)
            if dt < sunset + timedelta(seconds = interval):
                hGZ = hgzs[9]
            elif dt < sunset + timedelta(seconds = interval*3):
                hGZ = hgzs[10]
            elif dt < sunset + timedelta(seconds = interval*5):
                hGZ = hgzs[11]
            else:
                #下一天的子时
                hGZ = jiazhi_map[(h_idx//12+1)*12]
                zi_h = (sunset + timedelta(seconds = interval*5)).hour
                zi_m = (sunset + timedelta(seconds = interval*5)).minute+1
    return {
        "hGZ": hGZ,
        "isbefore": isbefore,
        "h": zi_h,
        "m": zi_m,
    }
