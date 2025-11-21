import requests
import datetime
import random

def create_session():
    """创建带重试机制的请求会话，避免临时网络问题"""
    session = requests.Session()
    retry = Retry(
        total=3,  # 最多重试3次
        backoff_factor=0.5,  # 重试间隔：0.5s → 1s → 1.5s
        status_forcelist=[429, 500, 502, 503, 504]  # 对这些状态码重试
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

# 稳定 API 列表（替换原有的 API_CONFIG）
API_CONFIG = [
    # 1. 一言API（稳定，支持多分类）
    {
        "name": "一言",
        "url": "https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d&c=e&c=f&c=g",
        "parser": lambda res: (res["hitokoto"], res.get("from", "未知来源"))
    },
    # 2. 古诗词API（替换为稳定版）
    {
        "name": "古诗词",
        "url": "https://api.gushi.ci/all.json",
        "parser": lambda res: (res["content"], res["author"] + "《" + res["title"] + "》")
    },
    # 3. 英语名言API（稳定版，带中文翻译）
    {
        "name": "英语短句",
        "url": "https://api.quotable.io/random?tags=inspire",
        "parser": lambda res: (
            f'"{res["content"]}"（中文翻译：{res.get("translation", "暂无")}）',
            res["author"]
        )
    }
]

def get_random_quote():
    """优化：用带重试的会话调用API，确保成功率"""
    session = create_session()
    while True:
        try:
            api = random.choice(API_CONFIG)
            response = session.get(api["url"], timeout=15)  # 超时时间延长到15s
            response.raise_for_status()
            data = response.json()
            content, source = api["parser"](data)
            # 过滤空内容（避免无效提交）
            if content and source:
                return {
                    "type": api["name"],
                    "content": content.strip(),
                    "source": source.strip(),
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                }
            else:
                print(f"{api['name']}返回空内容，尝试下一个...")
                continue
        except Exception as e:
            print(f"调用{api['name']}API失败：{str(e)[:50]}，尝试下一个...")
            continue

def write_to_markdown(quote):
    """将获取到的内容写入quotes.md"""
    # Markdown格式：日期 + 类型 + 内容 + 来源
    markdown_content = f"""
### {quote['date']} · {quote['type']}
> {quote['content']}
> —— {quote['source']}
"""
    # 追加到文件末尾（没有文件则自动创建）
    with open("quotes.md", "a", encoding="utf-8") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # 初始化quotes.md（如果文件不存在，添加标题）
    try:
        with open("quotes.md", "r", encoding="utf-8") as f:
            pass
    except FileNotFoundError:
        with open("quotes.md", "w", encoding="utf-8") as f:
            f.write("# 每日名言/诗词/英语短句合集\n")
            f.write("> 自动更新于 GitHub Actions，每天1条，持续积累～\n")
    
    # 获取内容并写入
    quote = get_random_quote()
    write_to_markdown(quote)
    print(f"成功添加 {quote['date']} 的{quote['type']}：{quote['content']} —— {quote['source']}")
