# -*- coding: utf-8 -*-
import sxtwl
from .datas import Gan,Zhi
# 八法逐日干支基数歌
# 甲己辰戌丑未十，乙庚申酉九为期，
# 丁壬寅卯八成数， 戊癸巳午七相宜，
# 丙辛亥子亦七数，逐日干支即得知。
# 八法临时干支基数歌
# 甲己子午九宜用，乙庚丑未八无疑，
# 丙辛寅申七作数，丁壬卯酉六须知，
# 戊癸辰戌各有五，巳亥单加四共齐，
# 阳日除九阴除六，不及零余穴下推。
d_temps = {"甲":10, "乙":9, "丙":7, "丁":8, "戊":7, "己":10, "庚":9, "辛":7, "壬":8, "癸":7,"子":7, "丑":10, "寅":8, "卯":8, "辰":10, 
            "巳":7, "午":7, "未":10, "申":9, "酉":9,"戌":10, "亥":7}


h_temps = {"甲":9, "乙":8, "丙":7, "丁":6, "戊":5, "己":9, "庚":8, "辛":7, "壬":6, "癸":5,"子":9, "丑":8, "寅":7, "卯":6, "辰":5, 
            "巳":4, "午":9, "未":8, "申":7, "酉":6,"戌":5, "亥":4}
# 坎一联申脉，照海坤二五，
# 震三属外关，巽四临泣数，
# 乾六是公孙，兑七后溪府，
# 艮八属内关，离九列缺主。
acupoint_list = ["列缺", "申脉", "照海", "外关", "临泣", "照海", "公孙", "后溪", "内关"]

def get_acupoint(d_tg,d_dz,h_tg,h_dz,sex)-> str:
    # print(str(h_tg)+str(h_dz))
    sum = d_temps[Gan[d_tg]]+d_temps[Zhi[d_dz]]+h_temps[Gan[h_tg]]+h_temps[Zhi[h_dz]]
    
    remainder = 0
    if d_tg % 2 == 0:
       remainder = sum%9
    else:
        remainder = sum%6
        if remainder == 0:
            remainder = 6
    acupoint = ""
    if sex==0 and remainder==5:
        acupoint = "内关"
    else:
        acupoint = acupoint_list[remainder]
    # print(acupoint)
    return acupoint

def get_turtle(year,month,day_,hour,minute,sex):
    day = sxtwl.fromSolar(
        year, month, day_)
    dGZ = day.getDayGZ()
    hGZ = day.getHourGZ(hour)
    if day.hasJieQi():
        jd = day.getJieQiJD()
        jieqi_t = sxtwl.JD2DD(jd)
        if jieqi_t.h == 23 and int(hour) >= 23 and jieqi_t.m < minute:
            day = day.after(1)
            dGZ = day.getDayGZ()
    else:
        if int(hour) >= 23:
            day = day.after(1)
            dGZ = day.getDayGZ()
    result =[]
    data= {}
    acupoints =[]
    h_tg = (hGZ.tg - hGZ.dz)%10
    for h_dz in range(0, hGZ.dz):
        acupoint = get_acupoint(dGZ.tg,dGZ.dz,h_tg,h_dz,sex)
        h_tg = (h_tg + 1)%10
        acupoints.append(acupoint)
    h_tg = hGZ.tg
    for h_dz in range(hGZ.dz, 12):
        acupoint = get_acupoint(dGZ.tg,dGZ.dz,h_tg,h_dz,sex)
        h_tg = (h_tg + 1)%10
        acupoints.append(acupoint)
    data["date"] = str(day.getSolarMonth())+'-'+str(day.getSolarDay())
    data["week"] = day.getWeek()
    data["acupoints"] = acupoints
    result.append(data)
    for days in range(1, 7):
        acupoints =[]
        data= {}
        day = day.after(1)
        dGZ = day.getDayGZ()
        for h_dz in range(0, 12):
            acupoint = get_acupoint(dGZ.tg,dGZ.dz,h_tg,h_dz,sex)
            h_tg = (h_tg + 1)%10
            acupoints.append(acupoint)
        data["date"] = str(day.getSolarMonth())+'-'+str(day.getSolarDay())
        data["week"] = day.getWeek()
        data["acupoints"] = acupoints
        result.append(data)
    return result
# print(result)
    


