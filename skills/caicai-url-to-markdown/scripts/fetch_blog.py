#!/usr/bin/env python3
"""
Fetch blog content from URL and convert to markdown (通用方案)
Supports two fetch strategies:
1. defuddle.md (recommended, for JavaScript-heavy sites like X.com, Medium)
2. Direct fetch with readability (for simple static sites)
"""

import sys
import re
import os
from urllib.parse import urlparse
import requests
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    from readability import Document
    from markdownify import markdownify
    from bs4 import BeautifulSoup
except ImportError as e:
    logger.error("Missing required packages. Install with: pip install readability-lxml markdownify beautifulsoup4 requests")
    sys.exit(1)


def extract_domain(url: str) -> str:
    """Extract domain from URL and convert to folder name"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    domain = re.sub(r'^www\.', '', domain)
    domain = domain.replace('.', '-')
    return domain


def title_to_kebab_case(title: str) -> str:
    """Convert title to kebab-case filename (2-6 words)"""
    title = re.sub(r'[^\w\s-]', '', title)
    title = title.lower()
    words = title.split()
    if len(words) > 6:
        words = words[:6]
    kebab = '-'.join(words)
    kebab = re.sub(r'-+', '-', kebab)
    kebab = kebab.strip('-')
    return kebab


def extract_title_from_defuddle(content: str) -> str:
    """Extract title from defuddle.md YAML frontmatter or content"""
    match = re.search(r'^title:\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "untitled"


def try_defuddle_md(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Try to fetch content using defuddle.md service"""
    try:
        logger.info("Trying defuddle.md service...")

        parsed = urlparse(url)
        defuddle_url = f"https://defuddle.md/{parsed.netloc}{parsed.path}"
        if parsed.query:
            defuddle_url += f"?{parsed.query}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(defuddle_url, headers=headers, timeout=60)
        response.raise_for_status()

        content = response.text

        if not content or len(content.strip()) < 100:
            logger.warning("defuddle.md returned empty or very short content")
            return None, None

        error_patterns = [
            "could not fetch", "error fetching",
            "failed to fetch", "unable to fetch"
        ]
        if any(pattern in content.lower() for pattern in error_patterns):
            logger.warning("defuddle.md returned error message")
            return None, None

        title = extract_title_from_defuddle(content)
        logger.info(f"defuddle.md success! Title: {title}")
        return title, content

    except Exception as e:
        logger.warning(f"defuddle.md failed: {e}")
        return None, None


def try_direct_fetch(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Try to fetch content directly using readability"""
    try:
        logger.info("Trying direct fetch with readability...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        html = response.text

        js_required_patterns = [
            "JavaScript is not available", "JavaScript is disabled",
            "enable JavaScript", "Please enable JavaScript"
        ]
        if any(pattern in html for pattern in js_required_patterns):
            logger.warning("Page requires JavaScript, direct fetch cannot handle it")
            return None, None

        doc = Document(html)
        title = doc.title()

        if not title or title.strip() == "":
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "untitled"

        title = re.sub(r'\|.*$', '', title)
        title = re.sub(r'-.*$', '', title)
        title = re.sub(r'\s+', ' ', title).strip()

        soup = BeautifulSoup(html, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        article = soup.find('article') or soup.find('main') or soup.find('div', class_='entry-content')
        html_content = str(article) if article else str(soup.find('body') or soup)

        markdown_content = markdownify(html_content, heading_style="ATX")
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        markdown_content = re.sub(r'\[Link to heading\]\(#[^)]+\)', '', markdown_content)

        logger.info(f"Direct fetch success! Title: {title}")
        return title, markdown_content

    except Exception as e:
        logger.warning(f"Direct fetch failed: {e}")
        return None, None


def save_markdown(domain: str, article_folder: str, content: str, source_url: str = "") -> str:
    """Save markdown content to article folder as 1-original.md"""
    os.makedirs(domain, exist_ok=True)
    article_path = os.path.join(domain, article_folder)
    os.makedirs(article_path, exist_ok=True)
    filepath = os.path.join(article_path, "1-original.md")

    if os.path.exists(filepath):
        logger.warning(f"File already exists: {filepath}")
        overwrite = input("File already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            logger.info("Operation cancelled.")
            sys.exit(0)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python fetch_blog.py <blog-url>")
        print("\nThis script is the generic fetcher for common sites:")
        print("  - X.com / Twitter")
        print("  - Medium")
        print("  - WeChat Articles (mp.weixin.qq.com)")
        print("  - Technical blogs")
        print("  - Static documentation sites")
        print("\nFor special sites, use router.py or dedicated scripts:")
        print("  - Feishu: fetch_feishu.py")
        print("  - Zhihu: fetch_zhihu.py")
        sys.exit(1)

    url = sys.argv[1]

    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            logger.error("Invalid URL format")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Invalid URL: {e}")
        sys.exit(1)

    logger.info("Starting blog fetch and conversion...")
    logger.info(f"URL: {url}")

    title, content = None, None

    # Strategy 1: Try defuddle.md (best for JavaScript-heavy sites)
    title, content = try_defuddle_md(url)

    # Strategy 2: Try direct fetch if defuddle failed
    if content is None:
        title, content = try_direct_fetch(url)

    if content is None:
        logger.error("Failed to fetch content from all available strategies.")
        logger.error("\nSuggestions:")
        logger.error("1. Check if the URL is accessible")
        logger.error("2. For sites requiring login, try the dedicated script")
        logger.error("3. Use router.py for automatic site detection")
        sys.exit(1)

    domain = extract_domain(url)
    article_folder = title_to_kebab_case(title)

    logger.info(f"Domain: {domain}")
    logger.info(f"Article folder: {article_folder}")

    filepath = save_markdown(domain, article_folder, content, source_url=url)

    logger.info(f"\n{'='*60}")
    logger.info(f"Successfully saved markdown to: {filepath}")
    logger.info(f"{'='*60}")

    return filepath


if __name__ == "__main__":
    main()
