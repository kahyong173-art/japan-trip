"""Put Cat's Japan itinerary into a TREK instance through its REST API.

Usage: python3 seed_trek.py BASE_URL EMAIL PASSWORD
Coordinates come from the Japanese government's GSI address search
(msearch.gsi.go.jp), looked up from each address below.
"""
import json
import sys
import urllib.request
import http.cookiejar

BASE, EMAIL, PASSWORD = sys.argv[1].rstrip('/'), sys.argv[2], sys.argv[3]
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
TOKEN = None


def api(method, path, body=None):
    req = urllib.request.Request(BASE + '/api' + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None)
    req.add_header('Content-Type', 'application/json')
    if TOKEN:
        req.add_header('Authorization', 'Bearer ' + TOKEN)
    try:
        with opener.open(req) as r:
            return json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        raise SystemExit(f'{method} {path} -> {e.code}: {e.read()[:400]}')


TOKEN = api('POST', '/auth/login', {'email': EMAIL, 'password': PASSWORD})['token']
cats = {c['name']: c['id'] for c in api('GET', '/categories')['categories']}
CAT = {'住宿': cats['Hotel'], '餐厅': cats['Restaurant'], '咖啡厅': cats['Bar/Cafe'],
       '景点': cats['Attraction'], '购物': cats['Shopping'], '活动': cats['Activity'],
       '自然': cats['Nature']}

trip = api('POST', '/trips', {
    'title': 'Cat 的日本之旅 🇯🇵',
    'description': '大阪 → 京都 → 河口湖 → 东京，11/17–12/1。\n'
                   '出发前换汇：RM 4,964.70 → ¥190,000（约 1 MYR = 38.27 JPY）。',
    'start_date': '2026-11-17', 'end_date': '2026-12-01', 'currency': 'JPY'})
trip = trip.get('trip', trip)
TID = trip['id']
days = api('GET', f'/trips/{TID}/days')
days = days.get('days', days)
DAY = {d['date']: d['id'] for d in days}

DAY_TITLES = {
    '2026-11-17': '大阪｜抵达 → 道顿堀 / 心斋桥',
    '2026-11-18': '京都一日｜清水寺 · 伏见稻荷 · 祇园',
    '2026-11-19': '大阪｜🎢 USJ',
    '2026-11-20': '🦌 奈良 → 宇治',
    '2026-11-21': '淡路岛 二次元之森 · 🛍 购物',
    '2026-11-22': '大阪 → 京都｜👘 和服 · 🍁 岚山',
    '2026-11-23': '京都 → 河口湖｜Chill 移动日',
    '2026-11-24': '🗻 河口湖 → 东京｜涩谷 · Shibuya Sky',
    '2026-11-25': '东京｜秋叶原 · 东京铁塔',
    '2026-11-26': '🧜‍♀️ DisneySea',
    '2026-11-27': '🍁 镰仓一日',
    '2026-11-28': '🖍 春日部 蜡笔小新',
    '2026-11-29': '🏎 卡丁车 → 原宿 / 表参道',
    '2026-11-30': '🏮 浅草寺 → 银座',
    '2026-12-01': '最后购物 → 机场',
}
for date, title in DAY_TITLES.items():
    api('PUT', f'/trips/{TID}/days/{DAY[date]}', {'title': title})

# (key, name, category, address, lat, lng, day, notes, opening_hours_note)
PLACES = [
    ('h1', 'Yuki Nihonbashi', '住宿', '大阪府大阪市浪速区日本橋4-15-24', 34.6614, 135.505173, None,
     '大阪住宿 11/17–11/22（已付 RM 1000.78）\nEN: 4-chōme-15-24 Nipponbashi, Naniwa-ku, Osaka'),
    ('h2', 'Premiere Taito City（京都）', '住宿', '京都府京都市山科区御陵天徳町21-1 Insight court', 34.991634, 135.812057, None,
     '京都住宿 11/22–11/23（已付 RM 438.11）'),
    ('h3', 'UENO SAKURA HOUSE', '住宿', '東京都台東区小島2-3-16', 35.705082, 139.783295, None,
     '东京住宿 11/23–11/24（已付 RM 182.28）'),
    ('h4', '浅草橋MYビル', '住宿', '東京都台東区浅草橋4-18-10', 35.698784, 139.781845, None,
     '东京住宿 11/24–12/1（已付 RM 2069.41），浅草桥附近'),
    ('p05', '道顿堀 道頓堀', '景点', '大阪府大阪市中央区道頓堀1', 34.668453, 135.502686, '2026-11-17', '抵达大阪当天'),
    ('p06', '心斋桥 心斎橋筋', '购物', '大阪府大阪市中央区心斎橋筋2', 34.670731, 135.501831, '2026-11-17', '抵达大阪当天'),
    ('p07', '御津八幡宫 御津八幡宮（狗狗神社）', '景点', '大阪府大阪市中央区西心斎橋2-10-7', 34.671307, 135.499344, '2026-11-17',
     '从难波站或心斋桥站步行 5–15 分钟。\n你记录的开放时间：神社 9:00–18:00，御守和绘马通常 17:00 截止（未核实）'),
    ('p08', '清水寺', '景点', '京都府京都市東山区清水1-294', 34.99588, 135.783142, '2026-11-18', 'cos 新一 · 🍁'),
    ('p09', '伏见稻荷大社 伏見稲荷大社', '景点', '京都府京都市伏見区深草藪之内町68', 34.967037, 135.773499, '2026-11-18', '🍁'),
    ('p10', '二年坂 · 三年坂', '景点', '京都府京都市東山区清水3', 34.997234, 135.781403, '2026-11-18', '接着清水寺逛'),
    ('p11', '祇园 祇園', '景点', '京都府京都市東山区祇園町南側', 35.002338, 135.775787, '2026-11-18', ''),
    ('p12', '日本环球影城 USJ', '活动', '大阪府大阪市此花区桜島2-1-33', 34.667965, 135.435638, '2026-11-19', '🎢 cos luffy'),
    ('p13', '奈良公园 · 东大寺', '自然', '奈良県奈良市雑司町469', 34.686119, 135.843765, '2026-11-20', '🦌 喂小鹿'),
    ('p14', '宇治 平等院', '景点', '京都府宇治市宇治蓮華116', 34.889317, 135.807281, '2026-11-20', '奈良之后去'),
    ('p15', '二次元之森 ニジゲンノモリ（淡路岛）', '活动', '兵庫県淡路市楠本2425-2', 34.562889, 134.991409, '2026-11-21',
     'cos naruto。地图位置只精确到「淡路市楠本」一带，出发前请再核对'),
    ('p16', '和服体验（店家待定）', '活动', '', None, None, '2026-11-22', '👘 还没选店，选好后补地址'),
    ('p17', '岚山 嵐山（渡月桥一带）', '自然', '京都府京都市右京区嵯峨天龍寺芒ノ馬場町', 35.015144, 135.675156, '2026-11-22', '🍁 随便逛'),
    ('p18', '河口湖', '自然', '山梨県南都留郡富士河口湖町船津', 35.475739, 138.758514, '2026-11-23',
     'Chill 移动日；11/24 看富士山后去东京'),
    ('p19', '涩谷 渋谷（Scramble 十字路口）', '购物', '東京都渋谷区道玄坂2-1', 35.659092, 139.700882, '2026-11-24', '🛍 涩谷购物'),
    ('p20', 'SHIBUYA SKY', '景点', '東京都渋谷区渋谷2-24-12', 35.657951, 139.702316, '2026-11-24', 'cos 几斗'),
    ('p21', '秋叶原 秋葉原', '购物', '東京都千代田区外神田1-17', 35.698269, 139.772385, '2026-11-25', 'cos 金木'),
    ('p22', '东京铁塔 東京タワー', '景点', '東京都港区芝公園4-2-8', 35.658649, 139.745468, '2026-11-25', '拍东京铁塔'),
    ('p23', '东京迪士尼海洋 DisneySea', '活动', '千葉県浦安市舞浜1-13', 35.631264, 139.874329, '2026-11-26', '🧜‍♀️'),
    ('p24', '镰仓 鶴岡八幡宮', '景点', '神奈川県鎌倉市雪ノ下2-1-31', 35.324554, 139.554749, '2026-11-27', '🍁 镰仓一日'),
    ('p25', '春日部（蜡笔小新）', '景点', '埼玉県春日部市粕壁1', 35.981686, 139.753677, '2026-11-28',
     '🖍 具体去哪里待定；地图位置是春日部市中心一带'),
    ('p26', '卡丁车（店家待定）', '活动', '', None, None, '2026-11-29', '🏎 早上；选好店后补地址'),
    ('p27', '原宿 竹下通り', '购物', '東京都渋谷区神宮前1-19', 35.67178, 139.703598, '2026-11-29', ''),
    ('p28', '表参道', '购物', '東京都渋谷区神宮前4-12-10', 35.667229, 139.708557, '2026-11-29', ''),
    ('p29', '浅草寺', '景点', '東京都台東区浅草2-3-1', 35.712856, 139.796585, '2026-11-30', '🏮'),
    ('p30', '银座 銀座', '购物', '東京都中央区銀座4-6', 35.67144, 139.765747, '2026-11-30', 'Shopping；12/1 最后购物 → 机场'),
    # Restaurants: not tied to a day, so they sit in the trip's place list ("想去").
    ('r31', '博多串焼き バッテンよかとぉ アメリカ村店', '餐厅', '', None, None, None,
     '串烧。⚠️ 地址待确认：请在 TREK 里搜索这家店，选对分店后保存位置'),
    ('r32', 'Hanakujira 花くじら 本店', '餐厅', '大阪府大阪市福島区福島2-8-21', 34.695274, 135.486862, None,
     '关东煮。你记录的营业时间 16:00–23:00（未核实）'),
    ('r33', '牛たんの檸檬 大阪本店', '餐厅', '大阪府大阪市中央区千日前2-5-2', 34.666683, 135.505157, None,
     '牛舌；你记录：日本桥站步行约 2 分钟'),
    ('r34', "Pâtisserie Del'immo（大丸東京店 4F）", '咖啡厅', '東京都千代田区丸の内1-9-1 大丸東京店 4F', 35.681252, 139.767242, None, '甜点'),
]

PID = {}
for key, name, cat, addr, lat, lng, day, notes in PLACES:
    body = {'name': name, 'category_id': CAT[cat], 'notes': notes or None}
    if addr:
        body['address'] = addr
    if lat is not None:
        body.update(lat=lat, lng=lng)
    PID[key] = api('POST', f'/trips/{TID}/places', body)['place']['id']
    if day:
        api('POST', f'/trips/{TID}/days/{DAY[day]}/assignments', {'place_id': PID[key]})

for key, start, end in [('h1', '2026-11-17', '2026-11-22'), ('h2', '2026-11-22', '2026-11-23'),
                        ('h3', '2026-11-23', '2026-11-24'), ('h4', '2026-11-24', '2026-12-01')]:
    api('POST', f'/trips/{TID}/accommodations',
        {'place_id': PID[key], 'start_day_id': DAY[start], 'end_day_id': DAY[end]})

ME = api('GET', '/auth/me')['user']['id']
# Prepaid hotels, in ringgit at Cat's own rate (RM 4964.70 -> ¥190,000).
# TREK's exchange_rate is units of the expense currency per 1 trip currency (MYR per JPY).
RATE = round(190000 / 4964.70, 2)
for key, name, amount, date in [('h1', '大阪住宿 Yuki Nihonbashi', 1000.78, '2026-11-17'),
                                ('h2', '京都住宿 Premiere Taito City', 438.11, '2026-11-22'),
                                ('h3', '东京住宿 UENO SAKURA HOUSE', 182.28, '2026-11-23'),
                                ('h4', '东京住宿 浅草橋MYビル', 2069.41, '2026-11-24')]:
    api('POST', f'/trips/{TID}/budget', {
        'name': name, 'category': '住宿', 'total_price': amount, 'currency': 'MYR',
        'exchange_rate': round(4964.70 / 190000, 6), 'expense_date': date, 'place_id': PID[key],
        'payers': [{'user_id': ME, 'amount': amount}],
        'note': f'已预付；按你的换汇 1 MYR ≈ {RATE} JPY 折算'})

api('POST', f'/trips/{TID}/days/{DAY["2026-11-17"]}/notes',
    {'text': '御津八幡宫的御守和绘马通常 17:00 截止，想买的话先去神社', 'icon': '⏰'})
api('POST', f'/trips/{TID}/days/{DAY["2026-12-01"]}/notes', {'text': '记得留时间去机场', 'icon': '✈️'})

print('trip', TID, 'places', len(PID))
