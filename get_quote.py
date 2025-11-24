import requests
import datetime
import os

# -------------------------- 三个指定API配置（修改显示名称）--------------------------
API_CONFIGS = [
    # 1. 每日一句
    {
        "name": "每日一句",  # 修改名称
        "url": "http://open.iciba.com/dsapi/",
        "method": "GET",
        "retry_count": 3,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: {
            "type": "每日一句",  # 修改返回类型名称
            "english": res["content"],
            "chinese": res["note"],
            "tts_url": res["tts"],
            "img_url": res["fenxiang_img"],
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
    },
    # 2. 每日一言
    {
        "name": "每日一言",  # 修改名称
        "url": "https://v1.hitokoto.cn/",
        "method": "GET",
        "retry_count": 3,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: {
            "type": "每日一言",  # 修改返回类型名称
            "content": res["hitokoto"],
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
    },
    # 3. 每日诗词
    {
        "name": "每日诗词",  # 修改名称
        "url": "https://v2.jinrishici.com/one.json",
        "method": "GET",
        "retry_count": 3,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "parser": lambda res: {
            "type": "每日诗词",  # 修改返回类型名称
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
    """将结果写入quotes.md（同步修改显示名称）"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    markdown_content = "\n## " + today + " 每日内容汇总\n"
    
    if not results:
        markdown_content += "> 今日暂无数据（三个接口均调用失败）\n"
    else:
        for res in results:
            if res["type"] == "每日一句":  # 匹配修改后的名称
                part = "\n### 📚 " + res['type'] + "\n"
                part += "- 英文：" + res['english'] + "\n"
                part += "- 中文翻译：" + res['chinese'] + "\n"
                part += "- 英文播放：[点击收听](" + res['tts_url'] + ")\n"
                part += "- 分享图片：![每日一句](" + res['img_url'] + ")\n"
                markdown_content += part
            
            elif res["type"] == "每日一言":  # 匹配修改后的名称
                part = "\n### 💬 " + res['type'] + "\n"
                part += "> " + res['content'] + "\n"
                markdown_content += part
            
            elif res["type"] == "每日诗词":  # 匹配修改后的名称
                part = "\n### 📜 " + res['type'] + "\n"
                part += "- 标题：" + res['title'] + "\n"
                part += "- 朝代/作者：" + res['dynasty'] + " · " + res['author'] + "\n"
                part += "- 内容：\n```\n" + res['content'] + "\n```\n"
                markdown_content += part
    
    # 追加到文件（不覆盖历史）
    with open("quotes.md", "a", encoding="utf-8") as f:
        f.write(markdown_content)

if __name__ == "__main__":
    # 初始化quotes.md（若不存在）
    if not os.path.exists("quotes.md"):
        with open("quotes.md", "w", encoding="utf-8") as f:
            f.write("# 每日内容合集（每日一句+每日一言+每日诗词）\n")  # 同步修改标题
            f.write("> 自动更新于 GitHub Actions（北京时间每天9点执行）\n")
            f.write("> 包含：每日一句（金山词霸）、每日一言、每日诗词，调用失败会重试3次\n")  # 同步说明
            f.write("\n<!-- 以下内容由脚本自动生成，无需手动修改 -->\n")
    
    # 核心流程：收集结果 → 写入文件
    print("📢 开始调用所有API...")
    results = collect_all_results()
    write_to_markdown(results)
    print(f"✅ 所有操作完成！成功记录 {len(results)}/{len(API_CONFIGS)} 个接口内容")
