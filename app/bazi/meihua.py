# -*- coding: utf-8 -*-
# CODES = ['UTF-8', 'UTF-16', 'GB18030', 'BIG5']
# UTF_8_BOM = b'\xef\xbb\xbf'


# def string_encoding(b):
#     for code in CODES:
#         try:
#             b.decode(encoding=code)
#             if 'UTF-8' == code and b.startswith(UTF_8_BOM):
#                 return 'UTF-8-SIG'
#             return code
#         except Exception:
#             continue
#     return '未知的字符编码类型'

def get_key(dict, value):
    return [k for k, v in dict.items() if v == value]

def change_str(str,pos):
    l=list(str)
    if(l[pos]=="0"):
        l[pos]="1"
    else:
        l[pos] = "0"

    newStr ="".join(l)
    return newStr

def baguaguaci(baguashuA,baguashuB):
    guaxiang = str(baguashuA)+str(baguashuB)
    result = baguaguaxiang[guaxiang]
    return result
#生体大吉，克体大凶。体克者吉，体生者凶
def shengke(shangwuxing,xiawuxing,shangtiyong):
    if shangwuxing == xiawuxing:
        return {"wuxing":shangwuxing+xiawuxing+"比合","tiyong":"体用比合（吉）"}
    wuxing=wuxingshengke[wuxingshu[shangwuxing]+wuxingshu[xiawuxing]]
    tiyong=""
    if wuxing is not None :
        if shangtiyong == "体":
            if "生" in wuxing:
                tiyong="体生用（凶）"
            else:
                tiyong="体克用（吉）"
        else:
            if "生" in wuxing:
                tiyong="用生体（吉）"
            else:
                tiyong="用克体（凶）"
    else:
        wuxing=wuxingshengke[wuxingshu[xiawuxing]+wuxingshu[shangwuxing]]
        if shangtiyong == "体":
            if "生" in wuxing:
                tiyong="用生体（吉）"
            else:
                tiyong="用克体（凶）"
        else:
            if "生" in wuxing:
                tiyong="体生用（凶）"
            else:
                tiyong="体克用（吉）"
    return {"wuxing":wuxing,"tiyong":tiyong}

baguashu = {
    "乾":1,
    "兑":2,
    "离":3,
    "震":4,
    "巽":5,
    "坎":6,
    "艮":7,
    "坤":0
}


baguaguaxiang = {
    "11":"乾为天",
    "12":"天泽履",
    "13":"天火同人",
    "14":"天雷无妄",
    "15":"天风姤",
    "16":"天水讼",
    "17":"天山遁",
    "10":"天地否",
    "21":"泽天夬",
    "22":"兑为泽",
    "23":"泽火革",
    "24":"泽雷随",
    "25":"泽风大过",
    "26":"泽水困",
    "27":"泽山咸",
    "20":"泽地萃",
    "31":"火天大有",
    "32":"火泽睽",
    "33":"离卦",
    "34":"火雷噬嗑",
    "35":"火风鼎",
    "36":"火水未济",
    "37":"火山旅",
    "30":"地火晋",
    "41":"雷天大壮",
    "42":"雷泽归妹",
    "43":"雷火丰",
    "44":"震为雷",
    "45":"雷风恒",
    "46":"雷水解",
    "47":"雷山小过",
    "40":"雷地豫",
    "51":"风天小畜",
    "52":"风泽中孚",
    "53":"风火家人",
    "54":"风雷益",
    "55":"巽为风",
    "56":"风水涣",
    "57":"风山渐",
    "50":"风地观",
    "61":"水天需",
    "62":"水泽节",
    "63":"水火既济",
    "64":"水雷屯",
    "65":"水风井",
    "66":"坎为水",
    "67":"水山蹇",
    "60":"水地比",
    "71":"山天大畜",
    "72":"山泽损",
    "73":"山火贲",
    "74":"山雷颐",
    "75":"山风蛊",
    "76":"山水蒙",
    "77":"艮为山",
    "70":"山地剥",
    "01":"地天泰",
    "02":"地泽临",
    "03":"地火明夷",
    "04":"地雷复",
    "05":"地风升",
    "06":"地水师",
    "07":"地山谦",
    "00":"坤为地",
}
#0 古文  1为白话文 2为邵雍
baguajiedu = {
    "乾为天":["乾。元，亨，利，贞。\n象曰：天行健，君子以自强不息。","乾卦：大吉大利，吉利的贞卜。\n《象辞》说：天道刚健，运行不已。君子观此卦象，从而以天为法，自强不息。","刚健旺盛，发育之功；完事顺利，谨防太强。得此卦者，天行刚健，自强不息，名利双收之象，宜把握机会，争取成果。女人得此卦则有过于刚直之嫌。"],
    "天泽履":["履。履虎尾，不咥人，亨。\n象曰：上天下泽，履。君子以辨上下，定民志。","履卦：踩着虎尾巴，老虎不咬人，吉利。\n《象辞》说：本卦上卦为乾，为天，下卦为兑，为泽，上天下泽，尊卑显别，这是履卦的卦象。君子观此卦象，从而分别上下尊卑，使人民循规蹈矩，安份守纪。","步履不安，困难危险；谦虚自重，敬慎事主。得此卦者，困难时期，多坎坷不顺，万事不宜急进，须循序渐进，谨慎行事。"],
    "天火同人":["同人。同人于野，亨。利涉大川，利君子贞。\n象曰：天与火，同人；君子以类族辨物。","同人卦：聚众于郊外，将行大事，吉利。有利于涉水渡河，有利于君子的卜问。\n《象辞》说：同人之卦，上卦为乾为天为君王，下卦为离为火为臣民，上乾下离象征君王上情下达，臣民下情上达，君臣意志和同，这是同人的卦象。君子观此卦象，取法于火，明烛天地，照亮幽隐，从而去分析物类，辨明情状。","人类相亲，与人和同；所求皆得，无不称心。得此卦者，吉祥如意，与人合作共事更佳，上下同心，谋事有成。"],
    "天雷无妄":["无妄。元，亨，利，贞。其匪正有眚，不利有攸往。\n象曰：天下雷行，物与无妄。先王以茂对时，育万物。","无妄卦：嘉美通泰，卜问得吉兆。行为不正当，则有灾殃，有所往则不利。\n《象辞》说：本卦上卦为乾为天，下卦为震为雷，天宇之下，春雷滚动，万物萌发，孳生繁衍，这是无妄的卦象。先王观此卦象，从而奋勉努力，顺应时令，保育万物。","不欺不妄，真实至诚；顺乎自然，福禄深宏。得此卦者，顺其自然，守正道者，诸事皆宜。但行为不检者，必招灾祸。"],
    "天风姤":["姤。女壮，勿用取女。\n象曰：天下有风，姤。后以施命诰四方。","姤卦：梦见女子受伤。筮遇此卦，不利于娶女。\n《象辞》说：本卦上卦为乾，乾为天；下卦为巽，巽为风，可见天下有风，是姤卦的卦象，君王观此卦象，从而效法于风之吹拂万物，施教化于天下，昭告四方。","阴长阳消，鸿运中衰；诸多阻滞，谨慎以防。得此卦者，阴长阳衰，诸事不顺，宜谨慎行事，更应注意桃色纠纷。"],
    "天水讼":["讼。有孚，窒惕，中吉，终凶。利见大人，不利涉大川。\n象曰：天与水违行，讼。君子以做事谋始。","讼卦：虽有利可图(获得俘虏)，但要警惕戒惧。其事中间吉利，后来凶险。占筮得此爻，有利于会见贵族王公，不利于涉水渡河。\n《象辞》说：上卦为乾，乾为天；下卦为坎，坎为水，天水隔绝，流向相背，事理乖舛，这是讼卦的卦象。君子观此卦象，以杜绝争讼为意，从而在谋事之初必须慎之又慎。","天高水深，达远不亲；慎谋退守，敬畏无凶。得此卦者，身心不安，事多不顺，与他人多争诉之事，宜修身养性，谨慎处事。"],
    "天山遁":["遁。亨。小利贞。\n象曰：天下有山，遁。君子以远小人，不恶而严。","遁卦：通达。小有利之占问。\n《象辞》说：本卦上卦为乾，乾为天，下卦为艮，艮为山，天下有山，天高山远，是遁卦的卦象。君子观此卦象，从而不用以恶报恶的方法对付小人，而是采取严厉的态度，挂冠悬笏，自甘退隐，远离小人。","逃避退隐，盛极必衰；言行严禁，待机再举。得此卦者，宜退不宜进。退守可以保身，若轻举妄动则会招灾。宜谨言慎行，待机行事。"],
    "天地否":["否。否之匪人。不利君子贞。大往小来。\n象曰：天地不交，否。君子以俭德辟难，不可荣以禄。","否卦：为小人所隔阂，这是不利于君子的占卜，事业也将由盛转衰。\n《象辞》说：天地隔阂不能交感，万物咽窒不能畅釜，这是否卦的卦象。君子观此卦象，从而在国家政治否塞之时，应思隐居不仕，以崇尚俭约来躲避灾难，不要以利禄为荣。","大往小来，闭塞不通；否极泰来，修德避难。得此卦者，万物闭塞之象，上下不合，诸事不顺，凡事宜忍，须待时运好转而有为。"],
    "泽天夬":["夬：扬于王庭，孚号。有厉，告自邑。不利即戎，利有攸往。\n象曰：泽上于天，夬。君子以施禄及下，居德则忌。","王庭里正跳舞作乐。有人呼告：“有敌人来犯。”邑中传来命令：“出击不利，要严阵以待。”筮遇此爻，出外旅行则吉利。\n《象辞》说：本卦上卦为兑，兑为泽；下卦为乾，乾为天，可见泽水上涨，浇灌大地，是夬卦的卦象。君子观此卦象，从而泽惠下施，不敢居功自傲，并以此为忌。","排除决去，必须刚断；始吉终凶，谨慎自重。得此卦者，大运将过，困难将至，宜提高警惕，谨言慎行。"],
    "兑为泽":["兑。亨，利，贞。\n象曰：丽泽，兑。君子以朋友讲习。","兑卦：亨通。吉利的贞卜。\n《象辞》说：本卦为两兑相叠，兑为泽，两泽相连，两水交流是兑卦的卦象。君子观此卦象，从而广交朋友，讲习探索，推广见闻。","泽润万物，双重喜悦；和乐群伦，确守正道。得此卦者，多喜庆之事，人情和合，但应坚守正道，否则犯灾。"],
    "泽火革":["革。己日乃孚。元亨利贞。悔亡。\n象曰：泽中有火，革。君子以治历明时。","革卦：祭祀之日用俘虏作人牲，亨通，吉利的卜问。没有悔恨。\n《象辞》说：本卦外卦为兑，兑为泽；内卦为离，离为火。内蒸外煏，水涸草枯，如同水泽之中，大火燃烧，这是革卦的卦象。君子观此卦象，了解到泽水涨落，草木枯荣的周期变化，从而修治历法，明确时令。","事多变动，坚守正道；顺天应人，实施变革。得此卦者，凡事均在变动之中，宜去旧立新，以应革新之象，则会吉祥。"],
    "泽雷随":["随。元亨，利贞，无咎。\n象曰：泽中有雷，随。君子以向晦入宴息。","随卦：大吉大利，卜得吉兆，没有灾害。\n《象辞》说：本卦下卦为震，震为雷，上卦为兑，兑为泽；雷入泽中，大地寒凝，万物蛰伏，是随卦的卦象。君子观此卦象，取法于随天时而沉寂的雷声，随时作息，向晚则入室休息。","随顺和同，贞固自持；随从机运，不能专横。得此卦者，宜随大势，其事可成。凡事与他人多沟通交流，可名利双收。切不可坚持己见，专横者事不成。"],
    "泽风大过":["大过。栋桡。利有攸往，亨。\n象曰：泽灭木，大过。君子以独立不惧，遁世无闷。","大过卦：屋粱压得弯曲了。有所往则有利，通泰。\n《象辞》说：本卦上卦为兑为泽，下卦为巽为木，上兑下巽，泽水淹没木舟，这是大过的卦象。君子观此卦象，以舟重则覆为戒，领悟到遭逢祸变，应守节不屈，稳居不仕，清静淡泊。","阳多阴少，势将颠覆；本未俱弱，量力而为。得此卦者，身心不安，事不如意，却又强意而行，大有后悔之时，谨防官非及水险。"],
    "泽水困":["困。亨，贞，大人吉，无咎。有言不信。\n象曰：泽无水，困。君子以致命遂志。","困卦：通泰。卜问王公贵族之事吉利，没有灾难。筮遇此爻，有罪之人无法申辩清楚。\n《象辞》说：本卦上卦为兑，兑为泽；下卦为坎，坎为水，水渗泽底，泽中干涸，是困卦的卦象。君子观此卦象，以处境艰难自励，穷且益坚，舍身捐命，以行其夙志。","泽上无水，受困穷之；万物不生，修德静守。得此卦者，陷入困境，事事不如意，宜坚守正道，等待时机。"],
    "泽山咸":["咸。亨，利贞。取女吉。\n象曰：山上有泽，咸。君子以虚受人。","咸卦：通达，吉利的贞卜。娶女，吉利。\n《象辞》说：本卦下卦为艮，艮为山，上卦为兑，兑为泽，山中有泽，山气水息，互相感应，是咸卦的卦象。君子观此卦象，取法于深邃的山谷，深广的大泽，从而虚怀若谷，以谦虚的态度，接受他人的教益。","两性交感，正道感应；物击则鸣，识时知机。得此卦者，宜谦虚待人，则会吉祥如意，谋事可成。但勿为不正当感情而意乱情迷。"],
    "泽地萃":["萃。亨，王假有庙。利见大人，亨，利贞。用大牲吉。利有攸往。\n象曰：泽上于地，萃。君子以除戎器，戒不虞。","萃卦：通泰。王到宗庙举行祭祀。占得此卦，利于会见贵族王公，亨通，这是吉利的贞兆。用牛牲祭祀，也很吉利，并且出行吉利。\n《象辞》说：本卦上卦为兑，兑为泽；下卦为坤，坤为地。泽水淹地，是萃卦的卦象。君子观此卦象，以洪水横流，祸乱丛聚为戒，从而修治兵器，戒备意外的变乱。","物产丰富，聚合丰盛；得贵接引，无往不利。得此卦者，运气大好，能得到贵人的帮助，获利丰厚，无往不利。"],
    "火天大有":["大有。元亨。\n象曰：火在天上，大有。君子以遏恶扬善，顺天休命。","大有卦：昌隆通泰。\n《象辞》说：本卦下卦为乾为天，上卦为离为火，火在天上，明烛四方，这是大有的卦象。君子观此卦象，取法于火，洞察善恶，抑恶扬善，从而顺应天命，祈获好运。","日丽中天，遍照万物；盛大富有，持盈保泰。得此卦者，正当好运，事事吉祥，大有收获，但需防物极必反，盛极转衰。"],
    "火泽睽":["睽。小事吉。\n象曰：上火下泽，睽。君子以同而异。","睽卦：筮遇此卦，小事吉利。\n《象辞》说：本卦上卦为离，离为火；下卦为兑，兑为泽。上火下泽，两相乖离，是睽卦的卦象。君子观此卦象，从而综合万物之所同，分析万物之所异。","人心外向，背道而驰；难以成事，不宜大举。得此卦者，运气不佳，水火不容，相互矛盾，诸事难成。"],
    "离卦":["离。利贞，亨。畜牝牛，吉。\n象曰：明两作，离。大人以继明照四方。","离卦：吉利的占问，通泰。饲养母牛，吉利。\n《象辞》说：今朝太阳升，明朝太阳升，相继不停顿，这是离卦的卦象。贵族王公观此卦象，从而以源源不断的光明照临四方。","附丽光明，谦虚缓进；公正柔和，顺守则吉。得此卦者，宜谦虚谨慎，稳步进取，则前途光明。急进及意气用事者必有所损失。"],
    "火雷噬嗑":["噬嗑。亨。利用狱。\n象曰：雷电噬嗑。先王以明罚敕法。","噬瞌卦：通泰。利于讼狱。\n《象辞》说：本卦下卦为震为雷，上卦为离为电，雷电交合是噬嗑的卦象。先王观此卦象，取法于威风凛凛的雷、照彻幽隐的电，思以严明治政，从而明察其刑罚，修正其法律。","咬碎硬骨，强硬态度；事多困阻，积极谋求。得此卦者，事不遂心，纷争难免，诸事被阻，宜坚守常规，不为利诱，可保平安。"],
    "火风鼎":["鼎。元吉，亨。\n象曰：木上有火，鼎。君子以正位凝命。","鼎卦：大吉大利，亨通。\n《象辞》说：本卦下卦为巽，巽为木；上卦为离，离为火。可见木上有火，以鼎烹物，这是《鼎》卦的卦象。君子观此卦象，取法于鼎足三分，正立不倚，从而持正守位，为君上所倚重，不负使命。","因败致功，因人成事；万事通达，平步青云。得此卦者，时运正佳，能得到朋友的帮助，取得不错的成就。与人合伙共事更佳。"],
    "火水未济":["未济。亨，小狐汔济，濡其尾，无攸利。\n象曰：火在水上，未济。君子以慎辨物居方。","未济卦：亨通。小狐狸快要渡过河，却打湿了尾巴。看来此行无所利。\n《象辞》说：本卦上卦为离，离为火；下卦为坎，坎为水。火在水上，水不能克火，是未济卦的卦象。君子观此卦象，有感于水火错位不能相克，从而以谨慎的态度辨辩事物的性质，审视其方位。","不能资助，待时而动；由小而大，不可躁进。得此卦者，运势不通，诸事不能如愿，宜由小及大，稳步进取，要耐心去突破难关，则终可成功。"],
    "火山旅":["旅。小亨，旅贞吉。\n象曰：山上有火，旅。君子以明慎用刑，而不留狱。","旅卦：稍见亨通。贞卜旅行，吉利。\n《象辞》说：本卦上卦为离，离为火；下卦为艮，艮为山。山上有火，洞照幽隐，这是旅卦的卦象。君子观此卦象，从而明察刑狱，慎重判决，既不敢滥施刑罚，也不敢延宕滞留。","旅途穷困，飘摇不定；小望可成，宏愿难求。得此卦者，事多变动，如在异乡，小事可成，大事难成，宜谨守常规。"],
    "地火晋":["晋。康侯用锡马蕃庶，昼日三接。\n象曰：明出地上，晋。君子以自昭明德。","晋卦：康侯用成王赐予的良马来繁殖马匹，一天多次配种。\n《象辞》说：“本卦上卦为离，离为日；下卦为坤，坤为地。太阳照大地，万物沐光辉”，是晋卦的卦象。君子观此卦象，从而光大自身的光明之德。","日出地上，万物进展；赏赐隆重，百谋皆遂。得此卦者，如旭日东升，气运旺盛，收入颇丰，谋事可成，百事如意。"],
    "雷天大壮":["大壮。利贞。\n象曰：雷在天上，大壮。君子以非礼弗履。","大壮卦：吉利的卜问。\n《象辞》说：本卦上卦为震，震为雷，下卦为乾，乾为天，天上鸣雷是大壮的卦象。君子观此卦象，以迅雷可畏，礼法森严，从而畏威知惧，唯礼是遵。","光明正大，强盛壮大；容忍和气，切忌冲动。得此卦者，运势过于强盛，宜心平气和，谨慎行事，否则必生过失。"],
    "雷泽归妹":["归妹。征凶，无攸利。\n象曰：泽上有雷，归妹。君子以永终知敝。","归妹卦：筮遇此爻，出征凶险。无所利。\n《象辞》说：归妹之卦，下卦为兑，兑为泽；上卦为震，震为雷。可见泽上雷鸣，雷鸣水动，用以喻男女心动相爱而成眷属。这是归妹卦的卦象。君子观此卦象，从而在长期的婚姻生活中，体察到婚姻的成功与失败。","违反常理，其道将穷；明察事理，止绝妄念。得此卦者，困难之时，做事有违常理，灾祸不断。宜明察事理，修身养性，断绝妄念。"],
    "雷火丰":["丰。亨。王假之，勿忧，宜日中。\n象曰：雷电皆至，丰。君子以折狱致刑。","丰卦：举行祭祀，君王将亲临宗庙。不要担心，最佳时刻当在正午时分。\n《象辞》说：本卦上卦为震，震为雷；下卦为离，离为电。电闪雷鸣，是上天垂示的重大天象，这也是丰卦的卦象。君子观此卦象，有感于电光雷鸣的精明和威严，从而裁断讼狱，施行刑罚。","盛大丰满，进财获利；谋望克遂，必有喜庆。得此卦者，运势正强，谋事可成，名利双收。但不宜过贪，要知足常乐，谨防乐极生悲，损财甚至火险。"],
    "震为雷":["震。亨。震来虩虩，笑言哑哑。震惊百里，不丧匕鬯。\n象曰：洊雷，震。君子以恐惧修省。","震卦：临祭之时，雷声传来，有的人吓得浑身发抖，片刻之后，才能谈笑如常。巨雷猝响，震惊百里，有的人却神态自若，手里拿着酒勺子，连一滴酒都没有洒出来。\n《象辞》说：本卦上下卦都为震，震为雷。可见巨雷连击，是震卦的卦象。君子观此卦象，从而戒惧恐惧，修省其身。","重雷发响，奋发图强；先难后易，先苦后甜。得此卦者，奋发振作，大可有为，但表面风光，内恐有难，宜谨言慎行，以免损失。"],
    "雷风恒":["恒。亨，无咎，利贞。利有攸往。\n象曰：雷风，恒。君子以立不易方。","恒卦：通达，没有过失，吉利的卜问。有所往则有利。\n《象辞》说：本卦上卦为震，震为雷，下卦为巽，巽为风，风雷荡涤，宇宙常新，这是恒卦的卦象。君子观此卦象，从而立于正道，坚守不易。","经常恒久，长久不变；君子以利，不易其方。得此卦者，须立身正道，坚守不易，持续努力，必能亨通。缺少毅力，朝三暮四者则不会成功。"],
    "雷水解":["解。利西南。无所往，其来复吉。有攸往，夙吉。\n象曰：雷雨作，解。君子以赦过宥罪。","解卦：利于西南行，但是，若没有确定的目标，则不如返回，返回吉利。如果有确定的目标，则宜早行，早行吉利。\n《象辞》说：本卦上卦为震，震为雷；下卦为坎，坎为雨，雷雨并作，化育万物，是解卦的卦象。君子观此卦象，从而赦免过失，宽宥罪人。","艰难化散，排难解纷；把握时机，趁早进行。得此卦者，能解脱先前之困难，宜把握良机，求谋事业，出外谋事者更佳。"],
    "雷山小过":["小过。亨，利贞。可小事，不可大事。飞鸟遗之音。不宜上，宜下，大吉。\n象曰：山上有雷，小过。君子以行过乎恭，丧过乎衰，用过乎俭。","小过卦：亨通，这是吉利的贞卜。但是只适宜于小事，不适宜大事。飞鸟空中过，叫声耳边留，警惕人们：登高必遇险，下行则吉利。\n《象辞》说：本卦下卦为艮，艮为山；上卦为震，震为雷，山上有雷，是小过的卦象。君子观此卦象，惧畏天雷，不敢有过失。因而行事不敢过于恭谦，居丧不敢过度哀伤，用度不敢过于节俭，唯适中而已。","阴顺阳困，柔软用事；谨慎自持，不宜急进。得此卦者，诸事不利，宜行小事，不宜成大事，更防因自身的过失惹来是非争讼。"],
    "雷地豫":["豫。利建侯行师。\n象曰：雷出地奋，豫。先王以作乐崇德，殷荐之上帝，以配祖考。","豫卦：有利于封侯建国，出兵打仗。\n《象辞》说：本卦上卦为震，震为雷，下卦为坤，坤为地。春雷轰鸣，大地震动，催发万物，这是豫卦的卦象。先王观此卦象，取法于声满大地的雷鸣，制作音乐，歌功颂德，光荣归于上帝，光荣归于祖考。","雷出地上，悦服快乐；安乐之中，预防忧患。得此卦者，顺天应时，事事吉祥，可得长辈之助，但须防色难，切不可沉迷于声色欢场之中。"],
    "风天小畜":["小畜。亨。密云不雨，自我西郊。\n象曰：风行天上，小畜。君子以懿文德。","小畜卦：吉利。在西郊一带浓云密布，但雨没有下来。\n《象辞》说：上卦为巽，巽为风；下卦为乾，乾为天，和风拂地，草木低昂，勃勃滋生，这是小畜的卦象。君子观此卦象，取法催发万物的和风，自励风范，推行德教。","力量寡弱，阻止前进；藏器待时，耐心推进。得此卦者，力量薄弱，运势反覆，宜蓄养实力，静待时机，急进则有险，凡事须耐心推进。"],
    "风泽中孚":["中孚。豚鱼，吉。利涉大川，利贞。\n象曰：泽上有风，中孚。君子以议狱缓死。","中孚卦：豚鱼献祭，虽物薄但心诚，吉利。并利于涉水过河。这是吉利的贞卜。\n《象辞》说：本卦上卦为巽，巽为风；下卦为兑，兑为泽，泽上有风，风起波涌。这是中孚的卦象。君子观此卦象，有感于风化邦国，唯德教为先，因而审议讼狱，不轻置重典。","信而有实，诚恳诚信；知己协助，谋望克遂。得此卦者，正直诚信者吉利，会得到朋友的帮助，谋事可成；心存邪念者则凶。"],
    "风火家人":["家人。利女贞。\n象曰：风自火出，家人。君子以言有物，而行有恒。","家人卦：卜问妇女之事吉利。\n《象辞》说：本卦外卦为巽，巽为风；内卦为离，离为火，内火外风，风助火势，火助风威，相辅相成，是家人的卦象。君子观此卦象，从而省悟到言辞须有内容才不致于空洞，德行须持之以恒才能充沛。","人心内向，家道兴隆；严正有恒，不能移心。得此卦者，与人合作共事者会有利，且多有喜事之象，家庭和睦者，能同心协力，发展事业。"],
    "风雷益":["益。利有攸往，利涉大川。\n象曰：风雷，益。君子以见善则迁，有过则改。","益卦：筮遇此爻，利于有所往，利于涉水渡河。\n《象辞》说：本卦上卦为巽，巽为风；下卦为震，震为雷，风雷激荡，是益卦的卦象。君子观此卦象，惊恐于风雷的威力，从而见善则从之，有过则改之。","损上益下，奋发有为；进取成名，商贾获利。得此卦者，正当好运，奋发图进，得人帮助，能获名利。"],
    "巽为风":["巽。小亨。利有攸往，利见大人。\n象曰：随风，巽。君子以申命行事。","巽卦：稍见亨通。利于出行，利于会见王公贵族。\n《象辞》说：本卦为巽卦相迭而成，巽为风，因而长风相随，吹拂不断，是巽卦的卦象。君子观此卦象，取法于长吹不断的风，从而不断地申明教义，反复地颁行政令，灌输纲常大义。","顺伏容人，谦虚行事；得贵多助，利在远处。得此卦者，运势起伏不定，宜随机应变，谦虚行事，则可得意外之收获。"],
    "风水涣":["涣。亨，王假有庙。利涉大川，利贞。\n象曰：风行水上，涣。先王以享于帝，立庙。","涣卦：亨通，因为君王亲临宗庙，禳灾祈福。利于涉水过江河。这是吉利的贞卜。\n《象辞》说：本卦上卦为巽，巽为风；下卦为坎，坎为水。风行水上，是涣卦的卦象。先王观此卦象，从而享祭天帝，建立宗庙，推行尊天孝祖的“德教”。","离散解消，灾害涣散；乘机观变，养威蓄锐。得此卦者，初有不顺，但终可解困，凡事宜小心则百事亨通，忌任性放纵。"],
    "风山渐":["渐。女归吉，利贞。\n象曰：山上有木，渐。君子以居贤德善俗。","渐卦：女大当嫁，这是好事。这是吉利的贞卜。\n《象辞》说：本卦下卦为艮，艮为山；上卦为巽，巽为木，木植山上，不断生长，是渐卦的卦象。君子观此卦象，取法于山之育林，从而以贤德自居，担负起改善风俗的社会责任。","循序渐进，积少成多；渐进即利，性急即败。得此卦者，逐步开运，凡事宜循序渐进，则谋事可成，不宜急进，性急则败。"],
    "风地观":["观。盥而不荐，有孚顒若。\n象曰：风行地上，观。先王以省方，观民设教。","观卦：祭祀时灌酒降神而不献人牲，因为用作祭祀的俘虏的头部肿了，不能用作祭品。\n《象辞》说：本卦上卦为巽为风，下卦为坤为地，风行大地吹拂万物，这是观的卦象。先王观此卦象取法于周流八方的风，从而巡视邦国，观察民情，推行教化。","以下观上，周游观览；平心静气，坚守岗位。得此卦者，处身于变化之中，心神不宁，宜多观察入微，待机行事，切勿妄进。"],
    "水天需":["需。有孚，光亨，贞吉。利涉大川。\n象曰：云上于天，需；君子以饮食宴乐。","需卦：抓到俘虏。大吉大利，吉利的卜问。有利于涉水渡河。\n《象辞》说：需的上卦为坎，表示云；下卦为乾，表示天。云浮聚于天上，待时降雨是需卦的卦象。君子观此卦象，可以宴饮安乐，待时而动。","坎陷当前，遇阻不进；大器晚成，收成在后。得此卦者，时机尚未成熟，需要耐心等待，急进反会见凶。"],
    "水泽节":["节。亨，苦节不可贞。\n象曰：泽上有水，节。君子以制数度，议德行。","节卦：亨通。如果以节制为苦，其凶吉则不可卜问。\n《象辞》说：本卦下卦为兑，兑为泽；上卦为坎，坎为水。泽中水满，因而须高筑堤防，这是节卦的卦象。君子观此卦象，从而建立政纲制度，确立伦理原则。","操守节度，适可而止；审时度势，能知变通。得此卦者，宜安分守己，切忌贪心不足，诸事必须节制，不宜过份，更要戒酒色。"],
    "水火既济":["既济。亨，小利贞，初吉终乱。\n象曰：水在火上，既济。君子以思患而预防之。","既济卦：亨通。这是小见吉利的贞卜。起初吉利，最后将发生变故。\n《象辞》说：本卦上卦为坎，坎为水；下卦为巽，巽为火。水上火下，水浇火熄，是既济之卦的卦象。君子观此卦象，从而有备于无患之时，防范于未然之际。","济助有成，坚忍自重；由大而小，确保盛运。得此卦者，事业有成，成功之象，但谨防盛极必衰，宜退守为吉，再进则凶。"],
    "水雷屯":["屯。元，亨，利，贞。勿用，有攸往，利建侯。\n象曰：云，雷，屯；君子以经纶。","屯卦。大吉大利，吉利的占卜。不利于出门。有利于建国封侯。\n《象辞》说：屯的上卦为坎，坎为云，下卦为震，震为雷。云行于上，雷动于下，是屯卦的卦象。君子观此卦象，取法于云雷，用云的恩泽，雷的威严来治理国事。","万物始生，开始困难；先劳后逸，苦尽甘来。得此卦者，身处困境，宜守不宜进，须多加辛苦努力，排除困难，方可通达，有初难后解之象。"],
    "水风井":["井。改邑不改井，无丧无得。往来井井。汔至，亦未繘井，羸其瓶，凶。\n象曰：木上有水，井。君子以劳民劝相。","井卦：改建邑落而不改建水井，等于什么也没有干。人们往来井边汲水，水井干涸淤塞，不去加以淘洗，反而将吊水罐打破，这是凶险之象。\n《象辞》说：本卦下卦为巽，巽为木；上卦为坎，坎为水。水下浸而树木生长，这是井卦的卦象。君子观此卦象，取法于井水养人，从而鼓励人民勤劳而互相劝勉。","静水通源，气运平静；不变所守，维持现状。得此卦者，宜修身养性，顺其自然，泰然处之，静有利，动则凶。"],
    "坎为水":["坎。习坎，有孚，维心亨，行有尚。\n象曰：水洊至，习坎。君子以常德行，习教事。","习坎卦：抓获俘虏，劝慰安抚他们，通泰。途中将得到帮助。\n《象辞》说：坎为永，水长流不滞，是坎卦的卦象。君子观此卦象，从而尊尚德行，取法于细水长流之象，学习教化人民的方法。","艰难危险，重险重陷；事多困阻，谨慎行事。得此卦者，运气不佳，多难危险，事多困阻，宜谨言慎行，退守保安。"],
    "水山蹇":["蹇。利西南，不利东北。利见大人，贞吉。\n象曰：山上有水，蹇。君子以反身修德。","蹇卦：筮遇此卦，利西南行，不利东北行。利见贵族王公，获吉祥之兆。\n《象辞》说：上卦为坎，坎为水；下卦为艮，艮为山，山石磷峋，水流曲折，是蹇卦的卦象。君子观此卦象，悟行道之不易，从而反求诸己，修养德行。","踏步难行，艰辛万苦；进退维谷，容忍待时。得此卦者，身心忧苦，举步维艰，宜守正道，不可妄动，涉险境者会有灾难。"],
    "水地比":["比。吉。原筮，元永贞，无咎。不宁方来，后夫凶。\n象曰：地上有水，比。先王以建万国，亲诸侯。","比卦：吉利。同时再卜筮，仍然大吉大利。卜问长时期的吉凶，也没有灾祸。不愿臣服的邦国来朝，迟迟不来者有难。\n《象辞》说：下卦为坤，上卦为坎，坤为地，坎为水，像地上有水，这是比卦的卦象。先王观此卦象，取法于水附大地，地纳江河之象，封建万国，亲近诸侯。","水行地上，亲比欢乐；人情亲顺，百事无忧。得此卦者，可获朋友之助，众人之力，谋事有成，荣显之极。"],
    "山天大畜":["大畜。利贞，不家食，吉。利涉大川。\n象曰：天在山中，大畜。君子以多识前言往行，以畜其德。","大畜卦：吉利的贞兆。不食于家，食于朝廷，吉利。筮遇此卦，有利于涉水渡河。\n《象辞》说：内卦为乾为天，外卦为艮为山，太阳照耀于山中，万物摄取阳光雨露，各遂其生，这是大畜的卦象。君子观此卦象，从而广泛地了解古人的嘉言善行，来培养自己的德行。","以阳畜阴，制止欲进；坚守正道，先凶后吉。得此卦者，宜坚守正道，脚踏实地，务实行事，方可成就大业。切勿骄傲自满，目空一切。"],
    "山泽损":["损。有孚，元吉，无咎，可贞。利有攸往。曷之用？二簋可用享。\n象曰：山下有泽，损。君子以征忿窒欲。","损卦：筮遇此卦，将有所俘获，大吉大利，没有灾难，是称心的卜问。而且所往将获利。将有人送来两盆食物，可享口福。\n《象辞》说：本卦上卦为艮，艮为山；下卦为兑，兑为泽，可见山下有泽是损卦的卦象。君子观此卦象，以泽水浸蚀山脚为戒，从而制止其忿怒，杜塞其贪欲。","损下益上，损盈益虚；先难后易，量入为出。得此卦者，损己利人，虽然开始会有所不顺，但付出总会有所回报，因祸得福之象。"],
    "山火贲":["贲。亨。小利有攸往。\n象曰：山下有火，贲。君子以明庶政，无敢折狱。","贲卦：通达。有所往则有小利。\n《象辞》说：本卦上卦为艮为山，下卦为离为火，山下有火，火燎群山，这是贲卦的卦象。君子观此卦象，思及猛火燎山，玉石俱焚，草木皆尽，以此为戒，从而明察各项政事，不敢以威猛断狱。","文饰光明，外实内需；隐忧之时，量力而为。得此卦者，表面风光，内在空虚，多虚少实。宜充实自己，稳重行事，量力而为。"],
    "山雷颐":["颐。贞吉。观颐，自求口实。\n象曰：山下有雷，颐。君子以慎言语，节饮食。","颐卦：占卜得吉兆。研究颐养之道，在于自食其力。\n《象辞》说：本卦上卦为艮为山，下卦为震为雷，雷出山中，万物萌发，这是颐卦的卦象。君子观此卦象，思生养之不易，从而谨慎言语，避免灾祸。节制饮食，修身养性。","养正养育，谨言节食；观察实务，自知审慎。得此卦者，对于言语及饮食，均须谨慎。宜守正道，谨言慎行，心怀阴谋者会招灾祸。"],
    "山风蛊":["蛊。元亨，利涉大川。先甲三日，后甲三日。\n象曰：山下有风，蛊。君子以振民育德。","蛊卦：大吉大利。利于涉水渡河，但须在甲前三日之辛日与甲后三日之丁日启程。\n《象辞》说：本卦上卦为艮为山，下卦为巽为风，贤人如山居于上，宣布德教施于下，所谓山下有风，这是巽卦盼卦象。君子观此卦象，取法于吹拂万物的风，从而振救万民，施行德教。","三蛊在器，事物败坏；辛勤丁宁，转危为安。得此卦者，艰难迷惑之时，事事不如意；宜大胆革新，奋发图强，艰苦努力，可转危为安。"],
    "山水蒙":["蒙。亨。匪我求童蒙，童蒙求我。初筮告，再三渎，渎则不告。利贞。\n象曰：山下出泉，蒙。君子以果行育德。","蒙卦：通泰。不是我有求于幼稚愚昧的人，而是幼稚愚昧的人有求于我。第一次占筮，神灵告诉了他。轻慢不敬的再三占筮，轻慢不敬的占筮，神灵就不会告诉他。但还是吉利的卜问。\n《象辞》说：上卦为艮，象征山；下卦为坎，象征泉。山下有泉，泉水喷涌而出，这是蒙卦的卦象。君子观此卦象，取法于一往无前的山泉，从而以果敢坚毅的行动来培养自身的品德。","智慧未开，蒙昧闭塞；犹豫不决，缺乏果断。得此卦者，智慧犹如童蒙，不辨是非，迷失方向；若能顺贤师良友之教，启其聪明则亨通。"],
    "艮为山":["艮。艮其背，不获其身。行其庭，不见其人。无咎。\n象曰：兼山，艮。君子以思不出其位。","艮卦：卸掉责任，挂笏隐退，朝列之中已看不到他的身影，在他的庭院中寻找，也没有找到。其人远走高飞，自无灾祸。\n《象辞》说：本卦为两艮卦相重，艮为山，可见艮卦的卦象是高山重立，渊深稳重。君子观此卦象，以此为戒，谋不踰位，明哲保身。","停留阻止，无可再进；随份勿贪，不可强求。得此卦者，前路受阻，不宜妄进，宜守待机。"],
    "山地剥":["剥。不利有攸往。\n象曰：山附于地，剥。上以厚下，安宅。","剥卦：有所往则不利。\n《象辞》说：本卦上卦为艮为山，下卦为坤为地，山在地上，风雨剥蚀，这是剥卦的卦象。君子观此卦象，以山石剥落，岩角崩塌为戒，从而厚结民心，使人民安居乐业。","剥削蚀烂，灾情之忧；进取难成，顺时而止。得此卦者，时运不佳，多有损失，前进有阻，宜顺时而止，安份自守。"],
    "地天泰":["豫。利建侯行师。\n象曰：雷出地奋，豫。先王以作乐崇德，殷荐之上帝，以配祖考。","豫卦：有利于封侯建国，出兵打仗。\n《象辞》说：本卦上卦为震，震为雷，下卦为坤，坤为地。春雷轰鸣，大地震动，催发万物，这是豫卦的卦象。先王观此卦象，取法于声满大地的雷鸣，制作音乐，歌功颂德，光荣归于上帝，光荣归于祖考。","小往大来，通泰祥瑞；泰极转否，事件固守。得此卦者，枯木逢春，鸿运当头，诸事皆顺，但须防乐极生悲。"],
    "地泽临":["临。元，亨，利，贞。至于八月有凶。\n象曰：泽上有地，临。君子以教思无穷，客保民无疆。","临卦：大吉大利，吉利的卜问。到了八月，可能有凶险。\n《象辞》说：本卦下卦为兑为泽，上卦为坤为地，堤岸高出大泽，河泽容于大地，这是临卦的卦象。君子观此卦象，君临天下，教化万民，覃恩极虑，保容万民，德业无疆。","以上临下，相佐相互；居安思危，时时慎戒。得此卦者，好运来到，诸事如意，人情和合，但行事不宜过于急进。"],
    "地火明夷":["明夷。利艰贞。\n象曰：明入地中，明夷。君子以莅众，用晦而明。","明夷卦：卜问艰难之事则利。\n《象辞》说：本卦内卦为离，离为日，外卦为坤，坤为地。太阳没入地中，是明夷的卦象。君子观此卦象，治民理政，不以苛察为明，而是外愚内慧，容物亲众。","日入地中，光明被伤；万事阻滞，等待时运。得此卦者，时运不佳，事事劳苦，宜坚守正道，忍耐自重，等待时机。"],
    "地雷复":["复。亨。出入无疾，朋来无咎。反复其道，七日来复，利有攸往。\n象曰：雷在地中，复。先王以至日闭关，商旅不行，后不省方。","复卦：通泰。出门、居处均无疾病。有钱可赚而可以无灾祸。往返途中，七日可归。有所往则有所利。\n《象辞》说：本卦内卦为震为雷，外卦为坤为地，天寒地冻，雷返归地中，往而有复，依时回归，这是复卦的卦象。先王观此卦象，取法于雷，在冬至之日关闭城门，不接纳商旅，君王也不巡视邦国。","循环往复，生机复萌；成功在望，性急即败。得此卦者，时运好转，顺势而为，谋事可成，但不宜过于急进。"],
    "地风升":["升。元亨。用见大人，勿恤，南征吉。\n象曰：地中生木，升。君子以顺德，积小以高大。","升卦：非常亨通，有利于会见王公贵族，不用担忧。占得此爻，出征南方吉利。\n《象辞》说：本卦外卦为坤，坤为地；内卦为巽，巽为木。可见木植于地中，是升卦的卦象。君子观此卦象，从而遵循德义，加强修养，从细小起步，逐步培育崇高的品德。","升腾上进，畅行其志；出暗向明，遂渐升进。得此卦者，运气升腾，诸事皆积极向上发展，谋事有成，名利双收。"],
    "地水师":["师。贞，丈人吉，无咎。\n象曰：地中有水，师。君子以容民畜众。","师卦：占问总指挥的军情，没有灾祸。\n《象辞》说：下卦为坎，坎为水；上卦为坤，坤为地，像“地中有水”，这是师卦的卦象。君子观此卦象，取法于容纳江河的大地，收容和畜养大众。","忧劳动众，变化无穷；公正无私，排除万难。得此卦者，困难重重，忧心劳众，宜包容别人，艰苦努力，摒除一切困难。"],
    "地山谦":["谦。亨，君子有终。\n象曰：地中有山，谦。君子以裒多益寡，称物平施。","谦卦：通泰。筮遇此卦，君子将有所成就。\n《象辞》说：本卦外卦为坤为地，内卦为艮为山，地中有山，内高外卑，居高不傲，这是谦卦的卦象。君子观此卦象，以谦让为怀，裁取多余昀，增益缺乏的，衡量财物的多寡而公平施予。","谦和忍让，尊人自卑；利用谦虚，万事可达。得此卦者，吉利平安，步步高升。谦虚忍让者前途大好，骄横者必招败。谦受益，满招损。"],
    "坤为地":["坤。元，亨，利牝马之贞。君子有攸往，先迷后得主。利西南得朋，东北丧朋。安贞，吉。\n象曰：地势坤，君子以厚德载物。","坤卦：大吉大利。占问雌马得到吉兆。君子前去旅行，先迷失路途，后来找到主人，吉利。西南行获得财物，东北行丧失财物。占问定居，得到吉兆。\n《象辞》说：大地的形势平铺舒展，顺承天道。君子观此卦象，取法于地，以深厚的德行来承担重大的责任。","柔顺和静，厚载之功；静守安顺，妄动招损。得此卦者，宜顺从运势，以静制动，不宜独立谋事，顺从他人，一起合作，可成大事。"],
}

bagua = {
    "乾": "111",
    "兑": "011",
    "离": "101",
    "震": "001",
    "巽": "110",
    "坎": "010",
    "艮": "100",
    "坤": "000"

}

wuxingbagua = {
    "乾": "金",
    "兑": "金",
    "离": "火",
    "震": "木",
    "巽": "木",
    "坎": "水",
    "艮": "土",
    "坤": "土"
}

wuxingshu = {
    "木":"1",
    "火":"2",
    "土":"3",
    "金":"4",
    "水":"5"
}
#金生水，水生木，木生火，火生土，土生金   金克木，木克土，土克水，水克火，火克金
wuxingshengke = {
    "12":"木生火",
    "23":"火生土",
    "34":"土生金",
    "45":"金生水",
    "51":"水生木",
    "13":"木克土",
    "35":"土克水",
    "52":"水克火",
    "24":"火克金",
    "41":"金克木",
}

yuanshubagua = {
    "乾": "天",
    "兑": "泽",
    "离": "火",
    "震": "雷",
    "巽": "风",
    "坎": "水",
    "艮": "山",
    "坤": "地"
}
#动爻
def get_meihua(shanggua,xiagua,dongyao): 

    #本卦
    shangbengua = get_key(baguashu,shanggua)[0]
    xiabengua = get_key(baguashu,xiagua)[0]
    shangbenguawuxing = wuxingbagua[shangbengua]
    xiabenguawuxing = wuxingbagua[xiabengua]

    bengua = bagua[get_key(baguashu, shanggua)[0]] + bagua[get_key(baguashu, xiagua)[0]]
    #互卦
    shanghuguaguaming = get_key(bagua, bengua[1:4])[0]
    xiahuguaguaming = get_key(bagua, bengua[2:5])[0]
    shanghugua = get_key(bagua, bengua[1:4])[0]
    xiahugua = get_key(bagua, bengua[2:5])[0]
    shanghuguawuxing = wuxingbagua[shanghugua]
    xiahuguawuxing = wuxingbagua[xiahugua]

    changpos = 6-dongyao
    if(changpos==6):
        changpos=0
    #变卦
    biangua = change_str(bengua, changpos)

    shangbianguaguaming = get_key(bagua, biangua[0:3])[0]
    xiabianguaguaming =get_key(bagua, biangua[3:6])[0]
    shangbiangua = get_key(bagua, biangua[0:3])[0]
    xiabiangua = get_key(bagua, biangua[3:6])[0]
    shangbianguawuxing = wuxingbagua[shangbiangua]
    xiabianguawuxing = wuxingbagua[xiabiangua]
    shangtiyong = ""
    if(shangbengua == shangbiangua):
        shangtiyong = "体"
        xiatiyong = "用"
        # print ("上体下用")
    else:
        shangtiyong = "用"
        xiatiyong = "体"
        # print ("下体上用")
    detail = {}
    detail['bengua'] = {
            'shangbengua': shangbengua,
            'xiabengua': xiabengua,
            'shangbenguawuxing': shangbenguawuxing,
            'xiabenguawuxing': xiabenguawuxing,
            'shangtiyong': shangtiyong,
            'xiatiyong': xiatiyong,  
            'guaci': baguaguaci(shanggua,xiagua),  
            'jiedu': baguajiedu[baguaguaci(shanggua,xiagua)],  
            'shengke':shengke(shangbenguawuxing,xiabenguawuxing,shangtiyong)
        }
    detail['hugua'] = {
            'shanghugua': shanghugua,
            'xiahugua': xiahugua,
            'shanghuguawuxing': shanghuguawuxing,
            'xiahuguawuxing': xiahuguawuxing,
            'shangtiyong': shangtiyong,
            'xiatiyong': xiatiyong,  
            'guaci': baguaguaci(baguashu[shanghuguaguaming],baguashu[xiahuguaguaming]),  
            'jiedu': baguajiedu[baguaguaci(baguashu[shanghuguaguaming],baguashu[xiahuguaguaming])], 
            'shengke':shengke(shanghuguawuxing,xiahuguawuxing,shangtiyong) 
        }
    detail['biangua'] = {
            'shangbiangua': shangbiangua,
            'xiabiangua': xiabiangua,
            'shangbianguawuxing': shangbianguawuxing,
            'xiabianguawuxing': xiabianguawuxing,
            'shangtiyong': shangtiyong,
            'xiatiyong': xiatiyong,  
            'guaci': baguaguaci(baguashu[shangbianguaguaming],baguashu[xiabianguaguaming]),  
            'jiedu': baguajiedu[baguaguaci(baguashu[shangbianguaguaming],baguashu[xiabianguaguaming])],  
            'shengke':shengke(shangbianguawuxing,xiabianguawuxing,shangtiyong) 
        }
    return detail