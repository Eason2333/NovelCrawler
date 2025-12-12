#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小说爬虫程序
使用 Playwright 处理需要 JavaScript 渲染的动态网页，从笔趣阁网站爬取小说内容并保存为 TXT 文件。

功能特点：
- 自动获取小说名称和章节列表
- 逐章下载小说内容
- 保存为 TXT 文件，文件名使用小说名称
- 支持单页应用（SPA）和动态内容加载

作者：Auto
创建时间：2024
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import os
from typing import List, Dict, Optional


class NovelSpider:
    """小说爬虫类，使用 Playwright 处理动态网页"""
    
    def __init__(self, book_url: str):
        """
        初始化爬虫
        
        :param book_url: 小说主页URL，例如: https://www.57389b.sbs/#/book/1233/
        """
        self.book_url = book_url
        self.novel_name = ""
        self.chapters: List[Dict[str, str]] = []
        self.playwright = None
        self.browser = None
        self.page = None
        
    def init_browser(self) -> bool:
        """
        初始化浏览器
        
        :return: 初始化是否成功
        """
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            return True
        except Exception as e:
            print(f"❌ 初始化浏览器失败: {e}")
            print("\n请先安装依赖：")
            print("  pip install playwright")
            print("  playwright install chromium")
            return False
    
    def get_novel_info(self) -> bool:
        """
        获取小说信息和章节列表
        
        :return: 是否成功获取
        """
        if not self.init_browser():
            return False
        
        print("📖 正在获取小说信息...")
        try:
            # 访问小说主页
            self.page.goto(self.book_url, wait_until='networkidle', timeout=30000)
            time.sleep(3)  # 等待页面完全加载
            
            # 获取页面源码
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # 获取小说名称
            self._extract_novel_name(soup)
            print(f"📚 小说名称: {self.novel_name}")
            
            # 等待章节列表加载
            self._wait_for_chapters()
            
            # 重新获取页面内容（可能在等待后更新了）
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # 提取章节列表
            if self._extract_chapters(soup):
                print(f"✅ 找到 {len(self.chapters)} 个章节")
                return True
            else:
                print("❌ 未找到章节列表")
                print(f"   页面标题: {self.page.title()}")
                return False
                
        except Exception as e:
            print(f"❌ 获取小说信息时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_novel_name(self, soup: BeautifulSoup) -> None:
        """从页面中提取小说名称"""
        # 扩展的选择器列表，支持更多网站结构
        title_selectors = [
            'h1',
            '.book-title',
            '#book-title',
            'title',
            '.bookname h1',
            '.bookname',
            '.book_info h1',
            '.book_info h2',
            '.book_con h1',
            '[class*="book-title"]',
            '[class*="book-name"]',
            '[class*="bookname"]',
            '[id*="bookname"]',
            '[id*="book-title"]',
        ]
        
        # 排除的文本（网站名称等）
        exclude_texts = ['笔趣阁', '小说', '小说网', '首页', '目录', '章节列表']
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text().strip()
                # 过滤掉网站名称和无关文本
                if title_text and title_text not in exclude_texts and len(title_text) > 1:
                    # 如果包含网站名称，尝试提取书名部分
                    for exclude in exclude_texts:
                        if exclude in title_text:
                            parts = title_text.split(exclude)
                            title_text = parts[0].strip() if parts[0].strip() else (parts[1].strip() if len(parts) > 1 else title_text)
                            break
                    
                    if title_text and title_text not in exclude_texts:
                        self.novel_name = title_text
                        self.novel_name = re.sub(r'[<>:"/\\|?*]', '', self.novel_name)
                        break
        
        # 如果还没找到，从title标签提取
        if not self.novel_name or self.novel_name in exclude_texts:
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text().strip()
                # 尝试提取书名（通常在title的前面部分）
                # 移除常见的分隔符和网站名称
                title_text = re.sub(r'[-_|].*$', '', title_text)  # 移除分隔符后的内容
                title_text = re.sub(r'^.*?[-_|]', '', title_text)  # 移除分隔符前的内容（如果前面是网站名）
                
                parts = title_text.replace('_', ' ').replace('-', ' ').replace('|', ' ').split()
                for part in parts:
                    if part and part not in exclude_texts and len(part) > 1:
                        self.novel_name = part
                        break
                self.novel_name = re.sub(r'[<>:"/\\|?*]', '', str(self.novel_name))
        
        # 如果还是没找到，使用默认名称（从URL提取）
        if not self.novel_name or self.novel_name in exclude_texts:
            # 尝试多种URL格式
            book_id_match = re.search(r'/book/(\d+)/?', self.book_url) or \
                           re.search(r'/(\d+_\d+)/?', self.book_url) or \
                           re.search(r'/(\d+)/?$', self.book_url.split('/')[-2] if '/' in self.book_url else '')
            if book_id_match:
                book_id = book_id_match.group(1) if hasattr(book_id_match, 'group') else str(book_id_match)
                self.novel_name = f"小说_{book_id}"
    
    def _wait_for_chapters(self) -> None:
        """等待章节列表加载"""
        # 扩展的选择器，支持更多网站结构
        selectors = [
            'a[href*="chapter"]',
            'a[href*="/chapter/"]',
            '.chapter-list a',
            '#chapter-list a',
            'dd a',
            'dt a',
            '.list-group-item a',
            'ul.list a',
            'div.list a',
            '.chapter a',
            '#list a',
            '.book_list a',
            'table a',
        ]
        
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, timeout=3000)
                break  # 找到就退出
            except:
                continue  # 继续尝试下一个
    
    def _extract_chapters(self, soup: BeautifulSoup) -> bool:
        """从页面中提取章节列表"""
        # 扩展的选择器列表，支持更多网站结构
        chapter_selectors = [
            'a[href*="chapter"]',
            'a[href*="/chapter/"]',
            '.chapter-list a',
            '#chapter-list a',
            'dd a',                    # 常见的小说网站结构
            'dt a',                    # 有些网站用dt标签
            '.list-group-item a',
            'ul.list a',
            'div.list a',
            '.chapter a',
            '#list a',                 # 章节列表容器
            '.book_list a',            # 书籍列表
            '.chapter_list a',         # 章节列表
            'table a',                 # 表格中的链接
            'tbody a',                 # 表格体中的链接
            '.listmain dd a',          # 常见结构
            '.listmain dt a',
            '#list dd a',
            '#list dt a',
        ]
        
        chapter_links = []
        for selector in chapter_selectors:
            links = soup.select(selector)
            if links and len(links) > 3:  # 至少3个链接才认为是章节列表
                chapter_links = links
                print(f"   使用选择器 '{selector}' 找到 {len(links)} 个章节")
                break
        
        # 如果特定选择器没找到，使用通用搜索
        if not chapter_links:
            chapter_links = self._search_chapters_generic(soup)
        
        # 去重并提取章节信息
        seen_urls = set()
        base_url = self.page.url.split('#')[0]
        
        for item in chapter_links:
            if isinstance(item, dict):
                url = item.get('url', '')
                title = item.get('title', '')
            else:
                url = item.get('href', '')
                title = item.get_text().strip()
                if not url.startswith('http'):
                    if url.startswith('/'):
                        url = base_url.rstrip('/') + url
                    else:
                        url = base_url.rstrip('/') + '/' + url
            
            if url and title and url not in seen_urls:
                seen_urls.add(url)
                self.chapters.append({
                    'title': title,
                    'url': url
                })
        
        return len(self.chapters) > 0
    
    def _search_chapters_generic(self, soup: BeautifulSoup) -> List:
        """通用方法搜索章节链接"""
        all_links = soup.find_all('a', href=True)
        base_url = self.page.url.split('#')[0]
        # 处理基础URL，确保有协议
        if not base_url.startswith('http'):
            base_url = self.book_url.split('#')[0]
        
        chapter_links = []
        exclude_texts = ['首页', '上一章', '下一章', '目录', '返回', '上一页', '下一页', '加入书架', '推荐', '收藏']
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # 跳过空链接和排除的文本
            if not text or text in exclude_texts:
                continue
            
            # 检查是否是章节链接的多种模式
            is_chapter = False
            
            # 1. URL模式检查
            if (
                'chapter' in href.lower() or
                '/book/' in href or
                re.search(r'/\d+\.html', href) or
                re.search(r'/\d+_\d+\.html', href) or  # 如: 8_8426/12345.html
                re.search(r'/\d+/\d+\.html', href) or  # 如: 8/8426/12345.html
                re.search(r'/\d+/\d+\.htm', href) or
                re.search(r'chapter/\d+', href, re.I) or
                re.search(r'/\d+\.htm', href)
            ):
                is_chapter = True
            
            # 2. 文本模式检查
            if (
                re.search(r'第.*章', text) or
                re.search(r'第.*节', text) or
                re.search(r'^\d+[、.]', text) or
                re.search(r'^\d+\s+', text) or
                re.search(r'第\d+章', text) or
                re.search(r'第\d+节', text)
            ):
                is_chapter = True
            
            # 3. 长度和格式检查（排除导航链接）
            if not is_chapter and len(text) < 50 and len(text) > 2:
                # 如果链接在特定的容器中（如章节列表区域）
                parent = link.parent
                if parent:
                    parent_class = parent.get('class', [])
                    parent_id = parent.get('id', '')
                    if any(keyword in str(parent_class).lower() or keyword in parent_id.lower() 
                           for keyword in ['list', 'chapter', 'book', 'content']):
                        is_chapter = True
            
            if is_chapter:
                # 构建完整URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = base_url.rstrip('/') + href
                    elif href.startswith('./') or href.startswith('../'):
                        # 处理相对路径
                        href = urljoin(base_url, href)
                    else:
                        # 相对路径，需要拼接
                        if base_url.endswith('/'):
                            href = base_url + href
                        else:
                            href = base_url + '/' + href
                
                chapter_links.append({
                    'title': text,
                    'url': href,
                    'element': link
                })
        
        if chapter_links:
            print(f"   通过通用搜索找到 {len(chapter_links)} 个可能的章节链接")
        
        return chapter_links
    
    def get_chapter_content(self, chapter_url: str) -> Optional[str]:
        """
        获取章节内容
        
        :param chapter_url: 章节URL
        :return: 章节内容文本，失败返回None
        """
        try:
            self.page.goto(chapter_url, wait_until='networkidle', timeout=20000)
            time.sleep(1)  # 等待内容加载
            
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # 扩展的内容选择器，支持更多网站结构
            content_selectors = [
                '#content',
                '.content',
                '#chaptercontent',
                '.chapter-content',
                '#novelcontent',
                '.text-content',
                '#text',
                '#chaptercontent',
                '.chaptercontent',
                '.bookcontent',
                '#bookcontent',
                '.novelcontent',
                '#novelcontent',
                '[id*="content"]',
                '[class*="content"]',
                '[id*="text"]',
                '[class*="text"]',
                '[id*="chapter"]',
                '[class*="chapter"]',
                '.readcontent',
                '#readcontent',
            ]
            
            content = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    text = content_elem.get_text().strip()
                    if len(text) > 200:  # 内容应该足够长
                        content = text
                        break
            
            # 如果特定选择器没找到，使用通用搜索
            if not content:
                # 尝试查找包含大量文本的元素
                # 优先查找div，然后是其他块级元素
                elements = soup.find_all(['div', 'article', 'section'], 
                                        class_=re.compile(r'content|text|chapter|novel|read|book', re.I))
                
                # 如果没找到，查找所有div
                if not elements:
                    elements = soup.find_all('div')
                
                for elem in elements:
                    text = elem.get_text().strip()
                    # 内容应该足够长，且不包含太多链接（排除导航区域）
                    links_count = len(elem.find_all('a'))
                    if len(text) > 500 and links_count < 10:  # 内容长且链接少
                        content = text
                        break
            
            if content:
                # 清理内容
                content = re.sub(r'\s+', '\n', content)
                content = re.sub(r'\n{3,}', '\n\n', content)  # 多个换行替换为两个
                content = content.strip()
            
            return content
        except Exception as e:
            print(f"   获取章节内容失败: {e}")
            return None
    
    def save_novel(self, output_dir: str = 'novels') -> bool:
        """
        保存小说到txt文件
        
        :param output_dir: 输出目录，默认为 'novels'
        :return: 是否保存成功
        """
        if not self.novel_name or not self.chapters:
            print("❌ 小说信息不完整，无法保存")
            return False
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filename = os.path.join(output_dir, f"{self.novel_name}.txt")
        
        print(f"\n📥 开始下载章节内容...")
        print(f"   保存路径: {filename}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入小说标题
                f.write(f"{self.novel_name}\n\n")
                f.write("=" * 50 + "\n\n")
                
                # 遍历所有章节
                total = len(self.chapters)
                for idx, chapter in enumerate(self.chapters, 1):
                    print(f"   [{idx}/{total}] {chapter['title']}")
                    
                    # 写入章节标题
                    f.write(f"\n\n{chapter['title']}\n\n")
                    
                    # 获取章节内容
                    content = self.get_chapter_content(chapter['url'])
                    if content:
                        f.write(content)
                        f.write("\n")
                    else:
                        f.write("[内容获取失败]\n")
                    
                    # 延迟，避免请求过快
                    time.sleep(0.5)
            
            print(f"\n✅ 下载完成！文件已保存到: {filename}")
            return True
        except Exception as e:
            print(f"❌ 保存文件时出错: {e}")
            return False
        finally:
            # 清理资源
            self._cleanup()
    
    def _cleanup(self) -> None:
        """清理浏览器资源"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass


def main():
    """主函数"""
    # 配置小说URL（可以修改为其他小说）
    # 支持多种网站格式：
    # - https://www.57389b.sbs/#/book/1233/
    # - http://www.xbiqushu.com/8_8426/
    book_url = "http://www.xbiqushu.com/8_8426/"  # 可以修改为其他小说URL
    
    print("=" * 60)
    print("📚 小说爬虫程序")
    print("=" * 60)
    print(f"目标URL: {book_url}")
    print()
    
    # 创建爬虫实例
    spider = NovelSpider(book_url)
    
    # 获取小说信息并保存
    if spider.get_novel_info():
        spider.save_novel()
    else:
        print("\n❌ 获取小说信息失败")
        print("\n可能的原因：")
        print("  1. 网络连接问题")
        print("  2. URL不正确")
        print("  3. 网站结构发生变化")
        print("  4. 需要登录或验证")
        print("\n提示：")
        print("  - 确保URL是小说目录页（包含章节列表的页面）")
        print("  - 可以尝试在浏览器中打开URL，确认页面正常显示")


if __name__ == '__main__':
    main()
