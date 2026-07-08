## 1. 使用的系统与工具
- **pydantic-settings** (`BaseSettings`)：作为统一配置加载器，提供类型校验、默认值与自动环境变量注入。
- **.env 文件**：通过 `SettingsConfigDict(env_file=...)` 指定 `.env` 路径，实现本地开发环境配置集中管理。
- **lru_cache 单例**：`get_settings()` 使用 `@lru_cache` 缓存 Settings 实例，避免重复读取与解析。

## 2. 核心文件与位置
- `backEnd/app/config.py`：定义 `Settings` 模型及 `get_settings()` 工厂函数。
- `backEnd/.env`：所有运行时配置键值对（数据库、JWT、MinIO、CORS、Deepseek API、编译器路径等）。
- `backEnd/app/database.py`：从 `config.get_settings()` 获取 `database_url` 并创建异步 SQLAlchemy Engine/Session。
- `backEnd/app/main.py`：在应用启动时读取 `settings.cors_origins_list` 挂载 CORS 中间件，并在 lifespan 中初始化数据库表与种子数据。

## 3. 架构与设计约定
- **单一配置源**：所有后端模块通过 `from app.config import get_settings` 获取配置，禁止在各处硬编码敏感信息或连接字符串。
- **分层字段组织**：按功能域分组声明字段（Database / JWT / MinIO / CORS / Deepseek API / Compiler paths），每个字段带合理默认值，便于本地开箱即用。
- **派生属性封装**：通过 `@property` 暴露组合后的 URL（`database_url`、`database_url_sync`）和列表（`cors_origins_list`），调用方无需关心拼接细节。
- **延迟初始化**：`get_settings()` 被 `database.py` 和 `main.py` 直接调用，但实际 Settings 实例仅在首次访问时构建，配合 `lru_cache` 保证全局唯一。
- **与环境无关的构造**：`.env` 路径基于 `__file__.parent.parent` 计算，不依赖工作目录，确保无论从哪里启动都能正确加载。

## 4. 开发者应遵循的规则
1. **新增配置项**：在 `Settings` 类中以相同风格添加字段，给出有意义的默认值；若需要派生值，用 `@property` 暴露。
2. **同步到 .env**：新字段必须同步写入 `backEnd/.env`，保持注释说明用途，避免遗漏导致运行时报错。
3. **不要绕过 get_settings()**：其他模块一律通过 `get_settings()` 获取配置，禁止直接实例化 `Settings()` 或硬编码常量。
4. **敏感信息不入仓库**：生产环境的密钥（如 `SECRET_KEY`、`DEEPSEEK_API_KEY`）应通过部署平台的环境变量注入，而非提交到版本库。
5. **类型安全优先**：利用 pydantic 的类型提示与校验，避免在业务代码中再做二次转换或断言。