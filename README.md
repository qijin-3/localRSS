# 多源RSS订阅生成器

统一管理和部署多个RSS订阅源的自动化工具。

## 📁 项目结构

```
localRSS/
├── sources/              # RSS源生成器目录
│   ├── yirenzhixia.py   # 一人之下漫画RSS源
│   └── ...              # 更多RSS源 (待添加)
├── output/              # 生成的RSS文件输出目录
│   ├── yirenzhixia.xml
│   └── ...
├── .github/
│   └── workflows/
│       └── update-rss.yml  # GitHub Actions自动化
├── generate_all.py      # 统一生成脚本
├── README.md
└── .gitignore
```

## 🚀 使用方法

### 本地生成所有RSS

```bash
# 进入项目目录
cd /Users/jin/SynologyDrive/Working/Dev/localRSS

# 生成所有RSS源
python3 generate_all.py
```

### 生成单个RSS源

```bash
# 单独运行某个源
python3 sources/yirenzhixia.py
```

## 📡 当前RSS源

| 名称 | 输出文件 | 源网站 | 描述 |
|------|----------|--------|------|
| 一人之下 | `yirenzhixia.xml` | baozimh.com | 包子漫画 - 一人之下漫画更新 |

## ➕ 添加新的RSS源

### 步骤：

1. **在 `sources/` 目录创建新的Python文件**

```bash
touch sources/新源名称.py
```

2. **编写RSS生成器** (参考 `yirenzhixia.py` 的模板)

必须包含的元素：
- `MANGA_URL` - 源网站URL
- `RSS_FILENAME` - 输出文件名
- `RSS_TITLE` - RSS标题
- `RSS_DESCRIPTION` - RSS描述
- `main()` 函数 - 主生成逻辑

3. **测试新源**

```bash
python3 sources/新源名称.py
```

4. **提交到Git**

```bash
git add sources/新源名称.py
git commit -m "Add: 新源名称 RSS source"
git push
```

### 示例模板

```python
#!/usr/bin/env python3
"""
新RSS源生成器
"""

import os
import sys
from pathlib import Path

# 配置
SOURCE_URL = "https://example.com/..."
RSS_FILENAME = "example.xml"
RSS_TITLE = "示例RSS"
RSS_DESCRIPTION = "示例RSS订阅"
MAX_ITEMS = 20

def fetch_content():
    """获取内容"""
    # 实现抓取逻辑
    pass

def parse_items(html):
    """解析条目"""
    # 实现解析逻辑
    pass

def generate_rss(items, output_file):
    """生成RSS XML"""
    # 实现RSS生成逻辑
    pass

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / RSS_FILENAME
    
    # 实现生成逻辑
    print(f"正在生成 {RSS_TITLE}...")
    # ...
    print(f"✓ RSS文件已生成: {output_file}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

## 🌐 在线部署 (GitHub)

### 部署步骤：

1. **创建GitHub仓库**

访问 https://github.com/new
- 仓库名称: `localRSS`
- 类型: Public

2. **初始化并推送**

```bash
cd /Users/jin/SynologyDrive/Working/Dev/localRSS
git init
git add .
git commit -m "Initial commit: Multi-source RSS generator"
git remote add origin https://github.com/你的用户名/localRSS.git
git branch -M main
git push -u origin main
```

3. **配置GitHub Actions权限**

- 进入仓库 Settings → Actions → General
- Workflow permissions 选择 "Read and write permissions"
- 保存

4. **手动触发首次运行**

- 进入 Actions 标签
- 选择 "Update All RSS Feeds"
- 点击 "Run workflow"

### RSS订阅地址格式

```
https://raw.githubusercontent.com/你的用户名/localRSS/main/output/源文件名.xml
```

例如：
```
https://raw.githubusercontent.com/你的用户名/localRSS/main/output/yirenzhixia.xml
```

## 🔧 配置选项

### 修改更新频率

编辑 `.github/workflows/update-rss.yml`:

```yaml
schedule:
  - cron: '0 */2 * * *'  # 每2小时
  - cron: '0 9,21 * * *' # 每天早晚
```

### 修改单个源的章节数量

编辑对应的源文件，修改 `MAX_CHAPTERS` 或 `MAX_ITEMS` 变量。

## 📦 依赖

```bash
pip install requests beautifulsoup4
```

## 🎯 特点

- ✅ **模块化设计** - 每个RSS源独立管理
- ✅ **统一生成** - 一键生成所有RSS源
- ✅ **自动化部署** - GitHub Actions自动更新
- ✅ **易于扩展** - 添加新源只需创建新文件
- ✅ **完全免费** - 利用GitHub免费资源

## 📝 最佳实践

1. **命名规范**
   - 源文件: 小写字母+下划线 (如 `manga_name.py`)
   - 输出文件: 与源文件同名 (如 `manga_name.xml`)

2. **代码规范**
   - 每个源文件必须可独立运行
   - 包含清晰的错误处理
   - 添加适当的日志输出

3. **测试**
   - 添加新源后本地测试
   - 确保生成的RSS文件有效
   - 在RSS阅读器中验证

## 🐛 故障排除

### 本地运行失败

1. 检查依赖是否安装: `pip list | grep -E "requests|beautifulsoup4"`
2. 检查网络连接
3. 查看错误信息

### GitHub Actions失败

1. 检查Actions日志
2. 确认权限设置正确
3. 验证源文件语法

### RSS无法订阅

1. 确认文件已生成到 `output/` 目录
2. 检查RSS文件格式是否正确
3. 使用RSS验证工具测试: https://validator.w3.org/feed/

## 📞 支持

如有问题，请：
1. 查看错误日志
2. 检查现有源文件作为参考
3. 在GitHub仓库创建Issue

---

**最后更新**: 2026-01-31
