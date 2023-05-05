# -*- coding: utf-8 -*-

import datetime
import collections
import sxtwl
from .common import *
from . import datas


Gans = collections.namedtuple("Gans", "year month day time")
Zhis = collections.namedtuple("Zhis", "year month day time")


class BaZi():
    def __init__(self, year: int, month: int, day: int, hour: int, sex: int,lunar:int=0,run:int=0,minute:int=0,early_isOpen:bool=False):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour = int(hour)
        self.sex = int(sex)
        self.lunar = int(lunar)
        self.run = run==1
        self.minute = int(minute)
        self.early_isOpen = int(early_isOpen)

    def get_detail(self):
        detail = {}
        if self.lunar == 1:
            day = sxtwl.fromLunar(self.year, self.month, self.day,self.run)
        else:
            day = sxtwl.fromSolar(
            self.year, self.month, self.day)
        detail['solarDay'] = {
            'year': day.getSolarYear(),
            'month': day.getSolarMonth(),
            'day': day.getSolarDay()
        }
        detail['lunarDay'] = {
            'year': day.getLunarYear(),
            'leap': "闰" if day.isLunarLeap() else "",
            'month': day.getLunarMonth(),
            'day': day.getLunarDay()
        }
        yGZ = day.getYearGZ()
        mGZ = day.getMonthGZ()
        dGZ = day.getDayGZ()
        hGZ = day.getHourGZ(self.hour)
        if day.hasJieQi():
            jd = day.getJieQiJD()
            jieqi_t = sxtwl.JD2DD(jd)
            if jieqi_t.h > int(self.hour) or (jieqi_t.h==self.hour and jieqi_t.m>= self.minute):
                tmp_day = day.before(1)
                yGZ = tmp_day.getYearGZ()
                mGZ = tmp_day.getMonthGZ()
            if jieqi_t.h==23 and int(self.hour)>=23 and jieqi_t.m< self.minute and not self.early_isOpen:
                tmp_day = day.after(1)
                dGZ = tmp_day.getDayGZ()
        else:
            if int(self.hour)>=23 and not self.early_isOpen:
                tmp_day = day.after(1)
                dGZ = tmp_day.getDayGZ()
        gans = Gans(
            year=datas.Gan[yGZ.tg], month=datas.Gan[mGZ.tg],
            day=datas.Gan[dGZ.tg], time=datas.Gan[hGZ.tg])
        zhis = Zhis(
            year=datas.Zhi[yGZ.dz], month=datas.Zhi[mGZ.dz],
            day=datas.Zhi[dGZ.dz], time=datas.Zhi[hGZ.dz])
        zhus = [item for item in zip(gans, zhis)]
        detail['sizhu'] = {
            'gans': ' '.join(list(gans)),
            'zhis': ' '.join(list(zhis))
        }
        # 十神
        me = datas.Gan[dGZ.tg]
        gan_shens = []
        for seq, item in enumerate(gans):
            if seq == 2:
                gan_shens.append('己')
            else:
                gan_shens.append(datas.ten_deities[me][item])
        zhi_shens = []
        for item in zhis:
            d = datas.zhi5[item]
            zhi_shens.append(datas.ten_deities[me][max(d, key=d.get)])
        detail['ten_deities'] = {
            'gan': gan_shens,
            'zhi': zhi_shens
        }
        # 计算八字强弱, 子平真诠的计算
        weak = True
        me_status = []
        shens = gan_shens + zhi_shens
        for item in zhis:
            me_status.append(datas.ten_deities[me][item])
            if datas.ten_deities[me][item] in ('长', '帝', '建'):
                weak = False
                break
        if weak and shens.count('比') + me_status.count('库') > 2:
            weak = False
        detail['weak'] = weak

        # 大运
        seq = datas.Gan.index(gans.year)
        if self.sex == 0:
            if seq % 2 == 0:
                direction = -1
            else:
                direction = 1
        else:
            if seq % 2 == 0:
                direction = 1
            else:
                direction = -1
        dayuns = []
        gan_seq = datas.Gan.index(gans.month)
        zhi_seq = datas.Zhi.index(zhis.month)
        for i in range(12):
            gan_seq += direction
            zhi_seq += direction
            dayuns.append(datas.Gan[gan_seq % 10] + datas.Zhi[zhi_seq % 12])
        dayunData = []
        dayunBig = []
        dayunYears = {}
        birthday = datetime.date(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay())
        count = 0
        for i in range(30):
            day_ = sxtwl.fromSolar(birthday.year, birthday.month, birthday.day)
            # if day_.hasJieQi() and day_.getJieQiJD() % 2 == 1
            if day_.hasJieQi() and day_.getJieQi() % 2 == 1:
                break
            birthday += datetime.timedelta(days=direction)
            count += 1
        ages = [(round(count / 3 + 10 * i), round(self.year + 10 * i + count // 3)) for i in range(12)]
        for (seq, value) in enumerate(ages):
            gan_ = dayuns[seq][0]
            zhi_ = dayuns[seq][1]
            zhi5_ = ''
            second_zhi = ''
            for gan in datas.zhi5[zhi_]:
                zhi5_ = zhi5_ + "{}{}{}　".format(gan, datas.gan5[gan], datas.ten_deities[me][gan])
                #if second_zhi == "":
                second_zhi = datas.ten_deities[me][gan]
            zhi__ = set()  # 大运地支关系
            for item in zhis:

                for type_ in datas.zhi_atts[zhi_]:
                    if item in datas.zhi_atts[zhi_][type_]:
                        zhi__.add(type_ + ":" + item)
            zhi__ = '  '.join(zhi__)
            empty = chr(12288)
            if zhi_ in datas.empties[zhus[2]]:
                empty = '空'
            dayunBig.append(
                {"age":int(value[0]),"year": int(value[1]), "dayun": dayuns[seq], "first": ten_deities[me][gan_], "second": second_zhi})
            dayunYears[str(int(value[1]))] = []
            out = "{1:<4d}{2:<5s}{3} {4}:{5}{8}{6:{0}<6s}{12}{7}{8}{9} - {10:{0}<15s} {11}".format(
                chr(12288), int(value[0]), '', dayuns[seq], datas.ten_deities[me][gan_], gan_, check_gan(gan_, gans),
                zhi_, yinyang(zhi_), datas.ten_deities[me][zhi_], zhi5_, zhi__, empty)
            dayunData.append(out)
            gan_index = datas.Gan.index(gan_)
            zhi_index = datas.Zhi.index(zhi_)
            zhis2 = list(zhis) + [zhi_]
            gans2 = list(gans) + [gan_]
            if value[0] > 100:
                continue
            for i in range(10):
                day2 = sxtwl.fromSolar(value[1] + i, 5, 1)
                yTG = day2.getYearGZ()
                gan2_ = datas.Gan[yTG.tg]
                zhi2_ = datas.Zhi[yTG.dz]
                zhi6_ = ''
                sub_second_zhi = ''
                for gan in zhi5[zhi2_]:
                    zhi6_ = zhi6_ + "{}{}{}　".format(gan, gan5[gan], datas.ten_deities[me][gan])
                    #if sub_second_zhi == "":
                    sub_second_zhi = datas.ten_deities[me][gan]
                # 大运地支关系
                zhi__ = set()  # 大运地支关系
                for item in zhis2:
                    for type_ in datas.zhi_atts[zhi2_]:
                        if item in datas.zhi_atts[zhi2_][type_]:
                            zhi__.add(type_ + ":" + item)
                zhi__ = '  '.join(zhi__)
                empty = chr(12288)
                if zhi2_ in datas.empties[zhus[2]]:
                    empty = '空'
                dayunYears[str(int(value[1]))].append(
                    {"age":int(value[0]) + i,"year": value[1] + i, "dayun": gan2_ + zhi2_, "first": ten_deities[me][gan2_],
                     "second": sub_second_zhi})
                out = "{1:>3d} {2:<5d}{3} {4}:{5}{8}{6:{0}<6s}{12}{7}{8}{9} - {10:{0}<15s} {11}".format(
                    chr(12288), int(value[0]) + i, value[1] + i, gan2_ + zhi2_, datas.ten_deities[me][gan2_], gan2_,
                    check_gan(gan2_, gans2),
                    zhi2_, yinyang(zhi2_), datas.ten_deities[me][zhi2_], zhi6_, zhi__, empty)
                dayunData.append(out)
            #流年集合添加重复的一年
            day2_dup = sxtwl.fromSolar(value[1] + 10, 5, 1)
            yTG_dup = day2_dup.getYearGZ()
            gan2_dup = datas.Gan[yTG_dup.tg]
            zhi2_dup = datas.Zhi[yTG_dup.dz]
            dayunYears[str(int(value[1]))].append(
                {"age":int(value[0]) + 10,"year": value[1] + 10, "dayun": gan2_dup + zhi2_dup, "first": '',
                "second": ''})  
        detail['dayun'] = dayunData
        detail['dayunbig'] = dayunBig
        detail['dayunyear'] = dayunYears

        #小运  在立春前要单独加上去年数据
        # xiaoyunAge = round(count / 3)
        xiaoyunYears = []
        brithtime = datetime.datetime(day.getSolarYear(), month = day.getSolarMonth(),day = day.getSolarDay(),hour = self.hour,minute = self.minute)
        # print(xiaoyunAge)
        for i in range(self.year, self.year + round(count // 3)+1):
            print(i)
            day_xiaoyun = sxtwl.fromSolar(i, 5, 1)
            yTG_xiaoyun = day_xiaoyun.getYearGZ()
            gan3_xiaoyun = datas.Gan[yTG_xiaoyun.tg]
            zhi3_xiaoyun = datas.Zhi[yTG_xiaoyun.dz]
            second_xiaoyun = ''
            for gan in zhi5[zhi3_xiaoyun]:
                zhi6_ = zhi6_ + "{}{}{}　".format(gan, gan5[gan], datas.ten_deities[me][gan])
                second_xiaoyun = datas.ten_deities[me][gan]
            # xiaoyunYears[str(self.year + i - 1)] = []
            xiaoyunYears.append(
                {"age":round(count / 3)-(self.year + round(count // 3)-i),"year": i, "dayun": gan3_xiaoyun + zhi3_xiaoyun, "first": ten_deities[me][gan3_xiaoyun],
                "second": second_xiaoyun})
        # if len(xiaoyunYears)==0:
        #     xiaoyunYears.append(dayunBig[0])
        lichunTime = getLichunTime(self.year)
        if lichunTime > brithtime:
            day_xiaoyun2 = sxtwl.fromSolar(self.year-1, 5, 1)
            yTG_xiaoyun2 = day_xiaoyun2.getYearGZ()
            gan3_xiaoyun2 = datas.Gan[yTG_xiaoyun2.tg]
            zhi3_xiaoyun2 = datas.Zhi[yTG_xiaoyun2.dz]
            second_xiaoyun2 = ''
            for gan in zhi5[zhi3_xiaoyun2]:
                zhi6_ = zhi6_ + "{}{}{}　".format(gan, gan5[gan], datas.ten_deities[me][gan])
                second_xiaoyun2 = datas.ten_deities[me][gan]
            # xiaoyunYears.append(
            #     {"age":0,"year": self.year, "dayun": gan3_xiaoyun2 + zhi3_xiaoyun2, "first": ten_deities[me][gan3_xiaoyun2],
            #     "second": second_xiaoyun2})
            xiaoyunYears.insert(0,{"age":0,"year": self.year, "dayun": gan3_xiaoyun2 + zhi3_xiaoyun2, "first": ten_deities[me][gan3_xiaoyun2],
                "second": second_xiaoyun2})
        hindex = jiazhi_map.index(gans.time+zhis.time)
        for xiaoyunYear in xiaoyunYears:
            hindex += direction
            xiaoyunYear["xiaoyunbazi"]=jiazhi_map[(hindex)%60]
        detail['xiaoyun'] = {"age":round(count / 3),"year": self.year}
        detail['xiaoyunyear'] = xiaoyunYears

        #起运和交运
        nextJieqi = getNextJie(day,self.hour,self.minute)
        prevJieqi = getPrevJie(day,self.hour,self.minute)
        
        if (datas.Gan.index(gans.year) % 2 == 0 and self.sex == 1) or (datas.Gan.index(gans.year) % 2 == 1 and self.sex == 0):  
            time = 120 * (nextJieqi.get("datetime")-brithtime).total_seconds()
        else:
            time = 120 * (brithtime-prevJieqi.get("datetime")).total_seconds()
        yuntime = brithtime + datetime.timedelta(seconds=time)
        days = datetime.timedelta(seconds=time).days

        # print(str(days//365)+"年"+str(days%365//30)+"月"+str(days%365%30)+ "日"+str()+ "时")
        jiaoyunJieqi = getPrevJie(sxtwl.fromSolar(yuntime.year, yuntime.month, yuntime.day),yuntime.hour,yuntime.minute)
        # print( jiaoyunJieqi.get("jieqi")+"后"+str(days)+"天")
        detail['qiyun'] = {"years":days//365, "months":days%365//30, "days":days%365%30, "hours":int(time/3600%24)}
        detail['jiaoyun'] = {"jieqi":jiaoyunJieqi.get("jieqi"),"days":(yuntime - jiaoyunJieqi.get("datetime")).days}
        detail['xiaoyunjieqi'] = prevJieqi.get("jieqi")
        detail['dayunjieqi'] = jiaoyunJieqi.get("jieqi")
        #司令
        silingday = (brithtime-prevJieqi.get("datetime")).days
        silingjieqi = prevJieqi.get("jieqi")
        siling_gan=""
        print(siling[silingjieqi])
        for key in siling[silingjieqi]:
            silingday -= siling[silingjieqi].get(key)
            siling_gan = key
            if silingday < 0: 
                break
        detail['siling'] = siling_gan

        # 格局
        ge = ''
        if (me, zhis.month) in jianlus:
            print(jianlu_desc)
            print("-" * 120)
            print(jianlus[(me, zhis.month)])
            print("-" * 120 + "\n")
            ge = '建'
        # elif (me == '丙' and ('丙','申') in zhus) or (me == '甲' and ('己','巳') in zhus):
        # print("格局：专财. 运行官旺 财神不背,大发财官。忌行伤官、劫财、冲刑、破禄之运。喜身财俱旺")
        elif (me, zhis.month) in (('甲', '卯'), ('庚', '酉'), ('壬', '子')):
            ge = '月刃'
        else:
            zhi = zhis[1]
            if zhi in wuhangs['土'] or (me, zhis.month) in (
            ('乙', '寅'), ('丙', '午'), ('丁', '巳'), ('戊', '午'), ('己', '巳'), ('辛', '申'), ('癸', '亥')):
                for item in zhi5[zhi]:
                    if item in gans[:2] + gans[3:]:
                        ge = datas.ten_deities[me][item]
            else:
                d = datas.zhi5[zhi]
                ge = datas.ten_deities[me][max(d, key=d.get)]
        detail['geju'] = ge
        print("格局:", ge, '\t', end=' ')

        return detail


def cal_hour(hour):
    if hour >=23 or hour<1:
        return '子'
    for k,v in zhi_time.items():
        hour_list = v.split('-')
        if hour>= int(hour_list[0]) and hour<int(hour_list[1]):
            return k

def get_birthday_by_bazi(year,month,day,hour):
    jds = sxtwl.siZhu2Year(getGZ(year), getGZ(month), getGZ(day), getGZ(hour),
                           1900, int(2100));
    ret_data=[]
    
    for jd in jds:
        t = sxtwl.JD2DD(jd)
        # print()
        sxt=sxtwl.fromSolar(t.Y, t.M, t.D)
        Lleap = "闰" if sxt.isLunarLeap() else ""
        ret_data.append({"solar":"%d-%d-%d %d:%d" % (t.Y, t.M, t.D, t.h, t.m),"lunar":"{}年{}{}月{}日 {}时".format(sxt.getLunarYear(), Lleap, sxt.getLunarMonth(), sxt.getLunarDay(),cal_hour(t.h))})
    #siZhu2Year接口无法根据节气具体时辰切换月柱
    prevMonth = jiazhi_map[(jiazhi_map.index(month)-1)%60]
    print(prevMonth)
    prevJds = sxtwl.siZhu2Year(getGZ(year), getGZ(str(prevMonth)), getGZ(day), getGZ(hour),
                           1900, 2100)     
    for jd in prevJds:
        mGZ=prevMonth
        t = sxtwl.JD2DD(jd)
        h=t.h
        m=t.m
        # print()
        sxt=sxtwl.fromSolar(t.Y, t.M, t.D)
        Lleap = "闰" if sxt.isLunarLeap() else ""
        if sxt.hasJieQi():
            jd = sxt.getJieQiJD()
            jieqi_t = sxtwl.JD2DD(jd)
            if int(t.h) > jieqi_t.h:
                tmp_day = sxt.after(1)
                mGZ = Gan[tmp_day.getMonthGZ().tg]+Zhi[tmp_day.getMonthGZ().dz]
            if jieqi_t.h > int(h) or (jieqi_t.h == h and jieqi_t.m >= m) and int(h)+2> jieqi_t.h:
                m=59
                h=(int(t.h)+1) % 24
                tmp_day = sxt.after(1)
                mGZ = Gan[tmp_day.getMonthGZ().tg]+Zhi[tmp_day.getMonthGZ().dz]
        if mGZ != month:
            continue
        ret_data.append({"solar":"%d-%d-%d %d:%d" % (t.Y, t.M, t.D, h, m),"lunar":"{}年{}{}月{}日 {}时".format(sxt.getLunarYear(), Lleap, sxt.getLunarMonth(), sxt.getLunarDay(),cal_hour(t.h))})
    return ret_data

def get_bazi_by_birthday(year,month,day_,hour,minute):
    day = sxtwl.fromSolar(
        year, month, day_)

    yGZ = day.getYearGZ()
    mGZ = day.getMonthGZ()
    dGZ = day.getDayGZ()
    hGZ = day.getHourGZ(hour)
    if day.hasJieQi():
        jd = day.getJieQiJD()
        jieqi_t = sxtwl.JD2DD(jd)
        if jieqi_t.h > int(hour) or (jieqi_t.h == hour and jieqi_t.m >= minute):
            tmp_day = day.before(1)
            yGZ = tmp_day.getYearGZ()
            mGZ = tmp_day.getMonthGZ()
        if jieqi_t.h == 23 and int(hour) >= 23 and jieqi_t.m < minute:
            tmp_day = day.after(1)
            dGZ = tmp_day.getDayGZ()
    else:
        if int(hour) >= 23:
            tmp_day = day.after(1)
            dGZ = tmp_day.getDayGZ()
    gans = Gans(
        year=datas.Gan[yGZ.tg], month=datas.Gan[mGZ.tg],
        day=datas.Gan[dGZ.tg], time=datas.Gan[hGZ.tg])
    zhis = Zhis(
        year=datas.Zhi[yGZ.dz], month=datas.Zhi[mGZ.dz],
        day=datas.Zhi[dGZ.dz], time=datas.Zhi[hGZ.dz])

    return {
        'gans': ' '.join(list(gans)),
        'zhis': ' '.join(list(zhis))
    }


def convert_lunar_to_solar(year,month,day,isRun):
    day = sxtwl.fromLunar(year,month,day,isRun==1)

    return (day.getSolarYear(),day.getSolarMonth(),day.getSolarDay())

def getYearJieQi(year):
    day = datetime.datetime(year, 1, 1)
    start = False
    jieqicount = 0
    ret = []
    for i in range(400):
        day_ = sxtwl.fromSolar(int(day.year), int(day.month), int(day.day))
        if day_.hasJieQi() and day_.getJieQi() % 2 == 1:
            if int(day_.getJieQi()) == 3:
                start = True
            if start:
                ret.append("%d/%d"%(int(day.month),int(day.day)))
                jieqicount += 1
            if jieqicount == 12:
                break
        day = day + datetime.timedelta(days=1)
    return ret



def cal_wuxing_color(year,month,day_,hour,minute,day_delta:int=0):
    day = sxtwl.fromSolar(
        year, month, day_)

    yGZ = day.getYearGZ()
    mGZ = day.getMonthGZ()
    dGZ = day.getDayGZ()
    hGZ = day.getHourGZ(hour)
    if day.hasJieQi():
        jd = day.getJieQiJD()
        jieqi_t = sxtwl.JD2DD(jd)
        if jieqi_t.h > int(hour) or (jieqi_t.h == hour and jieqi_t.m >= minute):
            tmp_day = day.before(1)
            yGZ = tmp_day.getYearGZ()
            mGZ = tmp_day.getMonthGZ()
        if jieqi_t.h == 23 and int(hour) >= 23 and jieqi_t.m < minute:
            tmp_day = day.after(1)
            dGZ = tmp_day.getDayGZ()
    else:
        if int(hour) >= 23:
            tmp_day = day.after(1)
            dGZ = tmp_day.getDayGZ()
    gans = Gans(
        year=Gan[yGZ.tg], month=Gan[mGZ.tg],
        day=Gan[dGZ.tg], time=Gan[hGZ.tg])
    zhis = Zhis(
        year=Zhi[yGZ.dz], month=Zhi[mGZ.dz],
        day=Zhi[dGZ.dz], time=Zhi[hGZ.dz])

    todaydate = datetime.date.today() + datetime.timedelta(days=day_delta)
    today = sxtwl.fromSolar(
        todaydate.year, todaydate.month, todaydate.day)
    tyGZ = today.getYearGZ()
    tmGZ = today.getMonthGZ()
    tdGZ = today.getDayGZ()
    tgans = [Gan[tyGZ.tg],Gan[tmGZ.tg],Gan[tdGZ.tg]]
    tzhis = [Zhi[tyGZ.dz],Zhi[tmGZ.dz],Zhi[tdGZ.dz]]


    me = gans.day
    gan_scores = {"甲": 0, "乙": 0, "丙": 0, "丁": 0, "戊": 0, "己": 0, "庚": 0, "辛": 0,
                  "壬": 0, "癸": 0}
    tgan_scores = {"甲": 0, "乙": 0, "丙": 0, "丁": 0, "戊": 0, "己": 0, "庚": 0, "辛": 0,
                  "壬": 0, "癸": 0}
    for item in gans:
        gan_scores[item] += 5
        tgan_scores[item] += 5

    for item in list(zhis) + [zhis.month]:
        for gan in zhi5[item]:
            gan_scores[gan] += zhi5[item][gan]
            tgan_scores[gan] += zhi5[item][gan]

    for item in tgans:
        tgan_scores[item] += 10
    for item in tzhis:
        for gan in zhi5[item]:
            tgan_scores[gan] += zhi5[item][gan]*2

    me_attrs_ = ten_deities[me].inverse
    strong = tgan_scores[me_attrs_['比']] + tgan_scores[me_attrs_['劫']] \
             + tgan_scores[me_attrs_['枭']] + tgan_scores[me_attrs_['印']]
    wuxing = ["","",""]
    wuxing_len = 3
    print(strong)
    if strong>60:
        if tgan_scores[me_attrs_['印']]>tgan_scores[me]:

            wuxing[0] = me_attrs_["财"]
            wuxing[1] = me_attrs_["食"]
            wuxing[2] = me_attrs_["官"]
        else:
            wuxing[0]=me_attrs_["官"]
            wuxing[1] = me_attrs_["食"]
            wuxing[2] = me_attrs_["财"]

    else:
        wuxing_len =2
        if tgan_scores[me_attrs_['印']]>tgan_scores[me]:
            wuxing[0]= me_attrs_["比"]
            wuxing[1]  =   me_attrs_["印"]
        else:
            wuxing[0]=me_attrs_["印"]
            wuxing[1]= me_attrs_["比"]


    for i in range(wuxing_len):
        wuxing[i] = gan5[wuxing[i]]

    color_map = {'木':['绿色','淡青色'],
                 '火': ['红色', '紫色'],
                 '土': ['黄色', '棕色'],
                 '金': ['白色', '银色'],
                 '水': ['黑色', '深蓝色'],
                }
    if wuxing_len==2:
        gan_num = tdGZ.tg %4
    else:
        gan_num = tdGZ.tg % 8
    ret =[]
    for i in range(wuxing_len):
        ret.append( color_map[wuxing[i]][(gan_num>>i)&0x1]   )
    month_map = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "腊"]
    day_map = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十", "十一", "十二", "十三", "十四", "十五", "十六", "十七",
               "十八", "十九", "二十",
               "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
    Lleap = "闰" if today.isLunarLeap() else ""
    lunar_str = "{}年  {}{}月{}".format(Gan[tyGZ.tg] + Zhi[tyGZ.dz], Lleap, month_map[today.getLunarMonth() - 1],
                                    day_map[today.getLunarDay() - 1])
    jieqi_map = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑",
                 "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
    jieqi = ""
    if today.hasJieQi():
        jieqi = jieqi_map[today.getJieQi()]

    return {"color":ret,"lunar":lunar_str,"jieqi":jieqi}
    # print('今日颜色:',color_map[main_wuxing],color_map[sec_wuxing][0])



def get_wuxings_by_birthyear(birthyear,nowyear):
    zhi_map = {"子":"水",
           "丑":"土",
           "寅":"木",
           "卯":"木",
           "辰":"土",
           "巳":"火",
           "午":"火",
           "未":"土",
           "申":"金",
           "酉":"金",
           "戌":"土",
           "亥":"水"}   
    year=nowyear-1      
    wuxingMap={}
    while year > birthyear:
        #1204年是甲子年，每隔六十年一个甲子
        idx = (year - 1204) % 60
        y = jiazhi_map[idx]
        ganWuxing = gan5[y[0]]
        zhiWuxing = zhi_map[y[1]]
        item={}
        if(ganWuxing == zhiWuxing):
            if (not ganWuxing in wuxingMap) | (wuxingMap.get(ganWuxing,{}).get('status',1) != 1):
                item['status'] = 1
                item['year'] = year   
                wuxingMap[ganWuxing] = item   
        #干生支
        elif (ten_deities[y[0]]["生"] == zhiWuxing):
            if not zhiWuxing in wuxingMap:
                item['status'] = 2
                item['year'] = year 
                wuxingMap[zhiWuxing] = item
        #支生干
        elif (ten_deities[y[0]]["生我"] == zhiWuxing):
            if not ganWuxing in wuxingMap:
                item['status'] = 3
                item['year'] = year 
                wuxingMap[ganWuxing] = item
        year = year-1
    return wuxingMap

def get_wuxing_by_selectyear(selectyear):
    jiazhi_map = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥",
            "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未", "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
            "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯", "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥",
            "壬子", "癸丑", "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"]
    zhi_map = {"子":"水",
           "丑":"土",
           "寅":"木",
           "卯":"木",
           "辰":"土",
           "巳":"火",
           "午":"火",
           "未":"土",
           "申":"金",
           "酉":"金",
           "戌":"土",
           "亥":"水"}
    nowyear = datetime.date.today().year 
    if(selectyear>nowyear):
        return None
    selectIdx = (selectyear - 1204) % 60
    selectZhu = jiazhi_map[selectIdx]
    selectGanWuxing = gan5[selectZhu[0]]
    selectZhiWuxing = zhi_map[selectZhu[1]]
    selectWuxing = selectGanWuxing
    if (ten_deities[selectZhu[0]]["生"] == selectZhiWuxing):
        selectWuxing = selectZhiWuxing
    for syear in range(nowyear,2200):
        #1204年是甲子年，每隔六十年一个甲子
        idx = (syear - 1204) % 60
        y = jiazhi_map[idx]
        ganWuxing = gan5[y[0]]
        zhiWuxing = zhi_map[y[1]]
        if(ganWuxing == zhiWuxing and ganWuxing == selectWuxing):
            return {"year":syear,"wuxing":ganWuxing}

def get_wuxing_ganzhi(wuxing): 
    return wuhangs.get(wuxing)

def get_dianpan_divination(year,month,day,hour,sex):
    day_shens = { 
        '将星':{"子":"子", "丑":"酉", "寅":"午", "卯":"卯", "辰":"子", "巳":"酉", 
                "午":"午", "未":"卯", "申":"子", "酉":"酉", "戌":"午", "亥":"卯"},      
        '华盖':{"子":"辰", "丑":"丑", "寅":"戌", "卯":"未", "辰":"辰", "巳":"丑", 
                "午":"戌", "未":"未", "申":"辰", "酉":"丑", "戌":"戌", "亥":"未"}, 
        '驿马': {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", 
                "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"},
        '劫煞': {"子":"巳", "丑":"寅", "寅":"亥", "卯":"申", "辰":"巳", "巳":"寅", 
            "午":"亥", "未":"申", "申":"巳", "酉":"寅", "戌":"亥", "亥":"申"},
        '亡神': {"子":"亥", "丑":"申", "寅":"巳", "卯":"寅", "辰":"亥", "巳":"申", 
                "午":"巳", "未":"寅", "申":"亥", "酉":"申", "戌":"巳", "亥":"寅"},    
        '桃花': {"子":"酉", "丑":"午", "寅":"卯", "卯":"子", "辰":"酉", "巳":"午", 
                "午":"卯", "未":"子", "申":"酉", "酉":"午", "戌":"卯", "亥":"子"},        
    }
    Gans = collections.namedtuple("Gans", "year month day time")
    Zhis = collections.namedtuple("Zhis", "year month day time")

    day = sxtwl.fromSolar(
        int(year), int(month), int(day))

    gz = day.getHourGZ(hour)
    yTG = day.getYearGZ()
    mTG = day.getMonthGZ()
    dTG  = day.getDayGZ()

    #　计算甲干相合    
    gans = Gans(year=Gan[yTG.tg], month=Gan[mTG.tg], 
                day=Gan[dTG.tg], time=Gan[gz.tg])
    zhis = Zhis(year=Zhi[yTG.dz], month=Zhi[mTG.dz], 
                day=Zhi[dTG.dz], time=Zhi[gz.dz])

    me = gans.day
    zhus = [item for item in zip(gans, zhis)]

    gan_shens = []
    for seq, item in enumerate(gans):    
        if seq == 2:
            gan_shens.append('--')
        else:
            gan_shens.append(ten_deities[me][item])
    #print(gan_shens)

    zhi_shens = [] # 地支的主气神
    for item in zhis:
        d = zhi5[item]
        zhi_shens.append(ten_deities[me][max(d, key=d.get)])
    #print(zhi_shens)
    shens = gan_shens + zhi_shens

    zhi_shens2 = [] # 地支的所有神，包含余气和尾气
    zhi_shen3 = []
    for item in zhis:
        d = zhi5[item]
        tmp = ''
        for item2 in d:
            zhi_shens2.append(ten_deities[me][item2])
            tmp += ten_deities[me][item2]
        zhi_shen3.append(tmp)
    shens2 = gan_shens + zhi_shens2
        
    shen_zhus = list(zip(gan_shens, zhi_shens))  
    dianpan_analysis=''
    # 比肩分析
    if '比' in gan_shens:
        #print("比：同性相斥。讨厌自己。老是想之前有没有搞错。没有持久性，最多跟你三五年。 散财，月上比肩，做事没有定性，不看重钱，感情不持久。不怀疑人家，人心很好。善意好心惹麻烦。年上问题不大。"
        # print("比如果地支刑，幼年艰苦，白手自立长、兄弟不合、也可能与妻子分居。地支冲：手足不和。女命忌讳比劫和合官杀，多为任性引发困难之事。")
        
        if gan_shens[0] == '比' and gan_shens[1] == '比':
            if(sex == 0):
                dianpan_analysis=dianpan_analysis+"比肩年月天干并现：不是老大，出身平常。仪容端庄，有自己的思想；不重视钱财,话多不能守秘。30岁以前是非小人不断。"
            else:
                dianpan_analysis=dianpan_analysis+"比肩年月天干并现：不是老大，出身平常。有自己的思想,不重视钱财,话多不能守秘。30岁以前是非小人不断。"
        if gan_shens[1] == '比' and '比' in zhi_shen3[1]:
            dianpan_analysis=dianpan_analysis+"月柱干支比肩：感情丰富。30岁以前钱不够花。"
            
        if gan_shens[0] == '比':
            dianpan_analysis=dianpan_analysis+"上面有哥或姐，出身一般。"
                    
        # 比肩过多
        if shens2.count('比') > 2 and '比' in zhi_shens:
            #dianpan_analysis=dianpan_analysis+shens2, zhi_shens2
            if(sex == 0):
                dianpan_analysis=dianpan_analysis+'----比肩过多：爱子女超过丈夫；轻易否定丈夫。换一种说法：有理想、自信、贪财、不惧内。'
                dianpan_analysis=dianpan_analysis+'你有帮夫运，多协助他的事业，多提意见，偶尔有争执，问题也不大。'
                dianpan_analysis=dianpan_analysis+'善意多言，引无畏之争；难以保守秘密，不适合多言；易犯无事忙的自我表现；不好意思拒绝他人;累积情绪而突然放弃。'
                dianpan_analysis=dianpan_analysis+"感情啰嗦对人警惕性低，乐天知命。"
                dianpan_analysis=dianpan_analysis+"天干有比，劳累命：事必躬亲。情感过程多有波折。除非有官杀制服。"
            else:
                dianpan_analysis=dianpan_analysis+'善意多言，引无畏之争；难以保守秘密，不适合多言；易犯无事忙的自我表现；不好意思拒绝他人;累积情绪而突然放弃。'
                dianpan_analysis=dianpan_analysis+"兄弟之间缺乏帮助。夫妻有时不太和谐。好友知交相处不会很久。"
                dianpan_analysis=dianpan_analysis+"天干有比，劳累命：事必躬亲。情感过程多有波折。除非有官杀制服。"
            
            
            if (not '官' in shens) and  (not '杀' in shens):
                dianpan_analysis=dianpan_analysis+"比肩多，四柱无正官七杀，性情急躁。"           
            if gan_shens.count('比') > 1:
                dianpan_analysis=dianpan_analysis+"天干2比肩：难以保守秘密,容易有言辞是非。" 
                
            if zhi_shens[2] == '比' and sex == 0:
                dianpan_analysis=dianpan_analysis+"女坐比:夫妻互恨。" 
                
            if '劫' in gan_shens and sex == 0:
                dianpan_analysis=dianpan_analysis+"天干比劫并立，女命感情丰富，多遇争夫。"   
                
            if gan_shens[0] == '比':
                dianpan_analysis=dianpan_analysis+"年干为比，不是长子，父母缘较薄，晚婚。" 
                
            if gan_shens[1] == '比':
                if zhi_shens[1] == '食':
                    dianpan_analysis=dianpan_analysis+"月柱比坐食，易得贵人相助。"
                if zhi_shens[1] == '伤':
                    dianpan_analysis=dianpan_analysis+"月柱比坐伤，一生只有小财气，难富贵。"   
                if zhi_shens[1] == '比':
                    dianpan_analysis=dianpan_analysis+"月柱比坐比，单亲家庭，一婚不能到头。地支三合或三会比，天干2比也如此。"
                if zhi_shens[1] == '财' and sex != 0:
                    dianpan_analysis=dianpan_analysis+"月柱比坐财，不利妻，也主父母身体不佳。因亲友、人情等招财物的无谓损失。"     
                if zhi_shens[1] == '杀':
                    dianpan_analysis=dianpan_analysis+"月柱比坐杀，稳重。"                  
            
            
            for seq, gan_ in enumerate(gan_shens):
                if gan_ != '比':
                    continue
                if zhis[seq] in  empties[zhus[2]]:  
                    if(sex == 0):
                        dianpan_analysis=dianpan_analysis+"比肩坐空亡，不利父亲与妻。年不利父，月不利父和妻，在时则没有关系。"
                    else:
                        dianpan_analysis=dianpan_analysis+"月柱30岁前结婚夫妻缘分偏薄。"
                if zhi_shens[seq] == '比':
                    dianpan_analysis=dianpan_analysis+"比坐比-平吉：与官杀对立，无主权。养子：克偏财，泄正印。吉：为朋友尽力；凶：受兄弟朋友拖累。父缘分薄，自我孤僻，多迟婚。"
                if zhi_shens[seq] == '劫':
                    if(sex == 0):
                       dianpan_analysis=dianpan_analysis+"父亲先亡。女比肩坐劫:夫妻互恨。还有刑冲，女恐有不测之灾：比如车祸、开刀和意外等。"    
                    else:
                        dianpan_analysis=dianpan_analysis+"比坐劫-大凶：为忌亲友受损，合作事业中途解散，与妻子不合。如年月3见比，父缘薄或已死别。"                    
                if ten_deities[gans[seq]][zhis[seq]] == '绝' and seq < 2:
                        dianpan_analysis=dianpan_analysis+"比肩坐绝，兄弟不多，或者很难谋面。戊和壬的准确率偏低些。"  
                if zhi_shens[seq] == '财':
                    dianpan_analysis=dianpan_analysis+"比肩坐财：因亲人、人情等原因引起无谓损失。" 
                if zhi_shens[seq] == '杀':
                     dianpan_analysis=dianpan_analysis+"比肩坐财:稳重。" 
                if zhi_shens[seq] == '枭':
                     dianpan_analysis=dianpan_analysis+"比肩坐偏印：三五年发达，后面守成。" 
                if zhi_shens[seq] == '劫' and Gan.index(me) % 2 == 0:
                     dianpan_analysis=dianpan_analysis+"比肩坐阳刃：在年不利父，在其他有刀伤、车祸、意外灾害。"                       
    if zhi_shens[2] == '比':
        dianpan_analysis=dianpan_analysis+"日支比：对家务事有家长式领导；钱来得不容易且有时有小损财。自我，如有刑冲，不喜归家！"
    if zhi_shens[3] == '比':
        dianpan_analysis=dianpan_analysis+"时支比：子女为人公正倔强、行动力强，能得资产。"   
    if '比' in (gan_shens[1],zhi_shens[1]):
        dianpan_analysis=dianpan_analysis+"月柱比：三十岁以前难有成就。冒进、不稳定。女友不持久、大男子主义。"
    if '比' in (gan_shens[3],zhi_shens[3]):
        dianpan_analysis=dianpan_analysis+"时柱比：与亲人意见不合。"

    if shens.count('比') + shens.count('劫') > 1 and sex != 0:
        dianpan_analysis=dianpan_analysis+"比劫大于2，感情阻碍、事业起伏不定。"
        
    # 劫财分析
    if '劫' in gan_shens:
        dianpan_analysis=dianpan_analysis+"劫财扶助，无微不至。劫财多者谦虚之中带有傲气。凡事先理情，而后情理。先细节后全局。性刚强、精明干练。"
        dianpan_analysis=dianpan_analysis+"务实，不喜欢抽象性的空谈。不容易认错，比较倔。有理想，但是不够灵活。不怕闲言闲语干扰。不顾及别人面子。"
        dianpan_analysis=dianpan_analysis+"合作事业有始无终。太重细节。做小领导还是可以的。有志向，自信。杀或食透干可解所有负面。"
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"命忌讳比劫和合官杀，多为任性引发困难之事。"

        if gan_shens[0] == '劫' and gan_shens[1] == '劫':
            dianpan_analysis=dianpan_analysis+"劫年月天干并现：喜怒形于色，30岁以前大失败一次。过度自信，精明反被精明误。"

        if gan_shens[1] == '劫' and '劫' in zhi_shen3[1]:
            dianpan_analysis=dianpan_analysis+"月柱干支劫：与父亲无缘，30岁以前任性，早婚防分手，自我精神压力极其重。"
        
            
        if shens2.count('劫') > 2:
            dianpan_analysis=dianpan_analysis+'----劫财过多, 婚姻不好'
            if (not '官' in shens) and  (not '杀' in shens):
                dianpan_analysis=dianpan_analysis+"比肩多，四柱无正官七杀，性情急躁。"  
        if zhis[2] == '劫':
            dianpan_analysis=dianpan_analysis+"日坐劫财，透天干。在年父早亡，在月夫妻关系不好。比如财产互相防范；鄙视对方；自己决定，哪怕对方不同意；老夫少妻；身世有差距；斤斤计较；敢爱敢恨的后遗症，以上多针对女。男的一般有双妻。天干有杀或食可解。"
                
    if zhus[2] in (('壬','子'),('丙','午'), ('戊','午')):
        dianpan_analysis=dianpan_analysis+"日主专位劫财，壬子和丙午，晚婚。不透天干，一般是眼光高、独立性强。对配偶不利，互相轻视；若刑冲，做事立场不明遭嫉妒，但不会有大灾。"
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"婚后通常还有自己的事业,能办事。"
    if ('劫','伤') in shen_zhus or ('伤','劫',) in shen_zhus:
        dianpan_analysis=dianpan_analysis+"同一柱中，劫财、阳刃伤官都有，外表华美，富屋穷人，婚姻不稳定，富而不久；年柱不利家长，月柱不利婚姻，时柱不利子女。伤官的狂妄。"     

    if gan_shens[0] == '劫':
        dianpan_analysis=dianpan_analysis+"年干劫财：家运不济。克父，如果坐劫财，通常少年失父；反之要看地支劫财根在哪一柱子。"
            
    if '劫' in (gan_shens[1],zhi_shens[1]):
        dianpan_analysis=dianpan_analysis+"月柱劫：容易孤注一掷，30岁以前难稳定。"
        if(sex != 0):
            dianpan_analysis=dianpan_analysis+"早婚不利。"
    if '劫' in (gan_shens[3],zhi_shens[3]):
        dianpan_analysis=dianpan_analysis+"时柱劫：只要不是去经济大权还好。"  
    if zhi_shens[2] == '劫' and sex != 0:
        dianpan_analysis=dianpan_analysis+"日支劫：男的克妻，一说是家庭有纠纷，对外尚无重大损失。如再透月或时天干，有严重内忧外患。"
        
    if '劫' in shens2 and  '比' in zhi_shens and '印' in shens2 and Gan.index(me) % 2 == 1:
        dianpan_analysis=dianpan_analysis+"阴干比劫印齐全，单身，可入道！"
        
    if zhi_shens[0] == '劫' and Gan.index(me) % 2 == 0: 
        dianpan_analysis=dianpan_analysis+"年阳刃：得不到长辈福；不知足、施恩反怨。"
    if zhi_shens[3] == '劫' and Gan.index(me) % 2 == 0 and sex != 0: 
        dianpan_analysis=dianpan_analysis+"时阳刃：与妻子不和，晚无结果，四柱再有比刃，有疾病与外灾。"
    if zhi_shens[1] == '劫' and Gan.index(me) % 2 == 0:
        dianpan_analysis=dianpan_analysis+"阳刃格：喜七杀或三四个官。" 
        if me in ('庚', '壬','戊'):
            dianpan_analysis=dianpan_analysis+"阳刃'庚', '壬','午'忌讳财运，逢冲多祸。庚逢辛酉凶，丁酉吉，庚辰和丁酉六合不凶。壬逢壬子凶，戊子吉；壬午和戊子换禄不凶。"
        else:
            dianpan_analysis=dianpan_analysis+"阳刃'甲', '丙',忌讳杀运，逢冲多还好。甲：乙卯凶，辛卯吉；甲申与丁卯暗合吉。丙：丙午凶，壬午吉。丙子和壬午换禄不凶。"
        
    
    # 偏印分析    
    if '枭' in gan_shens:
        dianpan_analysis=dianpan_analysis+"----偏印在天干如成格：偏印在前，偏财(财次之)在后，有天月德就是佳命(偏印格在日时，不在月透天干也麻烦)。忌讳倒食，但是坐绝没有这能力。"
        dianpan_analysis=dianpan_analysis+"经典认为：偏印不能扶身，要身旺；偏印见官杀未必是福；喜伤官，喜财；忌日主无根；"
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"顾兄弟姐妹。"
        else:
            dianpan_analysis=dianpan_analysis+"男六亲似冰。"
        dianpan_analysis=dianpan_analysis+"偏印格干支有冲、合、刑，地支是偏印的绝位也不佳。"
        
        #dianpan_analysis=dianpan_analysis+zhi_shen3
        if (gan_shens[1] == '枭' and '枭' in zhi_shen3[1]):        
            dianpan_analysis=dianpan_analysis+"枭月重叠：福薄慧多，青年孤独，有文艺宗教倾向。"
            
        if '枭' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"生财、配印；最喜偏财同时成格，偏印在前，偏财在后。最忌讳日时坐实比劫刃。"
        if shens2.count('枭') > 2:
            dianpan_analysis=dianpan_analysis+"偏印过多，性格孤僻，表达太含蓄，要别人猜，说话有时带刺。偏悲观。有偏财和天月德贵人可以改善。有艺术天赋。做事大多有始无终。"
            dianpan_analysis=dianpan_analysis+"对兄弟姐妹不错。"
            if(sex == 0):
                dianpan_analysis=dianpan_analysis+"偏印多，子女不多。"
            else:
                dianpan_analysis=dianpan_analysis+"因才干受子女尊敬。"           
            if '伤' in gan_shens and sex == 0: 
                dianpan_analysis=dianpan_analysis+"女命偏印多，又与伤官同透，夫离子散。有偏财和天月德贵人可以改善。"
            
        if gan_shens.count('枭') > 1:
            dianpan_analysis=dianpan_analysis+"天干两个偏印：迟婚，独身等，婚姻不好。三偏印，家族人口少，亲属不多。"
        if shen_zhus[0] == ('枭', '枭'):
            dianpan_analysis=dianpan_analysis+"偏印在年，干支俱透，不利于长辈。偏母当令，正母无权，可能是领养，庶出、同父异母等。"
            
        
    for seq, zhi_ in enumerate(zhi_shens):
        if zhi_ != '枭' and gan_shens[seq] != '枭':
            continue   
        if ten_deities[gans[seq]][zhis[seq]] == '绝':
            dianpan_analysis=dianpan_analysis+"偏印坐绝，或者天干坐偏印为绝，难以得志。费力不讨好。"      

        
    if zhi_shens[3]  == '枭' and gan_shens[0]  == '枭':
        dianpan_analysis=dianpan_analysis+"偏印透年干-时支，一直受家里影响。"
        
    if '枭' in (gan_shens[0],zhi_shens[0]):
        dianpan_analysis=dianpan_analysis+"偏印在年：少有富贵家庭；有宗教素养，不喜享乐，第六感强。"
    if '枭' in (gan_shens[1],zhi_shens[1]):
        dianpan_analysis=dianpan_analysis+"偏印在月：有慧少福，能舍己为人。"
        if zhi_shens[1]  == '枭' and len(zhi5[zhis[1]]) == 1:
            dianpan_analysis=dianpan_analysis+"偏印专位在月支：比较适合音乐，艺术，宗教等。"
            if gan_shens[1] == '枭':
                dianpan_analysis=dianpan_analysis+"干支偏印月柱，专位入格，有慧福浅。"   
    if '枭' in (gan_shens[3],zhi_shens[3]):
        dianpan_analysis=dianpan_analysis+""   
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"偏印在时：与后代分居。"
        else:
            dianpan_analysis=dianpan_analysis+"偏印在时：50以前奠定基础，晚年享清福。" 
    if zhi_shens[2] == '枭':
        dianpan_analysis=dianpan_analysis+"偏印在日支：家庭生活沉闷"
        if zhus[2] in (('丁','卯'),('癸','酉')):
            dianpan_analysis=dianpan_analysis+"日专坐偏印：丁卯和癸酉。婚姻不顺。又刑冲，因性格而起争端。"   
        
    # 印分析    
    if '印' in gan_shens:
        if '印' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"成格喜官杀、身弱、忌财克印。合印留财，见利忘义.透财官杀通关或印生比劫；合冲印若无他格或调候破格。日主强凶，禄刃一支可以食伤泄。"
            
        if (gan_shens[1] == '印' and '印' in zhi_shen3[1]) and sex == 0:        
            dianpan_analysis=dianpan_analysis+"印月重叠：女迟婚，月阳刃者离寡，能独立谋生，有修养的才女。"
                
        if shens2.count('印') > 2:
            dianpan_analysis=dianpan_analysis+"正印多的：聪明有谋略，比较含蓄，不害人，识时务。正印不怕日主死绝，反而怕太强。日主强，正印多，孤寂，不善理财。"
        for seq, gan_ in enumerate(gan_shens):
            if gan_ != '印':
                continue   
            if ten_deities[gans[seq]][zhis[seq]] in ('绝', '死'):
                if seq <3:
                    dianpan_analysis=dianpan_analysis+"正印坐死绝，或天干正印地支有冲刑，不利母亲。时柱不算。"  
            if zhi_shens[seq] == '财' and sex != 0:
                dianpan_analysis=dianpan_analysis+"男正印坐正财，夫妻不好。月柱正印坐正财专位，必离婚。在时柱，50多岁才有正常婚姻。"
            if zhi_shens[seq] == '印':
                dianpan_analysis=dianpan_analysis+"正印坐正印，专位，过于自信。务实，拿得起放得下。"         
                if(sex == 0):
                    dianpan_analysis=dianpan_analysis+"大多晚婚。母长寿；女子息迟，头胎恐流产。四柱没有官杀，没有良缘。"
                else:
                    dianpan_analysis=dianpan_analysis+"搞艺术比较好，经商则孤僻，不聚财。" 
            if zhi_shens[seq] == '枭' and len(zhi5[zhis[seq]]) == 1:
                dianpan_analysis=dianpan_analysis+"正印坐偏印专位：有多种职业;家庭不吉：亲人有疾或者特别嗜好。子息迟;财务双关。明一套，暗一套。女的双重性格。"  
                
            if zhi_shens[seq] == '伤':
                dianpan_analysis=dianpan_analysis+"适合清高的职业。不适合追逐名利，女的婚姻不好。"   
                
            if zhi_shens[seq] == '劫' and me in ('甲','庚','壬'):
                dianpan_analysis=dianpan_analysis+"正印坐阳刃，身心多伤，心疲力竭，偶有因公殉职。主要指月柱。工作看得比较重要。"   
                            
                
        if '杀' in gan_shens and '劫' in zhi_shens and me in ('甲','庚','壬'):
            dianpan_analysis=dianpan_analysis+""
            if(sex == 0):
                dianpan_analysis=dianpan_analysis+"正印、七杀、阳刃全：宗教人，否则独身，清高，身体恐有隐疾，性格狭隘缺耐心。"
            else:
                dianpan_analysis=dianpan_analysis+"正印、七杀、阳刃全：小疾多，婚姻不佳，恐非婚生子女。" 
                
        if '官' in gan_shens or '杀' in gan_shens: 
            dianpan_analysis=dianpan_analysis+"身弱官杀和印都透天干，格局佳。"
        else:
            dianpan_analysis=dianpan_analysis+"单独正印主秀气、艺术、文才。性格保守"
        if '官' in gan_shens or '杀' in gan_shens or '比' in gan_shens: 
            dianpan_analysis=dianpan_analysis+"正印多者，有比肩在天干，不怕财。有官杀在天干也不怕。财不强也没关系。"
        else:
            dianpan_analysis=dianpan_analysis+"正印怕财。"
        if '财' in gan_shens:     
            dianpan_analysis=dianpan_analysis+"印和财都透天干，都有根，最好先财后印，一生吉祥。先印后财，能力不错，但多为他人奔波。"
            
    if zhi_shens[3]  == '印' and len(zhi5[zhis[3]]) == 1:
        dianpan_analysis=dianpan_analysis+"时支专位正印:"
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"子女各居一方,亲情淡薄。"
        else:
            dianpan_analysis=dianpan_analysis+"忙碌到老。" 
        
    if gan_shens[3]  == '印' and '印' in zhi_shen3[3]:
        dianpan_analysis=dianpan_analysis+"时柱正印格，不论男女，老年辛苦，女的到死都要控制家产，子女无缘。"
        
    if gan_shens.count('印') + gan_shens.count('枭') > 1:
        dianpan_analysis=dianpan_analysis+"印枭在年干月干，性格迂腐，故作清高。"
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"女子息迟，婚姻有阻碍。"
        else:
            dianpan_analysis=dianpan_analysis+"印枭在时干，不利母子，性格不和谐。" 
    yin = ten_deities[me].inverse['印']
    yin_lu = ten_deities[yin].inverse['建']
    xiao = ten_deities[me].inverse['枭']
    xiao_lu = ten_deities[xiao].inverse['建']

    if zhis[1] in (yin_lu, xiao_lu) :
        dianpan_analysis=dianpan_analysis+"印或枭在月支，有压制丈夫的心态。"
        
    if zhis[3] in (yin_lu, xiao_lu) :
        dianpan_analysis=dianpan_analysis+"印或枭在时支，夫灾子寡。"

            
    # 偏财分析    
    if '才' in gan_shens:
        dianpan_analysis=dianpan_analysis+"偏财明现天干，不论是否有根:财富外人可见;实际财力不及外观一半。没钱别人都不相信;协助他人常超过自己的能力。"
        dianpan_analysis=dianpan_analysis+"偏财出天干，又与天月德贵人同一天干者。在年月有声明远扬的父亲，月时有聪慧的红颜知己。喜奉承。"
        dianpan_analysis=dianpan_analysis+"偏财透天干，四柱没有刑冲，长寿。时柱表示中年以后有自己的事业，善于理财。"
        if '才' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"比劫用食伤通关或官杀制；身弱有比劫仍然用食伤通关。如果时柱坐实比劫，晚年破产。" 
        dianpan_analysis=dianpan_analysis+"偏财透天干，讲究原则，不拘小节。喜奉承，善于享受。"
        
        if '比' in gan_shens or '劫' in gan_shens and gan_shens[3] == '才':
            dianpan_analysis=dianpan_analysis+"年月比劫，时干透出偏财。祖业凋零，再白手起家。有刑冲为千金散尽还复来。"
        if '杀' in gan_shens and '杀' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"偏财和七杀并位，地支又有根，父子外合心不合。因为偏财生杀攻身。偏财七杀在日时，则为有难伺候的女朋友。"
            
        if zhi_shens[0]  == '才':
            dianpan_analysis=dianpan_analysis+"偏财根透年柱，家世良好，且能承受祖业。"
            
        for seq, gan_ in enumerate(gan_shens):
            if gan_ != '才':
                pass
            if zhi_shens[seq] == '劫' :
                dianpan_analysis=dianpan_analysis+"偏财坐阳刃劫财,可做父缘薄，也可幼年家贫。也可以父先亡，要参考第一大运。"
                if len(zhi5[zhis[seq]]) == 1:
                    dianpan_analysis=dianpan_analysis+"偏财坐专位阳刃劫财,父亲去他乡。"
            if get_empty(zhus[2],zhis[seq]) == '空':
                dianpan_analysis=dianpan_analysis+"偏财坐空亡，财官难求。"                
                    
    if shens2.count('才') > 2:
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"乐善好施，有团队精神，女命偏财，听父亲的话。时柱偏财女，善于理财，中年以后有事业。"
        else:
            dianpan_analysis=dianpan_analysis+"偏财多的人慷慨，得失看淡。花钱一般不会后悔。偏乐观，甚至是浮夸。生活习惯颠倒。适应能力强。有团队精神。得女性欢心。小事很少失信。"
    if (zhi_shens[2]  == '才' and len(zhi5[zhis[2]]) == 1) or (zhi_shens[3]  == '才' and len(zhi5[zhis[3]]) == 1):
        dianpan_analysis=dianpan_analysis+"日时地支坐专位偏财。不见刑冲，时干不是比劫，大运也没有比劫刑冲，晚年发达。"
        
        
        
    # 财分析    

    if (gan_shens[0] in ('财', '才')  and gan_shens[1]  in ('财', '才')) or (gan_shens[1] in ('财', '才') and ('财' in zhi_shen3[1] or '才' in zhi_shen3[1])):
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"财或偏财月重叠：职业妇女，有理财办事能力。因自己理财能力而影响婚姻。一财得所，红颜失配。"
        else:
            dianpan_analysis=dianpan_analysis+"财或偏财月重叠：双妻。"
        dianpan_analysis=dianpan_analysis+"比肩坐财:稳重。"   
        if zhi_shens[seq] == '枭':
            dianpan_analysis=dianpan_analysis+"比肩坐偏印：三五年发达，后面守成。"   
        if zhi_shens[seq] == '劫' and Gan.index(me) % 2 == 0:
            dianpan_analysis=dianpan_analysis+"比肩坐阳刃：在年不利父，在其他有刀伤、车祸、意外灾害。"              


    if '财' in gan_shens: 
        if(sex != 0):
            dianpan_analysis=dianpan_analysis+"男日主合财星，夫妻恩爱。如果争合或天干有劫财，双妻。"
        if '财' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"比劫用食伤通关或官杀制；身弱有比劫仍然用食伤通关。"
            
        if '官' in gan_shens:
            dianpan_analysis=dianpan_analysis+"正官正财并行透出，(身强)出身书香门第。"
        if ('官' in gan_shens or '杀' in gan_shens):
            dianpan_analysis=dianpan_analysis+"官或杀与财并行透出，女压夫，财生官杀，老公压力大。"
        if gan_shens[0] == '财':
            dianpan_analysis=dianpan_analysis+"年干正财若为喜，富裕家庭，但不利母亲。"
        # if '财' in zhi_shens:
        #     if '官' in gan_shens or '杀' in gan_shens:
        #         dianpan_analysis=dianpan_analysis+"男财旺透官杀，女厌夫。"
        if gan_shens.count('财') > 1:
            dianpan_analysis=dianpan_analysis+"天干两正财，财源多，大多做好几种生意，好赶潮流，人云亦云。有时会做自己外行的生意。"
            if '财' not in zhi_shens2:
                dianpan_analysis=dianpan_analysis+"正财多而无根虚而不踏实。重财不富。"
                
    for seq, gan_ in enumerate(gan_shens):
        if gan_ != '财' and zhis[seq] != '财':
            continue   
        if zhis[seq] in day_shens['驿马'][zhis.day] and seq != 2 and sex == 0:
            dianpan_analysis=dianpan_analysis+"女柱有财+驿马，动力持家。"
        if zhis[seq] in day_shens['桃花'][zhis.day] and seq != 2 and sex == 0:
            dianpan_analysis=dianpan_analysis+"女柱有财+桃花，不吉利。"
        if zhis[seq] in empties[zhus[2]]:
            dianpan_analysis=dianpan_analysis+"财坐空亡，不持久。"
        if ten_deities[gans[seq]][zhis[seq]] in ('绝', '墓') and sex != 0:
            dianpan_analysis=dianpan_analysis+"男财坐绝或墓，不利婚姻。"
                
    if shens2.count('财') > 2:
        dianpan_analysis=dianpan_analysis+"正财多者，为人端正，有信用，简朴稳重。"
        if '财' in zhi_shens2 and (me not in zhi_shens2):
            dianpan_analysis=dianpan_analysis+"正财多而有根，日主不在生旺库，身弱惧内。"
            
    if zhi_shens[1] == '财' and sex == 0:
        dianpan_analysis=dianpan_analysis+"女命月支正财，有务实的婚姻观。"
        
    if zhi_shens[1] == '财' and sex != 0:
        dianpan_analysis=dianpan_analysis+"月令正财，无冲刑，有贤内助，但是母亲与妻子不和。生活简朴，多为理财人士。"
    if zhi_shens[3] == '财' and len(zhi5[zhis[3]]) == 1:
        dianpan_analysis=dianpan_analysis+"时支正财，一般两个儿子。"
    if (zhus[2] in (('戊','子'),) or zhus[3] in (('戊','子'),)) and sex != 0:
        dianpan_analysis=dianpan_analysis+"日支专位为正财，得勤俭老婆。即戊子。日时专位支正财，又透正官，中年以后发达，独立富贵。"
        
    if zhus[2] in (('壬','午'),('癸','巳'),):
        dianpan_analysis=dianpan_analysis+"坐财官印，只要四柱没有刑冲，大吉！"
        
    # if zhus[2] in (('甲','戌'),('乙','亥'),):
    #     dianpan_analysis=dianpan_analysis+"女('甲','戌'),('乙','亥'） 晚婚 -- 不准！"
        
    if ('财' == gan_shens[3] or  '财' == zhi_shens[3]) and sex != 0:
        dianpan_analysis=dianpan_analysis+"未必准确：时柱有正财，口快心直，不喜拖泥带水，刑冲则浮躁。阳刃也不佳，反之有美妻佳子。"
    if (not '财' in shens2) and (not '才' in shens2):
        dianpan_analysis=dianpan_analysis+"四柱无财，即便逢财运，也是虚名虚利，男的晚婚。"
        
        
    shang = ten_deities[me].inverse['财']
    if ten_deities[shang].inverse['建'] in zhis and sex == 0:
        dianpan_analysis=dianpan_analysis+"女命一财得所，红颜失配。"
        
    # 官分析    
    if '官' in gan_shens:
        if '官' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"官若成格：忌伤；忌混杂。有伤用财通关或印制。混杂用合或者身官两停。日主弱则不可扶。"
            
            if '比' in gan_shens or '劫' in gan_shens:
                dianpan_analysis=dianpan_analysis+"官格透比或劫：故做清高或有洁癖的文人。"

            if '伤' in gan_shens:
                dianpan_analysis=dianpan_analysis+"官格透伤：表里不一。"
                
            if '财' in gan_shens or '才' in gan_shens:
                dianpan_analysis=dianpan_analysis+"官格透财：聚财。"
                
            if '印' in gan_shens:
                dianpan_analysis=dianpan_analysis+"官格透印：人品清雅。"
            
        if (gan_shens[0] == '官' and gan_shens[1] == '官') or (gan_shens[1] == '官' and '官' in zhi_shen3[1]) and sex != 0:
            dianpan_analysis=dianpan_analysis+"官月重叠：女易离婚，早婚不吉利。为人性格温和。"
                
        if gan_shens[3] == '官' and len(zhi5[zhis[3]]) == 1 and sex != 0:
            dianpan_analysis=dianpan_analysis+"官专位时坐地支，男有得力子息。"
        if gan_shens[0] == '官' :
            dianpan_analysis=dianpan_analysis+"年干为官，身强出身书香门第。"
            if gan_shens[3] == '官' and sex != 0:
                dianpan_analysis=dianpan_analysis+"男命年干，时干都为官，对后代和头胎不利。"
        if (not '财' in gan_shens) and (not '印' in gan_shens):
            dianpan_analysis=dianpan_analysis+"官独透天干成格，四柱无财或印，为老实人。"
        if '伤' in gan_shens:
            dianpan_analysis=dianpan_analysis+"正官伤官通根透，又无其他格局，失策。尤其是女命，异地分居居多，婚姻不美满。"
        if '杀' in gan_shens:
            dianpan_analysis=dianpan_analysis+"年月干杀和偏官，30以前婚姻不稳定。月时多为体弱多病。"
            
        if '印' in gan_shens and '印' in zhi_shens2 and '官' in zhi_shens2:
            dianpan_analysis=dianpan_analysis+"官印同根透，无刑冲合，吉。"
            if '财' in gan_shens and '财' in zhi_shens2:
                dianpan_analysis=dianpan_analysis+"财官印同根透，无刑冲合，吉。"
            
        if (gan_shens[1] == '官' in ten_deities[me][zhis[1]] in ('绝', '墓')) and sex == 0:
            dianpan_analysis=dianpan_analysis+"官在月坐墓绝，不是特殊婚姻就是迟婚。如果与天月德同柱，依然不错。丈夫在库中：1，老夫少妻；2，不为外人所知的亲密感情；3，特殊又合法的婚姻。"
        if zhi_shens[1] == '官' and gan_shens[1] == '官':
            dianpan_analysis=dianpan_analysis+"月柱正官坐正官，婚变。月柱不宜通。坐禄的。"
        if zhi_shens[1] == '官' and '伤' in shens:
            dianpan_analysis=dianpan_analysis+"月支正官，又成伤官格，难做真正夫妻。有实，无名。"
        
        for seq, gan_ in enumerate(gan_shens):
            if gan_ != '官':
                continue   
            if zhi_shens[seq] in ('劫','比') :
                dianpan_analysis=dianpan_analysis+"天干正官，地支比肩或劫财，亲友之间不适合合作，但是他适合经营烂摊子。"
            if zhi_shens[seq] == '杀' :
                if(sex == 0):
                    dianpan_analysis=dianpan_analysis+"正官坐七杀，女命婚姻不佳。月柱尤其麻烦，二度有感情纠纷。年不算，时从轻。"
                else:
                    dianpan_analysis=dianpan_analysis+"正官坐七杀，男命恐有诉讼之灾。月柱尤其麻烦，二度有感情纠纷。年不算，时从轻。"
            if zhi_shens[seq] == '劫' and Gan.index(me) % 2 == 0:
                dianpan_analysis=dianpan_analysis+"要杀才能制服阳刃，有力不从心之事情。"
            if zhi_shens[seq] == '印':
                dianpan_analysis=dianpan_analysis+"官坐印，无刑冲合，吉"
            
                
    if shens2.count('官') > 2 and '官' in gan_shens and '官' in zhi_shens2:
        dianpan_analysis=dianpan_analysis+"正官多者，虚名。为人性格温和，比较实在。做七杀看"
    if zhi_shens[2]  == '官' and len(zhi5[zhis[2]]) == 1 and sex == 0:
        dianpan_analysis=dianpan_analysis+"日坐正官，淑女。"
        
    if gan_shens.count('官') > 2 and sex == 0:
        dianpan_analysis=dianpan_analysis+"天干2官，女下有弟妹要照顾，一生为情所困。"
        
        
        
    # 杀分析    
    if '杀' in gan_shens:
        dianpan_analysis=dianpan_analysis+"七杀是非多。但是对男人有时是贵格。七杀坐刑或冲，夫妻不和。可杀生印或食制印、身杀两停、阳刃驾杀。"
        if '杀' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"杀格：喜食神制，要食在前，杀在后。阳刃驾杀：杀在前，刃在后。身杀两停：比如甲寅日庚申月。杀印相生，忌食同成格。"
            
            if '比' in gan_shens or '劫' in gan_shens:
                dianpan_analysis=dianpan_analysis+"杀格透比或劫：性急但还有分寸。"

            if '杀' in gan_shens:
                dianpan_analysis=dianpan_analysis+"杀格透官：精明琐屑，不怕脏。"
                
            if '食' in gan_shens or '伤' in gan_shens:
                dianpan_analysis=dianpan_analysis+"杀格透食伤：外表宁静，内心刚毅。"
                
            if '印' in gan_shens:
                dianpan_analysis=dianpan_analysis+"杀格透印：圆润、精明干练。"
            
        if (gan_shens[0] == '杀' and gan_shens[1] == '杀') :
            dianpan_analysis=dianpan_analysis+"杀月干年干重叠：不是老大，出身平常，多灾，为人不稳重。"
            
        if (gan_shens[1] == '杀' and '杀' in zhi_shen3[1]):        
            dianpan_analysis=dianpan_analysis+"杀月重叠：女易离婚，其他格一生多病。"
            
        if gan_shens[0] == '杀':
            dianpan_analysis=dianpan_analysis+"年干七杀，早年不好。或家里穷或身体不好。"
            if gan_shens[1] == '杀':
                dianpan_analysis=dianpan_analysis+"年月天干七杀，家庭复杂。"
        if '官' in gan_shens:
            dianpan_analysis=dianpan_analysis+"官和杀同见天干不佳。"
        if gan_shens[1] == '杀' and zhi_shens[1] == '杀':
            dianpan_analysis=dianpan_analysis+"月柱都是七杀，克得太过。有福不会享。六亲福薄。时柱没关系。"
            if '杀' not in zhi_shens2 :
                dianpan_analysis=dianpan_analysis+"七杀年月浮现天干，性格好变，不容易定下来。30岁以前不行。"   
        if '杀' in zhi_shens and '劫' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"七杀地支有根时要有阳刃强为佳。杀身两停。"
        if gan_shens[1] == '杀' and gan_shens[3] == '杀':
            dianpan_analysis=dianpan_analysis+"月时天干为七杀：体弱多病"
        if gan_shens[0] == '杀' and gan_shens[3] == '杀':
            if(sex == 0):
                dianpan_analysis=dianpan_analysis+"七杀年干时干：女婚姻有阻碍。"
            else:
                dianpan_analysis=dianpan_analysis+"七杀年干时干：男头胎麻烦（概率）。"
        if gan_shens[3] == '杀':
            dianpan_analysis=dianpan_analysis+"七杀在时干，通月支：固执有毅力。"  
        if '印' in gan_shens:
            dianpan_analysis=dianpan_analysis+"身弱杀生印，不少是精明练达的商人。"
        if '财' in gan_shens or '才' in gan_shens:
            dianpan_analysis=dianpan_analysis+"财生杀，如果不是身弱有印，不佳。"
            for zhi_ in zhis: 
                if set((ten_deities[me].inverse['杀'], ten_deities[me].inverse['财'])) in set(zhi5[zhi_]):
                    dianpan_analysis=dianpan_analysis+"杀不喜与财同根透出，这样杀的力量太强。"


    for seq, gan_ in enumerate(gan_shens):
        if gan_ != '杀' and zhi_shens[seq] != '杀':
            continue   
        if gan_ == '杀' and '杀' in zhi_shen3[seq] and seq != 3:
            dianpan_analysis=dianpan_analysis+"七杀坐七杀，六亲福薄。"
        if get_empty(zhus[2],zhis[seq]) == '空' and sex == 0:
            dianpan_analysis=dianpan_analysis+"七杀坐空亡，女命夫缘薄。"
            
                
    if shens2.count('杀') > 2:
        dianpan_analysis=dianpan_analysis+"杀多者如果无制，性格刚强。打抱不平，不易听人劝。"
    if zhi_shens[2]  == '杀' and len(zhi5[zhis[2]]) == 1:
        dianpan_analysis=dianpan_analysis+"天元坐杀：乙酉，己卯，如无食神，阳刃，性急，聪明，对人不信任。如果七杀还透出月干无制，体弱多病，甚至夭折。如果在时干，晚年不好。"
        
    if zhus[2] in (('丁', '卯'), ('丁', '亥'), ('丁', '未')) and zhis.time == '子':
        dianpan_analysis=dianpan_analysis+"七杀坐桃花，如有刑冲，引感情引祸。忌讳午运。"
        
    if gan_shens.count('杀') > 2 :
        dianpan_analysis=dianpan_analysis+"天干2杀，不是老大、性格浮躁不持久。"

    shang = ten_deities[me].inverse['杀']
    if ten_deities[shang].inverse['建'] in zhis and sex == 0:
        dianpan_analysis=dianpan_analysis+"女地支有杀的禄：丈夫条件还可以。对外性格急，对丈夫还算顺从。"
        
    # 食分析    
    if '食' in gan_shens:
        if '食' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"食神成格的情况下，寿命比较好。食神和偏财格比较长寿。食神厚道，为人不慷慨。食神有口福。喜财忌偏印(只能偏财制)。"
            dianpan_analysis=dianpan_analysis+"食神无财一生衣食无忧，无大福。有印用比劫通关或财制。"
            
            
        if (gan_shens[0] == '食' and gan_shens[1] == '食') or (gan_shens[1] == '食' and '食' in zhi_shen3[1]):
            dianpan_analysis=dianpan_analysis+"食月重叠：生长安定环境，性格仁慈、无冲刑长寿。女早年得子。无冲刑偏印者是佳命。"


        if '枭' in gan_shens:
            if(sex != 0):
                dianpan_analysis=dianpan_analysis+"男的食神碰到偏印，身体不好。怕偏印，正印要好一点。四柱透出偏财可解。"
            if '劫' in gan_shens:
                dianpan_analysis=dianpan_analysis+"食神不宜与劫财、偏印齐出干。体弱多病。"
            if '杀' in gan_shens:
                dianpan_analysis=dianpan_analysis+"食神不宜与杀、偏印齐成格。体弱多病。"
        if '食' in zhi_shens and sex == 0:
            dianpan_analysis=dianpan_analysis+"食神天透地藏，女命阳日主适合社会性职业，阴日主适合上班族。"
        if (not '财' in gan_shens) and (not '才' in gan_shens):
            dianpan_analysis=dianpan_analysis+"食神多，要食伤生财才好，无财难发。"
        if '伤' in gan_shens:
            dianpan_analysis=dianpan_analysis+"食伤混杂：食神和伤官同透天干：志大才疏。"
        if '杀' in gan_shens:
            dianpan_analysis=dianpan_analysis+"食神制杀，杀不是主格，施舍后后悔。"



        for seq, gan_ in enumerate(gan_shens):
            if gan_ != '食':
                continue   
            if zhi_shens[seq] =='劫':
                dianpan_analysis=dianpan_analysis+"食神坐阳刃，辛劳。"
            
                
    if shens2.count('食') > 2:
        dianpan_analysis=dianpan_analysis+"食神四个及以上的为多，做伤官处理。食神多，要食伤生财才好，无财难发。"
        if '劫' in gan_shens or '比' in gan_shens:
            dianpan_analysis=dianpan_analysis+"食神带比劫，好施舍，乐于做社会服务。"
            
    if ('杀', '食') in shen_zhus or ( '食', '杀') in shen_zhus:
        dianpan_analysis=dianpan_analysis+"食神与七杀同一柱，易怒。食神制杀，最好食在前。有一定概率。"
        
    if (('枭', '食') in shen_zhus or ( '食', '枭') in shen_zhus) and sex == 0:
        dianpan_analysis=dianpan_analysis+"女命最怕食神偏印同一柱。不利后代。"
        
    if zhi_shens[2]  == '食' and len(zhi5[zhis[2]]) == 1:
        dianpan_analysis=dianpan_analysis+"日支食神专位容易发胖，有福。只有2日：癸卯，己酉。男命有有助之妻。"
        


    # 伤分析    
    if '伤' in gan_shens:
        dianpan_analysis=dianpan_analysis+"伤官有才华，但是清高。要生财，或者印制。"
        if '伤' in zhi_shens:
            dianpan_analysis=dianpan_analysis+"食神重成伤官，不适合伤官配印。金水、土金、木火命造更高。火土要调候，容易火炎土燥。伤官和七杀的局不适合月支为库。"
            dianpan_analysis=dianpan_analysis+"生财、配印。不考虑调候逆用比顺用好，调候更重要。生正财用偏印，生偏财用正印。\n伤官配印，如果透杀，透财不佳。伤官七杀同时成格，不透财为上好命局。"

        if (gan_shens[0] == '伤' and gan_shens[1] == '伤') or (gan_shens[1] == '伤' and '伤' in zhi_shen3[1]):
            dianpan_analysis=dianpan_analysis+"父母兄弟均无缘。孤苦，性刚毅好掌权。30岁以前有严重感情苦重，适合老夫少妻，继室先同居后结婚。"


        if '印' in gan_shens and ('财' not in gan_shens):
            dianpan_analysis=dianpan_analysis+"伤官配印，无财，有手艺，但是不善于理财。有一定个性"
        if gan_shens[0] == '伤' and gan_shens[1] == '伤' and (not '伤' in zhi_shens2):
            dianpan_analysis=dianpan_analysis+"年月天干都浮现伤官，亲属少。"

        if zhi_shens[1]  == '伤' and len(zhi5[zhis[1]]) == 1 and gan_shens[1] == '伤':
            dianpan_analysis=dianpan_analysis+"月柱：伤官坐专位伤官，夫缘不定。假夫妻。比如老板和小蜜。"


        for seq, gan_ in enumerate(gan_shens):
            if gan_ != '伤':
                continue   
            if zhi_shens[seq] =='劫':
                dianpan_analysis=dianpan_analysis+"伤官地支坐阳刃，力不从心。背禄逐马，克官劫财。影响15年。伤官坐劫财：只适合纯粹之精明商人或严谨掌握财之人。"      
                
    if shens2.count('伤') > 2 and sex == 0:
        dianpan_analysis=dianpan_analysis+"女命伤官多，即使不入伤官格，也缘分浅，多有苦情。"
        if gan_shens.count('伤') > 2:
            dianpan_analysis=dianpan_analysis+"天干2伤官：性骄，六亲不靠。婚前诉说家人，婚后埋怨老公。30岁以前为婚姻危机期。"
    if zhi_shens[2]  == '伤' and len(zhi5[zhis[2]]) == 1:
        if(sex == 0):
            dianpan_analysis=dianpan_analysis+"婚姻宫伤官：克夫。只有庚子日。"
        else:
            dianpan_analysis=dianpan_analysis+"婚姻宫伤官：对妻子不利。只有庚子日。"
        
    shang = ten_deities[me].inverse['伤']
    #dianpan_analysis=dianpan_analysis+"shang", shang, ten_deities[shang].inverse['建'], zhi_shens
    if ten_deities[shang].inverse['建'] in zhis and sex == 0:
        dianpan_analysis=dianpan_analysis+"女命地支伤官禄：婚姻受不得穷。"
    dianpan_analysis = "<p>"+dianpan_analysis+"</p>"
    return dianpan_analysis
