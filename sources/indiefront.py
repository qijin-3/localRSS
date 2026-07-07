#!/usr/bin/env python3
"""
独立开发前线 RSS生成器
抓取 indiefront.cn 的文章列表并生成RSS feed
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import sys
import os

# 配置
SOURCE_URL = "https://indiefront.cn/articles/"
RSS_FILENAME = "indiefront.xml"
MAX_ARTICLES = 30

# RSS元数据
RSS_TITLE = "独立开发前线"
RSS_DESCRIPTION = "发现优秀的独立产品与开发者 - indiefront.cn 文章订阅"
RSS_URL = "https://raw.githubusercontent.com/qijin-3/localRSS/main/output/indiefront.xml"


def fetch_page(url):
    """获取页面HTML"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"错误: 无法获取页面 {url} - {e}", file=sys.stderr)
        return None


def parse_articles(html):
    """解析文章列表页"""
    soup = BeautifulSoup(html, 'html.parser')
    articles = []

    # 每篇文章卡片是一个 <a class="group block" href="/articles/{id}/">
    cards = soup.find_all('a', class_='group', href=re.compile(r'^/articles/.+'))

    seen = set()
    for card in cards[:MAX_ARTICLES * 2]:  # 多取一些以应对去重
        try:
            link = card.get('href', '')
            if not link.startswith('/articles/'):
                continue

            # 规范化链接
            article_url = 'https://indiefront.cn' + link
            # 去重(同一文章可能多次出现)
            if article_url in seen:
                continue
            seen.add(article_url)

            # 提取标题:优先用图片的 alt 属性(更稳定)
            title = None
            img = card.find('img')
            if img and img.get('alt'):
                title = img['alt'].strip()

            # 退化方案:卡片内的标题文本
            if not title:
                # 标题通常在卡片的标题元素中
                for el in card.find_all(['h2', 'h3', 'p', 'span']):
                    text = el.get_text(strip=True)
                    # 跳过日期和"X 分钟"这类短文本
                    if text and len(text) > 8 and not re.match(r'^\d', text):
                        title = text
                        break

            if not title:
                continue

            # 提取日期:卡片中形如 "2026-07-04" 的文本
            pub_date = None
            for span in card.find_all('span'):
                text = span.get_text(strip=True)
                m = re.match(r'(20\d{2}-\d{2}-\d{2})', text)
                if m:
                    pub_date = m.group(1)
                    break

            articles.append({
                'title': title,
                'link': article_url,
                'pub_date': pub_date or datetime.now().strftime('%Y-%m-%d')
            })

            if len(articles) >= MAX_ARTICLES:
                break

        except Exception as e:
            print(f"警告: 解析文章卡片时出错 - {e}", file=sys.stderr)
            continue

    return articles


def fetch_description(article_url):
    """获取文章详情页的摘要(prose 容器的首段)"""
    html = fetch_page(article_url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    prose = soup.find('div', class_='prose')
    if not prose:
        # 退化方案:取 og:description / meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
        return None

    # 取正文第一段有意义的文本作为摘要
    for p in prose.find_all(['p', 'h2', 'h3']):
        text = p.get_text(strip=True)
        if text and len(text) > 10:
            # 截断过长的摘要
            if len(text) > 200:
                text = text[:200] + '...'
            return text
    return None


def format_pub_date(date_str):
    """格式化发布日期为RFC822格式"""
    try:
        # 解析 YYYY-MM-DD 格式
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%a, %d %b %Y 00:00:00 +0000')
    except Exception:
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')


def generate_rss(articles):
    """生成RSS XML"""
    rss = ET.Element('rss', version='2.0', attrib={
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    channel = ET.SubElement(rss, 'channel')

    # 频道信息
    ET.SubElement(channel, 'title').text = RSS_TITLE
    ET.SubElement(channel, 'link').text = SOURCE_URL
    ET.SubElement(channel, 'description').text = RSS_DESCRIPTION
    ET.SubElement(channel, 'language').text = 'zh-CN'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

    # atom:link 自引用
    atom_link = ET.SubElement(channel, 'atom:link')
    atom_link.set('href', RSS_URL)
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    # 文章条目
    for article in articles:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = article['title']
        ET.SubElement(item, 'link').text = article['link']
        ET.SubElement(item, 'description').text = article.get('description') or article['title']
        ET.SubElement(item, 'pubDate').text = format_pub_date(article['pub_date'])
        ET.SubElement(item, 'guid', isPermaLink='true').text = article['link']

    return rss


def prettify_xml(elem):
    """美化XML输出"""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')


def main():
    # 确定输出目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, 'output')
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, RSS_FILENAME)

    print(f"正在获取 {RSS_TITLE} 文章列表...")
    html = fetch_page(SOURCE_URL)
    if not html:
        sys.exit(1)

    print("正在解析文章...")
    articles = parse_articles(html)
    if not articles:
        print("警告: 未找到文章信息", file=sys.stderr)
        sys.exit(1)

    print(f"找到 {len(articles)} 篇文章")

    # 抓取每篇文章的摘要(限制并发影响,逐个抓取)
    print("正在获取文章摘要...")
    for i, article in enumerate(articles):
        desc = fetch_description(article['link'])
        if desc:
            article['description'] = desc
        else:
            article['description'] = article['title']
        if (i + 1) % 5 == 0:
            print(f"  已处理 {i + 1}/{len(articles)}")

    print("正在生成RSS...")
    rss = generate_rss(articles)
    xml_string = prettify_xml(rss)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)

    print(f"✓ RSS文件已生成: {output_file}")
    print(f"✓ 最新文章: {articles[0]['title'] if articles else 'N/A'}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
