<template>
  <div>
    <!-- Hero 区块 -->
    <section class="relative min-h-[70vh] md:min-h-[85vh] flex items-center px-4 md:px-8 lg:px-16 py-12 md:py-0 bg-memphis-yellow border-b-2 md:border-b-4 border-black overflow-hidden">
      <!-- Memphis 装饰元素 -->
      <svg class="absolute top-10 right-10 w-16 h-16 md:w-24 md:h-24 hidden md:block" viewBox="0 0 100 100">
        <polygon points="50,2 2,98 98,98" fill="#ff006e" stroke="#000" stroke-width="6" stroke-linejoin="miter" />
      </svg>
      <div class="absolute bottom-20 right-40 w-20 h-20 md:w-32 md:h-32 rounded-full border-4 border-black bg-memphis-teal hidden md:block" />
      <div class="absolute top-1/3 left-10 w-12 h-12 border-4 border-black bg-memphis-purple hidden md:block" style="transform: rotate(45deg)" />
      <div class="absolute bottom-10 left-20 w-40 h-2 bg-black hidden md:block" />

      <div class="max-w-screen-2xl mx-auto relative z-10">
        <div class="inline-block bg-memphis-coral text-white border-4 border-black px-3 py-1 md:px-4 md:py-2 font-mono text-xs md:text-sm mb-4 md:mb-6 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
          AI-POWERED INTERVIEW PLATFORM
        </div>
        <h1 class="font-black text-4xl md:text-6xl lg:text-7xl leading-tight tracking-tight mb-4 md:mb-6">
          AI模拟面试官<br />
          <span class="text-memphis-coral">&</span> 职业规划系统
        </h1>
        <p class="font-mono text-base md:text-xl max-w-xl mb-6 md:mb-8">
          智能模拟面试 · 简历深度分析 · 职业倾向测评 · 个性化发展<br />
          <br />
          一站式AI求职平台，助你斩获心仪Offer
        </p>
        <div class="flex flex-wrap gap-4">
          <button @click="$router.push('/auth')" class="bg-memphis-coral text-white font-black px-6 py-3 md:px-8 md:py-4 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all text-sm md:text-base cursor-pointer">
            免费开始面试模拟 →
          </button>
          <button @click="scrollToFeatures" class="bg-white text-black font-black px-6 py-3 md:px-8 md:py-4 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all text-sm md:text-base cursor-pointer">
            了解更多
          </button>
        </div>
      </div>
    </section>

    <!-- 数据统计条 -->
    <section class="bg-black text-white py-6 md:py-8 px-4 md:px-8 lg:px-16 border-b-4 border-memphis-coral">
      <div class="max-w-screen-2xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 text-center">
        <div>
          <div class="font-black text-2xl md:text-4xl text-memphis-yellow">10,000+</div>
          <div class="font-mono text-xs md:text-sm text-gray-400 mt-1">模拟面试次数</div>
        </div>
        <div>
          <div class="font-black text-2xl md:text-4xl text-memphis-teal">500+</div>
          <div class="font-mono text-xs md:text-sm text-gray-400 mt-1">面试题库</div>
        </div>
        <div>
          <div class="font-black text-2xl md:text-4xl text-memphis-coral">95%</div>
          <div class="font-mono text-xs md:text-sm text-gray-400 mt-1">用户满意度</div>
        </div>
        <div>
          <div class="font-black text-2xl md:text-4xl text-memphis-blue">50+</div>
          <div class="font-mono text-xs md:text-sm text-gray-400 mt-1">覆盖岗位</div>
        </div>
      </div>
    </section>

    <!-- 功能特色 -->
    <section id="features" class="py-12 md:py-24 px-4 md:px-8 lg:px-16 memphis-grid-bg">
      <div class="max-w-screen-2xl mx-auto">
        <div class="text-center mb-8 md:mb-16">
          <span class="inline-block bg-memphis-teal border-4 border-black px-3 py-1 font-mono text-xs md:text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] mb-4">CORE FEATURES</span>
          <h2 class="font-black text-3xl md:text-5xl tracking-tight">核心功能模块</h2>
          <p class="font-mono text-sm md:text-base mt-3 max-w-lg mx-auto">覆盖面试全流程，从模拟练习到职业规划的完整解决方案</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          <!-- 功能卡片 1: 模拟面试 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 hover:shadow-[5px_5px_0px_0px_rgba(255,0,110,1)] md:hover:shadow-[8px_8px_0px_0px_rgba(255,0,110,1)] hover:-translate-y-1 transition-all">
            <div class="w-12 h-12 md:w-14 md:h-14 bg-memphis-coral border-4 border-black flex items-center justify-center mb-4">
              <span class="text-white text-xl md:text-2xl">🎤</span>
            </div>
            <h3 class="font-black text-lg md:text-xl mb-2 tracking-tight">模拟面试</h3>
            <ul class="font-mono text-xs md:text-sm space-y-1 text-gray-700">
              <li>• 随机抽题 + 倒计时模拟</li>
              <li>• 语音回答 + ASR转文字</li>
              <li>• AI多轮追问面试官</li>
              <li>• 压力测试 / 情境模拟</li>
              <li>• SSE流式输出AI回答</li>
            </ul>
          </div>

          <!-- 功能卡片 2: 职业测评 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 hover:shadow-[5px_5px_0px_0px_rgba(255,190,11,1)] md:hover:shadow-[8px_8px_0px_0px_rgba(255,190,11,1)] hover:-translate-y-1 transition-all">
            <div class="w-12 h-12 md:w-14 md:h-14 bg-memphis-yellow border-4 border-black flex items-center justify-center mb-4">
              <span class="text-xl md:text-2xl">🧭</span>
            </div>
            <h3 class="font-black text-lg md:text-xl mb-2 tracking-tight">职业测评</h3>
            <ul class="font-mono text-xs md:text-sm space-y-1 text-gray-700">
              <li>• Holland六维度职业倾向</li>
              <li>• LLM个性化解读报告</li>
              <li>• 个性化发展路径图</li>
              <li>• 技能学习路线图</li>
              <li>• 求职信/自我介绍生成</li>
            </ul>
          </div>

          <!-- 功能卡片 3: 简历分析 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 hover:shadow-[5px_5px_0px_0px_rgba(131,56,236,1)] md:hover:shadow-[8px_8px_0px_0px_rgba(131,56,236,1)] hover:-translate-y-1 transition-all">
            <div class="w-12 h-12 md:w-14 md:h-14 bg-memphis-purple border-4 border-black flex items-center justify-center mb-4">
              <span class="text-white text-xl md:text-2xl">📄</span>
            </div>
            <h3 class="font-black text-lg md:text-xl mb-2 tracking-tight">简历分析</h3>
            <ul class="font-mono text-xs md:text-sm space-y-1 text-gray-700">
              <li>• PDF/DOCX上传解析</li>
              <li>• LLM结构化信息提取</li>
              <li>• 技能词云 + 经历时间线</li>
              <li>• 简历措辞AI优化</li>
              <li>• 一键导出PDF</li>
            </ul>
          </div>

          <!-- 功能卡片 4: 面经论坛 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 hover:shadow-[5px_5px_0px_0px_rgba(58,134,255,1)] md:hover:shadow-[8px_8px_0px_0px_rgba(58,134,255,1)] hover:-translate-y-1 transition-all">
            <div class="w-12 h-12 md:w-14 md:h-14 bg-memphis-blue border-4 border-black flex items-center justify-center mb-4">
              <span class="text-white text-xl md:text-2xl">💬</span>
            </div>
            <h3 class="font-black text-lg md:text-xl mb-2 tracking-tight">面经论坛</h3>
            <ul class="font-mono text-xs md:text-sm space-y-1 text-gray-700">
              <li>• 社区面经分享</li>
              <li>• 分类浏览 + 全文搜索</li>
              <li>• 点赞评论互动</li>
              <li>• STAR法则详解</li>
              <li>• 面试礼仪指南</li>
            </ul>
          </div>

          <!-- 功能卡片 5: OJ刷题 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 hover:shadow-[5px_5px_0px_0px_rgba(34,197,94,1)] md:hover:shadow-[8px_8px_0px_0px_rgba(34,197,94,1)] hover:-translate-y-1 transition-all">
            <div class="w-12 h-12 md:w-14 md:h-14 bg-[#22c55e] border-4 border-black flex items-center justify-center mb-4">
              <span class="text-white text-xl md:text-2xl">🧩</span>
            </div>
            <h3 class="font-black text-lg md:text-xl mb-2 tracking-tight">OJ刷题</h3>
            <ul class="font-mono text-xs md:text-sm space-y-1 text-gray-700">
              <li>• 算法题在线编写</li>
              <li>• 在线判题系统</li>
              <li>• 多难度分级</li>
              <li>• 解题进度追踪</li>
              <li>• 代码执行与调试</li>
            </ul>
          </div>

          <!-- 功能卡片 6: 更多亮点 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(255,0,110,1)] md:shadow-[8px_8px_0px_0px_rgba(255,0,110,1)] p-5 md:p-8 hover:shadow-[5px_5px_0px_0px_rgba(255,190,11,1)] md:hover:shadow-[8px_8px_0px_0px_rgba(255,190,11,1)] hover:-translate-y-1 transition-all">
            <div class="w-12 h-12 md:w-14 md:h-14 bg-memphis-orange border-4 border-black flex items-center justify-center mb-4">
              <span class="text-xl md:text-2xl">✨</span>
            </div>
            <h3 class="font-black text-lg md:text-xl mb-2 tracking-tight">更多亮点</h3>
            <ul class="font-mono text-xs md:text-sm space-y-1 text-gray-700">
              <li>• AI语音朗读 (TTS)</li>
              <li>• 面试题收藏 + 笔记</li>
              <li>• 环形倒计时动画</li>
              <li>• 面试防作弊检测</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section id="how-it-works" class="py-12 md:py-24 px-4 md:px-8 lg:px-16 bg-memphis-blue border-b-2 md:border-b-4 border-black">
      <div class="max-w-screen-2xl mx-auto">
        <div class="text-center mb-8 md:mb-16">
          <span class="inline-block bg-memphis-yellow border-4 border-black px-3 py-1 font-mono text-xs md:text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] mb-4">HOW IT WORKS</span>
          <h2 class="font-black text-3xl md:text-5xl tracking-tight text-white">四步开启AI面试之旅</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6">
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-6 text-center relative">
            <div class="absolute -top-4 -left-4 w-10 h-10 bg-memphis-coral border-4 border-black flex items-center justify-center font-black text-white text-lg">1</div>
            <div class="text-3xl mb-3 mt-2">📝</div>
            <h3 class="font-black text-base md:text-lg mb-2">上传简历</h3>
            <p class="font-mono text-xs md:text-sm text-gray-700">上传PDF/DOCX简历，AI自动解析提取关键信息</p>
          </div>
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-6 text-center relative">
            <div class="absolute -top-4 -left-4 w-10 h-10 bg-memphis-yellow border-4 border-black flex items-center justify-center font-black text-lg">2</div>
            <div class="text-3xl mb-3 mt-2">🎯</div>
            <h3 class="font-black text-base md:text-lg mb-2">选择岗位</h3>
            <p class="font-mono text-xs md:text-sm text-gray-700">选择目标岗位和难度，AI智能匹配面试题目</p>
          </div>
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-6 text-center relative">
            <div class="absolute -top-4 -left-4 w-10 h-10 bg-memphis-teal border-4 border-black flex items-center justify-center font-black text-lg">3</div>
            <div class="text-3xl mb-3 mt-2">🎤</div>
            <h3 class="font-black text-base md:text-lg mb-2">模拟面试</h3>
            <p class="font-mono text-xs md:text-sm text-gray-700">与AI面试官实时对话，支持语音和文字回答</p>
          </div>
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-6 text-center relative">
            <div class="absolute -top-4 -left-4 w-10 h-10 bg-memphis-purple border-4 border-black flex items-center justify-center font-black text-white text-lg">4</div>
            <div class="text-3xl mb-3 mt-2">📈</div>
            <h3 class="font-black text-base md:text-lg mb-2">获取报告</h3>
            <p class="font-mono text-xs md:text-sm text-gray-700">获得多维度评估报告和改进建议，持续提升</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 技术架构 -->
    <section id="tech" class="py-12 md:py-24 px-4 md:px-8 lg:px-16 bg-memphis-cream">
      <div class="max-w-screen-2xl mx-auto">
        <div class="text-center mb-8 md:mb-16">
          <span class="inline-block bg-memphis-orange border-4 border-black px-3 py-1 font-mono text-xs md:text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] mb-4">TECH STACK</span>
          <h2 class="font-black text-3xl md:text-5xl tracking-tight">技术架构</h2>
          <p class="font-mono text-sm md:text-base mt-3">现代化技术栈，高性能AI驱动</p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
          <div class="memphis-card p-4 text-center hover:shadow-[5px_5px_0px_0px_rgba(255,0,110,1)] hover:-translate-y-1 transition-all">
            <div class="text-2xl mb-2">🖥️</div>
            <div class="font-black text-xs md:text-sm">Vue 3</div>
            <div class="font-mono text-[10px] md:text-xs text-gray-600">前端框架</div>
          </div>
          <div class="memphis-card p-4 text-center hover:shadow-[5px_5px_0px_0px_rgba(58,134,255,1)] hover:-translate-y-1 transition-all">
            <div class="text-2xl mb-2">⚡</div>
            <div class="font-black text-xs md:text-sm">FastAPI</div>
            <div class="font-mono text-[10px] md:text-xs text-gray-600">后端服务</div>
          </div>
          <div class="memphis-card p-4 text-center hover:shadow-[5px_5px_0px_0px_rgba(0,245,212,1)] hover:-translate-y-1 transition-all">
            <div class="text-2xl mb-2">🧠</div>
            <div class="font-black text-xs md:text-sm">DeepSeek</div>
            <div class="font-mono text-[10px] md:text-xs text-gray-600">AI大模型</div>
          </div>
          <div class="memphis-card p-4 text-center hover:shadow-[5px_5px_0px_0px_rgba(131,56,236,1)] hover:-translate-y-1 transition-all">
            <div class="text-2xl mb-2">🗄️</div>
            <div class="font-black text-xs md:text-sm">MySQL 8</div>
            <div class="font-mono text-[10px] md:text-xs text-gray-600">数据库</div>
          </div>
          <div class="memphis-card p-4 text-center hover:shadow-[5px_5px_0px_0px_rgba(255,190,11,1)] hover:-translate-y-1 transition-all">
            <div class="text-2xl mb-2">🎙️</div>
            <div class="font-black text-xs md:text-sm">edge-tts</div>
            <div class="font-mono text-[10px] md:text-xs text-gray-600">语音合成</div>
          </div>
          <div class="memphis-card p-4 text-center hover:shadow-[5px_5px_0px_0px_rgba(251,86,7,1)] hover:-translate-y-1 transition-all">
            <div class="text-2xl mb-2">🧊</div>
            <div class="font-black text-xs md:text-sm">Three.js</div>
            <div class="font-mono text-[10px] md:text-xs text-gray-600">3D数字人</div>
          </div>
        </div>

        <!-- 架构图示 -->
        <div class="mt-8 md:mt-12 memphis-card p-5 md:p-8">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 text-center">
            <div class="bg-memphis-yellow border-4 border-black p-4">
              <div class="font-black text-sm md:text-base mb-2">前端层</div>
              <div class="font-mono text-xs text-gray-700">Vue 3 + TypeScript + Vite</div>
              <div class="font-mono text-xs text-gray-700">Pinia + ECharts + TailwindCSS</div>
            </div>
            <div class="bg-memphis-teal border-4 border-black p-4">
              <div class="font-black text-sm md:text-base mb-2">AI层</div>
              <div class="font-mono text-xs text-gray-700">DeepSeek API + edge-tts</div>
              <div class="font-mono text-xs text-gray-700">Three.js + VRM 数字人</div>
            </div>
            <div class="bg-memphis-coral text-white border-4 border-black p-4">
              <div class="font-black text-sm md:text-base mb-2">后端层</div>
              <div class="font-mono text-xs text-gray-200">FastAPI + SQLAlchemy 2.0</div>
              <div class="font-mono text-xs text-gray-200">Alembic + PyMuPDF + MySQL</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 定价方案 -->
    <section id="pricing" class="py-12 md:py-24 px-4 md:px-8 lg:px-16 bg-memphis-purple border-b-2 md:border-b-4 border-black">
      <div class="max-w-screen-2xl mx-auto">
        <div class="text-center mb-8 md:mb-16">
          <span class="inline-block bg-white border-4 border-black px-3 py-1 font-mono text-xs md:text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] mb-4">PRICING</span>
          <h2 class="font-black text-3xl md:text-5xl tracking-tight text-white">定价方案</h2>
          <p class="font-mono text-sm md:text-base mt-3 text-gray-200">选择适合你的方案，开启AI面试之旅</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 max-w-5xl mx-auto">
          <!-- 免费版 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all">
            <div class="font-black text-lg md:text-xl mb-1">免费版</div>
            <div class="font-black text-3xl md:text-4xl my-3">¥0<span class="font-mono text-sm font-normal text-gray-600">/月</span></div>
            <ul class="font-mono text-xs md:text-sm space-y-2 mb-6">
              <li>✓ 每日3次模拟面试</li>
              <li>✓ 基础评分报告</li>
              <li>✓ 50道精选题库</li>
              <li class="text-gray-400">✗ AI多轮追问</li>
              <li class="text-gray-400">✗ 简历分析</li>
            </ul>
            <button class="w-full bg-white text-black border-4 border-black memphis-btn-primary py-2 md:py-3 text-sm">
              免费开始
            </button>
          </div>

          <!-- 专业版 -->
          <div class="bg-memphis-yellow border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 relative scale-105">
            <div class="absolute -top-4 left-1/2 -translate-x-1/2 bg-memphis-coral text-white border-4 border-black px-3 py-1 font-black text-xs">
              推荐
            </div>
            <div class="font-black text-lg md:text-xl mb-1">专业版</div>
            <div class="font-black text-3xl md:text-4xl my-3">¥49<span class="font-mono text-sm font-normal text-gray-700">/月</span></div>
            <ul class="font-mono text-xs md:text-sm space-y-2 mb-6">
              <li>✓ 无限次模拟面试</li>
              <li>✓ 多维度深度评估</li>
              <li>✓ 完整题库500+</li>
              <li>✓ AI多轮追问</li>
              <li>✓ 简历分析优化</li>
              <li>✓ Live 2D 数字人</li>
              <li>✓ 数字人捏脸系统</li>
            </ul>
            <button class="w-full bg-black text-white border-4 border-black memphis-btn-primary py-2 md:py-3 text-sm">
              立即订阅
            </button>
          </div>

          <!-- 企业版 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-8 hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all">
            <div class="font-black text-lg md:text-xl mb-1">企业版</div>
            <div class="font-black text-3xl md:text-4xl my-3">定制<span class="font-mono text-sm font-normal text-gray-600">报价</span></div>
            <ul class="font-mono text-xs md:text-sm space-y-2 mb-6">
              <li>✓ 专业版全部功能</li>
              <li>✓ 自定义题库</li>
              <li>✓ 团队管理后台</li>
              <li>✓ 数据报表分析</li>
              <li>✓ 专属技术支持</li>
            </ul>
            <button class="w-full bg-memphis-purple text-white border-4 border-black memphis-btn-primary py-2 md:py-3 text-sm">
              联系销售
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-12 md:py-24 px-4 md:px-8 lg:px-16 bg-memphis-coral border-b-2 md:border-b-4 border-black relative overflow-hidden">
      <svg class="absolute top-5 left-10 w-16 h-16 hidden md:block" viewBox="0 0 100 100">
        <polygon points="50,2 2,98 98,98" fill="#ffbe0b" stroke="#000" stroke-width="6" stroke-linejoin="miter" />
      </svg>
      <div class="absolute bottom-5 right-20 w-20 h-20 rounded-full border-4 border-black bg-memphis-teal hidden md:block" />
      <div class="max-w-3xl mx-auto text-center relative z-10">
        <h2 class="font-black text-3xl md:text-5xl text-white tracking-tight mb-4">准备好斩获心仪Offer了吗？</h2>
        <p class="font-mono text-sm md:text-base text-white/80 mb-6 md:mb-8">立即开始AI模拟面试，获取专业评估报告，规划你的职业未来</p>
        <button @click="$router.push('/auth')" class="bg-white text-black font-black px-8 py-4 md:px-12 md:py-5 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all text-sm md:text-lg cursor-pointer">
          免费开始使用 →
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
function scrollToFeatures() {
  const el = document.getElementById('features')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>
