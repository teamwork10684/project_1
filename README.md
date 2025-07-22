# PopQuiz 部署教程

本项目包含前端（Vue3）和后端两部分，需分别部署。

---

## 一、前端部署（vue_popquiz）

### 1. 安装 Node.js

- 请前往 [Node.js 官网](https://nodejs.org/) 下载并安装最新版 Node.js（建议 LTS 版本）。

### 2. 安装依赖

- 打开终端（命令行），切换到前端项目目录，或者直接在vue_popquiz中打开终端：
  ```bash
  cd 你的路径/vue_popquiz
  ```
- 安装依赖包：
  ```bash
  npm install
  ```

### 3. 启动前端项目

- 启动开发服务器：
  ```bash
  npm run dev
  ```
- 启动后，终端会显示本地访问地址，使用浏览器访问即可预览和开发。

---

## 二、后端部署（flask_popquiz）

### 1. 安装 Python 3.11

- 请前往 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.11。
- 安装时请勾选“Add Python to PATH”。

**本地AI题目生成功能需安装 [Ollama](https://ollama.com/)，并下载/运行 deepseek-r1:7b 模型。**

- 安装 Ollama 后，在命令行执行，确保可以进行对话：

```bash
ollama run deepseek-r1:7b
```

**PPT转PDF功能需安装 [LibreOffice](https://www.libreoffice.org/download/download/)。**

- 安装后请确保 `flask_popquiz/config.yaml` 中的 `libreoffice_executable` 路径与实际安装路径一致。

1. 进入后端目录：

- 打开终端，切换到后端目录：
  ```bash
  cd flask_popquiz
  ```
- 安装依赖包：
  ```bash
  pip install -r requirements.txt
  ```

### 3. 安装 Ollama 并下载模型

- 访问 [Ollama 官网](https://ollama.com/) 下载并安装 Ollama。
- 安装完成后，在命令行运行，确保能在命令行对话：
  ```bash
  ollama run deepseek-r1:7b
  ```
- 确保 Ollama 服务已启动在默认端口。

### 4. 安装 LibreOffice

- 前往 [LibreOffice 官网](https://www.libreoffice.org/download/download/) 下载并安装 LibreOffice。
- 安装完成后，确保 `soffice.exe` 路径与 `app.py` 中的 `LIBREOFFICE_PATH` 配置一致(app.py中为默认安装路径)。

### 5. 启动后端服务

- 在 `flask_popquiz` 目录下运行：
  ```bash
  python app.py
  ```
- 后端服务默认监听 5000 端口,若需修改请在`flask_popquiz/app.py`的最后一行将`port`改为你所需的端口,同时修改 `vue_popquiz/src/api/index.js`和 `vue_popquiz/src/utils/websocket.js`中对应端口。

---

## 其他说明（非常重要）!!!

- 数据库需提前创建并配置好（建表命令详见 `api_doc/create_tables.sql` ）。
- 在app.py中修改本地数据库连接密码和数据库名称 `app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://你的账户！！！(默认为root):你的密码！！！@localhost:3306/你的数据库名称！！！?charset=utf8mb4'`
- 如需修改端口或其他参数，请在 `app.py` 中调整。
- 如遇依赖安装问题，请确保 pip 已升级到最新版。

- 如需本地AI题目生成，需提前安装并运行 Ollama，确保 `ollama_model_name` 与实际模型一致。
- 如需PPT转PDF，需提前安装 LibreOffice 并配置好 `libreoffice_executable` 路径。

---

如有问题请联系开发者。
