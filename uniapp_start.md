# 🚀 Uni-app 快速上手指南

## 1️⃣ 安装 Node.js

请先前往 [Node.js 官网](https://nodejs.org/) 下载并安装最新版 Node.js。
（建议使用 LTS 版本，体验更稳定！）

---

## 2️⃣ 全局安装 Vue CLI

在终端中输入以下命令，安装 Vue CLI 工具：

```bash
npm install -g @vue/cli
```

✨ 安装成功后可使用 `vue` 命令。

---

## 3️⃣ 下载 uni-app 模板

推荐使用 degit 快速拉取官方模板：

```bash
npx degit dcloudio/uni-preset-vue#vite popquiz
```

⚡️ 如果下载较慢，可前往 [Gitee 镜像](https://gitee.com/dcloud/uni-preset-vue/repository/archive/vite.zip) 下载并手动解压。

---

## 4️⃣ 安装依赖

进入项目目录，安装依赖包：

```bash
cd 路径/uni-popquiz 
npm install
```

🐢 如果速度较慢，可尝试使用管理员 CMD 或 `cnpm install`。

---

## 5️⃣ 启动开发环境

在项目根目录下运行：

```bash
npm run dev:h5
```

🌈 打开浏览器访问提示的本地地址，即可预览 H5 端效果！

---

> 💡 温馨提示：
>
> - 如需开发小程序等多端，请参考 [uni-app 官方文档](https://uniapp.dcloud.net.cn/)。
