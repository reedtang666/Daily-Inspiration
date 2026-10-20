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


def get_today_str() -> str:
    """获取北京时间当日日期字符串 YYYY-MM-DD"""
    return datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d")


def format_weekday(date_str: str) -> str:
    """根据 YYYY-MM-DD 返回中文星期"""
    try:
        dt = datetime.date.fromisoformat(date_str)
        return WEEKDAY_MAP.get(dt.weekday(), "")
    except ValueError:
        return ""


# -------------------------- 三个指定 API 配置 --------------------------
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
            "english": res.get("content", "").strip(),
            "chinese": res.get("note", "").strip(),
            "tts_url": res.get("tts", "").strip(),
            "img_url": res.get("fenxiang_img", "").strip(),
            "date": get_today_str(),
        },
    },
    # 2. 每日一言（Hitokoto）
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
            "content": res.get("hitokoto", "").strip(),
            "from": (res.get("from") or "").strip(),
            "from_who": (res.get("from_who") or "").strip(),
            "category": HITOKOTO_TYPE_MAP.get(res.get("type", ""), ""),
            "date": get_today_str(),
        },
    },
    # 3. 每日诗词（今日诗词）
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
        "parser": lambda res: {
            "type": "每日诗词",
            "title": res["data"]["origin"]["title"].strip(),
            "dynasty": res["data"]["origin"]["dynasty"].strip(),
            "author": res["data"]["origin"]["author"].strip(),
            "content": "\n".join(res["data"]["origin"]["content"]).strip(),
            "summary": (res["data"].get("content") or "").strip(),
            "tags": res["data"].get("matchTags") or [],
            "date": get_today_str(),
        },
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


def collect_daily_record(today: str, all_records: dict[str, dict]) -> dict:
    """收集今日所有 API 结果并返回标准化单日记录字典"""
    seen_hitokoto, seen_poems = build_seen_sets(all_records, exclude_date=today)
    record = {"date": today, "quote": None, "hitokoto": None, "poem": None}

    for api in API_CONFIGS:
        res = call_api(api, seen_hitokoto, seen_poems)
        if res:
            # 清理冗余字段，保持 JSON 干净
            clean_res = {k: v for k, v in res.items() if k not in ("type", "date")}
            record[api["key"]] = clean_res

    return record


# -------------------------- Markdown 渲染引擎 --------------------------
def render_daily_card(record: dict, heading_level: str = "##") -> str:
    """将单日数据渲染为精美的 Markdown 灵感卡片"""
    dt = record["date"]
    weekday = format_weekday(dt)
    title_suffix = f" · {weekday}" if weekday else ""
    sub_heading = "#" + heading_level

    lines = [f"{heading_level} 🗓️ {dt}{title_suffix}", ""]

    quote = record.get("quote")
    hitokoto = record.get("hitokoto")
    poem = record.get("poem")

    if not quote and not hitokoto and not poem:
        lines.append("> ⚠️ 今日暂无数据（三个接口均调用失败）")
        lines.append("")
        return "\n".join(lines)

    # 1. 每日一句（图文并排卡片）
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

    # 2. 每日一言（带署名与分类标签）
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
            lines.append(f"> <p align=\"right\">—— {' · '.join(sign_parts)}</p>")
        lines.append("")

    # 3. 每日诗词（古风排版 + 名句高亮 + 标签 + 长诗折叠保护）
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
        "| 月份 | 收录天数 | 每日一句 | 每日一言 | 每日诗词 | 归档直达 |",
        "| :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for ym in sorted(grouped.keys(), reverse=True):
        recs = grouped[ym]
        days_cnt = len(recs)
        q_cnt = sum(1 for r in recs if r.get("quote"))
        h_cnt = sum(1 for r in recs if r.get("hitokoto"))
        p_cnt = sum(1 for r in recs if r.get("poem"))
        lines.append(
            f"| **{ym}** | {days_cnt} 天 | {q_cnt} 篇 | {h_cnt} 条 | {p_cnt} 首 | [📂 查看 {ym} 归档]({link_prefix}{ym}.md) |"
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

    lines = [
        f"# 🗓️ {year_month} 每日灵感归档",
        "",
        "> [⬅️ 返回仓库首页](../README.md) &nbsp;｜&nbsp; [📖 返回当月精选合集](../quotes.md)",
        "",
        f"本月共打卡 **{days_cnt}** 天，累计收录每日一句 **{q_cnt}** 篇、每日一言 **{h_cnt}** 条、每日诗词 **{p_cnt}** 首。",
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

    current_month_records = [
        rec
        for dt, rec in sorted(all_records.items(), key=lambda x: x[0], reverse=True)
        if dt.startswith(current_ym)
    ]

    lines = [
        "# ✨ 每日灵感合集（Daily Inspiration）",
        "",
        "> ⏰ 自动更新于 GitHub Actions（北京时间每天 09:00 执行）  ",
        f"> 📊 累计打卡 **{total_days}** 天 · 每日一句 **{total_quotes}** 篇 · 每日一言 **{total_hitokoto}** 条 · 每日诗词 **{total_poems}** 首  ",
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

    board_lines = [
        "<!-- TODAY_BOARD_START -->",
        '<div align="center">',
        "",
        f"![累计打卡](https://img.shields.io/badge/累计打卡-{total_days}_天-2ea44f?style=for-the-badge&logo=github) "
        f"![收录诗词](https://img.shields.io/badge/收录诗词-{total_poems}_首-0969da?style=for-the-badge&logo=bookstack) "
        f"![最近更新](https://img.shields.io/badge/最近更新-{latest_date.replace('-', '--')}-f97316?style=for-the-badge&logo=clockify)",
        "",
        "</div>",
        "",
        "## 🌟 今日灵感看板",
        "",
        render_daily_card(latest_rec, heading_level="###").rstrip(),
        "",
        "## 🗂️ 历史月度归档",
        "",
        "> 📁 完整结构化数据存储于 [`data/`](data/) 目录，按月归档 Markdown 存储于 [`archives/`](archives/) 目录，当月汇总可查看 [`quotes.md`](quotes.md)。",
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
        # 首次注入：插入在第一段描述之后、「## ✨ 核心功能」之前
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
        rec = migrated.get(dt, {"date": dt, "quote": None, "hitokoto": None, "poem": None})

        # 1. 解析每日一句
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

        # 2. 解析每日一言
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

        # 3. 解析每日诗词
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
        "hitokoto": today_record.get("hitokoto") or existing_today.get("hitokoto"),
        "poem": today_record.get("poem") or existing_today.get("poem"),
    }
    all_records[today] = merged_record

    # 保存当月 JSON 并全量刷新视图
    current_ym = today[:7]
    month_records = {
        dt: rec for dt, rec in all_records.items() if dt.startswith(current_ym)
    }
    save_month_data(current_ym, month_records)
    render_all_views(all_records)

    success_cnt = sum(
        1 for k in ("quote", "hitokoto", "poem") if merged_record.get(k) is not None
    )
    print(f"✅ 所有操作完成！{today} 成功记录 {success_cnt}/{len(API_CONFIGS)} 个接口内容")


if __name__ == "__main__":
    main()
