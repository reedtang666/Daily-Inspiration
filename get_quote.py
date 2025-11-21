import requests
import datetime
import random

# -------------------------- 配置：3个稳定公开API（无需申请key）--------------------------
API_CONFIG = [
    # 1. 一言API（中文名言/短句，支持不同分类）
    {
        "name": "一言",
        "url": "https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d&c=e&c=f&c=g",  # a-g覆盖各类名言
        "parser": lambda res: (res["hitokoto"], res.get("from", "未知来源"))  # 提取内容和来源
    },
    # 2. 古诗词API（随机诗句）
    {
        "name": "古诗词",
        "url": "https://v2.jinrishici.com/sentence",
        "parser": lambda res: (res["data"]["content"], res["data"]["author"] + "《" + res["data"]["origin"] + "》")
    },
    # 3. 英语名言API（英文名言+中文翻译）
    {
        "name": "英语短句",
        "url": "https://api.quotable.io/random",
        "parser": lambda res: (f'"{res["content"]}" (中文翻译：{res["translation"] if "translation" in res else "暂无"})', res["author"])
    }
]

def get_random_quote():
    """随机调用一个API，获取名言/诗词/英语短句"""
    while True:
        try:
            # 随机选一个API
            api = random.choice(API_CONFIG)
            response = requests.get(api["url"], timeout=10)
            response.raise_for_status()  # 抛出HTTP错误
            data = response.json()
            content, source = api["parser"](data)
            return {
                "type": api["name"],
                "content": content.strip(),
                "source": source.strip(),
                "date": datetime.date.today().strftime("%Y-%m-%d")
            }
        except Exception as e:
            print(f"调用{api['name']}API失败：{e}，尝试下一个...")
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
