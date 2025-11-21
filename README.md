# Daily-Inspiration: 每日名言/诗词/英语短句自动收集项目

一个 **全自动化、零手动操作** 的灵感收集项目，每天通过 GitHub Actions 定时抓取名言、古诗词、英语励志短句，自动写入文档并提交到 GitHub，持续积累属于你的「灵感知识库」。

## ✨ 核心功能
- **自动更新**：每天 UTC 时间 0 点（北京时间 8 点）自动运行，无需手动触发；
- **多源数据**：随机切换 3 个稳定公开 API，覆盖中文名言、古诗词、英语励志短句；
- **格式统一**：所有内容按「日期 + 类型 + 内容 + 来源」整理，美观易读；
- **零成本部署**：基于 GitHub 免费服务，无需服务器，fork 即可使用；
- **可扩展**：支持新增 API 源、自定义内容格式、生成静态展示页面。

## 📋 项目展示
### 内容示例（`quotes.md`）
```markdown
# 每日名言/诗词/英语短句合集
> 自动更新于 GitHub Actions，每天1条，持续积累～
> 数据来源：一言API、古诗词API、Quotable API（随机切换）

<!-- 以下内容由脚本自动生成，无需手动修改 -->

### 2025-11-21 · 古诗词
> 春风得意马蹄疾，一日看尽长安花。
> —— 孟郊《登科后》

### 2025-11-22 · 英语短句
> "The only way to do great work is to love what you do."（中文翻译：成就伟大事业的唯一途径是热爱你所做的事）
> —— Steve Jobs

### 2025-11-23 · 一言
> 人生没有白走的路，每一步都算数。
> —— 未知来源
```

### GitHub 提交记录
每天自动生成规范的提交信息，保持绿色贡献图：
- `feat: add 2025-11-21 quote`
- `feat: add 2025-11-22 quote`

## 🛠️ 技术栈
- **核心脚本**：Python 3.10+（简洁易维护，仅依赖 `requests` 库）；
- **自动化工具**：GitHub Actions（定时任务 + 自动提交代码）；
- **数据存储**：Markdown（轻量、易读、可检索）；
- **API 来源**：
  - 一言 API：提供中文名言/短句；
  - 古诗词 API：提供随机诗句 + 作者/标题；
  - Quotable API：提供英语励志名言 + 中文翻译。

## 🚀 快速开始（5 分钟部署）
### 1. Fork 仓库
点击 GitHub 仓库右上角「Fork」，将项目复制到你的账号下。

### 2. 确认文件完整性
Fork 后，仓库应包含以下核心文件（无需修改，直接使用）：
```
Daily-Inspiration/
├─ quotes.md          # 自动更新的内容合集
├─ get_quote.py       # 核心爬虫脚本
├─ requirements.txt   # 依赖库（仅 requests）
└─ .github/
   └─ workflows/
      └─ auto-submit.yml  # GitHub Actions 配置
```

### 3. 手动测试（可选）
为确保正常运行，可手动触发一次工作流：
1. 进入你的仓库 → 点击顶部「Actions」；
2. 左侧选择「Auto Add Daily Quote」；
3. 点击右侧「Run workflow」→ 再次点击「Run workflow」；
4. 等待 1-2 分钟，若所有步骤显示绿色对勾，说明运行成功；
5. 打开 `quotes.md`，会发现新增了一条当日内容。

### 4. 完成！
之后每天会自动运行，无需任何手动操作，持续积累内容～

## ⚙️ 自定义配置（可选）
### 1. 修改定时时间
编辑 `.github/workflows/auto-submit.yml` 中的 `cron` 表达式，调整自动更新时间（UTC 时区）：
```yaml
schedule:
  - cron: '0 0 * * *'  # 默认：UTC 0 点（北京时间 8 点）
```
- 若想改为北京时间每天凌晨 1 点：`cron: '15 17 * * *'`（UTC 17:15 = 北京时间 01:15）；
- 时区换算工具：[Cron 时区转换](https://crontab.guru/time-zones.html)。

### 2. 新增/替换 API 源
编辑 `get_quote.py` 中的 `API_CONFIG` 列表，可添加自定义 API：
```python
API_CONFIG = [
    # 原有配置...
    # 新增：网易云热评 API（示例）
    {
        "name": "网易云热评",
        "url": "https://api.uomg.com/api/rand.music.comment?format=json",
        "parser": lambda res: (res["content"], "网易云音乐热评")
    }
]
```
- 需确保 API 返回 JSON 格式，且 `parser` 函数能正确提取「内容」和「来源」。

### 3. 修改内容格式
编辑 `get_quote.py` 中的 `write_to_markdown` 函数，自定义输出格式：
```python
def write_to_markdown(quote):
    # 示例：添加标签和分隔线
    markdown_content = f"""
---
### {quote['date']} · {quote['type']} 🏷️
> {quote['content']}
> —— {quote['source']}
"""
    with open("quotes.md", "a", encoding="utf-8") as f:
        f.write(markdown_content)
```

### 4. 仅保留某类内容
若只想收集古诗词，删除 `API_CONFIG` 中其他配置：
```python
API_CONFIG = [
    # 仅保留古诗词 API
    {
        "name": "古诗词",
        "url": "https://api.gushi.ci/all.json",
        "parser": lambda res: (res["content"], res["author"] + "《" + res["title"] + "》")
    }
]
```

## 📈 扩展方向
1. **静态网页展示**：用 Vue/React 或 Hugo/Gatsby 读取 `quotes.md`，生成个人灵感网站；
2. **数据可视化**：用 Python 的 `matplotlib` 或 `pyecharts` 统计内容类型分布、月度更新数量；
3. **多语言支持**：新增日语、法语等名言 API，按标签分类；
4. **邮件推送**：集成 SMTP 服务，每天将新内容推送至邮箱；
5. **内容筛选**：添加关键词过滤，只保留符合主题的内容（如「编程」「成长」）。

## ❌ 常见问题排查
### 1. GitHub Actions 运行失败？
- 查看日志：进入「Actions」→ 点击失败任务 → 展开标红步骤，查看具体错误；
- 权限问题：确保 `auto-submit.yml` 中已配置 `permissions: contents: write` 和 `token: ${{ secrets.GITHUB_TOKEN }}`；
- API 调用失败：脚本会自动重试下一个 API，若所有 API 都失败，检查网络或替换为其他 API。

### 2. quotes.md 无新增内容？
- 检查脚本是否生成内容：本地运行 `python get_quote.py`，看是否输出「成功添加」日志；
- 检查 Git 提交：查看 Actions 日志中「Commit and push changes」步骤，是否显示「No changes to commit」。

### 3. 中文乱码？
- 脚本中已指定 `encoding="utf-8"`，确保本地文件编码为 UTF-8 即可。

## 🤝 贡献指南
欢迎提交 PR 或 Issues 改进项目：
1. Fork 仓库；
2. 创建分支：`git checkout -b feature/xxx`；
3. 提交修改：`git commit -m "feat: add xxx function"`；
4. 推送分支：`git push origin feature/xxx`；
5. 提交 PR。

## 📄 许可证
本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

---

✨ 持续积累，让每一次提交都成为成长的见证～  
如果觉得项目有用，欢迎 Star 支持！🌟  
仓库地址：[reedtang666/Daily-Inspiration](https://github.com/reedtang666/Daily-Inspiration)
```

✨ 持续积累，让每一次提交都成为成长的见证～
如果觉得项目有用，欢迎 Star 支持！
🌟仓库地址：reedtang666/Daily-Inspiration
