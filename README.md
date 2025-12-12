# 📚 小说爬虫程序

一个使用 Playwright 从多个小说网站爬取小说内容并保存为 TXT 文件的 Python 爬虫程序。

**支持的网站：**
- 笔趣阁系列网站（如：`https://www.57389b.sbs/#/book/1233/`）
- 其他小说网站（如：`http://www.xbiqushu.com/8_8426/`）
- 更多网站（通过智能选择器自动适配）

## ✨ 功能特点

- 🎯 **自动获取**：自动识别小说名称和章节列表
- 📖 **批量下载**：逐章下载所有章节内容
- 💾 **保存为TXT**：自动保存为文本文件，文件名使用小说名称
- 🚀 **支持动态网站**：使用 Playwright 处理 JavaScript 渲染的单页应用（SPA）
- 🔧 **智能解析**：多种选择器策略，自动适配不同网站结构
- 🌐 **多网站支持**：通过智能选择器和通用搜索，支持多个小说网站

## 📋 系统要求

- Python 3.7+
- 网络连接

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Python 包
pip install -r requirements.txt

# 安装 Playwright 浏览器（只需运行一次）
playwright install chromium
```

### 2. 运行程序

```bash
python main.py
```

### 3. 修改小说URL

编辑 `main.py` 文件，修改 `book_url` 变量：

```python
# 支持多种网站格式
book_url = "http://www.xbiqushu.com/8_8426/"  # 示例1
# book_url = "https://www.57389b.sbs/#/book/1233/"  # 示例2
```

**注意：** 请确保URL是小说目录页（包含章节列表的页面），而不是单个章节页面。

## 📁 项目结构

```
PythonProject/
├── main.py              # 主程序文件
├── requirements.txt     # Python依赖包
├── README.md           # 项目说明文档
├── docs/               # 技术文档目录
│   ├── 技术文档.md     # 详细技术说明
│   └── API文档.md      # API接口文档
└── novels/             # 输出目录（自动创建）
    └── 小说名称.txt    # 下载的小说文件
```

## 📖 使用说明

### 基本使用

1. **配置小说URL**
   
   在 `main.py` 的 `main()` 函数中修改 `book_url`：
   ```python
   book_url = "https://www.57389b.sbs/#/book/1233/"
   ```

2. **运行程序**
   ```bash
   python main.py
   ```

3. **查看结果**
   
   下载的小说会保存在 `novels/` 目录下，文件名为小说名称。

### 自定义输出目录

在代码中修改 `save_novel()` 方法的 `output_dir` 参数：

```python
spider.save_novel(output_dir='my_novels')  # 自定义输出目录
```

## 🔧 技术架构

### 核心技术

- **Playwright**: 浏览器自动化，处理 JavaScript 渲染
- **BeautifulSoup4**: HTML 解析和内容提取
- **Python 3.7+**: 编程语言

### 工作流程

1. **初始化浏览器** → 启动 Playwright 无头浏览器
2. **访问小说主页** → 加载页面并等待 JavaScript 执行
3. **提取小说信息** → 解析 HTML 获取小说名称和章节列表
4. **下载章节内容** → 逐章访问并提取内容
5. **保存为TXT** → 将所有章节保存到文本文件

## 📝 代码示例

### 基本使用

```python
from main import NovelSpider

# 创建爬虫实例
spider = NovelSpider("https://www.57389b.sbs/#/book/1233/")

# 获取小说信息
if spider.get_novel_info():
    # 保存小说
    spider.save_novel()
```

### 自定义配置

```python
spider = NovelSpider(book_url)

# 获取信息
if spider.get_novel_info():
    # 自定义输出目录
    spider.save_novel(output_dir='my_novels')
    
    # 访问章节列表
    print(f"小说名称: {spider.novel_name}")
    print(f"章节数量: {len(spider.chapters)}")
```

## ⚠️ 注意事项

1. **遵守法律法规**
   - 请遵守网站的 robots.txt 和使用条款
   - 仅用于个人学习和研究目的
   - 不要用于商业用途

2. **请求频率**
   - 程序已内置延迟机制（每章 0.5 秒）
   - 请勿修改为过快的请求频率
   - 避免对服务器造成压力

3. **网站结构变化**
   - 如果网站结构发生变化，可能需要调整选择器
   - 查看 `docs/技术文档.md` 了解如何修改

4. **网络问题**
   - 确保网络连接稳定
   - 如果下载中断，可以重新运行程序（会覆盖已下载的文件）

## 🐛 常见问题

### Q: 提示"初始化浏览器失败"

**A:** 请确保已安装 Playwright 浏览器：
```bash
playwright install chromium
```

### Q: 找不到章节列表

**A:** 可能的原因：
1. URL 不正确
2. 网站结构发生变化
3. 需要登录或验证
4. 网络连接问题

### Q: 下载的内容不完整

**A:** 检查：
1. 网络连接是否稳定
2. 网站是否正常访问
3. 查看错误信息，可能需要调整选择器

### Q: 如何爬取其他网站的小说？

**A:** 代码已经内置了多种选择器策略，可以自动适配大部分小说网站：
1. **直接尝试**：直接修改URL运行，代码会自动尝试多种选择器
2. **如果失败**：查看输出信息，了解使用了哪个选择器
3. **手动调整**：如果自动适配失败，可以修改 `main.py` 中的选择器列表
   - 章节选择器：`_extract_chapters` 方法中的 `chapter_selectors`
   - 内容选择器：`get_chapter_content` 方法中的 `content_selectors`

## 📚 相关文档

- [技术文档](docs/技术文档.md) - 详细的技术说明和实现原理
- [API文档](docs/API文档.md) - 类和方法的使用说明

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目仅供学习和研究使用。

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 强大的浏览器自动化工具
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析库

---

**注意**：请合理使用爬虫，遵守相关法律法规和网站使用条款。
