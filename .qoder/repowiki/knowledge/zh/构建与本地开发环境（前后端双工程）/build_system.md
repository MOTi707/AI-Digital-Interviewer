本仓库为前后端分离的单体项目，未引入统一的 CI/CD、容器化或 Makefile 等跨平台构建系统，而是通过各自子工程的包管理器脚本 + Windows 启动批处理完成本地开发与预览。

- 后端（backEnd）
  - 依赖管理：Python venv + requirements.txt 固定版本；无 Dockerfile / docker-compose。
  - 运行入口：uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload，由根目录 start.cmd 一键拉起。
  - 数据库迁移：Alembic，连接串硬编码在 alembic.ini（mysql+pymysql://root@localhost:3306/hr_interview），需手动执行 alembic upgrade head。
  - 初始化数据：根目录提供 hr_interview.sql 与 add_comments.sql，需在 MySQL 中手动导入。

- 前端（frontEnd）
  - 构建工具：Vite + Vue3 + TypeScript，脚本定义在 package.json：
    - npm run dev → Vite 开发服务器（默认 5173 端口）。
    - npm run build → vue-tsc -b && vite build 产出静态资源到 dist/。
    - npm run preview → 本地预览生产构建产物。
  - 开发代理：vite.config.ts 将 /api 请求反向代理至 http://localhost:8000，解决开发期跨域问题。
  - 样式：Tailwind CSS v4（通过 @tailwindcss/vite 插件集成）。

- 统一启动（Windows）
  - 根目录 start.cmd 依次启动后端（带 --reload 热重载）与前端，并在浏览器打开 http://localhost:5173。

- 缺失项
  - 无 Dockerfile / docker-compose.yml、无 Makefile、无 GitHub Actions / Jenkins 等 CI 流水线、无发布/打包脚本。
  - 数据库 URL、端口等配置直接写死在源码/配置文件内，未使用环境变量注入。

开发者约定
- 新增 Python 依赖后同步更新 backEnd/requirements.txt。
- 新增前端依赖后更新 frontEnd/package.json，并重新生成 package-lock.json。
- 修改 Alembic 模型后，在 backEnd/ 下执行 alembic revision --autogenerate -m "描述" 生成迁移文件，再 alembic upgrade head 应用。
- 本地联调时保持 start.cmd 中的后端 8000 端口与前端 5173 端口不变，或通过 vite.config.ts 调整代理目标。