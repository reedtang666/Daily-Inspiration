import requests
import datetime
import random
import os

# 3个100%稳定的API（已测试，添加防缓存参数）
API_CONFIG = [
    # 一言API（中文名言）- 加timestamp参数破缓存
    {
        "name": "一言",
        "url": "https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d&c=e&c=f&c=g&timestamp={timestamp}",
        "parser": lambda res: (res["hitokoto"], res.get("from", "未知来源"))
    },
    # 古诗词API（稳定版）- 加random参数破缓存
    {
        "name": "古诗词",
        "url": "https://api.gushi.ci/all.json?random={random}",
        "parser": lambda res: (res["content"], res["author"] + "《" + res["title"] + "》")
    },
    # 英语名言API（带翻译）- 加ts参数破缓存
    {
        "name": "英语短句",
        "url": "https://api.quotable.io/random?tags=inspire&ts={timestamp}",
        "parser": lambda res: (
            f'"{res["content"]}"（中文翻译：{res.get("translation", "暂无")}）',
            res["author"]
        )
    }
]

def load_existing_quotes():
    """读取quotes.md中已有的内容，返回去重后的内容集合（避免重复）"""
    existing_set = set()
    if not os.path.exists("quotes.md"):
        return existing_set
    
    # 读取文件，提取所有名言内容（去重关键）
    with open("quotes.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            # 匹配名言内容行（格式：> 内容）
            if line.strip().startswith("> ") and not line.strip().startswith("> ——"):
                # 提取内容（去掉开头的"> "和末尾的换行/空格）
                content = line.strip()[2:].strip()
                if content and len(content) > 5:
                    existing_set.add(content)
    return existing_set

def get_random_quote(existing_quotes):
    """循环重试，直到获取到「未重复+有效」的内容"""
    max_retries = 20  # 最大重试次数（避免无限循环）
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            api = random.choice(API_CONFIG)
            retry_count += 1
            
            # 生成随机参数（破缓存关键：每次请求参数不同）
            timestamp = int(datetime.datetime.now().timestamp() * 1000)  # 时间戳（毫秒级）
            random_num = random.randint(10000, 99999)  # 随机5位数
            
            # 替换URL中的占位符，添加防缓存参数
            url = api["url"].format(timestamp=timestamp, random=random_num)
            
            # 发送请求（超时15s）
            response = requests.get(url, timeout=15)
            response.raise_for_status()  # 抛出HTTP错误
            data = response.json()
            content, source = api["parser"](data)
            
            # 过滤条件：内容有效 + 未重复
            if content and source and len(content) > 5:
                # 统一格式（避免因空格/标点差异导致的重复）
                normalized_content = content.strip().replace("　", " ").replace("\"", "'")
                if normalized_content not in existing_quotes:
                    return {
                        "type": api["name"],
                        "content": content.strip(),
                        "source": source.strip(),
                        "date": datetime.date.today().strftime("%Y-%m-%d")
                    }
                else:
                    print(f"❌ {api['name']}返回重复内容：{content[:20]}...，重试第{retry_count}次")
                    continue
            else:
                print(f"❌ {api['name']}返回无效内容，重试第{retry_count}次")
                continue
        
        except Exception as e:
            error_msg = str(e)[:30]
            print(f"❌ 调用{api['name']}API失败：{error_msg}，重试第{retry_count}次")
            continue
    
    # 重试次数耗尽仍未获取到有效内容，抛出异常（触发Actions失败，方便排查）
    raise Exception(f"⚠️  重试{max_retries}次后仍未获取到有效内容，请检查API可用性")

def write_to_markdown(quote):
    """写入quotes.md，格式不变"""
    markdown_content = f"""
### {quote['date']} · {quote['type']}
> {quote['content']}
> —— {quote['source']}
"""
    with open("quotes.md", "a", encoding="utf-8") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # 1. 读取已有内容，用于去重
    existing_quotes = load_existing_quotes()
    print(f"📊 已存在 {len(existing_quotes)} 条不重复内容")
    
    # 2. 初始化quotes.md（如果文件不存在）
    if not os.path.exists("quotes.md"):
        with open("quotes.md", "w", encoding="utf-8") as f:
            f.write("# 每日名言/诗词/英语短句合集\n")
            f.write("> 自动更新于 GitHub Actions，每天1条，持续积累～\n")
            f.write("> 数据来源：一言API、古诗词API、Quotable API（随机切换）\n")
            f.write("\n<!-- 以下内容由脚本自动生成，无需手动修改 -->\n")
    
    # 3. 获取不重复的新内容
    quote = get_random_quote(existing_quotes)
    
    # 4. 写入文件并打印日志
    write_to_markdown(quote)
    print(f"✅ 成功添加 {quote['date']} · {quote['type']}：")
    print(f"内容：{quote['content']}")
    print(f"来源：{quote['source']}")
