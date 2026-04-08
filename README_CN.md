# Caicai Skills

[![GitHub](https://img.shields.io/github/license/nextcaicai/caicai-skills)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/nextcaicai/caicai-skills)](https://github.com/nextcaicai/caicai-skills/stargazers)

[English](README.md) | 中文

> 一套用于自动化内容创作、翻译和开发工作流的 Claude Code 技能集合。

---

## 前置要求

- 已安装 Claude Code CLI
- 已配置 Git 并连接 GitHub
- Python 3.8+ 环境（用于基于 Python 的技能）

## 安装

### 快速安装（推荐）

```bash
npx skills add nextcaicai/caicai-skills
```

### 注册为插件市场

在 Claude Code 中运行以下命令：

```bash
/plugin marketplace add nextcaicai/caicai-skills
```

然后通过 Browse UI 安装技能：

1. 选择 **Browse and install plugins**
2. 选择 **caicai-skills**
3. 选择要安装的插件
4. 选择 **Install now**

### 直接安装

```bash
# 安装特定技能
/plugin install caicai-blog-translator@caicai-skills
/plugin install caicai-url-to-markdown@caicai-skills
```

或直接告诉 Claude Code：

> 请安装 github.com/nextcaicai/caicai-skills 中的技能

### 更新技能

要更新技能到最新版本：

1. 在 Claude Code 中运行 `/plugin`
2. 切换到 **Marketplaces** 标签页（使用方向键或 Tab）
3. 选择 **caicai-skills**
4. 选择 **Update marketplace**

你也可以 **启用自动更新** 以自动获取最新版本。

---

## 可用技能

技能按类别组织：

### 内容技能

#### caicai-blog-translator（博客翻译）

抓取、翻译并润色英文博客文章为中文，采用四步工作流程（抓取 → 初译 → 审校 → 润色）。

```bash
# 翻译 URL 博客
/translate "https://example.com/blog/article"

# 使用自定义选项翻译
/translate "https://x.com/user/status/123" --style casual
```

**功能特性**：
- 通过 `defuddle.md` 自动抓取内容（支持 JavaScript 渲染网站）
- 四步翻译工作流程，确保质量控制
- 智能语气检测（X.com 用口语化"你"，技术文档用正式"您"）
- 保留图片和 Markdown 格式
- 支持术语表

**翻译风格**：

| 风格 | 语气 | 适用场景 |
|------|------|----------|
| 口语化 | "你" + 语气词 | X.com 帖子、个人随笔 |
| 正式化 | "您" + 专业用语 | 技术文档、企业博客 |

**工作流程**：
1. **抓取** - 从 URL 提取内容
2. **初译** - 第一轮翻译，根据语境选择语气
3. **审校** - 生成结构化审校报告，检查术语一致性
4. **润色** - 润色优化，确保中文表达自然流畅

---

#### caicai-url-to-markdown（URL 转 Markdown）

将 URL 转换为干净的 Markdown 格式。支持多种站点类型，自动路由到最佳抓取策略。

```bash
# 根据 URL 自动路由
python3 scripts/router.py "<url>"

# 特定站点的直接用法
python3 scripts/fetch_feishu.py "https://my.feishu.cn/wiki/xxx"
python3 scripts/fetch_zhihu.py "https://zhuanlan.zhihu.com/p/xxx"
python3 scripts/fetch_blog.py "https://x.com/user/status/xxx"
```

**支持的站点**：

| 站点 | 策略 | 说明 |
|------|------|------|
| **飞书/Lark** | Open API | 需要 FEISHU_APP_ID/SECRET |
| **知乎** | curl_impersonate / puppeteer | 双阶段反爬策略 |
| **X.com/Twitter** | defuddle.md | 处理 JavaScript 渲染内容 |
| **Medium** | defuddle.md | 完整的元数据提取 |
| **微信公众号** | defuddle.md | 支持 mp.weixin.qq.com |
| **其他站点** | defuddle.md / 直连 | 自动回退策略 |

**架构**：
```
router.py（入口）
    ├── fetch_feishu.py  → 飞书 Open API
    ├── fetch_zhihu.py   → 知乎（反爬）
    └── fetch_blog.py    → 通用站点
            ├── defuddle.md
            └── 直连抓取 (readability)
```

**安装**：
```bash
pip install -r requirements.txt

# 知乎文章抓取（可选，二选一）
# 方案 A: curl_impersonate（更快）
brew install curl-impersonate

# 方案 B: puppeteer-extra（备用）
npm install -g puppeteer-extra puppeteer-extra-plugin-stealth
```

**输出结构**：
```
<domain>/<article-folder>/1-original.md
```

示例：`x-com/article-title/1-original.md`

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">Made with ❤️ by <a href="https://github.com/nextcaicai">@nextcaicai</a></p>
