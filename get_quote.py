import requests
import datetime
import random
import os

# -------------------------- 替换为「国内稳定API」（GitHub Actions环境可用）--------------------------
API_CONFIG = [
    # 1. 中文名言（国内稳定接口，无缓存）
    {
        "name": "中文名言",
        "url": "https://api.iyk0.com/mingyan/?format=json",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: (res["content"], res.get("author", "未知作者"))
    },
    # 2. 古诗词（诗词名句网，国内节点，稳定）
    {
        "name": "古诗词",
        "url": "https://api.shicimingju.com/api/route.php?type=json&do=randomOne",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: (res["content"], res["author"] + "《" + res["title"] + "》")
    },
    # 3. 英语短句（国内接口，带中文翻译，无地域限制）
    {
        "name": "英语短句",
        "url": "https://api.iyk0.com/english/?format=json",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: (
            f'"{res["content"]}"（中文翻译：{res.get("translation", "暂无")}）',
            res.get("author", "Unknown")
        )
    }
]

def load_existing_quotes():
    """读取已有内容去重（保留原逻辑）"""
    existing_set = set()
    if not os.path.exists("quotes.md"):
        return existing_set
    
    with open("quotes.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip().startswith("> ") and not line.strip().startswith("> ——"):
                content = line.strip()[2:].strip()
                if content and len(content) > 5:
                    existing_set.add(content.replace("　", " ").replace("\"", "'"))
    return existing_set

def get_random_quote(existing_quotes):
    """优化请求策略：增加请求头、调整重试逻辑，确保成功率"""
    max_retries = 15  # 合理重试次数（新API稳定，无需20次）
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            api = random.choice(API_CONFIG)
            retry_count += 1
            
            # 防缓存：添加随机参数（新API也需要，避免重复）
            url = api["url"] + f"&rand={random.randint(10000, 99999)}"
            
            # 发送请求：带浏览器请求头（避免被API拦截），超时延长到20s
            response = requests.get(
                url,
                headers=api["headers"],
                timeout=20,
                verify=False  # 忽略SSL证书验证（部分国内API可能证书不规范）
            )
            response.raise_for_status()
            
            # 解析JSON（处理可能的编码问题）
            try:
                data = response.json()
            except ValueError:
                # 若返回非JSON格式，尝试用UTF-8解码后再解析
                response.encoding = "utf-8"
                data = response.json()
            
            content, source = api["parser"](data)
            
            # 过滤：有效+未重复
            normalized_content = content.strip().replace("　", " ").replace("\"", "'")
            if content and source and len(content) > 5 and normalized_content not in existing_quotes:
                return {
                    "type": api["name"],
                    "content": content.strip(),
                    "source": source.strip(),
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                }
            else:
                print(f"❌ {api['name']}内容无效/重复：{content[:20]}...，重试第{retry_count}次")
                continue
        
        except Exception as e:
            error_msg = str(e)[:50]  # 显示完整错误信息，方便排查
            print(f"❌ 调用{api['name']}API失败：{error_msg}，重试第{retry_count}次")
            continue
    
    # 重试失败后，抛出友好异常（避免无意义循环）
    raise Exception(f"⚠️  重试{max_retries}次后仍未获取内容，建议检查API是否正常")

def write_to_markdown(quote):
    """保持原格式不变"""
    markdown_content = f"""
### {quote['date']} · {quote['type']}
> {quote['content']}
> —— {quote['source']}
"""
    with open("quotes.md", "a", encoding="utf-8") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # 1. 读取已有内容去重
    existing_quotes = load_existing_quotes()
    print(f"📊 已存在 {len(existing_quotes)} 条不重复内容")
    
    # 2. 初始化文件（若不存在）
    if not os.path.exists("quotes.md"):
        with open("quotes.md", "w", encoding="utf-8") as f:
            f.write("# 每日名言/诗词/英语短句合集\n")
            f.write("> 自动更新于 GitHub Actions，每天1条，持续积累～\n")
            f.write("> 数据来源：国内稳定公开API（中文名言、古诗词、英语短句）\n")
            f.write("\n<!-- 以下内容由脚本自动生成，无需手动修改 -->\n")
    
    # 3. 获取新内容并写入
    quote = get_random_quote(existing_quotes)
    write_to_markdown(quote)
    print(f"✅ 成功添加 {quote['date']} · {quote['type']}：")
    print(f"内容：{quote['content']}")
    print(f"来源：{quote['source']}")
