## 1. 体系与工具链
- 框架：Vue3 + Vite + TypeScript，使用 Tailwind CSS v4（通过 `@tailwindcss/vite` 插件集成）。
- 设计语言：自定义 Memphis 视觉风格，强调粗黑边框、硬阴影、高饱和撞色与无圆角几何感。
- 字体：全局使用 Noto Sans SC（正文）与 Space Mono（等宽），在 Tailwind 与 CSS 变量中同时声明。
- 构建产物：Vite 打包，Tailwind 扫描 `src/**/*.{vue,js,ts,jsx,tsx}` 生成原子类。

## 2. 核心文件与包
- `frontEnd/tailwind.config.ts`：扩展 Tailwind 主题，定义 `memphis.*` 色彩族与字体族。
- `frontEnd/src/style.css`：通过 `@theme` 注入 CSS 变量，集中定义 Memphis 背景纹理、组件基类（按钮/卡片/输入）、滚动条主题与弹窗过渡。
- `frontEnd/package.json`：依赖 `tailwindcss`、`@tailwindcss/vite`、`vue`、`pinia`、`vue-router` 等。
- 布局组件：`DashboardLayout.vue`、`AdminLayout.vue` 作为全站骨架，统一应用 Memphis 风格。

## 3. 架构与约定
- 设计令牌（Design Tokens）
  - 颜色：`memphis.coral/yellow/teal/blue/purple/orange/cream/black/white` 九色，对应 CSS 变量 `--color-memphis-*`，可在模板中以 `bg-memphis-coral`、`text-memphis-blue` 等形式直接使用。
  - 字体：`font-sans = 'Noto Sans SC'`，`font-mono = 'Space Mono'`。
- 全局样式分层
  - `style.css` 顶层 `@import "tailwindcss"` 后紧跟 `@theme` 块，将 Tailwind 配置中的 token 同步到 CSS 变量，保证 Tailwind 与原生 CSS 共享同一套主题。
  - 基础 UI 以 `.memphis-btn-primary`、`.memphis-card`、`.memphis-input` 等语义化类封装通用外观（粗边框、硬阴影、零圆角、hover 位移）。
  - 装饰性背景类 `.memphis-dot-bg`、`.memphis-grid-bg`、`.memphis-zigzag` 提供 Memphis 标志性点阵/网格/锯齿纹样。
  - 全局滚动条通过 `::-webkit-scrollbar` 与 `scrollbar-color` 定制为细窄、带黑色边线的 Memphis 风格。
- 组件级样式策略
  - 页面/布局组件优先使用 Tailwind 原子类组合表达 Memphis 风格（如 `border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px]`），避免新增大量重复 CSS。
  - 复杂交互或可复用控件才下沉到 `style.css` 的 `.memphis-*` 类。
- 动画与过渡
  - 弹窗采用 `.modal-fade-enter-active / .modal-fade-leave-active` 等 Vue Transition 钩子实现淡入淡出。
  - 按钮/卡片 hover 通过 `translate` + 阴影偏移模拟“按压”效果，保持 Memphis 的立体感。

## 4. 开发者规范
- 颜色使用：优先引用 `memphis.*` 调色板，不要手写十六进制色值；新增颜色需同步更新 `tailwind.config.ts` 与 `@theme` 块。
- 字体使用：正文用 `font-sans`，代码/等宽内容用 `font-mono`，禁止随意引入新字体。
- 边框与阴影：遵循“4px 实线黑框 + 硬阴影”的 Memphis 语法，圆角一律为 0；hover 时通过 `translate` 与缩小阴影制造按下感。
- 背景纹理：需要 Memphis 装饰时使用 `.memphis-dot-bg` / `.memphis-grid-bg` / `.memphis-zigzag`，避免自行编写 SVG/CSS 图案。
- 组件样式优先级：能用 Tailwind 原子类表达的样式优先写在模板 class 中；只有跨页面复用的基础控件才放入 `style.css` 的 `.memphis-*` 命名空间。
- 滚动条与过渡：如需自定义滚动条或弹窗动画，参考现有 `::-webkit-scrollbar` 与 `.modal-fade-*` 写法，保持一致的粗细与配色。
- 构建与扫描：新增 Vue/TS 文件无需手动维护 Tailwind 扫描列表，`content` 已覆盖 `src/**/*.{vue,js,ts,jsx,tsx}`。