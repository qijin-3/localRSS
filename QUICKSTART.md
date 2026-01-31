# 🚀 快速开始

## 本地使用

### 生成所有RSS

```bash
cd /Users/jin/SynologyDrive/Working/Dev/localRSS
python3 generate_all.py
```

生成的RSS文件在 `output/` 目录下。

### 添加新的RSS源

1. 复制模板：
```bash
cp sources/yirenzhixia.py sources/新源名称.py
```

2. 编辑新文件，修改配置项：
   - `MANGA_URL`
   - `RSS_FILENAME`
   - `RSS_TITLE`
   - `RSS_DESCRIPTION`
   - 解析逻辑

3. 测试：
```bash
python3 sources/新源名称.py
```

4. 提交：
```bash
git add sources/新源名称.py
git commit -m "Add: 新源名称"
```

## 在线部署到GitHub

### 1. 创建GitHub仓库

访问：https://github.com/new
- 名称：`localRSS`
- 类型：Public
- 不要勾选任何初始化选项

### 2. 推送代码

```bash
cd /Users/jin/SynologyDrive/Working/Dev/localRSS

# 添加远程仓库
git remote add origin https://github.com/你的用户名/localRSS.git

# 推送
git push -u origin main
```

### 3. 配置GitHub Actions

1. 进入仓库页面
2. Settings → Actions → General
3. Workflow permissions → 选择 "Read and write permissions"
4. Save

### 4. 手动运行一次

1. Actions 标签
2. "Update All RSS Feeds" workflow
3. Run workflow

## RSS订阅地址

部署完成后，你的RSS订阅地址格式为：

```
https://raw.githubusercontent.com/你的用户名/localRSS/main/output/源文件名.xml
```

### 当前可用的源：

- **一人之下**: `https://raw.githubusercontent.com/你的用户名/localRSS/main/output/yirenzhixia.xml`

## 推荐RSS阅读器

- 🌐 **Feedly** - https://feedly.com (网页/手机)
- 📱 **NetNewsWire** - iOS/macOS (免费)
- 📱 **Reeder** - iOS/macOS (付费)
- 💻 **Fluent Reader** - 跨平台 (免费)

## 维护

### 更新所有源
GitHub Actions 会每小时自动更新，或者手动触发 workflow。

### 添加新源
1. 在 `sources/` 创建新文件
2. 推送到GitHub
3. 自动生效

### 修改更新频率
编辑 `.github/workflows/update-rss.yml` 中的 cron 表达式。

---

**项目结构说明**：
- `sources/` - 每个RSS源一个文件
- `output/` - 生成的RSS文件
- `generate_all.py` - 统一生成器

详细文档见 `README.md`。
