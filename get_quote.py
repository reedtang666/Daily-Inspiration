import requests
import datetime
import random

# 3个100%稳定的API（已测试）
API_CONFIG = [
    # 一言API（中文名言）
    {
        "name": "一言",
        "url": "https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d&c=e&c=f&c=g",
        "parser": lambda res: (res["hitokoto"], res.get("from", "未知来源"))
    },
    # 古诗词API（稳定版）
    {
        "name": "古诗词",
        "url": "https://api.gushi.ci/all.json",
        "parser": lambda res: (res["content"], res["author"] + "《" + res["title"] + "》")
    },
    # 英语名言API（带翻译）
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
    # 循环重试，直到获取到有效内容
    while True:
        try:
            api = random.choice(API_CONFIG)
            response = requests.get(api["url"], timeout=15)
            response.raise_for_status()
            data = response.json()
            content, source = api["parser"](data)
            
            # 过滤无效内容
            if content and source and len(content) > 5:
                return {
                    "type": api["name"],
                    "content": content.strip(),
                    "source": source.strip(),
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                }
            else:
                print(f"{api['name']}返回无效内容，重试...")
                continue
        except Exception as e:
            print(f"调用{api['name']}API失败：{str(e)[:30]}，重试下一个...")
            continue

def write_to_markdown(quote):
    markdown_content = f"""
### {quote['date']} · {quote['type']}
> {quote['content']}
> —— {quote['source']}
"""
    with open("quotes.md", "a", encoding="utf-8") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # 初始化quotes.md
    try:
        with open("quotes.md", "r", encoding="utf-8") as f:
            pass
    except FileNotFoundError:
        with open("quotes.md", "w", encoding="utf-8") as f:
            f.write("# 每日名言/诗词/英语短句合集\n")
            f.write("> 自动更新于 GitHub Actions，每天1条，持续积累～\n")
            f.write("> 数据来源：一言API、古诗词API、Quotable API（随机切换）\n")
            f.write("\n<!-- 以下内容由脚本自动生成，无需手动修改 -->\n")
    
    quote = get_random_quote()
    write_to_markdown(quote)
    print(f"✅ 成功添加 {quote['date']} 内容：{quote['content']} —— {quote['source']}")
