#!/usr/bin/env python3
"""
Fetch Zhihu article with anti-bot bypass.
Two-stage strategy:
  1. curl_impersonate (HTTP/TLS impersonation) + Readability
  2. Puppeteer-extra (browser automation) with modal removal and scrolling
"""

import sys
import re
import os
import subprocess
import shutil
from typing import Optional, Tuple, Dict
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    from readability import Document
    from markdownify import markdownify
    from bs4 import BeautifulSoup
except ImportError as e:
    logger.error("Missing packages: pip install readability-lxml markdownify beautifulsoup4")
    sys.exit(1)


ZH_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "cache-control": "max-age=0",
}


def is_zhihu_url(url: str) -> bool:
    """检查是否为知乎 URL"""
    patterns = [
        r'zhuanlan\.zhihu\.com/p/\d+',
        r'zhihu\.com/question/\d+',
        r'zhihu\.com/p/\d+'
    ]
    return any(re.search(p, url) for p in patterns)


def extract_zhihu_id(url: str) -> Optional[str]:
    """提取文章/回答 ID"""
    patterns = [
        r'zhuanlan\.zhihu\.com/p/(\d+)',
        r'zhihu\.com/question/\d+/answer/(\d+)',
        r'zhihu\.com/p/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def has_curl_impersonate() -> bool:
    """检查是否安装了 curl_impersonate"""
    return shutil.which("curl_impersonate") is not None or shutil.which("curl_chrome120") is not None


def curl_impersonate_fetch(url: str) -> Optional[str]:
    """
    Stage 1: 使用 curl_impersonate 获取页面
    模拟现代 Chrome 的 TLS/HTTP 指纹
    """
    # 尝试不同的 curl_impersonate 变体
    curl_commands = [
        ["curl_chrome120", "--silent", "--show-error", "-L", "-A", ZH_HEADERS["user-agent"], url],
        ["curl_impersonate", "--silent", "--show-error", "-L", "-A", ZH_HEADERS["user-agent"], url],
    ]

    for cmd in curl_commands:
        if not shutil.which(cmd[0]):
            continue

        try:
            logger.info(f"Trying {cmd[0]} for {url}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and len(result.stdout) > 1000:
                logger.info(f"{cmd[0]} success!")
                return result.stdout
            else:
                logger.warning(f"{cmd[0]} failed: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            logger.warning(f"{cmd[0]} timeout")
        except Exception as e:
            logger.warning(f"{cmd[0]} error: {e}")

    return None


def clean_zhihu_html(html: str) -> str:
    """清理知乎 HTML，移除登录弹窗等干扰元素"""
    soup = BeautifulSoup(html, 'html.parser')

    # 移除干扰元素
    selectors_to_remove = [
        # 登录/注册弹窗
        '.Modal-wrapper',
        '.SignFlowModal',
        '.login-modal',
        '[class*="Modal"][class*="show"]',
        # 悬浮按钮
        '.CornerButtons',
        '.Sticky',
        # 评论区（通常不需要）
        '.Comments',
        '.Comment',
        # 推荐/相关文章
        '.Recommendations',
        '.RelatedReadings',
        # 操作栏
        '.ContentItem-actions',
        '.RichContent-actions',
        # 广告/推广
        '[class*="Ad"]',
        '[class*="ad-"]',
    ]

    for selector in selectors_to_remove:
        for elem in soup.select(selector):
            elem.decompose()

    # 移除 backdrop 遮罩
    for elem in soup.find_all(style=re.compile(r'backdrop|z-index.*1000', re.I)):
        elem.decompose()

    return str(soup)


def extract_with_readability(html: str) -> Tuple[Optional[str], Optional[str]]:
    """
    使用 Mozilla Readability 提取正文
    Returns: (title, content_html)
    """
    try:
        doc = Document(html)
        title = doc.title()
        content_html = doc.summary()

        if not content_html or len(content_html) < 500:
            return None, None

        return title, content_html
    except Exception as e:
        logger.warning(f"Readability extraction failed: {e}")
        return None, None


def html_to_markdown(html: str, title: str = "") -> str:
    """将 HTML 转换为 Markdown"""
    # 使用 BeautifulSoup 进一步清理
    soup = BeautifulSoup(html, 'html.parser')

    # 移除 script/style
    for elem in soup(['script', 'style']):
        elem.decompose()

    # 转换图片链接（知乎图片可能有防盗链）
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src and src.startswith('//'):
            img['src'] = 'https:' + src
        # 移除 data-actualsrc 等属性，使用实际可访问的链接
        if img.get('data-actualsrc'):
            img['src'] = img['data-actualsrc']

    # 转换为 markdown
    md = markdownify(str(soup), heading_style="ATX")

    # 清理
    md = re.sub(r'\n{3,}', '\n\n', md)
    md = re.sub(r'\[Link to heading\]\(#[^)]+\)', '', md)

    # 添加标题
    if title and not md.startswith('# '):
        md = f"# {title}\n\n{md}"

    return md.strip()


def find_chrome_executable() -> Optional[str]:
    """查找 Chrome/Chromium/Edge 可执行文件"""
    env_path = os.environ.get('CHROME_PATH')
    if env_path and os.path.exists(env_path):
        return env_path

    candidates = [
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/microsoft-edge",
        # Windows (via WSL or direct)
        "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
        "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    # 尝试 which
    for cmd in ['google-chrome', 'chromium', 'chromium-browser', 'chrome']:
        if shutil.which(cmd):
            return cmd

    return None


def puppeteer_fetch(url: str) -> Optional[str]:
    """
    Stage 2: 使用 puppeteer-extra 获取页面
    包含滚动、移除登录弹窗等操作
    """
    chrome_path = find_chrome_executable()
    if not chrome_path:
        logger.error("Chrome/Chromium not found. Set CHROME_PATH or install Chrome.")
        return None

    # 创建临时 JS 脚本
    puppeteer_script = '''
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        executablePath: process.env.CHROME_PATH || undefined,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920,1080',
        ]
    });

    const page = await browser.newPage();

    // 设置 headers
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    });

    // 设置 viewport
    await page.setViewport({ width: 1920, height: 1080 });

    try {
        // 访问页面
        await page.goto(process.argv[2], {
            waitUntil: 'networkidle2',
            timeout: 60000
        });

        // 等待内容加载
        await new Promise(r => setTimeout(r, 3000));

        // 移除登录弹窗
        await page.evaluate(() => {
            const selectors = [
                '.Modal-wrapper',
                '.SignFlowModal',
                '[class*="Modal"][class*="show"]',
                '.login-modal',
            ];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.remove());
            });
            // 移除 backdrop
            document.querySelectorAll('[style*="backdrop"], [style*="z-index: 1000"]').forEach(el => el.remove());
        });

        // 展开全文（如果有按钮）
        const expandBtn = await page.$('.ContentItem-expandButton, .Post-ExpandButton');
        if (expandBtn) {
            await expandBtn.click();
            await new Promise(r => setTimeout(r, 1000));
        }

        // 滚动触发懒加载
        for (let i = 0; i < 5; i++) {
            await page.evaluate(() => window.scrollBy(0, 800));
            await new Promise(r => setTimeout(r, 500));
        }

        // 获取 HTML
        const html = await page.content();
        console.log(html);

    } catch (e) {
        console.error('Puppeteer error:', e.message);
        process.exit(1);
    } finally {
        await browser.close();
    }
})();
'''

    # 写入临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(puppeteer_script)
        temp_script = f.name

    try:
        env = os.environ.copy()
        env['CHROME_PATH'] = chrome_path
        # 添加 NODE_PATH 以便临时脚本能找到全局安装的模块
        npm_root = "/Users/cailangri/.npm-global/lib/node_modules"
        env['NODE_PATH'] = npm_root + ':' + env.get('NODE_PATH', '')

        logger.info(f"Launching puppeteer with {chrome_path}")
        result = subprocess.run(
            ['node', temp_script, url],
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )

        if result.returncode == 0 and len(result.stdout) > 5000:
            logger.info("Puppeteer fetch success!")
            return result.stdout
        else:
            logger.warning(f"Puppeteer failed: {result.stderr[:300]}")
            return None

    except Exception as e:
        logger.warning(f"Puppeteer error: {e}")
        return None
    finally:
        os.unlink(temp_script)


def is_blocked_content(html: str) -> bool:
    """检查内容是否被拦截或需要登录

    注意：知乎页面通常包含导航栏的"登录/注册"按钮，
    所以需要检查更明确的拦截标志
    """
    # 明确的拦截/错误标志
    blocked_patterns = [
        '您当前请求存在异常',
        'code:403',
        '请登录后查看',  # 明确的登录要求
        '需要登录才能',
        '登录以继续',
    ]

    html_lower = html.lower()
    for pattern in blocked_patterns:
        if pattern.lower() in html_lower:
            return True

    # 检查内容是否过短
    if len(html) < 5000:
        return True

    # 检查是否有文章正文内容（知乎文章通常有 RichContent 或 Post-RichTextContainer）
    content_indicators = [
        'RichContent-inner',
        'Post-RichTextContainer',
        'ContentItem-RichText',
        'RichText',
    ]
    has_content = any(indicator in html for indicator in content_indicators)

    # 如果 HTML 很长且有内容标志，认为不是被拦截
    if len(html) > 50000 and has_content:
        return False

    # 默认认为被拦截（需要进一步验证）
    return not has_content


def fetch_zhihu(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    主函数：两阶段抓取策略
    Returns: (title, markdown_content)
    """
    logger.info(f"Fetching Zhihu article: {url}")

    # ===== Stage 1: curl_impersonate =====
    if has_curl_impersonate():
        logger.info("Stage 1: Trying curl_impersonate...")
        html = curl_impersonate_fetch(url)

        if html and not is_blocked_content(html):
            logger.info("Stage 1 success, extracting content...")
            html = clean_zhihu_html(html)
            title, content_html = extract_with_readability(html)

            if content_html:
                markdown = html_to_markdown(content_html, title or "")
                if len(markdown) > 500:
                    return title, markdown

    # ===== Stage 2: Puppeteer =====
    logger.info("Stage 2: Trying puppeteer-extra...")

    # 检查 node 和 puppeteer 是否可用
    if not shutil.which('node'):
        logger.error("Node.js not found. Please install Node.js for puppeteer fallback.")
        return None, None

    html = puppeteer_fetch(url)

    if html:
        if is_blocked_content(html):
            logger.error("Content blocked or requires login. Please provide authenticated cookies.")
            return None, None

        logger.info("Stage 2 success, extracting content...")
        html = clean_zhihu_html(html)
        title, content_html = extract_with_readability(html)

        if content_html:
            markdown = html_to_markdown(content_html, title or "")
            return title, markdown

    return None, None


def main():
    if len(sys.argv) != 2:
        print("Usage: python fetch_zhihu.py <zhihu-url>")
        print("\nTwo-stage anti-bot strategy:")
        print("  1. curl_impersonate (HTTP/TLS impersonation)")
        print("  2. puppeteer-extra (browser automation)")
        print("\nRequirements:")
        print("  Option A: curl_impersonate (faster)")
        print("    - Install: https://github.com/yifeikong/curl-impersonate")
        print("  Option B: puppeteer-extra (fallback)")
        print("    - npm install puppeteer-extra puppeteer-extra-plugin-stealth")
        print("    - Set CHROME_PATH if Chrome not in standard location")
        sys.exit(1)

    url = sys.argv[1]

    if not is_zhihu_url(url):
        logger.error(f"Invalid Zhihu URL: {url}")
        logger.error("Supported formats:")
        logger.error("  - https://zhuanlan.zhihu.com/p/12345678")
        logger.error("  - https://www.zhihu.com/question/12345678/answer/87654321")
        sys.exit(1)

    title, content = fetch_zhihu(url)

    if content:
        print(content)
    else:
        print("\n" + "="*60, file=sys.stderr)
        print("FAILED TO FETCH ZHIHU CONTENT", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print("\nPossible reasons:", file=sys.stderr)
        print("  - Article requires login to view", file=sys.stderr)
        print("  - Anti-bot measures detected", file=sys.stderr)
        print("  - Network restrictions", file=sys.stderr)
        print("\nFallback options:", file=sys.stderr)
        print("  1. Copy article text manually and save to file", file=sys.stderr)
        print("  2. Use browser dev tools to copy rendered HTML", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
