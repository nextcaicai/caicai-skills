# Caicai Skills

[![GitHub](https://img.shields.io/github/license/nextcaicai/caicai-skills)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/nextcaicai/caicai-skills)](https://github.com/nextcaicai/caicai-skills/stargazers)

English | [中文](README_CN.md)

> A collection of Claude Code skills for automating content creation, translation, and development workflows.

---

## Prerequisites

- Claude Code CLI installed
- Git configured with GitHub access
- Python 3.8+ environment (for Python-based skills)

## Installation

### Quick Install (Recommended)

```bash
npx skills add nextcaicai/caicai-skills
```

### Register as Plugin Marketplace

Run the following command in Claude Code:

```bash
/plugin marketplace add nextcaicai/caicai-skills
```

Then install skills via Browse UI:

1. Select **Browse and install plugins**
2. Select **caicai-skills**
3. Select the plugin(s) you want to install
4. Select **Install now**

### Direct Install

```bash
# Install specific skill
/plugin install caicai-blog-translator@caicai-skills
/plugin install caicai-url-to-markdown@caicai-skills
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

---

## Available Skills

Skills are organized by category:

### Content Skills

#### caicai-blog-translator

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
1. **Fetch** - Extract content from URL
2. **Draft** - First-round translation with context-aware tone
3. **Review** - Generate structured review report with terminology checks
4. **Final** - Polish and refine for natural Chinese flow

---

#### caicai-url-to-markdown

Convert URLs to clean Markdown format. Supports multiple site types with automatic routing to the best fetching strategy.

```bash
# Auto-route based on URL
python3 scripts/router.py "<url>"

# Direct usage for specific sites
python3 scripts/fetch_feishu.py "https://my.feishu.cn/wiki/xxx"
python3 scripts/fetch_zhihu.py "https://zhuanlan.zhihu.com/p/xxx"
python3 scripts/fetch_blog.py "https://x.com/user/status/xxx"
```

**Supported Sites**:

| Site | Strategy | Notes |
|------|----------|-------|
| **Feishu/Lark** | Open API | Requires FEISHU_APP_ID/SECRET |
| **Zhihu** | curl_impersonate / puppeteer | Two-stage anti-bot strategy |
| **X.com/Twitter** | defuddle.md | Handles JavaScript-rendered content |
| **Medium** | defuddle.md | Full metadata extraction |
| **WeChat Articles** | defuddle.md | mp.weixin.qq.com support |
| **Other sites** | defuddle.md / Direct | Auto-fallback strategy |

**Architecture**:
```
router.py (entry point)
    ├── fetch_feishu.py  → Feishu Open API
    ├── fetch_zhihu.py   → Zhihu (anti-bot)
    └── fetch_blog.py    → Generic sites
            ├── defuddle.md
            └── Direct Fetch (readability)
```

**Installation**:
```bash
pip install -r requirements.txt

# For Zhihu articles (optional, choose one)
# Option A: curl_impersonate (faster)
brew install curl-impersonate

# Option B: puppeteer-extra (fallback)
npm install -g puppeteer-extra puppeteer-extra-plugin-stealth
```

**Output Structure**:
```
<domain>/<article-folder>/1-original.md
```

Example: `x-com/article-title/1-original.md`

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ by <a href="https://github.com/nextcaicai">@nextcaicai</a></p>
