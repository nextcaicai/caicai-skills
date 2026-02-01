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

The skill organizes files by domain with complete translation workflow artifacts:

```
<project-root>/
└── <domain>/
    └── <blog>.md              # English version (original)
    └── 初译-<blog>.md          # First-round Chinese translation
    └── 审校-<blog>.md          # Review report with terminology checks
    └── 中译-<blog>.md          # Final polished Chinese version
```

### Naming Convention

- **Domain**: Extracted from URL (e.g., `github-com`, `medium-com`, `mp-weixin-qq-com`)
- **English filename**: `<blog>` - Extracted from page title or URL path, converted to kebab-case, 2-6 words
  - Examples: `understanding-machine-learning.md`, `react-hooks-guide.md`
- **Workflow file prefixes**:
  - `初译-` : First-round translation (raw output from Step 2)
  - `审校-` : Review report with terminology and quality analysis (Step 3)
  - `中译-` : Final polished translation (Step 4)
  - Examples: `初译-react-hooks-guide.md`, `审校-react-hooks-guide.md`, `中译-react-hooks-guide.md`

**File Naming Examples:**

```
github-com/
  ├── state-management-patterns.md
  ├── 初译-state-management-patterns.md
  ├── 审校-state-management-patterns.md
  └── 中译-state-management-patterns.md

medium-com/
  ├── advanced-typescript-tips.md
  ├── 初译-advanced-typescript-tips.md
  ├── 审校-advanced-typescript-tips.md
  └── 中译-advanced-typescript-tips.md

mp-weixin-qq-com/
  ├── wechat-mini-program-guide.md
  ├── 初译-wechat-mini-program-guide.md
  ├── 审校-wechat-mini-program-guide.md
  └── 中译-wechat-mini-program-guide.md
```

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
3. Save English to: `rust-lang-org/rust-1-75-0-release.md`
4. **Step 2 - First-round Translation:** Use `references/translation_prompt.md` to translate
   - Save to: `rust-lang-org/初译-rust-1-75-0-release.md`
5. **Step 3 - Review Report:** Use `references/review_prompt.md` to generate review report
   - Check terminology against `assets/glossary.md`
   - Save to: `rust-lang-org/审校-rust-1-75-0-release.md`
6. **Step 4 - Polish:** Use `references/polishing_prompt.md` + review report to finalize
   - Save final Chinese to: `rust-lang-org/中译-rust-1-75-0-release.md`

### Scenario 2: Multiple Blogs from Same Domain

When users translate multiple blogs from the same site, all files are organized under the same domain directory for easy management.

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
