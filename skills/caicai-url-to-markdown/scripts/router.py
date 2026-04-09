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


def run_script(script_name: str, url: str, force: bool = False) -> Tuple[Optional[str], Optional[str], str]:
    """
    运行指定的抓取脚本
    Returns: (title, content, error_message) or (None, None, error_message)
    """
    script_path = os.path.join(get_script_dir(), script_name)

    if not os.path.exists(script_path):
        error_msg = f"脚本不存在: {script_path}"
        logger.warning(error_msg)
        return None, None, error_msg

    try:
        cmd = [sys.executable, script_path, url]
        if force:
            cmd.append('--force')

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            error_msg = f"{script_name} 执行失败 (exit code {result.returncode}):\n"
            if result.stderr:
                error_msg += f"STDERR:\n{result.stderr}\n"
            if result.stdout:
                error_msg += f"STDOUT:\n{result.stdout}"
            logger.warning(error_msg)
            return None, None, error_msg

        # 最后一行是文件路径，前面是日志输出
        lines = result.stdout.strip().split('\n')
        content = None
        title = "untitled"

        # 尝试读取输出的文件路径并获取内容
        if lines:
            potential_path = lines[-1].strip()
            if potential_path.endswith('.md') and os.path.exists(potential_path):
                try:
                    with open(potential_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 从内容中提取标题
                    for line in content.split('\n')[:30]:
                        if line.startswith('title:'):
                            title = line.split(':', 1)[1].strip().strip('"\'')
                            break
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                        if line.startswith('## '):
                            title = line[3:].strip()
                            break
                except Exception as e:
                    logger.warning(f"读取文件失败: {e}")
                    content = result.stdout
            else:
                content = result.stdout

        return title, content, ""

    except subprocess.TimeoutExpired:
        error_msg = f"{script_name} 执行超时"
        logger.warning(error_msg)
        return None, None, error_msg
    except Exception as e:
        error_msg = f"{script_name} 执行出错: {e}"
        logger.warning(error_msg)
        return None, None, error_msg


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


def fetch(url: str, force: bool = False) -> Tuple[Optional[str], Optional[str], str]:
    """
    主入口：路由并执行抓取
    Returns: (title, content, error_message) or (None, None, error_message)
    """
    script, description = route(url)
    logger.info(f"路由决策: {description} -> {script}")

    return run_script(script, url, force)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='URL to Markdown Router')
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('--force', '-f', action='store_true', help='Force overwrite if file exists')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')

    args = parser.parse_args()

    url = args.url
    script, description = route(url)

    print(f"URL: {url}")
    print(f"路由: {description} ({script})")
    print("-" * 50)

    title, content, error_msg = fetch(url, force=args.force)

    if content:
        print(content)
    else:
        print("抓取失败", file=sys.stderr)
        if error_msg:
            print(f"\n错误详情:\n{error_msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
