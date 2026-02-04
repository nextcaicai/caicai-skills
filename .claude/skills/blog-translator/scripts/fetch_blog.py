#!/usr/bin/env python3
"""
Fetch blog content from URL and convert to markdown
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


def extract_title(readability_doc: Document, url: str) -> str:
    """Extract title from readability document or URL"""
    # First try to get title from document
    title = readability_doc.title()
    if title and len(title.strip()) > 0:
        title = title.strip()
    else:
        # Fallback to URL path
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        # Get last part of path or use domain
        if path:
            title = path.split('/')[-1]
        else:
            title = extract_domain(url)

    # Clean title for filename
    # Remove common suffixes
    title = re.sub(r'\|.*$', '', title)  # Remove | Site Name
    title = re.sub(r'-.*$', '', title)   # Remove - Site Name
    title = re.sub(r'\s+', ' ', title)   # Normalize whitespace
    title = title.strip()

    return title


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
    elif len(words) < 2:
        # If too short, add more context from the title
        pass

    # Join with hyphens
    kebab = '-'.join(words)

    # Clean up any double hyphens or trailing hyphens
    kebab = re.sub(r'-+', '-', kebab)
    kebab = kebab.strip('-')

    return kebab


def clean_html_with_beautifulsoup(html: str) -> str:
    """Use BeautifulSoup to extract article content while preserving structure"""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()

    # Try to find article or main content area
    article = soup.find('article') or soup.find('main') or soup.find('div', class_='entry-content')

    if article:
        return str(article)

    # Fallback: find the element with the most text content
    body = soup.find('body')
    if body:
        return str(body)

    return str(soup)


def fetch_and_convert(url: str) -> Tuple[str, str]:
    """Fetch URL content and convert to markdown"""
    try:
        logger.info(f"Fetching URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Try readability first for title extraction
        doc = Document(response.text)
        title = extract_title(doc, url)

        # Use BeautifulSoup to extract content while preserving lists
        html_content = clean_html_with_beautifulsoup(response.text)

        # Convert HTML to markdown with options to preserve lists
        markdown_content = markdownify(
            html_content,
            heading_style="ATX"
        )

        # Clean up excessive newlines
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

        # Clean up "Link to heading" anchor links (e.g., [Link to heading](#anchor))
        # These are visual noise in markdown and don't provide value for reading
        markdown_content = re.sub(r'\[Link to heading\]\(#[^)]+\)', '', markdown_content)

        # Also clean up other common anchor link patterns that are noise
        # Pattern like: ## [](#anchor)**Heading Text**
        markdown_content = re.sub(r'## \[\]\(#[^)]+\)', '## ', markdown_content)

        logger.info(f"Extracted title: {title}")

        return title, markdown_content

    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing content: {e}")
        sys.exit(1)


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


def generate_filename_from_url(url: str) -> Tuple[str, str, str]:
    """Generate domain and filename from URL"""
    # Extract domain
    domain = extract_domain(url)

    # Mock fetching just to get title
    # In real usage, this would fetch the actual content
    logger.info("Fetching content to extract title...")

    # For this script, we'll actually fetch to get the real title
    # This is a more accurate approach
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        doc = Document(response.text)
        title = extract_title(doc, url)
        kebab_title = title_to_kebab_case(title)

        # Add .md extension
        filename = f"{kebab_title}.md"

        return domain, filename, title

    except Exception as e:
        logger.error(f"Error extracting title: {e}")
        # Fallback to using URL path
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        if path_parts:
            fallback_title = path_parts[-1].replace('-', ' ')
            kebab_title = title_to_kebab_case(fallback_title)
        else:
            kebab_title = 'article'

        filename = f"{kebab_title}.md"
        return domain, filename, kebab_title


def main():
    if len(sys.argv) != 2:
        print("Usage: python fetch_blog.py <blog-url>")
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

    # Fetch content
    title, markdown_content = fetch_and_convert(url)

    # Generate filename
    domain = extract_domain(url)
    kebab_title = title_to_kebab_case(title)
    filename = f"{kebab_title}.md"

    # Use kebab_title as article folder name
    article_folder = kebab_title

    logger.info(f"Domain: {domain}")
    logger.info(f"Article folder: {article_folder}")

    # Save to file
    filepath = save_markdown(domain, article_folder, markdown_content)

    logger.info(f"\nSuccessfully saved English markdown to: {filepath}")
    logger.info(f"\nNext steps:")
    logger.info(f"1. Create first-round translation: {domain}/{article_folder}/2-draft.md")
    logger.info(f"2. Create review report: {domain}/{article_folder}/3-review.md")
    logger.info(f"3. Create final version: {domain}/{article_folder}/4-final.md")

    return filepath


if __name__ == "__main__":
    main()
