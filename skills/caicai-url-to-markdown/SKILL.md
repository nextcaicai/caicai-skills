---
name: caicai-url-to-markdown
description: 将 URL 内容抓取并转换为 Markdown 格式。使用场景：(1) 用户请求"把这个网页转成 markdown" (2) 用户提供 URL 并要求保存为 markdown 文件 (3) 需要抓取网页内容进行后续处理时。自动根据 URL 类型选择最佳抓取方案。
---

# Caicai Url To Markdown

## Overview

将 URL 内容抓取并转换为干净的 Markdown 格式。采用路由架构，根据 URL 类型自动分发到专用脚本或通用方案。

## Architecture

```
router.py (统一入口)
    ├── fetch_feishu.py  → 飞书 Open API
    ├── fetch_zhihu.py   → 知乎 Playwright
    └── fetch_blog.py    → 通用方案 (X.com/公众号/技术博客等)
            ├── defuddle.md
            └── Direct Fetch
```

## Installation

### Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP requests
- `readability-lxml` - Content extraction
- `markdownify` - HTML to Markdown conversion
- `beautifulsoup4` - HTML parsing

### Optional Dependencies

**For Zhihu articles (puppeteer-extra):**
```bash
npm install -g puppeteer-extra puppeteer-extra-plugin-stealth puppeteer
```

**For Zhihu articles (curl_impersonate - recommended):**
```bash
# macOS
brew install curl-impersonate
```

**For Feishu documents:**
```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

## Quick Start

推荐使用 router 自动路由：

```bash
python3 scripts/router.py "<url>"
```

或直接调用专用脚本：

```bash
# 飞书文档
python3 scripts/fetch_feishu.py "https://my.feishu.cn/wiki/xxx"

# 通用站点
python3 scripts/fetch_blog.py "https://example.com/article"
```

## Site-Specific Handlers

### 飞书文档 (feishu.cn / larksuite.com)

**路由：** `router.py` → `fetch_feishu.py`

**前置条件：**
```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

**权限设置：**
1. 访问 [飞书开发者平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 开启权限：`docx:document:readonly`, `wiki:wiki:readonly`
4. 发布应用版本
5. 将应用添加到文档协作者

### 知乎 (zhihu.com / zhuanlan.zhihu.com)

**路由：** `router.py` → `fetch_zhihu.py`

**两阶段反爬策略：**

1. **Stage 1** - curl_impersonate (HTTP/TLS 指纹模拟)
   - 模拟现代 Chrome 的 TLS/HTTP 指纹
   - 快速、轻量、无需浏览器

2. **Stage 2** - puppeteer-extra (浏览器自动化)
   - stealth 插件绕过检测
   - 自动移除登录弹窗和遮罩
   - 滚动触发懒加载内容

**前置条件（二选一）：**

方案 A - curl_impersonate (推荐，更快)：
```bash
# macOS
brew install curl-impersonate

# 或使用预编译版本
# https://github.com/yifeikong/curl-impersonate
```

方案 B - puppeteer-extra (备用)：
```bash
npm install -g puppeteer-extra puppeteer-extra-plugin-stealth
```

**环境变量：**
```bash
# 如果 Chrome 不在标准路径
export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

**限制说明：**
- 部分付费/专栏文章需要登录
- 如遇账号限制，请手动复制内容

### 通用站点

**路由：** `router.py` → `fetch_blog.py`

支持的站点：
- **X.com / Twitter** - 通过 defuddle.md
- **微信公众号** (mp.weixin.qq.com)
- **Medium**
- **技术博客和文档站点**

策略优先级：
1. **defuddle.md** - JavaScript 渲染的站点
2. **Direct Fetch** - 静态站点

## Output

- 域名提取：自动从 URL 提取域名并转换为目录名（如 `x.com` → `x-com`）
- 文件命名：从标题生成 kebab-case 文件名（2-6 个词）
- 输出路径：`<domain>/<article-folder>/1-original.md`

## Scripts

### router.py

统一路由入口，根据 URL 自动选择最佳抓取方案。

```bash
python3 scripts/router.py "https://any-url.com/article"
```

### fetch_feishu.py

飞书文档专用脚本，使用飞书 Open API。

```bash
python3 scripts/fetch_feishu.py "https://my.feishu.cn/wiki/xxx"
```

### fetch_zhihu.py

知乎文章专用脚本，使用 Playwright。

```bash
python3 scripts/fetch_zhihu.py "https://zhuanlan.zhihu.com/p/xxx"
```

### fetch_blog.py

通用抓取脚本，适用于大多数公开网站。

```bash
python3 scripts/fetch_blog.py "https://x.com/user/status/xxx"
```

## Fallback

如果自动抓取失败：

1. 在浏览器中打开文章
2. 手动复制内容或导出为 Markdown
3. 保存到 `<domain>/<article>/1-original.md`
