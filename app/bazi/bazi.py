# -*- coding: utf-8 -*-

import datetime
import collections
import sxtwl
from .common import *
from . import datas

Gans = collections.namedtuple("Gans", "year month day time")
Zhis = collections.namedtuple("Zhis", "year month day time")


class BaZi():
    def __init__(self, year: int, month: int, day: int, hour: int, sex: int,lunar:int=0,run:int=0,minute:int=0):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour = int(hour)
        self.sex = int(sex)
        self.lunar = int(lunar)
        self.run = run==1
        self.minute = int(minute)

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
        detail['dayun'] = dayunData
        detail['dayunbig'] = dayunBig
        detail['dayunyear'] = dayunYears

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
        day=sxtwl.fromSolar(t.Y, t.M, t.D)
        Lleap = "闰" if day.isLunarLeap() else ""
        # print("农历:", end='')
        # print("\t{}年{}{}月{}日 {}时".format(day.getLunarYear(), Lleap, day.getLunarMonth(), day.getLunarDay(),cal_hour(t.h)))
        ret_data.append({"solar":"%d-%d-%d %d:%d" % (t.Y, t.M, t.D, t.h, t.m),"lunar":"{}年{}{}月{}日 {}时".format(day.getLunarYear(), Lleap, day.getLunarMonth(), day.getLunarDay(),cal_hour(t.h))})
    return ret_data

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


