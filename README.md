# Caicai Skills

[![GitHub](https://img.shields.io/github/license/nextcaicai/caicai-skills)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/nextcaicai/caicai-skills)](https://github.com/nextcaicai/caicai-skills/stargazers)

English | [中文](#中文)

> A collection of Claude Code skills for automating content creation, translation, and development workflows.

---

## English

### Prerequisites

- Claude Code CLI installed
- Git configured with GitHub access
- Python 3.8+ environment (for blog-translator skill)

### Installation

#### Quick Install (Recommended)

```bash
npx skills add nextcaicai/caicai-skills
```

#### Register as Plugin Marketplace

Run the following command in Claude Code:

```bash
/plugin marketplace add nextcaicai/caicai-skills
```

Then install skills via Browse UI:

1. Select **Browse and install plugins**
2. Select **caicai-skills**
3. Select the plugin(s) you want to install
4. Select **Install now**

#### Direct Install

```bash
# Install specific skill
/plugin install blog-translator@caicai-skills
```

Or simply tell Claude Code:

> Please install skills from github.com/nextcaicai/caicai-skills

### Update Skills

To update skills to the latest version:

1. Run `/plugin` in Claude Code
2. Switch to **Marketplaces** tab (use arrow keys or Tab)
3. Select **caicai-skills**
4. Choose **Update marketplace**

You can also **Enable auto-update** to get the latest versions automatically.

### Available Skills

Skills are organized by category:

#### Content Skills

Content creation and translation skills.

##### blog-translator

Fetch, translate, and polish English blog articles into Chinese with a 4-step workflow (Fetch → Draft → Review → Final).

```bash
# Translate a blog from URL
/translate "https://example.com/blog/article"

# Translate with custom options
/translate "https://x.com/user/status/123" --style casual
```

**Features**:
- Automatic content fetching via `defuddle.md` (handles JavaScript-rendered sites)
- 4-step translation workflow with quality control
- Smart tone detection (casual "你" for X.com, formal "您" for tech docs)
- Image preservation and markdown formatting
- Terminology glossary support

**Translation Styles**:

| Style | Tone | Best For |
|-------|------|----------|
| Casual | "你" + modal particles | X.com posts, personal essays |
| Formal | "您" + professional | Technical documentation, corporate blogs |

**Workflow**:
1. **Fetch** - Extract content from URL using `fetch_blog.py`
2. **Draft** - First-round translation with context-aware tone
3. **Review** - Generate structured review report with terminology checks
4. **Final** - Polish and refine for natural Chinese flow

---

## 中文

### 前置要求

- 已安装 Claude Code CLI
- 已配置 Git 并连接 GitHub
- Python 3.8+ 环境（用于 blog-translator 技能）

### 安装

#### 快速安装（推荐）

```bash
npx skills add nextcaicai/caicai-skills
```

#### 注册为插件市场

在 Claude Code 中运行以下命令：

```bash
/plugin marketplace add nextcaicai/caicai-skills
```

然后通过 Browse UI 安装技能：

1. 选择 **Browse and install plugins**
2. 选择 **caicai-skills**
3. 选择要安装的插件
4. 选择 **Install now**

#### 直接安装

```bash
# 安装特定技能
/plugin install blog-translator@caicai-skills
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

### 可用技能

技能按类别组织：

#### 内容技能

内容创作和翻译技能。

##### blog-translator（博客翻译）

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
1. **抓取** - 使用 `fetch_blog.py` 从 URL 提取内容
2. **初译** - 第一轮翻译，根据语境选择语气
3. **审校** - 生成结构化审校报告，检查术语一致性
4. **润色** - 润色优化，确保中文表达自然流畅

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ by <a href="https://github.com/nextcaicai">@nextcaicai</a></p>
