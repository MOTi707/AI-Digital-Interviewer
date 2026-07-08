本仓库为前后端分离的单体工程，依赖管理按子工程独立采用各自生态的标准方案：后端 Python 使用 `requirements.txt` 声明式锁定版本，前端 Vue3 应用使用 `package.json` + `package-lock.json` 进行依赖与锁文件管理。未使用私有仓库、vendor 或 pipenv/poetry/lockfile 等高级特性，整体风格简洁直接。

## 1. 后端依赖（Python / FastAPI）
- **声明文件**：`backEnd/requirements.txt`
- **包管理器**：pip（通过 `.venv` 虚拟环境隔离）
- **版本策略**：核心框架与数据库驱动采用精确版本号（如 `fastapi==0.115.12`、`uvicorn[standard]==0.34.2`、`sqlalchemy[asyncio]==2.0.41`、`alembic==1.16.1`），第三方库对次要/补丁版本放宽为 `>=`（如 `aiomysql>=0.2.0`、`pymysql>=1.1.0`、`httpx>=0.27.0`、`PyMuPDF>=1.27.0`、`edge-tts>=6.1.0`），在保持可复现性的同时保留小幅升级空间。
- **虚拟环境**：`.venv/` 目录存在但未纳入版本控制，本地开发通过 `python -m venv .venv && pip install -r requirements.txt` 安装。
- **无私有源配置**：未发现 `pip.conf`、`setup.cfg` 中的 index-url 或 `--extra-index-url` 设置，默认使用 PyPI。

## 2. 前端依赖（Vue3 / Vite）
- **声明文件**：`frontEnd/package.json`（`dependencies` 与 `devDependencies` 明确区分运行期与构建期依赖）
- **锁文件**：`frontEnd/package-lock.json`（lockfileVersion 3），由 npm 生成并随代码提交，确保团队与 CI 构建一致性。
- **版本策略**：全部使用 `^` 语义化范围（如 `vue@^3.5.38`、`pinia@^3.0.4`、`tailwindcss@^4.3.1`、`vite@^8.1.0`），允许小版本自动升级；TypeScript 使用 `~` 限定次版本（`typescript~6.0.2`）以缩小变更面。
- **包管理器**：npm（从 lockfile 可见 registry 指向 `https://registry.npmjs.org`），未发现 `.npmrc` 自定义源或镜像配置。
- **构建脚本**：`dev`/`build`/`preview` 通过 Vite 与 `vue-tsc -b` 组合，依赖均在 devDependencies 中声明。

## 3. 架构约定与约束
- **双清单并行**：后端 `requirements.txt` 与前端 `package.json` 共同构成项目完整依赖契约，新增依赖需同步更新对应清单。
- **不提交运行时缓存**：`backEnd/.venv` 与 `frontEnd/node_modules` 均未纳入版本控制，避免二进制差异与仓库膨胀。
- **无 vendoring / 私有注册表**：未发现 `vendor/`、`poetry.lock`、`Pipfile.lock`、`.npmrc` 等机制，所有包均从公共源拉取。
- **Docker/CI 集成缺失**：根目录未见 Dockerfile 或 CI 配置文件，依赖安装流程目前仅通过本地脚本 `start.cmd` 驱动。

## 4. 开发者应遵循的规则
- 新增后端依赖时，在 `backEnd/requirements.txt` 中显式添加，优先使用 `==` 锁定关键包版本，必要时用 `>=` 放宽非关键包。
- 新增前端依赖时，在 `frontEnd/package.json` 的 `dependencies` 或 `devDependencies` 中添加，并提交生成的 `package-lock.json`。
- 不要手动编辑 `package-lock.json`，应通过 `npm install` 让 npm 维护。
- 不要在仓库中提交 `.venv/` 或 `node_modules/`，如需共享预编译产物请使用其他机制（当前仓库未启用）。
- 若未来引入私有包或内部 registry，应在 `backEnd/` 下增加 `pip.conf` 或在 `frontEnd/` 下增加 `.npmrc`，并在 README 中说明配置方式。