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

#### 内容抓取策略

`fetch_blog.py` 使用以下策略自动处理不同类型的网站：

**策略 1：defuddle.md（推荐，适用于大多数网站）**
- 自动处理 JavaScript 渲染的网站（如 X.com、Medium）
- 使用方式：在 URL 前添加 `https://defuddle.md/`
- 例如：`https://x.com/user/status/123` → `https://defuddle.md/x.com/user/status/123`

**策略 2：直接抓取（适用于静态网站）**
- 用于传统的技术博客、文档站点
- 使用 Readability 提取正文内容

**处理流程：**
脚本会自动尝试两种策略，优先使用 defuddle.md，失败后回退到直接抓取。

**特殊情况（需要登录的内容）：**
对于需要登录才能查看的内容（如私密推文、付费文章）：
1. 在浏览器中登录并查看文章
2. 手动复制内容保存到 `<domain>/<article>/1-original.md`
3. 从 Step 2 继续翻译流程

### Step 2: First-Round Translation (English to Chinese)

1. Read the English markdown file
2. Use the fixed translation prompt from `references/translation_prompt.md`
3. Translate entire content maintaining technical accuracy
4. Save the first-round translation to `<project-root>/<domain>/初译-<blog>.md`

**Translation Style Guidelines:**

| Content Type | Tone | Heading Style | Example |
|--------------|------|---------------|---------|
| X.com posts, personal essays | Casual - use "你" | 一、二、三 或 1）2）3） | 一、你没有想法，是因为干扰太多了 |
| Technical documentation | Formal - use "您" | ## 1. ## 2. | ## 1. 系统架构概述 |
| Corporate blogs | Formal - use "您" | ## 1. ## 2. | ## 1. 产品特性 |

**Key Translation Principles:**
- **Prioritize Chinese equivalents** over English loanwords (e.g., "brain-fried" → "大脑被榨干" rather than "brain-fried")
- **Use modal particles** (了, 呢, 吧, 嘛) for casual content to enhance spoken feel
- **Preserve imagery** - translate metaphors vividly rather than abstractly
- **Break long sentences** - one English sentence often becomes 2-3 Chinese phrases

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

**Polishing Focus Areas:**
- Verify "你" vs "您" matches the original tone
- Check for natural modal particles in casual content
- Ensure vivid imagery is preserved (e.g., "slot machine" → "老虎机")
- Confirm sentence rhythm feels natural when read aloud
- Remove consecutive "的" characters by restructuring

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

**Key Features:**
- Context-aware tone selection ("你" vs "您")
- Imagery and metaphor translation guidance
- Modal particles for colloquial feel
- Sentence breaking and flow optimization

### references/review_prompt.md

Structured review report prompt used in Step 3. Generates a comprehensive review report including:
- Terminology consistency check against glossary
- Translation accuracy assessment
- Fluency and style optimization suggestions
- Formatting verification
- Priority-ranked modification recommendations

### references/polishing_prompt.md

Fixed polishing prompt with style guidelines used in Step 4. Load this when reviewing and refining the Chinese translation, incorporating feedback from the review report.

**Key Features:**
- Tone and register verification
- Imagery preservation checks
- Rhythm and flow optimization
- Heading style adaptation
- Redundancy removal

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

### Scenario 3: Complex Site with Login Requirement (e.g., Private Content)

User: "翻译这篇需要登录的博客"

Workflow:
1. **尝试 fetch_blog.py：**
   - Run: `python3 scripts/fetch_blog.py "<url>"`
   - 对于公开内容，defuddle.md 通常可以正常处理

2. **如果抓取失败（需要登录）：**
   - 在浏览器中手动访问并登录
   - 复制文章内容
   - 手动创建 `x-com/article-title/1-original.md` 并粘贴内容

3. **继续标准翻译流程：**
   - Step 2: 翻译到 `2-draft.md`
   - Step 3: 审校到 `3-review.md`
   - Step 4: 润色到 `4-final.md`

## Implementation Notes

- Always verify the English markdown file was created successfully before proceeding to translation
- **Step 2 (First-round Translation):** Generate a complete but raw translation without over-polishing
  - Choose "你" or "您" based on content type (see style guidelines table)
  - Prioritize Chinese expressions over English loanwords
  - Break long sentences for natural Chinese rhythm
- **Step 3 (Review Report):** This is a critical quality gate - systematically check terminology against glossary
  - The review report serves as documentation for translation decisions
  - It helps identify terms that should be added to the glossary for future consistency
  - Review reports can be shared with human editors for collaborative improvement
- **Step 4 (Polish):** Address all high and medium priority issues from the review report
  - Verify tone consistency (你/您, modal particles)
  - Ensure imagery and metaphors are vivid
  - Check sentence rhythm and flow
- **CRITICAL - Preserve Images:** All image references `![alt](url)` must be preserved in translation
  - defuddle.md automatically extracts images and converts to markdown format
  - During translation (Step 2 & 4), never remove or modify image markdown
  - Keep images in their original positions relative to text content
- Preserve all code blocks, URLs, and technical terms during translation
- Maintain consistent formatting between all versions (English, 初译, 审校, 中译)
- Check for existing files before overwriting to avoid data loss
- Consider keeping all workflow files (初译, 审校, 中译) for traceability, or delete 初译 if space is limited

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
