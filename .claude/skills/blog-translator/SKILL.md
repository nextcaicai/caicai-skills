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

### Step 2: Translate English Markdown to Chinese

1. Read the English markdown file
2. Use the fixed translation prompt from `references/translation_prompt.md`
3. Translate entire content maintaining technical accuracy

### Step 3: Polish Chinese Translation

1. Use the fixed polishing prompt from `references/polishing_prompt.md`
2. Apply terminology glossary and style guidelines
3. Review and refine translation for natural flow
4. Save polished Chinese version to `<project-root>/<domain>/中译-<blog>.md`

## File Organization

The skill organizes files by domain with bilingual versions:

```
<project-root>/
└── <domain>/
    └── <blog>.md           # English version
    └── 中译-<blog>.md       # Chinese version
```

### Naming Convention

- **Domain**: Extracted from URL (e.g., `github-com`, `medium-com`, `mp-weixin-qq-com`)
- **English filename**: `<blog>` - Extracted from page title or URL path, converted to kebab-case, 2-6 words
  - Examples: `understanding-machine-learning.md`, `react-hooks-guide.md`
- **Chinese filename**: `中译-<blog>` - Prefixed with `中译-` to the English filename
  - Examples: `中译-understanding-machine-learning.md`, `中译-react-hooks-guide.md`

**File Naming Examples:**

```
github-com/
  ├── state-management-patterns.md
  └── 中译-state-management-patterns.md

medium-com/
  ├── advanced-typescript-tips.md
  └── 中译-advanced-typescript-tips.md

mp-weixin-qq-com/
  ├── wechat-mini-program-guide.md
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

### references/polishing_prompt.md

Fixed polishing prompt with terminology glossary and style guidelines used in Step 3. Load this when reviewing and refining the Chinese translation.

### references/glossary.md

Optional: Domain-specific terminology glossary for consistent translations across multiple blog translations.

## Common Usage Scenarios

### Scenario 1: Translate a Single Blog

User: "请帮我翻译并保存这个博客：https://blog.rust-lang.org/2024/01/04/rust-1.75.0.html"

Workflow:
1. Extract domain: `rust-lang-org`
2. Run: `python3 scripts/fetch_blog.py "https://blog.rust-lang.org/2024/01/04/rust-1.75.0.html"`
3. Save English to: `rust-lang-org/rust-1-75-0-release.md`
4. Translate using prompt from `references/translation_prompt.md`
5. Polish using prompt from `references/polishing_prompt.md`
6. Save Chinese to: `rust-lang-org/中译-rust-1-75-0-release.md`

### Scenario 2: Multiple Blogs from Same Domain

When users translate multiple blogs from the same site, all files are organized under the same domain directory for easy management.

## Implementation Notes

- Always verify the English markdown file was created successfully before proceeding to translation
- Preserve all code blocks, URLs, and technical terms during translation
- Maintain consistent formatting between English and Chinese versions
- Check for existing files before overwriting to avoid data loss

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
