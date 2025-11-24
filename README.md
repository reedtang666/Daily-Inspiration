# Daily-Inspiration: 每日内容合集（每日一句+每日一言+每日诗词）

一个 **全自动化、零手动操作** 的每日内容收集项目，每天通过 GitHub Actions 定时调用 3 个指定 API（每日一句、每日一言、每日诗词），全量记录成功结果并自动提交到 GitHub，持续积累属于你的「每日灵感知识库」。

## ✨ 核心功能
- **自动更新**：每天北京时间 9 点（UTC 1 点）自动运行，无需手动触发；
- **全量 API 调用**：固定调用 3 个指定 API，每个 API 失败会自动重试 3 次，成功即记录；
- **格式差异化展示**：按内容类型定制展示格式（英文+翻译+音频+图片/纯文字/诗词详情），美观易读；
- **零成本部署**：基于 GitHub 免费服务，无需服务器，fork 即可使用；
- **兜底容错**：3 个 API 均失败时，记录「今日暂无数据」，确保提交不中断。

## 📋 项目展示
### 内容示例（`quotes.md`）
```markdown
# 每日内容合集（每日一句+每日一言+每日诗词）
> 自动更新于 GitHub Actions（北京时间每天9点执行）
> 包含：每日一句（金山词霸）、每日一言、每日诗词，调用失败会重试3次

<!-- 以下内容由脚本自动生成，无需手动修改 -->

## 2025-11-24 每日内容汇总

### 📚 每日一句
- 英文：The best preparation for tomorrow is doing your best today.
- 中文翻译：对明天最好的准备，就是今天做到最好。
- 英文播放：[点击收听](https://xxx.iciba.com/xxx.mp3)
- 分享图片：![每日一句](https://xxx.iciba.com/xxx.jpg)

### 💬 每日一言
> 人生如逆旅，我亦是行人。

### 📜 每日诗词
- 标题：山居秋暝
- 朝代/作者：唐 · 王维
- 内容：
```
空山新雨后，天气晚来秋。
明月松间照，清泉石上流。
竹喧归浣女，莲动下渔舟。
随意春芳歇，王孙自可留。
```

## 2025-11-23 每日内容汇总

### 📚 每日一句
- 英文：Nothing is impossible to a willing heart.
- 中文翻译：心之所向，无所不成。
- 英文播放：[点击收听](https://xxx.iciba.com/xxx.mp3)
- 分享图片：![每日一句](https://xxx.iciba.com/xxx.jpg)

### 💬 每日一言
> 静水流深，沧笙踏歌。
```

### GitHub 提交记录
每天自动生成规范的提交信息，保持绿色贡献图：
- `feat: add 2025-11-24 daily content`
- `feat: add 2025-11-23 daily content`

## 🛠️ 技术栈
- **核心脚本**：Python 3.10+（简洁易维护，仅依赖 `requests` 库）；
- **自动化工具**：GitHub Actions（定时任务 + 自动提交代码）；
- **数据存储**：Markdown（轻量、易读、可检索）；
- **API 来源（固定 3 个，无需额外申请 Key）**：
  - 每日一句：金山词霸 API（`http://open.iciba.com/dsapi/`）→ 英文+中文翻译+音频+图片；
  - 每日一言：一言 API（`https://v1.hitokoto.cn/`）→ 二次元/网络风格纯文字；
  - 每日诗词：今日诗词 API（`https://v2.jinrishici.com/one.json`）→ 古风诗词（标题+朝代+作者+原文）。

## 🚀 快速开始（5 分钟部署）
### 1. Fork 仓库
点击 GitHub 仓库右上角「Fork」，将项目复制到你的账号下。

### 2. 确认文件完整性
Fork 后，仓库应包含以下核心文件（无需修改，直接使用）：
```
Daily-Inspiration/
├─ quotes.md          # 自动更新的内容合集（按日期分组）
├─ get_quote.py       # 核心脚本（API调用+重试+写入文件）
├─ requirements.txt   # 依赖库（仅 requests==2.32.3）
└─ .github/
   └─ workflows/
      └─ auto-submit.yml  # GitHub Actions 定时任务配置（北京时间9点执行）
```

### 3. 手动测试（可选）
为确保正常运行，可手动触发一次工作流：
1. 进入你的仓库 → 点击顶部「Actions」；
2. 左侧选择「Auto Collect Daily Content」；
3. 点击右侧「Run workflow」→ 再次点击「Run workflow」；
4. 等待 1-2 分钟，若所有步骤显示绿色对勾，说明运行成功；
5. 打开 `quotes.md`，会发现新增当日内容汇总。

### 4. 完成！
之后每天北京时间 9 点会自动运行，无需任何手动操作，持续积累内容～

## ⚙️ 自定义配置（可选）
### 1. 修改定时时间
编辑 `.github/workflows/auto-submit.yml` 中的 `cron` 表达式，调整自动更新时间（UTC 时区，北京时间 = UTC+8）：
```yaml
schedule:
  - cron: '0 1 * * *'  # 默认：UTC 1 点（北京时间 9 点）
```
- 若想改为北京时间每天 8 点：`cron: '0 0 * * *'`（UTC 0 点 = 北京时间 8 点）；
- 若想改为北京时间每天 10 点：`cron: '0 2 * * *'`（UTC 2 点 = 北京时间 10 点）；
- 时区换算工具：[Cron 时区转换](https://crontab.guru/time-zones.html)。

### 2. 调整 API 重试次数
编辑 `get_quote.py` 中的 `API_CONFIGS` 列表，修改每个 API 的 `retry_count`（默认 3 次）：
```python
API_CONFIGS = [
    {
        "name": "每日一句",
        "url": "http://open.iciba.com/dsapi/",
        "retry_count": 5,  # 改为重试5次
        # 其他配置不变...
    },
    # 其他 API 同理...
]
```

### 3. 自定义内容展示格式
编辑 `get_quote.py` 中的 `write_to_markdown` 函数，调整输出格式（示例：修改诗词展示样式）：
```python
elif res["type"] == "每日诗词":
    part = "\n### 📜 " + res['type'] + "\n"
    part += "**标题**：" + res['title'] + "\n"
    part += "**朝代/作者**：" + res['dynasty'] + " · " + res['author'] + "\n"
    part += "**内容**：\n> " + res['content'].replace("\n", "\n> ") + "\n"
    markdown_content += part
```

### 4. 替换/新增 API 源
编辑 `get_quote.py` 中的 `API_CONFIGS` 列表，替换或新增 API（需适配 `parser` 解析函数）：
```python
API_CONFIGS = [
    # 原有 3 个 API 配置...
    # 新增：网易云热评 API（示例）
    {
        "name": "网易云热评",
        "url": "https://api.uomg.com/api/rand.music.comment?format=json",
        "retry_count": 3,
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "parser": lambda res: {
            "type": "网易云热评",
            "content": res["content"],
            "source": "网易云音乐",
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
    }
]
```
- 需确保 API 返回 JSON 格式，且 `parser` 函数能正确提取所需字段。

## 📈 扩展方向
1. **静态网页展示**：用 Vue/React 或 Hugo/Gatsby 读取 `quotes.md`，生成个人灵感网站（支持按类型筛选、搜索）；
2. **邮件/微信推送**：集成 SMTP 服务或企业微信机器人，每天将新内容推送至邮箱/微信；
3. **内容备份**：自动同步 `quotes.md` 到 Notion/语雀，多平台备份；
4. **数据可视化**：用 Python 的 `matplotlib` 或 `pyecharts` 统计每月内容类型分布、API 成功率；
5. **内容筛选**：添加关键词过滤功能，屏蔽不想要的内容（如敏感词、重复内容）。

## ❌ 常见问题排查
### 1. GitHub Actions 运行失败？
- 查看日志：进入「Actions」→ 点击失败任务 → 展开标红步骤，查看具体错误；
- 权限问题：确保 `auto-submit.yml` 中已配置 `permissions: contents: write` 和 `token: ${{ secrets.GITHUB_TOKEN }}`；
- API 调用失败：检查 API 地址是否失效，或网络是否可访问（可本地运行 `python get_quote.py` 测试）；
- 日期格式错误：确保 `auto-submit.yml` 中提交信息使用 `TODAY=$(date -d "UTC+8" +"%Y-%m-%d")`。

### 2. quotes.md 无新增内容？
- 检查脚本是否生成内容：本地运行 `python get_quote.py`，看是否输出「成功记录 X/3 个接口内容」；
- 检查 Git 提交：查看 Actions 日志中「Commit and push changes」步骤，是否显示「No changes to commit」（无新内容时触发）；
- 确认 API 调用成功：查看脚本运行日志，是否有「✅ XX API 调用成功」的输出。

### 3. 中文乱码/格式错乱？
- 中文乱码：脚本中已指定 `encoding="utf-8"`，确保本地文件编码为 UTF-8；
- 格式错乱：检查 `write_to_markdown` 函数中的字符串拼接逻辑，避免遗漏换行符。

## 🤝 贡献指南
欢迎提交 PR 或 Issues 改进项目：
1. Fork 仓库；
2. 创建分支：`git checkout -b feature/xxx`（如 `feature/add-wechat-push`）；
3. 提交修改：`git commit -m "feat: add wechat push function"`；
4. 推送分支：`git push origin feature/xxx`；
5. 提交 PR，描述修改内容和测试结果。

## 📄 许可证
本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

---

✨ 每日积累，不负时光～  
如果觉得项目有用，欢迎 Star 支持！🌟  
仓库地址：[reedtang666/Daily-Inspiration](https://github.com/reedtang666/Daily-Inspiration)
