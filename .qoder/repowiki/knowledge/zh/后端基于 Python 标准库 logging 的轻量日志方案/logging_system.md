## 系统概述
本仓库在后端（FastAPI）中采用 Python 标准库 `logging` 作为唯一日志框架，未引入 loguru、structlog、sentry 等第三方日志组件。前端（Vue3）未发现专门的日志记录代码。

## 关键文件与位置
- `backEnd/app/services/code_executor.py`：应用层唯一显式使用 `logging.getLogger(__name__)` 获取 logger 并输出 debug/warning 级别日志，用于编译器路径检测、安全拦截等场景。
- `backEnd/alembic/env.py`：通过 `logging.config.fileConfig` 加载 alembic.ini 中的日志配置。
- `backEnd/alembic.ini`：定义 Alembic 迁移工具的日志器、处理器与格式化器，将 root/sqlalchemy/alembic 三个 logger 路由到 stderr 控制台输出。

## 架构与约定
- **Logger 命名空间**：遵循 Python 惯例，以模块名 `__name__` 作为 logger 名称（如 `app.services.code_executor`），便于按包层级过滤。
- **日志级别策略**：
  - `debug`：编译器自动发现路径等调试信息。
  - `warning`：编译器缺失、代码安全拦截等可恢复异常。
  - 未见 `info`/`error`/`critical` 的使用，整体日志量偏少。
- **结构化字段**：当前仅使用 `%s` 占位符拼接字符串，未采用 JSON 结构化日志或统一字段（如 request_id、user_id）。
- **Sink 目标**：仅输出到 stderr 控制台；无文件轮转、远程收集或 APM 集成。
- **Alembic 独立配置**：数据库迁移工具通过 `alembic.ini` 单独配置日志级别（root=WARNING、sqlalchemy.engine=WARNING、alembic=INFO），与应用运行时解耦。

## 开发者应遵循的规则
1. 新增日志请使用 `import logging; logger = logging.getLogger(__name__)` 模式，避免全局 `logging.info()` 调用。
2. 合理选择级别：诊断性信息用 `debug`，业务异常/警告用 `warning`，严重错误建议抛出异常而非仅打日志。
3. 暂不强制要求结构化日志字段，但建议在关键路径（如 OJ 执行、鉴权失败）补充上下文参数以便排查。
4. 如需持久化或集中收集日志，应在 FastAPI lifespan 启动阶段统一配置根 logger handler（例如 RotatingFileHandler 或 HTTP sink），而非在各模块分散配置。