import requests
import datetime
import random

# -------------------------- 简化版：去掉Retry依赖，直接调用API（更稳定）--------------------------
API_CONFIG = [
    # 1. 一言API（稳定，支持多分类）
    {
        "name": "一言",
        "url": "https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d&c=e&c=f&c=g",
        "parser": lambda res: (res["hitokoto"], res.get("from", "未知来源"))
    },
    # 2. 古诗词API（稳定版）
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
    """简化版：直接调用API，失败自动重试下一个，无需Retry类"""
    while True:
        try:
            api = random.choice(API_CONFIG)
            # 超时时间设为15s，避免卡壳
            response = requests.get(api["url"], timeout=15)
            response.raise_for_status()  # 抛出HTTP错误（比如404、500）
            data = response.json()
            content, source = api["parser"](data)
            
            # 过滤空内容，确保提交有效
            if content and source and len(content) > 5:
                return {
                    "type": api["name"],
                    "content": content.strip(),
                    "source": source.strip(),
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                }
            else:
                print(f"{api['name']}返回无效内容，尝试下一个API...")
                continue
        except Exception as e:
            # 捕获所有异常，打印简要信息，继续尝试下一个API
            print(f"调用{api['name']}API失败：{str(e)[:30]}，尝试下一个...")
            continue

def write_to_markdown(quote):
    """将内容写入quotes.md，格式不变"""
    markdown_content = f"""
### {quote['date']} · {quote['type']}
> {quote['content']}
> —— {quote['source']}
"""
    # 追加模式写入，编码设为utf-8避免中文乱码
    with open("quotes.md", "a", encoding="utf-8") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # 初始化quotes.md（如果文件不存在则创建）
    try:
        with open("quotes.md", "r", encoding="utf-8") as f:
            pass  # 文件存在，不做操作
    except FileNotFoundError:
        with open("quotes.md", "w", encoding="utf-8") as f:
            f.write("# 每日名言/诗词/英语短句合集\n")
            f.write("> 自动更新于 GitHub Actions，每天1条，持续积累～\n")
            f.write("> 数据来源：一言API、古诗词API、Quotable API（随机切换）\n")
            f.write("\n<!-- 以下内容由脚本自动生成，无需手动修改 -->\n")
    
    # 核心流程：获取内容 → 写入文件 → 打印日志（供Actions查看）
    quote = get_random_quote()
    write_to_markdown(quote)
    print(f"✅ 成功添加 {quote['date']} 的{quote['type']}：")
    print(f"内容：{quote['content']}")
    print(f"来源：{quote['source']}")
