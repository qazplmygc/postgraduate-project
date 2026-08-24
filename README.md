# EdgeNexus · 边云合智

云边协同研究知识站：文献检索、专利对照、论文复现、会议视频、WAIC 笔记、项目管理、开学汇报。

---

## 两种打开方式

| 方式 | 适合 | 地址 |
|------|------|------|
| **在线版（免费）** | 手机 / 平板 / 任意浏览器 · 浏览笔记与结构 | 部署后见下方 |
| **本地版** | 打开 `D:\刚需` 里的 PDF、完整功能 | 双击 `search\open.bat` → http://127.0.0.1:8765 |

在线版可浏览全部 HTML/JSON 内容；**本地 PDF 库**仍需在本机用 `open.bat` 打开（隐私与体积原因不上传 GitHub）。

---

## 免费部署到公网（推荐 GitHub Pages）

### 1. 创建 GitHub 仓库

1. 打开 [github.com/new](https://github.com/new)
2. 仓库名例如：`edgenexus`（小写）
3. 选 **Public**（GitHub Pages 免费需公开仓库）
4. 不要勾选 README（本地已有）

### 2. 上传本项目

在项目文件夹打开终端（PowerShell）：

```powershell
cd "D:\刚需\1. literature pdf"
git init -b main
git add -A
git commit -m "EdgeNexus: static site for cloud-edge research"
git remote add origin https://github.com/你的用户名/edgenexus.git
git push -u origin main
```

### 3. 开启 GitHub Pages

1. 仓库 → **Settings** → **Pages**
2. **Build and deployment** → Source 选 **GitHub Actions**
3. 推送 `main` 后 Actions 会自动部署（约 1–2 分钟）
4. 访问：`https://你的用户名.github.io/edgenexus/`

首次部署后把仓库地址里的 Pages URL 记在手机备忘录，** anywhere 可开**。

### 4. 更新网站

改完文件后：

```powershell
git add -A
git commit -m "update content"
git push
```

等 Actions 跑完即可刷新线上。

---

## 其他免费托管（可选）

| 平台 | 特点 | 做法 |
|------|------|------|
| [Cloudflare Pages](https://pages.cloudflare.com/) | 全球 CDN，绑定 GitHub 自动部署 | Connect Git → 选仓库 → Build 留空，输出目录 `/` |
| [Gitee Pages](https://gitee.com/help/articles/4136) | 国内访问较快 | Gitee 建库 → 服务 → Gitee Pages |
| [Netlify Drop](https://app.netlify.com/drop) | 拖文件夹即上线 | 把整个项目文件夹拖进 Drop（无需 git） |

---

## 本地运行（PDF + API）

```powershell
cd search
pip install -r requirements.txt   # 若尚未安装依赖
python server.py
# 或双击 search\open.bat
```

- 文献检索：http://127.0.0.1:8765/search/
- 开学汇报：http://127.0.0.1:8765/briefing/
- 项目管理：http://127.0.0.1:8765/projects/

---

## 目录

```
├── search/       文献检索 + 本地 PDF 服务
├── patents/      专利对照
├── reproduce/    论文复现案例
├── videos/       会议视频与白皮书
├── waic/         WAIC 2026 学习笔记
├── projects/     在研项目管理
├── briefing/     开学见导师汇报（幻灯片页）
└── index.html    入口跳转
```

---

## 说明

- 在线版顶部会显示黄色提示条：**在线预览模式**
- 复现案例的论文 PDF 链到 `D:\刚需\…`；在线环境会提示用 DOI 或本地打开
- 单文件超过 100MB 勿提交 GitHub；大 PDF 可放本地或 Git LFS
