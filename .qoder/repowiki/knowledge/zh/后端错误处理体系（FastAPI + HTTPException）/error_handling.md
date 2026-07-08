本仓库的后端基于 FastAPI，采用「统一异常处理器 + 业务层 raise HTTPException」的模式进行错误处理，前端通过标准 HTTP 状态码与 JSON detail 字段消费错误信息。

## 1. 系统/框架
- FastAPI：作为 Web 框架，提供内置的 HTTPException、RequestValidationError 等异常类型。
- SQLAlchemy AsyncSession：在依赖注入中统一管理事务提交/回滚。

## 2. 核心文件与职责
- backEnd/app/main.py
  - 注册全局异常处理器 @app.exception_handler(RequestValidationError)，将 Pydantic 验证错误转换为 {"detail": [...]} 的 422 响应，并过滤掉可能包含二进制内容的 input 字段以避免 UnicodeDecodeError。
  - 挂载 /api/health 健康检查路由。
- backEnd/app/dependencies.py
  - 定义 get_current_user 认证依赖，校验 Bearer Token 后若失败直接 raise HTTPException(status=401, detail=...)，并在未激活用户时返回 401。
- backEnd/app/database.py
  - get_db() 依赖在 try/except Exception 中捕获数据库操作异常，执行 session.rollback() 后再 raise，保证事务一致性。
- 各 routers/*.py（如 admin.py、auth.py、interview.py 等）
  - 在路由函数内对资源不存在、权限不足等场景直接 raise HTTPException(status_code=xxx, detail="中文描述")，例如 403 无管理员权限、404 资源不存在、400 参数错误等。

## 3. 架构与约定
- 错误传播路径：路由 → 服务层（如有）→ 抛出 HTTPException → FastAPI 统一序列化 → 客户端。
- 状态码约定：
  - 401：认证失败 / Token 无效 / 用户被禁用。
  - 403：鉴权失败（如非管理员访问管理接口）。
  - 404：资源不存在。
  - 400：业务参数错误。
  - 422：Pydantic 模型验证失败（由全局处理器统一包装）。
- 错误体格式：{"detail": "..."} 或验证错误时为 {"detail": [ {...}, ... ]}。
- 数据库异常：不向客户端暴露原始 SQL 异常，仅回滚事务后向上抛出，由上层路由决定如何转换为 HTTP 错误。

## 4. 开发者应遵循的规则
1. 不要在路由或服务层自行 try/except 再 return JSONResponse，统一使用 raise HTTPException(status_code=..., detail=...)。
2. detail 使用简洁中文，便于前端直接展示给用户。
3. 不要吞掉异常：数据库层已做 rollback，其他层捕获后应重新 raise 或转为合适的 HTTPException。
4. 避免在 detail 中泄露敏感信息（如内部堆栈、SQL 语句），当前实现已通过过滤 input 字段规避部分风险。
5. 新增业务错误码时，优先复用现有 4xx 状态码，必要时扩展 detail 结构（保持向后兼容）。