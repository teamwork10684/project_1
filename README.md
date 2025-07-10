# PopQuiz 项目说明

本项目旨在开发一个基于 AI 的智能 Pop Quiz 系统，支持多端互动答题，适用于课堂、讲座等多种场景。

---

## 📁 目录结构

```
popquiz/
├── api_doc/                # 存放 OpenAPI/Swagger 等接口文档
│   └── popquiz_api.yml
├── flask_popquiz/          # 后端服务目录（Flask）
├── uni_popquiz/            # 微信小程序前端项目（uni-app）
├── vue_popquiz/            # Vue 前端项目（适用于 H5 桌面/移动端）
├── start.md                # 前端快速启动与开发环境搭建指南
├── recommend_plugins.md    # 推荐开发插件说明
└── README.md               # 项目主说明文档
```

- `api_doc/`：存放 OpenAPI/Swagger 等接口文档，便于前后端协作与接口规范管理。
- `flask_popquiz/`：后端服务目录，基于 Flask 框架开发，实现题目生成、答题、统计等核心业务逻辑。
- `uni_popquiz/`：微信小程序端前端项目，基于 uni-app 实现，适配微信小程序平台。
- `vue_popquiz/`：Vue 前端项目，适用于桌面端，支持现代 Web 体验。
- `start.md`：提供前端项目的快速启动与开发环境搭建指南，适合新手快速上手。
- `recommend_plugins.md`：推荐 VSCode 及相关开发插件，涵盖 uni-app、Vue、API 文档、Python 等常用开发场景，提升开发效率。
- `README.md`：项目主说明文档，介绍项目背景、结构、进度和使用方法。

---

## 🚧 当前进度

- 项目处于初步开发阶段，目录结构已搭建，部分 API 文档和基础代码已开始编写。
- 后端与前端功能正在逐步完善中。

---

## 📝 使用说明

1. 查看接口文档：
   - 进入 `api_doc/` 文件夹，查阅 `popquiz_api.yml`，可用 Swagger 等工具进行可视化预览。
2. 后端开发：
   - 进入 `flask_popquiz/`，基于 Flask 进行后端开发与调试。
3. 微信小程序开发：
   - 进入 `uni_popquiz/`，使用 uni-app 相关工具进行微信小程序端开发。
4. Vue 前端开发：
   - 进入 `vue_popquiz/`，使用 Vue 相关工具进行 H5 前端开发。
5. 参考 `start.md` 获取前端环境搭建与运行指引。
6. 参考 `recommend_plugins.md` 获取开发推荐插件。

---

## 📌 备注

- 本项目为初步开发阶段，文档与代码会持续更新。
- 欢迎提出建议或参与开发！
