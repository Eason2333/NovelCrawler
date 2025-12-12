# API 文档

## NovelSpider 类

### 类概述

`NovelSpider` 是小说爬虫的核心类，负责从动态网站爬取小说内容。

### 初始化

```python
NovelSpider(book_url: str)
```

**参数：**
- `book_url` (str): 小说主页URL，例如：`"https://www.57389b.sbs/#/book/1233/"`

**示例：**
```python
spider = NovelSpider("https://www.57389b.sbs/#/book/1233/")
```

---

## 公共方法

### get_novel_info()

获取小说信息和章节列表。

**签名：**
```python
def get_novel_info(self) -> bool
```

**返回值：**
- `bool`: 成功返回 `True`，失败返回 `False`

**功能：**
1. 初始化浏览器
2. 访问小说主页
3. 提取小说名称
4. 提取章节列表

**示例：**
```python
if spider.get_novel_info():
    print(f"小说名称: {spider.novel_name}")
    print(f"章节数量: {len(spider.chapters)}")
```

**异常：**
- 如果浏览器初始化失败，会打印错误信息并返回 `False`
- 如果页面加载失败，会打印错误信息并返回 `False`

---

### get_chapter_content()

获取单个章节的内容。

**签名：**
```python
def get_chapter_content(self, chapter_url: str) -> Optional[str]
```

**参数：**
- `chapter_url` (str): 章节URL

**返回值：**
- `Optional[str]`: 章节内容文本，失败返回 `None`

**示例：**
```python
content = spider.get_chapter_content("https://www.57389b.sbs/#/book/1233/chapter/1")
if content:
    print(content)
```

---

### save_novel()

保存小说到TXT文件。

**签名：**
```python
def save_novel(self, output_dir: str = 'novels') -> bool
```

**参数：**
- `output_dir` (str, 可选): 输出目录，默认为 `'novels'`

**返回值：**
- `bool`: 成功返回 `True`，失败返回 `False`

**功能：**
1. 创建输出目录（如果不存在）
2. 逐章下载内容
3. 保存为TXT文件
4. 自动清理浏览器资源

**示例：**
```python
# 使用默认目录
spider.save_novel()

# 自定义输出目录
spider.save_novel(output_dir='my_novels')
```

**文件格式：**
```
小说名称

==================================================

第一章 标题

章节内容...

第二章 标题

章节内容...
```

---

## 公共属性

### novel_name

**类型：** `str`

**说明：** 小说名称，在调用 `get_novel_info()` 后可用。

**示例：**
```python
spider.get_novel_info()
print(spider.novel_name)  # 输出：武侠世界的慕容复
```

---

### chapters

**类型：** `List[Dict[str, str]]`

**说明：** 章节列表，每个元素包含 `title` 和 `url`。

**结构：**
```python
[
    {'title': '第一章 标题', 'url': 'https://...'},
    {'title': '第二章 标题', 'url': 'https://...'},
    ...
]
```

**示例：**
```python
spider.get_novel_info()
for chapter in spider.chapters:
    print(f"{chapter['title']}: {chapter['url']}")
```

---

## 私有方法（内部使用）

### _extract_novel_name()

提取小说名称。

**签名：**
```python
def _extract_novel_name(self, soup: BeautifulSoup) -> None
```

---

### _wait_for_chapters()

等待章节列表加载。

**签名：**
```python
def _wait_for_chapters(self) -> None
```

---

### _extract_chapters()

提取章节列表。

**签名：**
```python
def _extract_chapters(self, soup: BeautifulSoup) -> bool
```

**返回值：**
- `bool`: 成功提取返回 `True`

---

### _search_chapters_generic()

通用方法搜索章节链接。

**签名：**
```python
def _search_chapters_generic(self, soup: BeautifulSoup) -> List
```

**返回值：**
- `List`: 章节链接列表

---

### _cleanup()

清理浏览器资源。

**签名：**
```python
def _cleanup(self) -> None
```

---

## 使用示例

### 基本使用

```python
from main import NovelSpider

# 创建爬虫实例
spider = NovelSpider("https://www.57389b.sbs/#/book/1233/")

# 获取小说信息
if spider.get_novel_info():
    # 保存小说
    spider.save_novel()
else:
    print("获取小说信息失败")
```

### 自定义输出目录

```python
spider = NovelSpider(book_url)
if spider.get_novel_info():
    spider.save_novel(output_dir='my_novels')
```

### 访问章节信息

```python
spider = NovelSpider(book_url)
if spider.get_novel_info():
    print(f"小说: {spider.novel_name}")
    print(f"共 {len(spider.chapters)} 章")
    
    # 获取第一章内容
    if spider.chapters:
        first_chapter = spider.chapters[0]
        content = spider.get_chapter_content(first_chapter['url'])
        print(content)
```

### 批量处理多个小说

```python
book_urls = [
    "https://www.57389b.sbs/#/book/1233/",
    "https://www.57389b.sbs/#/book/1234/",
]

for url in book_urls:
    spider = NovelSpider(url)
    if spider.get_novel_info():
        spider.save_novel()
```

---

## 错误处理

### 浏览器初始化失败

**错误信息：**
```
❌ 初始化浏览器失败: ...
请先安装依赖：
  pip install playwright
  playwright install chromium
```

**解决方法：**
```bash
pip install playwright
playwright install chromium
```

### 获取小说信息失败

**可能原因：**
1. URL不正确
2. 网络连接问题
3. 网站结构变化
4. 需要登录

**检查方法：**
```python
spider = NovelSpider(book_url)
if not spider.get_novel_info():
    print("获取失败，请检查URL和网络连接")
```

### 章节内容获取失败

**处理方式：**
- 程序会在文件中标记 `[内容获取失败]`
- 继续下载其他章节
- 不会中断整个下载过程

---

## 注意事项

1. **资源清理**
   - `save_novel()` 方法会自动清理浏览器资源
   - 如果手动调用 `get_chapter_content()`，记得调用 `_cleanup()`

2. **请求频率**
   - 程序内置了延迟机制（每章0.5秒）
   - 不要修改为过快的频率

3. **线程安全**
   - 当前实现不是线程安全的
   - 如需多线程，需要添加锁机制

---

**最后更新：** 2024年

