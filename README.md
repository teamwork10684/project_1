# PopQuiz 智能弹出测验系统

## 项目简介

PopQuiz 是一个基于 AI 的智能弹出测验系统，支持实时题目生成、答题互动、数据统计和多端支持，适用于演讲互动和学习场景。项目采用前后端分离架构，前端基于 Vue3，后端基于 Flask，支持本地和远程 AI 题目生成。

---

## 1. 获取项目源码

### 方式一：下载压缩包

1. 访问项目 GitHub 主页，点击右上角“代码”按钮，选择“下载 ZIP”
2. 解压后，使用终端 `cd` 到项目目录

### 方式二：使用 Git 克隆

1. 安装 [Git](https://git-scm.com/downloads)
2. 打开终端，输入：

```bash
git clone https://github.com/teamwork10684/project_1.git
```

3. 进入项目目录：

```bash
cd popquiz
```

---

## 2. 数据库安装与创建

### 2.1 安装 MySQL

- Windows 用户可参考：[MySQL 官方安装教程](https://dev.mysql.com/doc/refman/8.0/en/windows-installation.html)

### 2.2 创建数据库

推荐：双击 `api_doc/create_tables.bat`根据提示创建数据库并导入表结构，以下为手动创建导入方式：
在本项目文件夹中打开终端

1. 登录 MySQL：

```bash
mysql -u root -p
```

    执行后在提示下输入密码

2. 创建数据库（如 popquiz）：

```sql
CREATE DATABASE popquiz DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 导入表结构：

```sql
use popquiz;
source api_doc/create_tables.sql;
```

---

## 3. 安装依赖与启动

### 3.1 后端

**请确保已安装 Python 3.11。**

- [Python 3.11 下载地址](https://www.python.org/downloads/release/python-3110/)
- 安装时请勾选“Add Python to PATH”。

1. 进入后端目录：

```bash
cd flask_popquiz
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 启动后端服务：

```bash
python app.py
```

### 3.2 前端

**请确保已安装 Node.js（建议 LTS 版本）。**

- [Node.js 官网下载](https://nodejs.org/)

1. 进入前端目录：

```bash
cd vue_popquiz
```

2. 安装依赖：

```bash
npm install
```

3. 启动前端服务：

```bash
npm run dev
```

---

## 4. 配置文件说明

后端配置文件位于 `flask_popquiz/config.yaml`，主要包含以下内容：

### 4.1 题目生成相关配置（question_generate）

- `ollama_model_name`：本地 ollama 模型名称（如 deepseek-r1:7b）。
- `use_api`：是否使用 API 提供商（如 OpenAI、阿里云等）。
- `api.api_key`：如使用 API，需填写对应的 API Key。
- `api.model_name`：API 模型名称（如 qwen-max）。
- `api.base_url`：API 基础地址（如 OpenAI 兼容接口地址）。

### 4.2 数据库配置（database）

- `host`：数据库主机地址（如 localhost）。
- `port`：数据库端口（默认 3306）。
- `user`：数据库用户名（如 root）。
- `password`：数据库密码。
- `name`：数据库名（如 popquiz）。

### 4.3 上传目录（upload_dir）

- 上传文件的根目录，需确保该目录存在且有写入权限（如 C:/popquiz_file）。

### 4.4 LibreOffice 路径（libreoffice_executable）

- 用于 PPT 转 PDF 的 LibreOffice 可执行文件路径（默认路径为 C:/Program Files/LibreOffice/program/soffice.exe）。

### 4.5 Flask 端口（flask_port）

- 后端 Flask 服务监听的端口（默认 5000）。
- 若修改请同步修改 `vue_popquiz/src/api/index.js`与 `vue_popquiz/src/utils/websocket.js`中对应请求端口

如需修改配置，请编辑 `flask_popquiz/config.yaml`，修改后重启后端服务生效。

---

如有问题欢迎提 issue 或联系开发团队。
