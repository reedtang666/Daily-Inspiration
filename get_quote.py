import requests
import datetime
import os

# -------------------------- 三个指定API配置（按需求定义）--------------------------
API_CONFIGS = [
    # 1. 每日一句
    {
        "name": "每日一句",
        "url": "http://open.iciba.com/dsapi/",
        "method": "GET",
        "retry_count": 3,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: {
            "type": "金山词霸每日一句",
            "english": res["content"],
            "chinese": res["note"],
            "tts_url": res["tts"],
            "img_url": res["fenxiang_img"],
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
    },
    # 2. 今日一言
    {
        "name": "今日一言",
        "url": "https://v1.hitokoto.cn/",
        "method": "GET",
        "retry_count": 3,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: {
            "type": "一言",
            "content": res["hitokoto"],
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
    },
    # 3. 今日诗词
    {
        "name": "今日诗词",
        "url": "https://v2.jinrishici.com/one.json",
        "method": "GET",
        "retry_count": 3,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: {
            "type": "今日诗词",
            "title": res["data"]["origin"]["title"],
            "dynasty": res["data"]["origin"]["dynasty"],
            "author": res["data"]["origin"]["author"],
            "content": "\n".join(res["data"]["origin"]["content"]),  # 诗词分行展示
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
    }
]

def call_api(api_config):
    """调用单个API，带重试机制（最多3次）"""
    api_name = api_config["name"]
    url = api_config["url"]
    headers = api_config["headers"]
    parser = api_config["parser"]
    max_retries = api_config["retry_count"]
    
    for retry in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=15,
                verify=False,  # 忽略SSL证书问题
                allow_redirects=True
            )
            response.raise_for_status()  # 抛出HTTP错误（4xx/5xx）
            
            # 解析JSON
            response.encoding = response.apparent_encoding or "utf-8"
            data = response.json()
            result = parser(data)
            print(f"✅ {api_name} 调用成功")
            return result
        
        except Exception as e:
            error_msg = str(e)[:50]
            if retry < max_retries:
                print(f"❌ {api_name} 调用失败（第{retry}次）：{error_msg}，重试...")
                continue
            else:
                print(f"❌ {api_name} 重试{max_retries}次后仍失败：{error_msg}")
                return None

def collect_all_results():
    """调用所有API，收集成功结果"""
    results = []
    for api in API_CONFIGS:
        result = call_api(api)
        if result:
            results.append(result)
    return results

def write_to_markdown(results):
    """将结果写入quotes.md（按API类型整理格式）"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    markdown_content = f"\n## {today} 每日内容汇总\n"  # 按日期分组
    
    if not results:
        markdown_content += "> 今日暂无数据（三个接口均调用失败）\n"
    else:
        for res in results:
            if res["type"] == "每日一句":
                # 金山词霸格式：英文+中文+链接+图片
                markdown_content += f"""
### 📚 {res['type']}
- 英文：{res['english']}
- 中文翻译：{res['chinese']}
- 英文播放：[点击收听]({res['tts_url']})
- 分享图片：![每日一句]({res['img_url']})
"""
            elif res["type"] == "今日一言":
                # 一言格式：纯文字
                markdown_content += f"""
### 💬 {res['type']}
> {res['content']}
"""
            elif res["type"] == "今日诗词":
                # 今日诗词格式：标题+朝代+作者+诗词内容
                markdown_content += f"""
### 📜 {res['type']}
- 标题：{res['title']}
- 朝代/作者：{res['dynasty']} · {res['author']}
- 内容：
