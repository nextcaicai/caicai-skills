#!/usr/bin/env python3
"""
URL Router - 根据 URL 类型分发到对应的抓取脚本
"""

import sys
import re
import os
import subprocess
from urllib.parse import urlparse
from typing import Optional, Tuple, Callable
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_script_dir() -> str:
    """获取脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))


def is_feishu_url(url: str) -> bool:
    """飞书/Lark 文档"""
    patterns = [
        r'feishu\.cn/(docx|docs|wiki)/',
        r'larksuite\.com/(docx|docs|wiki)/',
        r'my\.feishu\.cn/(docx|docs|wiki)/'
    ]
    return any(re.search(p, url) for p in patterns)


def is_zhihu_url(url: str) -> bool:
    """知乎文章/回答"""
    patterns = [
        r'zhuanlan\.zhihu\.com/p/\d+',
        r'zhihu\.com/question/\d+',
        r'zhihu\.com/p/\d+'
    ]
    return any(re.search(p, url) for p in patterns)


def is_wechat_url(url: str) -> bool:
    """微信公众号"""
    patterns = [
        r'mp\.weixin\.qq\.com',
        r'weixin\.qq\.com'
    ]
    return any(re.search(p, url) for p in patterns)


def is_x_url(url: str) -> bool:
    """X/Twitter"""
    patterns = [
        r'x\.com/\w+/status/',
        r'twitter\.com/\w+/status/'
    ]
    return any(re.search(p, url) for p in patterns)


def run_script(script_name: str, url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    运行指定的抓取脚本
    Returns: (title, content) or (None, None)
    """
    script_path = os.path.join(get_script_dir(), script_name)

    if not os.path.exists(script_path):
        logger.warning(f"脚本不存在: {script_path}")
        return None, None

    try:
        result = subprocess.run(
            [sys.executable, script_path, url],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            logger.warning(f"{script_name} 执行失败: {result.stderr}")
            return None, None

        content = result.stdout

        # 从内容中提取标题
        title = "untitled"
        for line in content.split('\n')[:30]:
            if line.startswith('# '):
                title = line[2:].strip()
                break
            if line.startswith('## '):
                title = line[3:].strip()
                break

        return title, content

    except subprocess.TimeoutExpired:
        logger.warning(f"{script_name} 执行超时")
        return None, None
    except Exception as e:
        logger.warning(f"{script_name} 执行出错: {e}")
        return None, None


def route(url: str) -> Tuple[str, str]:
    """
    根据 URL 路由到对应的处理脚本
    Returns: (script_name, description)
    """
    if is_feishu_url(url):
        return 'fetch_feishu.py', '飞书文档 API'

    if is_zhihu_url(url):
        return 'fetch_zhihu.py', '知乎 Playwright'

    if is_wechat_url(url):
        return 'fetch_blog.py', '微信公众号 (通用方案)'

    if is_x_url(url):
        return 'fetch_blog.py', 'X/Twitter (通用方案)'

    # 默认使用通用方案
    return 'fetch_blog.py', '通用方案 (defuddle/direct)'


def fetch(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    主入口：路由并执行抓取
    Returns: (title, content) or (None, None)
    """
    script, description = route(url)
    logger.info(f"路由决策: {description} -> {script}")

    return run_script(script, url)


def main():
    if len(sys.argv) != 2:
        print("Usage: python router.py <url>")
        print("\n路由规则:")
        print("  - 飞书文档      -> fetch_feishu.py (Open API)")
        print("  - 知乎文章      -> fetch_zhihu.py (Playwright)")
        print("  - 微信公众号    -> fetch_blog.py (通用方案)")
        print("  - X/Twitter     -> fetch_blog.py (通用方案)")
        print("  - 其他站点      -> fetch_blog.py (自动选择最佳策略)")
        sys.exit(1)

    url = sys.argv[1]
    script, description = route(url)

    print(f"URL: {url}")
    print(f"路由: {description} ({script})")
    print("-" * 50)

    title, content = fetch(url)

    if content:
        print(content)
    else:
        print("抓取失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
