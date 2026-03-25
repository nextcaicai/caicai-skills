#!/usr/bin/env python3
"""
Fetch blog content from URL and convert to markdown
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

# Configure logging
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
    # Remove common prefixes
    domain = re.sub(r'^www\.', '', domain)
    # Convert dots to hyphens
    domain = domain.replace('.', '-')
    return domain


def title_to_kebab_case(title: str) -> str:
    """Convert title to kebab-case filename (2-6 words)"""
    # Remove special characters except spaces and hyphens
    title = re.sub(r'[^\w\s-]', '', title)
    # Convert to lowercase
    title = title.lower()
    # Split into words
    words = title.split()
    # Limit to 2-6 words
    if len(words) > 6:
        words = words[:6]
    # Join with hyphens
    kebab = '-'.join(words)
    # Clean up any double hyphens or trailing hyphens
    kebab = re.sub(r'-+', '-', kebab)
    kebab = kebab.strip('-')
    return kebab


def extract_title_from_defuddle(content: str) -> str:
    """Extract title from defuddle.md YAML frontmatter or content"""
    # Try to extract title from YAML frontmatter
    match = re.search(r'^title:\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    # Fallback: extract first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "untitled"


def try_defuddle_md(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Try to fetch content using defuddle.md service
    Returns (title, content) or (None, None) if failed
    """
    try:
        logger.info("Trying defuddle.md service...")

        # Convert URL to defuddle.md format
        # https://x.com/neethanwu/status/... -> https://defuddle.md/x.com/neethanwu/status/...
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

        # Check if defuddle returned valid content (not an error page)
        if not content or len(content.strip()) < 100:
            logger.warning("defuddle.md returned empty or very short content")
            return None, None

        # Check if it's an error message
        error_patterns = [
            "could not fetch",
            "error fetching",
            "failed to fetch",
            "unable to fetch"
        ]
        content_lower = content.lower()
        if any(pattern in content_lower for pattern in error_patterns):
            logger.warning("defuddle.md returned error message")
            return None, None

        # Extract title from content
        title = extract_title_from_defuddle(content)

        logger.info(f"defuddle.md success! Title: {title}")
        return title, content

    except requests.RequestException as e:
        logger.warning(f"defuddle.md failed: {e}")
        return None, None
    except Exception as e:
        logger.warning(f"defuddle.md unexpected error: {e}")
        return None, None


def try_direct_fetch(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Try to fetch content directly using readability
    Returns (title, content) or (None, None) if failed
    """
    try:
        logger.info("Trying direct fetch with readability...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        html = response.text

        # Check if we got a JavaScript-required page
        js_required_patterns = [
            "JavaScript is not available",
            "JavaScript is disabled",
            "enable JavaScript",
            "Please enable JavaScript"
        ]
        if any(pattern in html for pattern in js_required_patterns):
            logger.warning("Page requires JavaScript, direct fetch cannot handle it")
            return None, None

        # Try readability
        doc = Document(html)
        title = doc.title()

        if not title or title.strip() == "":
            # Fallback: try to get title from HTML
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            else:
                title = "untitled"

        # Clean title
        title = re.sub(r'\|.*$', '', title)  # Remove | Site Name
        title = re.sub(r'-.*$', '', title)   # Remove - Site Name
        title = re.sub(r'\s+', ' ', title)   # Normalize whitespace
        title = title.strip()

        # Use BeautifulSoup to extract content
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        # Try to find article or main content area
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='entry-content')

        if article:
            html_content = str(article)
        else:
            body = soup.find('body')
            html_content = str(body) if body else str(soup)

        # Convert to markdown
        markdown_content = markdownify(html_content, heading_style="ATX")

        # Clean up
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        markdown_content = re.sub(r'\[Link to heading\]\(#[^)]+\)', '', markdown_content)
        markdown_content = re.sub(r'## \[\]\(#[^)]+\)', '## ', markdown_content)

        logger.info(f"Direct fetch success! Title: {title}")
        return title, markdown_content

    except requests.RequestException as e:
        logger.warning(f"Direct fetch failed: {e}")
        return None, None
    except Exception as e:
        logger.warning(f"Direct fetch unexpected error: {e}")
        return None, None


def save_markdown(domain: str, article_folder: str, content: str) -> str:
    """Save markdown content to article folder as 1-original.md"""
    # Create domain directory if it doesn't exist
    os.makedirs(domain, exist_ok=True)

    # Create article subfolder
    article_path = os.path.join(domain, article_folder)
    os.makedirs(article_path, exist_ok=True)

    # Full path for 1-original.md
    filepath = os.path.join(article_path, "1-original.md")

    # Check if file already exists
    if os.path.exists(filepath):
        logger.warning(f"File already exists: {filepath}")
        overwrite = input("File already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            logger.info("Operation cancelled.")
            sys.exit(0)

    # Write content
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
        print("\nThis script supports two fetch strategies:")
        print("  1. defuddle.md - For JavaScript-heavy sites (X.com, Medium)")
        print("  2. Direct fetch - For simple static sites")
        sys.exit(1)

    url = sys.argv[1]

    # Validate URL
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

    # Strategy 1: Try defuddle.md (best for JavaScript-heavy sites)
    title, content = try_defuddle_md(url)

    # Strategy 2: Try direct fetch if defuddle failed
    if content is None:
        title, content = try_direct_fetch(url)

    # If all strategies failed
    if content is None:
        logger.error("\n" + "="*60)
        logger.error("Failed to fetch content from all available strategies.")
        logger.error("="*60)
        logger.error("\nSuggestions:")
        logger.error("1. Check if the URL is accessible and not behind a paywall")
        logger.error("2. For sites requiring login, defuddle.md may not work")
        logger.error("3. Try again later if the site is experiencing issues")
        logger.error("4. You can manually save the article content to 1-original.md")
        sys.exit(1)

    # Generate filename
    domain = extract_domain(url)
    kebab_title = title_to_kebab_case(title)
    article_folder = kebab_title

    logger.info(f"Domain: {domain}")
    logger.info(f"Article folder: {article_folder}")

    # Save to file
    filepath = save_markdown(domain, article_folder, content)

    logger.info(f"\n{'='*60}")
    logger.info(f"Successfully saved English markdown to: {filepath}")
    logger.info(f"{'='*60}")
    logger.info(f"\nNext steps:")
    logger.info(f"  1. Create first-round translation: {domain}/{article_folder}/2-draft.md")
    logger.info(f"  2. Create review report: {domain}/{article_folder}/3-review.md")
    logger.info(f"  3. Create final version: {domain}/{article_folder}/4-final.md")

    return filepath


if __name__ == "__main__":
    main()
