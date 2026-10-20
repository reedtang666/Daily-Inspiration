# Daily-Inspiration: 每日内容合集（每日一句+每日一言+每日诗词）让你每天都是不一样，激励自己从现在开始

一个 **全自动化、零手动操作** 的每日内容收集项目，每天通过 GitHub Actions 定时调用 3 个指定 API（每日一句、每日一言、每日诗词），全量记录成功结果并自动提交到 GitHub，持续积累属于你的「每日灵感知识库」。

<!-- TODAY_BOARD_START -->
<div align="center">

![累计打卡](https://img.shields.io/badge/累计打卡-331_天-2ea44f?style=for-the-badge&logo=github) ![收录诗词](https://img.shields.io/badge/收录诗词-329_首-0969da?style=for-the-badge&logo=bookstack) ![最近更新](https://img.shields.io/badge/最近更新-2026--10--20-f97316?style=for-the-badge&logo=clockify)

</div>

## 🌟 今日灵感看板

### 🗓️ 2026-10-20 · 星期二

#### 📚 每日一句

<table>
<tr>
<td width="65%" valign="middle">

> **The wind reads every leaf before it falls.**
>
> 风在每片叶子落下前，都读过它。

[🎧 点击收听原声](https://staticedu-wps-cache.iciba.com/audio/4c2a033ae1ac3ec85c70265d06d070be.mp3) &nbsp;｜&nbsp; [🖼️ 查看高清日签](https://staticedu-wps-cache.iciba.com/image/62f3e760ade60ad22b6848478349b8c4.png)

</td>
<td width="35%" align="center" valign="middle">
<img src="https://staticedu-wps-cache.iciba.com/image/62f3e760ade60ad22b6848478349b8c4.png" alt="每日一句 (2026-10-20)" width="240" />
</td>
</tr>
</table>

#### 💬 每日一言

> 「 心事诉与明月收，若问情根深几许，朝朝暮暮共白头。 」

#### 📜 每日诗词

**《望天门山》** · 〔唐代〕李白

> 天门中断楚江开，碧水东流至此回。  
> 两岸青山相对出，孤帆一片日边来。

## 🗂️ 历史月度归档

> 📁 完整结构化数据存储于 [`data/`](data/) 目录，按月归档 Markdown 存储于 [`archives/`](archives/) 目录，当月汇总可查看 [`quotes.md`](quotes.md)。

| 月份 | 收录天数 | 每日一句 | 每日一言 | 每日诗词 | 归档直达 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2026-10** | 20 天 | 20 篇 | 20 条 | 20 首 | [📂 查看 2026-10 归档](archives/2026-10.md) |
| **2026-09** | 30 天 | 30 篇 | 30 条 | 30 首 | [📂 查看 2026-09 归档](archives/2026-09.md) |
| **2026-08** | 31 天 | 31 篇 | 31 条 | 31 首 | [📂 查看 2026-08 归档](archives/2026-08.md) |
| **2026-07** | 31 天 | 31 篇 | 31 条 | 31 首 | [📂 查看 2026-07 归档](archives/2026-07.md) |
| **2026-06** | 30 天 | 30 篇 | 30 条 | 30 首 | [📂 查看 2026-06 归档](archives/2026-06.md) |
| **2026-05** | 31 天 | 31 篇 | 31 条 | 31 首 | [📂 查看 2026-05 归档](archives/2026-05.md) |
| **2026-04** | 30 天 | 30 篇 | 30 条 | 29 首 | [📂 查看 2026-04 归档](archives/2026-04.md) |
| **2026-03** | 31 天 | 31 篇 | 31 条 | 31 首 | [📂 查看 2026-03 归档](archives/2026-03.md) |
| **2026-02** | 28 天 | 28 篇 | 28 条 | 28 首 | [📂 查看 2026-02 归档](archives/2026-02.md) |
| **2026-01** | 31 天 | 31 篇 | 31 条 | 31 首 | [📂 查看 2026-01 归档](archives/2026-01.md) |
| **2025-12** | 31 天 | 31 篇 | 31 条 | 30 首 | [📂 查看 2025-12 归档](archives/2025-12.md) |
| **2025-11** | 7 天 | 7 篇 | 7 条 | 7 首 | [📂 查看 2025-11 归档](archives/2025-11.md) |
<!-- TODAY_BOARD_END -->

## ✨ 核心功能
- **自动更新**：每天北京时间 9 点（UTC 1 点）自动运行，无需手动触发；
- **首页今日看板**：自动刷新 `README.md` 顶部的动态统计徽章、今日最新灵感卡片与月度归档索引；
- **结构化归档与极速浏览**：
  - 原始数据按月持久化至 [`data/YYYY-MM.json`](data/)，便于检索、统计与二次开发；
  - 历史内容按月生成 [`archives/YYYY-MM.md`](archives/) 归档文件；
  - [`quotes.md`](quotes.md) 仅展示**当月最新内容（倒序排列）+ 历史归档导航**，告别单文件数千行导致的加载卡顿；
- **精致图文排版**：
  - **每日一句**：左右分栏图文混排卡片，附带原声朗读与高清日签链接；
  - **每日一言**：带分类标签与出处/作者署名展示；
  - **每日诗词**：古风引用排版，附带名句高亮、意境标签，超过 10 句的长诗自动启用 `<details>` 折叠；
- **智能历史去重**：自动比对历史已收录的一言与诗词，抽中重复内容时自动重新抽取，保证每日新鲜感；
- **每日 GitHub 提交**：确保每天都有代码提交，在你的 GitHub profile 上显示绿色贡献方块（contributions），保持活跃度；
- **兜底容错与幂等更新**：同一天多次运行自动合并更新、不产生重复日期块；3 个 API 均失败时仍会创建提交确保每日贡献记录不中断。

## 🛠️ 技术栈
- **核心脚本**：Python 3.10+（简洁易维护，优先使用 `requests` 库，无依赖环境下自动回退至标准库 `urllib`）；
- **自动化工具**：GitHub Actions（定时任务 + 自动提交代码）；
- **数据存储**：JSON 结构化数据（`data/`）+ Markdown 按月归档（`archives/` & `quotes.md`）；
- **API 来源（固定 3 个，无需额外申请 Key）**：
  - 每日一句：金山词霸 API（`http://open.iciba.com/dsapi/`）→ 英文+中文翻译+音频+分享日签；
  - 每日一言：一言 API（`https://v1.hitokoto.cn/`）→ 句子正文+出处+作者+分类标签；
  - 每日诗词：今日诗词 API（`https://v2.jinrishici.com/one.json`）→ 古风诗词（标题+朝代+作者+原文+推荐名句+意境标签）。

## 🚀 快速开始（5 分钟部署）
### 1. Fork 仓库
点击 GitHub 仓库右上角「Fork」，将项目复制到你的账号下。

### 2. 确认文件完整性
Fork 后，仓库包含以下核心目录与文件（无需修改，直接使用）：
```
Daily-Inspiration/
├─ README.md          # 仓库首页（含自动更新的「今日灵感看板」与归档索引）
├─ quotes.md          # 当月最新内容合集（按日期倒序）+ 历史归档导航
├─ archives/          # 按月拆分的 Markdown 历史归档（如 2025-11.md ~ 2026-10.md）
├─ data/              # 按月存储的结构化 JSON 数据（如 2025-11.json ~ 2026-10.json）
├─ get_quote.py       # 核心脚本（API调用+智能去重+JSON存储+多视图渲染）
├─ requirements.txt   # 依赖库（requests==2.32.3）
└─ .github/
   └─ workflows/
      └─ auto-submit.yml  # GitHub Actions 定时任务配置（北京时间9点执行）
```

### 3. 手动测试与常用命令（可选）
- **日常采集并更新所有视图**：
  ```bash
  python3 get_quote.py
  ```
- **仅修改排版样式后重新渲染所有 Markdown（不请求 API）**：
  ```bash
  python3 get_quote.py --render-only
  ```
- **从旧版单文件 `quotes.md` 迁移历史数据**：
  ```bash
  python3 get_quote.py --migrate
  ```
- **GitHub Actions 手动触发**：
  1. 进入你的仓库 → 点击顶部「Actions」；
  2. 左侧选择「Auto Collect Daily Content」；
  3. 点击右侧「Run workflow」→ 再次点击「Run workflow」；
  4. 等待 1-2 分钟，若所有步骤显示绿色对勾，说明运行成功。

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

### 2. 调整 API 重试次数与去重开关
编辑 `get_quote.py` 中的 `API_CONFIGS` 列表，修改每个 API 的 `retry_count`（默认 3 次）或 `dedup`（是否开启历史去重）：
```python
API_CONFIGS = [
    {
        "name": "每日一句",
        "key": "quote",
        "url": "http://open.iciba.com/dsapi/",
        "retry_count": 5,  # 改为重试5次
        "dedup": False,
        # 其他配置不变...
    },
    # 其他 API 同理...
]
```

### 3. 自定义卡片展示格式
编辑 `get_quote.py` 中的 `render_daily_card` 函数，调整单日卡片的 Markdown/HTML 排版，然后运行 `python3 get_quote.py --render-only` 即可一键刷新全量历史归档与首页看板。

## 📈 扩展方向
1. **静态网页展示**：用 Vue/React 或 Hugo/Gatsby 读取 `quotes.md`，生成个人灵感网站（支持按类型筛选、搜索）；
2. **邮件/微信推送**：集成 SMTP 服务或企业微信机器人，每天将新内容推送至邮箱/微信；
3. **内容备份**：自动同步 `quotes.md` 到 Notion/语雀，多平台备份；
4. **数据可视化**：用 Python 的 `matplotlib` 或 `pyecharts` 统计每月内容类型分布、API 成功率；
5. **内容筛选**：添加关键词过滤功能，屏蔽不想要的内容（如敏感词、重复内容）。

## ❌ 常见问题排查
### 1. GitHub Actions 运行失败？
- 查看日志：进入「Actions」→ 点击失败任务 → 展开标红步骤，查看具体错误；
- 权限问题：确保 `.github/workflows/auto-submit.yml` 中已配置 `permissions: contents: write` 和 `token: ${{ secrets.GITHUB_TOKEN }}`；
- API 调用失败：检查 API 地址是否失效，或网络是否可访问（可本地运行 `python get_quote.py` 测试）；
- 日期格式错误：确保 `.github/workflows/auto-submit.yml` 中提交信息使用 `TODAY=$(TZ='Asia/Shanghai' date +"%Y-%m-%d")`。

### 2. 每天是否有 GitHub 提交记录（绿色小方框）？
- **保证每日提交**：工作流确保每天都有提交，维护你的 GitHub contributions 图表绿色记录；
  - 正常情况：脚本获取内容并写入 `quotes.md`，提交信息为 `feat: add YYYY-MM-DD daily content`
  - API 全部失败：脚本写入「今日暂无数据（三个接口均调用失败）」到 `quotes.md`，同样会提交
  - 特殊情况：如果脚本未修改 `quotes.md`（极少发生），会创建空提交 `chore: daily run YYYY-MM-DD (no new content)`
- 查看提交历史：进入仓库主页，查看最近的提交记录，应该看到每天都有新提交；
- 检查 Actions 日志：如果没有看到每日提交，进入「Actions」查看工作流运行日志，确认是否有错误。

### 3. quotes.md 无新增内容？
- 检查脚本是否生成内容：本地运行 `python get_quote.py`，看是否输出「成功记录 X/3 个接口内容」；
- API 全部失败时：脚本会写入「今日暂无数据（三个接口均调用失败）」，这仍然会触发正常提交；
- 确认 API 调用成功：查看脚本运行日志，是否有「✅ XX API 调用成功」的输出。

### 4. 中文乱码/格式错乱？
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

✨ 每日积累，不负时光～ ～ ～   
如果觉得项目有用，欢迎 Star 支持！🌟  
仓库地址：[reedtang666/Daily-Inspiration](https://github.com/reedtang666/Daily-Inspiration)
