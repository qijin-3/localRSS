#!/usr/bin/env python3
"""
一人之下漫画RSS生成器
抓取包子漫画网站的更新并生成RSS feed
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
MANGA_URL = "https://www.baozimh.com/comic/yirenzhixia-dongmantang"
RSS_FILENAME = "yirenzhixia.xml"
MAX_CHAPTERS = 20

# RSS元数据
RSS_TITLE = "一人之下 - 包子漫画"
RSS_DESCRIPTION = "一人之下漫画更新订阅"


def fetch_manga_page():
    """获取漫画页面HTML"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        response = requests.get(MANGA_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"错误: 无法获取页面 - {e}", file=sys.stderr)
        return None


def parse_chapters(html):
    """解析章节列表"""
    soup = BeautifulSoup(html, 'html.parser')
    chapters = []
    
    # 查找章节列表区域
    chapter_items = soup.find_all('div', class_='comics-chapters')
    if not chapter_items:
        # 尝试其他可能的选择器
        chapter_items = soup.find_all('a', href=re.compile(r'/comic/chapter/yirenzhixia-dongmantang/'))
    
    for item in chapter_items[:MAX_CHAPTERS]:
        try:
            if item.name == 'a':
                link = item
            else:
                link = item.find('a')
            
            if not link:
                continue
                
            chapter_url = link.get('href', '')
            if not chapter_url.startswith('http'):
                chapter_url = 'https://www.baozimh.com' + chapter_url
            
            # 提取章节标题
            chapter_title = link.get_text(strip=True)
            
            # 尝试从周围元素获取更新日期
            date_text = None
            parent = link.parent
            if parent:
                date_span = parent.find('span', class_='comic-update')
                if date_span:
                    date_text = date_span.get_text(strip=True)
            
            chapters.append({
                'title': chapter_title,
                'link': chapter_url,
                'pub_date': date_text or datetime.now().strftime('%Y-%m-%d')
            })
        except Exception as e:
            print(f"警告: 解析章节时出错 - {e}", file=sys.stderr)
            continue
    
    return chapters


def format_pub_date(date_str):
    """格式化发布日期为RFC822格式"""
    try:
        # 尝试解析中文日期格式 "2026年01月30日"
        match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', date_str)
        if match:
            year, month, day = match.groups()
            dt = datetime(int(year), int(month), int(day))
        else:
            # 尝试解析 YYYY-MM-DD 格式
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%a, %d %b %Y 00:00:00 +0000')
    except:
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')


def generate_rss(chapters, output_file):
    """生成RSS XML"""
    # 创建RSS根元素
    rss = ET.Element('rss', version='2.0', attrib={
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    channel = ET.SubElement(rss, 'channel')
    
    # 添加频道信息
    ET.SubElement(channel, 'title').text = RSS_TITLE
    ET.SubElement(channel, 'link').text = MANGA_URL
    ET.SubElement(channel, 'description').text = RSS_DESCRIPTION
    ET.SubElement(channel, 'language').text = 'zh-CN'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # 添加atom:link自引用
    atom_link = ET.SubElement(channel, 'atom:link')
    atom_link.set('href', f'file://{output_file}')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')
    
    # 添加章节条目
    for chapter in chapters:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = chapter['title']
        ET.SubElement(item, 'link').text = chapter['link']
        ET.SubElement(item, 'description').text = f"{RSS_TITLE} - {chapter['title']}"
        ET.SubElement(item, 'pubDate').text = format_pub_date(chapter['pub_date'])
        ET.SubElement(item, 'guid', isPermaLink='true').text = chapter['link']
    
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
    
    print(f"正在获取 {RSS_TITLE} 更新...")
    html = fetch_manga_page()
    if not html:
        sys.exit(1)
    
    print("正在解析章节...")
    chapters = parse_chapters(html)
    if not chapters:
        print("警告: 未找到章节信息", file=sys.stderr)
        sys.exit(1)
    
    print(f"找到 {len(chapters)} 个章节")
    
    print("正在生成RSS...")
    rss = generate_rss(chapters, output_file)
    xml_string = prettify_xml(rss)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    print(f"✓ RSS文件已生成: {output_file}")
    print(f"✓ 最新章节: {chapters[0]['title'] if chapters else 'N/A'}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
