---
name: blog-translator
description: Translate English blog articles into Chinese by fetching content from URLs, converting to markdown, translating, and polishing. Use when users want to save and translate English blog articles, generate bilingual markdown files, or organize blog content by domain.
---

# Blog Translator

## Overview

Fetches English blog content from URLs, saves as English markdown, translates to Chinese, and produces polished bilingual markdown files organized by domain.

## Workflow

When user requests to save and translate an English blog:

### Step 1: Fetch Blog Content & Save as English Markdown

#### 标准流程（适用于大多数技术博客）

1. Extract domain from URL to determine organization directory
2. Run `fetch_blog.py` script with the blog URL
3. Script will:
   - Extract article title (prefer HTML title tag, fallback to URL path)
   - Get main article content and convert to clean markdown
   - Generate filename in kebab-case from title (2-6 words)
   - Save to `<project-root>/<domain>/<blog>.md`

**Example:**
```bash
# User: "Translate and save this blog: https://example.com/blog/understanding-machine-learning"
# Run:
python3 scripts/fetch_blog.py "https://example.com/blog/understanding-machine-learning"

# Output saved to: example-com/understanding-machine-learning.md
```

#### 复杂网站处理（反爬/需登录/JavaScript渲染）

当 `fetch_blog.py` 遇到以下情况时：
- 返回 JavaScript 错误页面（如 X.com、部分 SPA 网站）
- 需要登录才能查看内容
- 遇到 Cloudflare 等反爬保护
- 内容需要滚动加载或交互后才显示

**请使用 dev-browser skill 协助抓取：**

**前置准备（关键步骤）：**
```
# 必须先连接到用户的 Chrome，这样才能获取已登录状态
# 不要直接使用 dev-browser，而是先执行：
/connect to my Chrome
# 或让用户确认 Chrome 扩展已连接
```

**抓取流程：**
1. **连接到 Chrome**（使用 dev-browser extension 模式）
   - 确保 Chrome 扩展已安装并运行
   - 连接到用户已登录的 Chrome 实例

2. **访问目标 URL**
   - 使用 dev-browser 导航到文章页面
   - 如需登录，在浏览器中完成登录流程
   - 等待页面完全加载（包括 JavaScript 渲染内容）

3. **提取内容**
   - 使用 `getAISnapshot()` 获取页面结构
   - 或使用 `page.evaluate()` 提取文章正文
   - 对于长文章，可能需要滚动加载全部内容

4. **保存到文件**
   - 手动创建 `<domain>/<article>/1-original.md`
   - 将提取的内容保存为 Markdown 格式
   - 添加文章元数据（标题、作者、来源URL、日期）

5. **继续后续步骤**
   - 从 Step 2 开始继续翻译流程

**示例场景：**
- **X/Twitter 文章**（需要登录 + JavaScript 渲染）
- **Medium 付费文章**（需要登录）
- **部分技术文档站点**（需要绕过反爬）
- **需要滚动加载的长文章**

**示例命令序列：**
```
User: "翻译这篇 X 文章：https://x.com/username/status/123456"

# 1. 先连接到 Chrome
"connect to my Chrome"

# 2. 使用 dev-browser 访问并提取内容
"go to https://x.com/username/status/123456"
"extract the article content"

# 3. 手动保存到文件
# 保存到 x-com/article-title/1-original.md

# 4. 继续标准翻译流程
"根据 1-original.md 进行 Step 2 翻译"
```

### Step 2: First-Round Translation (English to Chinese)

1. Read the English markdown file
2. Use the fixed translation prompt from `references/translation_prompt.md`
3. Translate entire content maintaining technical accuracy
4. Save the first-round translation to `<project-root>/<domain>/初译-<blog>.md`

### Step 3: Generate Review Report (审校报告)

1. Compare the first-round translation against the original English text
2. Use the review prompt from `references/review_prompt.md`
3. Check terminology consistency against `assets/glossary.md`
4. Identify issues in accuracy, fluency, and formatting
5. Generate a structured review report and save to `<project-root>/<domain>/审校-<blog>.md`

**Review Report Includes:**
- Terminology consistency check results
- Translation accuracy issues
- Fluency and style optimization suggestions
- Formatting verification
- Priority-ranked modification recommendations

### Step 4: Polish and Finalize

1. Read the review report from Step 3
2. Use the polishing prompt from `references/polishing_prompt.md`
3. Apply terminology glossary and address all issues from the review report
4. Refine translation for natural flow and technical accuracy
5. Save the final polished version to `<project-root>/<domain>/中译-<blog>.md`

## File Organization

The skill organizes files by domain, with each article's workflow artifacts in its own subdirectory for easy management:

```
<project-root>/
└── <domain>/
    └── <blog>/                    # Article folder (kebab-case title)
        ├── 1-original.md          # English version (original)
        ├── 2-draft.md             # First-round Chinese translation
        ├── 3-review.md            # Review report with terminology checks
        └── 4-final.md             # Final polished Chinese version
```

### Naming Convention

- **Domain**: Extracted from URL (e.g., `github-com`, `medium-com`, `mp-weixin-qq-com`)
- **Article folder**: `<blog>` - Extracted from page title, converted to kebab-case, 2-6 words
  - Examples: `understanding-machine-learning/`, `react-hooks-guide/`
- **Workflow file naming** (numbered for workflow clarity):
  - `1-original.md` : English original (Step 1)
  - `2-draft.md` : First-round translation (Step 2)
  - `3-review.md` : Review report with terminology checks (Step 3)
  - `4-final.md` : Final polished Chinese version (Step 4)

**File Naming Examples:**

```
github-com/
  ├── state-management-patterns/
  │   ├── 1-original.md
  │   ├── 2-draft.md
  │   ├── 3-review.md
  │   └── 4-final.md
  └── react-hooks-guide/
      ├── 1-original.md
      ├── 2-draft.md
      ├── 3-review.md
      └── 4-final.md

medium-com/
  ├── advanced-typescript-tips/
  │   ├── 1-original.md
  │   ├── 2-draft.md
  │   ├── 3-review.md
  │   └── 4-final.md
  └── rust-memory-management/
      ├── 1-original.md
      ├── 2-draft.md
      ├── 3-review.md
      └── 4-final.md
```

**Advantages of this structure:**
- All versions of the same article are grouped together
- Easy to locate and manage multiple articles from the same domain
- Numbered files clearly show the workflow progression
- Clean separation between different articles

## Scripts

### scripts/fetch_blog.py

Core script to fetch blog content and convert to markdown. Run with a URL to extract and save blog content.

**Usage:**
```bash
python3 scripts/fetch_blog.py "<blog-url>"
```

This script handles:
- Content extraction from various blog platforms
- HTML to markdown conversion
- File naming and organization by domain
- Error handling for network issues

## References

### references/translation_prompt.md

Fixed translation prompt used in Step 2. Load this when translating English markdown to Chinese.

### references/review_prompt.md

Structured review report prompt used in Step 3. Generates a comprehensive review report including:
- Terminology consistency check against glossary
- Translation accuracy assessment
- Fluency and style optimization suggestions
- Formatting verification
- Priority-ranked modification recommendations

### references/polishing_prompt.md

Fixed polishing prompt with style guidelines used in Step 4. Load this when reviewing and refining the Chinese translation, incorporating feedback from the review report.

### assets/glossary.md

通用技术术语对照表，用于统一翻译风格。润色翻译时参考此文件确保术语一致性。针对特定领域博客，可在此文件末尾追加专业术语。

## Common Usage Scenarios

### Scenario 1: Translate a Single Blog

User: "请帮我翻译并保存这个博客：https://blog.rust-lang.org/2024/01/04/rust-1.75.0.html"

Workflow:
1. Extract domain: `rust-lang-org`
2. Run: `python3 scripts/fetch_blog.py "https://blog.rust-lang.org/2024/01/04/rust-1.75.0.html"`
3. Save English to: `rust-lang-org/rust-1-75-0-release/1-original.md`
4. **Step 2 - First-round Translation:** Use `references/translation_prompt.md` to translate
   - Save to: `rust-lang-org/rust-1-75-0-release/2-draft.md`
5. **Step 3 - Review Report:** Use `references/review_prompt.md` to generate review report
   - Check terminology against `assets/glossary.md`
   - Save to: `rust-lang-org/rust-1-75-0-release/3-review.md`
6. **Step 4 - Polish:** Use `references/polishing_prompt.md` + review report to finalize
   - Save final Chinese to: `rust-lang-org/rust-1-75-0-release/4-final.md`

### Scenario 2: Multiple Blogs from Same Domain

When users translate multiple blogs from the same site, all files are organized under the same domain directory for easy management.

### Scenario 3: Complex Site with Login/Anti-Scraping (e.g., X.com)

User: "翻译这篇 X 博客：https://x.com/EricBuess/status/2019817656745128366"

Workflow:
1. **Check if fetch_blog.py can handle it:**
   - Run: `python3 scripts/fetch_blog.py "https://x.com/EricBuess/status/2019817656745128366"`
   - If it returns "JavaScript is not available" or fails, proceed to dev-browser

2. **Connect to Chrome:**
   - Prompt user: "This site requires browser automation. Connect to your Chrome?"
   - User confirms and Chrome extension is ready
   - Execute: `connect to my Chrome` (or equivalent)

3. **Navigate and Extract:**
   - Use dev-browser to navigate to the URL
   - Wait for JavaScript rendering
   - Extract article content using `getAISnapshot()` or `page.evaluate()`
   - Save extracted content to `x-com/claude-code-agent-teams/1-original.md`

4. **Continue with standard workflow:**
   - Step 2: Translate to `2-draft.md`
   - Step 3: Review to `3-review.md`
   - Step 4: Polish to `4-final.md`

## Implementation Notes

- Always verify the English markdown file was created successfully before proceeding to translation
- **Step 2 (First-round Translation):** Generate a complete but raw translation without over-polishing
- **Step 3 (Review Report):** This is a critical quality gate - systematically check terminology against glossary
  - The review report serves as documentation for translation decisions
  - It helps identify terms that should be added to the glossary for future consistency
  - Review reports can be shared with human editors for collaborative improvement
- **Step 4 (Polish):** Address all high and medium priority issues from the review report
- Preserve all code blocks, URLs, and technical terms during translation
- Maintain consistent formatting between all versions (English, 初译, 审校, 中译)
- Check for existing files before overwriting to avoid data loss
- Consider keeping all workflow files (初译, 审校, 中译) for traceability, or delete 初译 if space is limited

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
