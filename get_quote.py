import argparse
import datetime
import glob
import json
import os
import re
from zoneinfo import ZoneInfo

try:
    import requests
    import urllib3
    # 忽略 InsecureRequestWarning（针对 verify=False）
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    requests = None

# -------------------------- 常量与路径配置 --------------------------
TIMEZONE = ZoneInfo("Asia/Shanghai")
DATA_DIR = "data"
ARCHIVE_DIR = "archives"
QUOTES_MD_PATH = "quotes.md"
README_MD_PATH = "README.md"

WEEKDAY_MAP = {
    0: "星期一",
    1: "星期二",
    2: "星期三",
    3: "星期四",
    4: "星期五",
    5: "星期六",
    6: "星期日",
}

HITOKOTO_TYPE_MAP = {
    "a": "动画",
    "b": "漫画",
    "c": "游戏",
    "d": "文学",
    "e": "原创",
    "f": "网络",
    "g": "其他",
    "h": "影视",
    "i": "诗词",
    "j": "网易云",
    "k": "哲学",
    "l": "机灵",
}

# -------------------------- 农历、干支生肖、二十四节气与节日计算 --------------------------
# 1900-2100 年农历数据表
LUNAR_INFO = [
    0x04BD8, 0x04AE0, 0x0A570, 0x054D5, 0x0D260, 0x0D950, 0x16554, 0x056A0, 0x09AD0, 0x055D2,
    0x04AE0, 0x0A5B6, 0x0A4D0, 0x0D250, 0x1D255, 0x0B540, 0x0D6A0, 0x0ADA2, 0x095B0, 0x14977,
    0x04970, 0x0A4B0, 0x0B4B5, 0x06A50, 0x06D40, 0x1AB54, 0x02B60, 0x09570, 0x052F2, 0x04970,
    0x06566, 0x0D4A0, 0x0EA50, 0x06E95, 0x05AD0, 0x02B60, 0x186E3, 0x092E0, 0x1C8D7, 0x0C950,
    0x0D4A0, 0x1D8A6, 0x0B550, 0x056A0, 0x1A5B4, 0x025D0, 0x092D0, 0x0D2B2, 0x0A950, 0x0B557,
    0x06CA0, 0x0B550, 0x15355, 0x04DA0, 0x0A5D0, 0x14573, 0x052D0, 0x0A9A8, 0x0E950, 0x06AA0,
    0x0AEA6, 0x0AB50, 0x04B60, 0x0AAE4, 0x0A570, 0x05260, 0x0F263, 0x0D950, 0x05B57, 0x056A0,
    0x096D0, 0x04DD5, 0x04AD0, 0x0A4D0, 0x0D4D4, 0x0D250, 0x0D558, 0x0B540, 0x0B5A0, 0x195A6,
    0x095B0, 0x049B0, 0x0A974, 0x0A4B0, 0x0B27A, 0x06A50, 0x06D40, 0x0AF46, 0x0AB60, 0x09570,
    0x04AF5, 0x04970, 0x064B0, 0x074A3, 0x0EA50, 0x06B58, 0x05AC0, 0x0AB60, 0x096D5, 0x092E0,
    0x0C960, 0x0D954, 0x0D4A0, 0x0DA50, 0x07552, 0x056A0, 0x0ABB7, 0x025D0, 0x092D0, 0x0CAB5,
    0x0A950, 0x0B4A0, 0x0BAA4, 0x0AD50, 0x055D9, 0x04BA0, 0x0A5B0, 0x15176, 0x052B0, 0x0A930,
    0x07954, 0x06AA0, 0x0AD50, 0x05B52, 0x04B60, 0x0A6E6, 0x0A4E0, 0x0D260, 0x0EA65, 0x0D530,
    0x05AA0, 0x076A3, 0x096D0, 0x04AFB, 0x04AD0, 0x0A4D0, 0x1D0B6, 0x0D250, 0x0D520, 0x0DD45,
    0x0B5A0, 0x056D0, 0x055B2, 0x049B0, 0x0A577, 0x0A4B0, 0x0AA50, 0x1B255, 0x06D20, 0x0ADA0,
    0x14B63, 0x09370, 0x049F8, 0x04970, 0x064B0, 0x168A6, 0x0EA50, 0x06AA0, 0x1A6C4, 0x0AAE0,
    0x092E0, 0x0D2E3, 0x0C960, 0x0D557, 0x0D4A0, 0x0DA50, 0x05D55, 0x056A0, 0x0A6D0, 0x055D4,
    0x052D0, 0x0A9B8, 0x0A950, 0x0B4A0, 0x0B6A6, 0x0AD50, 0x055A0, 0x0ABA4, 0x0A5B0, 0x052B0,
    0x0B273, 0x06930, 0x07337, 0x06AA0, 0x0AD50, 0x14B55, 0x04B60, 0x0A570, 0x054E4, 0x0D160,
    0x0E968, 0x0D520, 0x0DAA0, 0x16AA6, 0x056D0, 0x04AE0, 0x0A9D4, 0x0A2D0, 0x0D150, 0x0F252,
    0x0D520,
]

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZODIAC = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
LUNAR_MONTH_NAMES = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
LUNAR_DAY_PREFIX = ["初", "十", "廿", "三"]
LUNAR_DAY_DIGIT = ["十", "一", "二", "三", "四", "五", "六", "七", "八", "九"]

# 21 世纪二十四节气 C 值表
SOLAR_TERMS_C21 = [
    ("小寒", 1, 5.4055), ("大寒", 1, 20.12),
    ("立春", 2, 3.87),   ("雨水", 2, 18.73),
    ("惊蛰", 3, 5.63),   ("春分", 3, 20.646),
    ("清明", 4, 4.81),   ("谷雨", 4, 20.1),
    ("立夏", 5, 5.52),   ("小满", 5, 21.04),
    ("芒种", 6, 5.678),  ("夏至", 6, 21.37),
    ("小暑", 7, 7.108),  ("大暑", 7, 22.83),
    ("立秋", 8, 7.5),    ("处暑", 8, 23.13),
    ("白露", 9, 7.646),  ("秋分", 9, 23.042),
    ("寒露", 10, 8.318), ("霜降", 10, 23.438),
    ("立冬", 11, 7.438), ("小雪", 11, 22.36),
    ("大雪", 12, 7.18),  ("冬至", 12, 21.94),
]

SOLAR_TERM_ADJUST = {
    (2026, "雨水"): -1,
    (2084, "春分"): 1,
    (2008, "小满"): 1,
    (2016, "立秋"): 1,
    (2089, "霜降"): 1,
    (2089, "立冬"): 1,
    (1978, "小雪"): 1,
    (2021, "冬至"): -1,
}

LUNAR_FESTIVALS = {
    (1, 1): "🏮 春节",
    (1, 15): "🏮 元宵节",
    (2, 2): "🐉 龙抬头",
    (5, 5): "🌿 端午节",
    (7, 7): "🌌 七夕节",
    (7, 15): "🕯️ 中元节",
    (8, 15): "🌕 中秋节",
    (9, 9): "🏔️ 重阳节",
    (12, 8): "🥣 腊八节",
    (12, 23): "🍬 北方小年",
    (12, 24): "🍬 南方小年",
}

SOLAR_FESTIVALS = {
    (1, 1): "🎉 元旦",
    (2, 14): "🌹 情人节",
    (3, 8): "🌸 妇女节",
    (5, 1): "🛠️ 劳动节",
    (5, 4): "🌱 青年节",
    (6, 1): "🎈 儿童节",
    (9, 10): "🏫 教师节",
    (10, 1): "🇨🇳 国庆节",
    (10, 24): "💻 程序员节",
}


def _lunar_leap_month(y: int) -> int:
    return LUNAR_INFO[y - 1900] & 0xF


def _lunar_leap_days(y: int) -> int:
    if _lunar_leap_month(y):
        return 30 if (LUNAR_INFO[y - 1900] & 0x10000) else 29
    return 0


def _lunar_month_days(y: int, m: int) -> int:
    return 30 if (LUNAR_INFO[y - 1900] & (0x10000 >> m)) else 29


def _lunar_year_days(y: int) -> int:
    return sum(_lunar_month_days(y, m) for m in range(1, 13)) + _lunar_leap_days(y)


def solar_to_lunar(dt: datetime.date) -> tuple[int, int, int, bool]:
    """将公历日期转换为 (农历年, 农历月, 农历日, 是否闰月)"""
    offset = (dt - datetime.date(1900, 1, 31)).days
    year = 1900
    while year < 2100:
        days = _lunar_year_days(year)
        if offset < days:
            break
        offset -= days
        year += 1

    leap = _lunar_leap_month(year)
    months = []
    for m in range(1, 13):
        months.append((m, False, _lunar_month_days(year, m)))
        if m == leap:
            months.append((m, True, _lunar_leap_days(year)))

    for m, is_leap, days in months:
        if offset < days:
            return year, m, offset + 1, is_leap
        offset -= days
    return year, 12, 1, False


def format_lunar_day(day: int) -> str:
    if day == 10:
        return "初十"
    if day == 20:
        return "二十"
    if day == 30:
        return "三十"
    return LUNAR_DAY_PREFIX[day // 10] + LUNAR_DAY_DIGIT[day % 10]


def get_solar_term(dt: datetime.date) -> str:
    """获取指定公历日期的二十四节气名称（若非节气当天则返回空字符串）"""
    if not (2000 <= dt.year <= 2099):
        return ""
    y = dt.year % 100
    for name, m, c in SOLAR_TERMS_C21:
        if m == dt.month:
            leap_cnt = (y - 1) // 4 if m <= 2 else y // 4
            day = int(y * 0.2422 + c) - leap_cnt + SOLAR_TERM_ADJUST.get((dt.year, name), 0)
            if day == dt.day:
                return name
    return ""


def get_calendar_meta(date_str: str) -> dict:
    """获取指定 YYYY-MM-DD 的完整传统历法信息（星期、干支生肖年、农历月日、节气、节日）"""
    try:
        dt = datetime.date.fromisoformat(date_str)
    except ValueError:
        return {"weekday": "", "lunar_text": "", "badges": []}

    weekday = WEEKDAY_MAP.get(dt.weekday(), "")
    ly, lm, ld, is_leap = solar_to_lunar(dt)

    gan = TIAN_GAN[(ly - 4) % 10]
    zhi = DI_ZHI[(ly - 4) % 12]
    zodiac = ZODIAC[(ly - 4) % 12]
    leap_prefix = "闰" if is_leap else ""
    lunar_month_str = f"{leap_prefix}{LUNAR_MONTH_NAMES[lm - 1]}月"
    lunar_day_str = format_lunar_day(ld)
    lunar_text = f"{gan}{zhi}{zodiac}年 {lunar_month_str}{lunar_day_str}"

    badges = []
    # 1. 二十四节气
    term = get_solar_term(dt)
    if term:
        badges.append(f"🌿 {term}")

    # 2. 农历传统节日（含除夕判断）
    next_ly, next_lm, next_ld, next_leap = solar_to_lunar(dt + datetime.timedelta(days=1))
    if not next_leap and (next_lm, next_ld) == (1, 1):
        badges.append("🧨 除夕")
    elif not is_leap and (lm, ld) in LUNAR_FESTIVALS:
        badges.append(LUNAR_FESTIVALS[(lm, ld)])

    # 3. 公历节日
    if (dt.month, dt.day) in SOLAR_FESTIVALS:
        badges.append(SOLAR_FESTIVALS[(dt.month, dt.day)])

    return {
        "weekday": weekday,
        "lunar_text": lunar_text,
        "badges": badges,
    }


def get_today_str() -> str:
    """获取北京时间当日日期字符串 YYYY-MM-DD"""
    return datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d")


def parse_bing_response(res: dict) -> dict:
    """解析必应每日壁纸 API 响应"""
    img_info = (res.get("images") or [{}])[0]
    url_path = (img_info.get("url") or "").strip()
    urlbase = (img_info.get("urlbase") or "").strip()
    full_copyright = (img_info.get("copyright") or "").strip()
    title = (img_info.get("title") or "").strip() or "今日必应壁纸"

    # 拆分故事描述与摄影师署名，格式通常为: "描述与地点 (© 摄影师)"
    story = full_copyright
    author = ""
    m = re.match(r"^(.*?)\s*[\(（](©.*?)[\)）]\s*$", full_copyright)
    if m:
        story = m.group(1).strip()
        author = m.group(2).strip()

    # 优先基于 urlbase 构造无多余查询参数的纯净 1080P 与 4K UHD 地址
    if urlbase.startswith("/"):
        url_1080p = f"https://cn.bing.com{urlbase}_1920x1080.jpg"
        url_4k = f"https://cn.bing.com{urlbase}_UHD.jpg"
    else:
        clean_path = url_path.split("&")[0] if "&" in url_path else url_path
        url_1080p = f"https://cn.bing.com{clean_path}" if clean_path.startswith("/") else clean_path
        url_4k = url_1080p

    return {
        "type": "必应壁纸",
        "title": title,
        "story": story,
        "author": author,
        "copyright": full_copyright,
        "url_1080p": url_1080p,
        "url_4k": url_4k,
        "date": get_today_str(),
    }


def parse_poem_response(res: dict) -> dict:
    """安全解析今日诗词 API 响应，防止个别字段为 None 时抛出异常"""
    data = res.get("data") or {}
    origin = data.get("origin") or {}
    raw_lines = origin.get("content") or []
    content = "\n".join(str(line).strip() for line in raw_lines if line).strip()
    if not content:
        raise ValueError("诗词正文为空")

    return {
        "type": "每日诗词",
        "title": (origin.get("title") or "无题").strip(),
        "dynasty": (origin.get("dynasty") or "古诗").strip(),
        "author": (origin.get("author") or "佚名").strip(),
        "content": content,
        "summary": (data.get("content") or "").strip(),
        "tags": [str(t).strip() for t in (data.get("matchTags") or []) if t],
        "date": get_today_str(),
    }


# -------------------------- 四个指定 API 配置 --------------------------
API_CONFIGS = [
    # 1. 每日一句（金山词霸）
    {
        "name": "每日一句",
        "key": "quote",
        "url": "http://open.iciba.com/dsapi/",
        "method": "GET",
        "retry_count": 3,
        "dedup": False,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "parser": lambda res: {
            "type": "每日一句",
            "english": (res.get("content") or "").strip(),
            "chinese": (res.get("note") or "").strip(),
            "tts_url": (res.get("tts") or "").strip(),
            "img_url": (res.get("fenxiang_img") or "").strip(),
            "date": get_today_str(),
        },
    },
    # 2. 必应每日 4K 壁纸
    {
        "name": "必应壁纸",
        "key": "bing",
        "url": "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN",
        "method": "GET",
        "retry_count": 3,
        "dedup": False,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "parser": parse_bing_response,
    },
    # 3. 每日一言（Hitokoto）
    {
        "name": "每日一言",
        "key": "hitokoto",
        "url": "https://v1.hitokoto.cn/",
        "method": "GET",
        "retry_count": 3,
        "dedup": True,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "parser": lambda res: {
            "type": "每日一言",
            "content": (res.get("hitokoto") or "").strip(),
            "from": (res.get("from") or "").strip(),
            "from_who": (res.get("from_who") or "").strip(),
            "category": HITOKOTO_TYPE_MAP.get(res.get("type", ""), ""),
            "date": get_today_str(),
        },
    },
    # 4. 每日诗词（今日诗词）
    {
        "name": "每日诗词",
        "key": "poem",
        "url": "https://v2.jinrishici.com/one.json",
        "method": "GET",
        "retry_count": 3,
        "dedup": True,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "parser": parse_poem_response,
    },
]


# -------------------------- 数据存储与历史加载 --------------------------
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)


def load_all_data() -> dict[str, dict]:
    """加载 data/*.json 中的所有历史数据，返回 {date_str: record_dict}（按日期升序）"""
    ensure_dirs()
    all_records = {}
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                month_data = json.load(f)
                if isinstance(month_data, dict):
                    all_records.update(month_data)
        except Exception as e:
            print(f"⚠️ 读取数据文件 {path} 失败: {e}")
    return dict(sorted(all_records.items(), key=lambda x: x[0]))


def save_month_data(year_month: str, month_records: dict[str, dict]):
    """保存指定月份（YYYY-MM）的数据到 data/YYYY-MM.json"""
    ensure_dirs()
    sorted_records = dict(sorted(month_records.items(), key=lambda x: x[0]))
    file_path = os.path.join(DATA_DIR, f"{year_month}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sorted_records, f, ensure_ascii=False, indent=2)


def save_all_data(all_records: dict[str, dict]):
    """将全量记录按月切分保存到 data/YYYY-MM.json"""
    grouped: dict[str, dict[str, dict]] = {}
    for dt, rec in all_records.items():
        ym = dt[:7]
        grouped.setdefault(ym, {})[dt] = rec
    for ym, recs in grouped.items():
        save_month_data(ym, recs)


def build_seen_sets(all_records: dict[str, dict], exclude_date: str = "") -> tuple[set, set]:
    """构建已收录的一言与诗词集合，用于智能去重"""
    seen_hitokoto = set()
    seen_poems = set()
    for dt, rec in all_records.items():
        if dt == exclude_date:
            continue
        h = rec.get("hitokoto")
        if h and h.get("content"):
            seen_hitokoto.add(h["content"].strip())
        p = rec.get("poem")
        if p and p.get("title"):
            seen_poems.add(f"{p.get('title', '')}_{p.get('author', '')}")
    return seen_hitokoto, seen_poems


# -------------------------- API 调用与去重 --------------------------
def _http_get_json(url: str, headers: dict, timeout: int = 15) -> dict:
    """发送 HTTP GET 请求并解析 JSON（优先使用 requests，无依赖时回退至标准库 urllib）"""
    if requests is not None:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
        )
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
        return response.json()
    else:
        import ssl
        import urllib.request

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)


def call_api(api_config: dict, seen_hitokoto: set, seen_poems: set):
    """调用单个 API，带失败重试机制与历史内容去重"""
    api_name = api_config["name"]
    api_key = api_config["key"]
    url = api_config["url"]
    headers = api_config["headers"]
    parser = api_config["parser"]
    max_retries = api_config["retry_count"]
    enable_dedup = api_config.get("dedup", False)

    max_dedup_attempts = 4 if enable_dedup else 1
    last_valid_result = None

    for dedup_attempt in range(1, max_dedup_attempts + 1):
        for retry in range(1, max_retries + 1):
            try:
                data = _http_get_json(url, headers=headers, timeout=15)
                result = parser(data)
                last_valid_result = result

                # 检查是否与历史记录重复
                if enable_dedup and dedup_attempt < max_dedup_attempts:
                    if api_key == "hitokoto" and result.get("content") in seen_hitokoto:
                        print(f"🔄 {api_name} 抽中历史重复内容，正在重新抽取 ({dedup_attempt}/{max_dedup_attempts - 1})...")
                        break
                    if api_key == "poem":
                        poem_id = f"{result.get('title', '')}_{result.get('author', '')}"
                        if poem_id in seen_poems:
                            print(f"🔄 {api_name}《{result.get('title')}》已收录过，正在重新抽取 ({dedup_attempt}/{max_dedup_attempts - 1})...")
                            break

                print(f"✅ {api_name} 调用成功")
                return result

            except Exception as e:
                error_msg = str(e)[:60]
                if retry < max_retries:
                    print(f"❌ {api_name} 调用失败（第{retry}次）：{error_msg}，重试...")
                    continue
                else:
                    print(f"❌ {api_name} 重试{max_retries}次后仍失败：{error_msg}")
                    return last_valid_result

    if last_valid_result:
        print(f"✅ {api_name} 调用成功（使用兜底结果）")
    return last_valid_result


def backfill_recent_bing_wallpapers(all_records: dict[str, dict]):
    """利用必应壁纸历史归档参数（idx=0&n=8, idx=7&n=8）自动回填最近两周缺失的必应壁纸"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    updated_months = set()
    for idx in (0, 7):
        url = f"https://cn.bing.com/HPImageArchive.aspx?format=js&idx={idx}&n=8&mkt=zh-CN"
        try:
            data = _http_get_json(url, headers=headers, timeout=15)
            for img in data.get("images") or []:
                enddate = img.get("enddate", "")
                if len(enddate) == 8:
                    dt_str = f"{enddate[:4]}-{enddate[4:6]}-{enddate[6:8]}"
                    if dt_str in all_records and not all_records[dt_str].get("bing"):
                        parsed = parse_bing_response({"images": [img]})
                        clean_bing = {k: v for k, v in parsed.items() if k not in ("type", "date")}
                        all_records[dt_str]["bing"] = clean_bing
                        updated_months.add(dt_str[:7])
        except Exception as e:
            print(f"⚠️ 回填必应近期壁纸 (idx={idx}) 跳过: {str(e)[:50]}")

    for ym in updated_months:
        m_recs = {dt: rec for dt, rec in all_records.items() if dt.startswith(ym)}
        save_month_data(ym, m_recs)
    if updated_months:
        print(f"🌄 已自动为近期历史记录补全必应 4K 壁纸！")


def collect_daily_record(today: str, all_records: dict[str, dict]) -> dict:
    """收集今日所有 API 结果并返回标准化单日记录字典"""
    seen_hitokoto, seen_poems = build_seen_sets(all_records, exclude_date=today)
    record = {"date": today, "quote": None, "bing": None, "hitokoto": None, "poem": None}

    for api in API_CONFIGS:
        res = call_api(api, seen_hitokoto, seen_poems)
        if res:
            clean_res = {k: v for k, v in res.items() if k not in ("type", "date")}
            record[api["key"]] = clean_res

    return record


# -------------------------- Markdown 渲染引擎 --------------------------
def render_daily_card(record: dict, heading_level: str = "##") -> str:
    """将单日数据渲染为精美的 Markdown 灵感卡片（含农历、干支生肖、节气、必应壁纸）"""
    dt = record["date"]
    cal = get_calendar_meta(dt)
    weekday = cal["weekday"]
    lunar_text = cal["lunar_text"]
    badges = cal["badges"]

    meta_parts = [p for p in (weekday, lunar_text) if p]
    title_suffix = f" · {' · '.join(meta_parts)}" if meta_parts else ""
    badge_suffix = " &nbsp;" + " ".join(f"`{b}`" for b in badges) if badges else ""
    sub_heading = "#" + heading_level

    lines = [f"{heading_level} 🗓️ {dt}{title_suffix}{badge_suffix}", ""]

    quote = record.get("quote")
    bing = record.get("bing")
    hitokoto = record.get("hitokoto")
    poem = record.get("poem")

    if not quote and not bing and not hitokoto and not poem:
        lines.append("> ⚠️ 今日暂无数据（接口调用失败）")
        lines.append("")
        return "\n".join(lines)

    # 1. 必应每日 4K 壁纸（若有）
    if bing and bing.get("url_1080p"):
        b_title = bing.get("title", "今日必应壁纸")
        b_story = bing.get("story") or bing.get("copyright", "")
        b_author = bing.get("author", "")
        u_1080 = bing.get("url_1080p", "")
        u_4k = bing.get("url_4k") or u_1080

        lines.append(f"{sub_heading} 🌄 必应每日壁纸")
        lines.append("")
        lines.append("<table>")
        lines.append("<tr>")
        lines.append('<td width="55%" align="center" valign="middle">')
        lines.append(f'<img src="{u_1080}" alt="{b_title} ({dt})" width="420" />')
        lines.append("</td>")
        lines.append('<td width="45%" valign="middle">')
        lines.append("")
        lines.append(f"**📍 {b_title}**")
        lines.append("")
        if b_story:
            lines.append(f"> {b_story}")
            lines.append("")
        if b_author:
            lines.append(f"📷 *{b_author}*")
            lines.append("")
        lines.append(f"[🖼️ 1080P 高清壁纸]({u_1080}) &nbsp;｜&nbsp; [💎 4K 原图 (UHD)]({u_4k})")
        lines.append("")
        lines.append("</td>")
        lines.append("</tr>")
        lines.append("</table>")
        lines.append("")

    # 2. 每日一句（图文并排卡片）
    if quote:
        eng = quote.get("english", "")
        chn = quote.get("chinese", "")
        tts = quote.get("tts_url", "")
        img = quote.get("img_url", "")

        lines.append(f"{sub_heading} 📚 每日一句")
        lines.append("")
        lines.append("<table>")
        lines.append("<tr>")
        lines.append('<td width="65%" valign="middle">')
        lines.append("")
        lines.append(f"> **{eng}**")
        lines.append(">")
        lines.append(f"> {chn}")
        lines.append("")
        action_links = []
        if tts:
            action_links.append(f"[🎧 点击收听原声]({tts})")
        if img:
            action_links.append(f"[🖼️ 查看高清日签]({img})")
        if action_links:
            lines.append(" &nbsp;｜&nbsp; ".join(action_links))
            lines.append("")
        lines.append("</td>")
        if img:
            lines.append('<td width="35%" align="center" valign="middle">')
            lines.append(f'<img src="{img}" alt="每日一句 ({dt})" width="240" />')
            lines.append("</td>")
        lines.append("</tr>")
        lines.append("</table>")
        lines.append("")

    # 3. 每日一言（带署名与分类标签）
    if hitokoto:
        content = hitokoto.get("content", "")
        source = hitokoto.get("from", "")
        author = hitokoto.get("from_who", "")
        category = hitokoto.get("category", "")

        cat_badge = f" `{category}`" if category else ""
        lines.append(f"{sub_heading} 💬 每日一言{cat_badge}")
        lines.append("")
        lines.append(f"> 「 {content} 」")

        if source or author:
            sign_parts = []
            if author:
                sign_parts.append(author)
            if source:
                sign_parts.append(f"《{source}》")
            lines.append(">")
            lines.append(f'> <p align="right">—— {" · ".join(sign_parts)}</p>')
        lines.append("")

    # 4. 每日诗词（古风排版 + 名句高亮 + 标签 + 长诗折叠保护）
    if poem:
        title = poem.get("title", "")
        dynasty = poem.get("dynasty", "")
        author = poem.get("author", "")
        content = poem.get("content", "")
        summary = poem.get("summary", "")
        tags = poem.get("tags") or []

        tag_str = " ".join(f"`#{t}`" for t in tags) if tags else ""
        tag_suffix = f" &nbsp;{tag_str}" if tag_str else ""

        lines.append(f"{sub_heading} 📜 每日诗词{tag_suffix}")
        lines.append("")
        lines.append(f"**《{title}》** · 〔{dynasty}〕{author}")
        lines.append("")

        if summary:
            lines.append(f"✨ **名句摘录**：「 *{summary}* 」")
            lines.append("")

        poem_lines = [line.strip() for line in content.splitlines() if line.strip()]
        if len(poem_lines) <= 10:
            for pl in poem_lines:
                lines.append(f"> {pl}  ")
            lines.append("")
        else:
            # 超过 10 行的长诗：展示前 6 行 + 折叠余下诗句，兼顾美观与阅读连续性
            for pl in poem_lines[:6]:
                lines.append(f"> {pl}  ")
            lines.append("")
            rest_lines = poem_lines[6:]
            lines.append(
                f"<details><summary>📖 展开阅读余下 {len(rest_lines)} 句（全诗共 {len(poem_lines)} 句）</summary>"
            )
            lines.append("")
            for pl in rest_lines:
                lines.append(f"> {pl}  ")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    return "\n".join(lines)


def build_archive_summary_table(all_records: dict[str, dict], link_prefix: str = "archives/") -> str:
    """生成月度归档导航表格"""
    grouped: dict[str, list[dict]] = {}
    for dt, rec in all_records.items():
        ym = dt[:7]
        grouped.setdefault(ym, []).append(rec)

    lines = [
        "| 月份 | 收录天数 | 每日一句 | 每日一言 | 每日诗词 | 必应壁纸 | 归档直达 |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for ym in sorted(grouped.keys(), reverse=True):
        recs = grouped[ym]
        days_cnt = len(recs)
        q_cnt = sum(1 for r in recs if r.get("quote"))
        h_cnt = sum(1 for r in recs if r.get("hitokoto"))
        p_cnt = sum(1 for r in recs if r.get("poem"))
        b_cnt = sum(1 for r in recs if r.get("bing"))
        lines.append(
            f"| **{ym}** | {days_cnt} 天 | {q_cnt} 篇 | {h_cnt} 条 | {p_cnt} 首 | {b_cnt} 张 | [📂 查看 {ym} 归档]({link_prefix}{ym}.md) |"
        )
    return "\n".join(lines)


def render_monthly_archive_file(year_month: str, month_records: dict[str, dict]):
    """生成 archives/YYYY-MM.md 归档文件（按日期倒序排列）"""
    ensure_dirs()
    recs_desc = [
        month_records[dt] for dt in sorted(month_records.keys(), reverse=True)
    ]
    days_cnt = len(recs_desc)
    q_cnt = sum(1 for r in recs_desc if r.get("quote"))
    h_cnt = sum(1 for r in recs_desc if r.get("hitokoto"))
    p_cnt = sum(1 for r in recs_desc if r.get("poem"))
    b_cnt = sum(1 for r in recs_desc if r.get("bing"))

    lines = [
        f"# 🗓️ {year_month} 每日灵感归档",
        "",
        "> [⬅️ 返回仓库首页](../README.md) &nbsp;｜&nbsp; [📖 返回当月精选合集](../quotes.md)",
        "",
        f"本月共打卡 **{days_cnt}** 天，累计收录每日一句 **{q_cnt}** 篇、每日一言 **{h_cnt}** 条、每日诗词 **{p_cnt}** 首、必应壁纸 **{b_cnt}** 张。",
        "",
        "---",
        "",
    ]

    for idx, rec in enumerate(recs_desc):
        lines.append(render_daily_card(rec, heading_level="##"))
        if idx < len(recs_desc) - 1:
            lines.append("---")
            lines.append("")

    archive_path = os.path.join(ARCHIVE_DIR, f"{year_month}.md")
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def render_quotes_md(all_records: dict[str, dict]):
    """生成精简且美观的 quotes.md（保留当月最新内容倒序 + 全量历史归档导航）"""
    if not all_records:
        return

    latest_date = max(all_records.keys())
    current_ym = latest_date[:7]
    total_days = len(all_records)
    total_quotes = sum(1 for r in all_records.values() if r.get("quote"))
    total_hitokoto = sum(1 for r in all_records.values() if r.get("hitokoto"))
    total_poems = sum(1 for r in all_records.values() if r.get("poem"))
    total_bing = sum(1 for r in all_records.values() if r.get("bing"))

    current_month_records = [
        rec
        for dt, rec in sorted(all_records.items(), key=lambda x: x[0], reverse=True)
        if dt.startswith(current_ym)
    ]

    lines = [
        "# ✨ 每日灵感合集（Daily Inspiration）",
        "",
        "> ⏰ 自动更新于 GitHub Actions（北京时间每天 09:00 执行）  ",
        f"> 📊 累计打卡 **{total_days}** 天 · 每日一句 **{total_quotes}** 篇 · 每日一言 **{total_hitokoto}** 条 · 每日诗词 **{total_poems}** 首 · 必应壁纸 **{total_bing}** 张  ",
        "> 💡 为保证最佳阅读体验，本页仅展示**当月最新内容（按日期倒序）**，历史月份请通过下方归档表查阅。",
        "",
        "## 🗂️ 历史月度归档索引",
        "",
        build_archive_summary_table(all_records, link_prefix="archives/"),
        "",
        "---",
        "",
        f"## 📅 {current_ym} 当月灵感记录（共 {len(current_month_records)} 天）",
        "",
    ]

    for idx, rec in enumerate(current_month_records):
        lines.append(render_daily_card(rec, heading_level="###"))
        if idx < len(current_month_records) - 1:
            lines.append("---")
            lines.append("")

    with open(QUOTES_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def update_readme(all_records: dict[str, dict]):
    """更新 README.md 中的动态统计徽章、今日灵感看板与归档导航"""
    if not all_records or not os.path.exists(README_MD_PATH):
        return

    latest_date = max(all_records.keys())
    latest_rec = all_records[latest_date]
    total_days = len(all_records)
    total_poems = sum(1 for r in all_records.values() if r.get("poem"))
    cal = get_calendar_meta(latest_date)
    lunar_badge_text = cal["lunar_text"].replace(" ", "_").replace("-", "--")

    board_lines = [
        "<!-- TODAY_BOARD_START -->",
        '<div align="center">',
        "",
        f"![累计打卡](https://img.shields.io/badge/累计打卡-{total_days}_天-2ea44f?style=for-the-badge&logo=github) "
        f"![收录诗词](https://img.shields.io/badge/收录诗词-{total_poems}_首-0969da?style=for-the-badge&logo=bookstack) "
        f"![农历岁次](https://img.shields.io/badge/岁次-{lunar_badge_text}-8b5cf6?style=for-the-badge) "
        f"![最近更新](https://img.shields.io/badge/最近更新-{latest_date.replace('-', '--')}-f97316?style=for-the-badge&logo=clockify)",
        "",
        "**[🌟 今日看板](#-今日灵感看板)** &nbsp;·&nbsp; "
        "**[📅 当月精选合集](quotes.md)** &nbsp;·&nbsp; "
        "**[🗂️ 历史月度归档](#️-历史月度归档)** &nbsp;·&nbsp; "
        "**[✨ 核心功能](#-核心功能)** &nbsp;·&nbsp; "
        "**[🚀 快速部署](#-快速开始5-分钟部署)**",
        "",
        "</div>",
        "",
        "---",
        "",
        "## 🌟 今日灵感看板",
        "",
        render_daily_card(latest_rec, heading_level="###").rstrip(),
        "",
        "---",
        "",
        "## 🗂️ 历史月度归档",
        "",
        "> 📁 完整结构化数据存储于 [`data/`](data/) 目录，按月归档 Markdown 存储于 [`archives/`](archives/) 目录，当月最新汇总请查看 [`quotes.md`](quotes.md)。",
        "",
        build_archive_summary_table(all_records, link_prefix="archives/"),
        "<!-- TODAY_BOARD_END -->",
    ]
    board_block = "\n".join(board_lines)

    with open(README_MD_PATH, "r", encoding="utf-8") as f:
        readme_text = f.read()

    if "<!-- TODAY_BOARD_START -->" in readme_text and "<!-- TODAY_BOARD_END -->" in readme_text:
        pattern = re.compile(
            r"<!-- TODAY_BOARD_START -->.*?<!-- TODAY_BOARD_END -->", re.S
        )
        new_readme = pattern.sub(board_block, readme_text)
    else:
        target = "## ✨ 核心功能"
        if target in readme_text:
            new_readme = readme_text.replace(target, f"{board_block}\n\n{target}", 1)
        else:
            new_readme = readme_text + "\n\n" + board_block + "\n"

    with open(README_MD_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme)


def render_all_views(all_records: dict[str, dict]):
    """根据全量记录渲染所有归档文件、quotes.md 和 README.md"""
    grouped: dict[str, dict[str, dict]] = {}
    for dt, rec in all_records.items():
        ym = dt[:7]
        grouped.setdefault(ym, {})[dt] = rec

    for ym, m_recs in sorted(grouped.items()):
        render_monthly_archive_file(ym, m_recs)

    render_quotes_md(all_records)
    update_readme(all_records)


# -------------------------- 历史 quotes.md 数据迁移解析 --------------------------
def migrate_from_legacy_quotes_md() -> dict[str, dict]:
    """从旧版平铺的 quotes.md 中无损提取全部历史记录并保存为 JSON"""
    if not os.path.exists(QUOTES_MD_PATH):
        print("⚠️ quotes.md 不存在，跳过迁移")
        return {}

    with open(QUOTES_MD_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    blocks = re.split(r"^## (\d{4}-\d{2}-\d{2}) 每日内容汇总\n", text, flags=re.M)[1:]
    if not blocks:
        print("ℹ️ quotes.md 已是新版格式或不包含旧版汇总块")
        return load_all_data()

    migrated: dict[str, dict] = load_all_data()
    count = 0

    for i in range(0, len(blocks), 2):
        dt = blocks[i].strip()
        body = blocks[i + 1]
        rec = migrated.get(
            dt, {"date": dt, "quote": None, "bing": None, "hitokoto": None, "poem": None}
        )

        m_quote = re.search(
            r"### 📚 每日一句\n- 英文：(.*?)\n- 中文翻译：(.*?)\n- 英文播放：\[点击收听\]\((.*?)\)\n- 分享图片：!\[每日一句\]\((.*?)\)",
            body,
            re.S,
        )
        if m_quote:
            rec["quote"] = {
                "english": m_quote.group(1).strip(),
                "chinese": m_quote.group(2).strip(),
                "tts_url": m_quote.group(3).strip(),
                "img_url": m_quote.group(4).strip(),
            }

        m_hitokoto = re.search(
            r"### 💬 每日一言\n> (.*?)(?=\n\n### |\n*$)", body, re.S
        )
        if m_hitokoto:
            existing_h = rec.get("hitokoto") or {}
            rec["hitokoto"] = {
                "content": m_hitokoto.group(1).strip(),
                "from": existing_h.get("from", ""),
                "from_who": existing_h.get("from_who", ""),
                "category": existing_h.get("category", ""),
            }

        m_poem = re.search(
            r"### 📜 每日诗词\n- 标题：(.*?)\n- 朝代/作者：(.*?) · (.*?)\n- 内容：\n```\n(.*?)\n```",
            body,
            re.S,
        )
        if m_poem:
            existing_p = rec.get("poem") or {}
            rec["poem"] = {
                "title": m_poem.group(1).strip(),
                "dynasty": m_poem.group(2).strip(),
                "author": m_poem.group(3).strip(),
                "content": m_poem.group(4).strip(),
                "summary": existing_p.get("summary", ""),
                "tags": existing_p.get("tags", []),
            }

        migrated[dt] = rec
        count += 1

    save_all_data(migrated)
    print(f"✅ 成功从旧版 quotes.md 迁移 {count} 天的历史数据到 data/*.json")
    return dict(sorted(migrated.items(), key=lambda x: x[0]))


# -------------------------- 主流程入口 --------------------------
def main():
    parser = argparse.ArgumentParser(description="Daily Inspiration 每日灵感采集与归档工具")
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="将旧版 quotes.md 历史数据迁移到 data/*.json 并重新生成所有归档与看板",
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="仅根据现有 data/*.json 重新渲染 quotes.md、archives/*.md 和 README.md（不调用 API）",
    )
    args = parser.parse_args()

    if args.migrate:
        all_records = migrate_from_legacy_quotes_md()
        render_all_views(all_records)
        print("🎉 历史数据迁移、月度归档拆分及 README 看板渲染全部完成！")
        return

    all_records = load_all_data()
    if args.render_only:
        render_all_views(all_records)
        print("🎉 所有 Markdown 视图与看板已重新渲染完成！")
        return

    # 默认每日采集流程
    today = get_today_str()
    print(f"📢 开始采集 {today} 每日灵感内容...")
    today_record = collect_daily_record(today, all_records)

    # 幂等合并：如果当日已有部分成功记录，新采集成功的字段覆盖，失败字段保留当日已有值
    existing_today = all_records.get(today, {})
    merged_record = {
        "date": today,
        "quote": today_record.get("quote") or existing_today.get("quote"),
        "bing": today_record.get("bing") or existing_today.get("bing"),
        "hitokoto": today_record.get("hitokoto") or existing_today.get("hitokoto"),
        "poem": today_record.get("poem") or existing_today.get("poem"),
    }
    all_records[today] = merged_record

    # 顺便回填近期缺失的必应 4K 壁纸（最多支持回填近 15 天）
    backfill_recent_bing_wallpapers(all_records)

    # 保存当月 JSON 并全量刷新视图
    current_ym = today[:7]
    month_records = {
        dt: rec for dt, rec in all_records.items() if dt.startswith(current_ym)
    }
    save_month_data(current_ym, month_records)
    render_all_views(all_records)

    success_cnt = sum(
        1 for k in ("quote", "bing", "hitokoto", "poem") if merged_record.get(k) is not None
    )
    print(f"✅ 所有操作完成！{today} 成功记录 {success_cnt}/{len(API_CONFIGS)} 个接口内容")


if __name__ == "__main__":
    main()
