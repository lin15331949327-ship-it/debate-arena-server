# 三Agent辩论场 — 方案B落地计划 (Project Chimera生成)

> Chimera管线: Phase 0 Twin → Phase 1 Dual Research → Phase 1.5 Skeleton → Phase 2 Planner+Reviewer

---

## Phase 0: 结构化任务书
# Phase 0: Task Spec

# Web辩论室方案

## 一、整体架构

基于现有3Agent辩论引擎v3和飞书集成，采用前后端分离架构，新增Web辩论室模块。

### 推荐技术栈
- **前端**: React + D3.js（热力图）+ WebSocket（实时通信）
- **后端**: Node.js（Express）+ Redis（状态管理）+ WebSocket Server
- **数据层**: 飞书API + 知识库缓存

## 二、核心功能实现

### 1. Web辩论室
- 实时辩论界面，展示3Agent辩论过程
- 支持旁观者登录、发言、投票
- 辩论历史回放功能

### 2. 碰撞热力图
- 基于D3.js实现观点碰撞可视化
- 横轴：时间线，纵轴：观点强度
- 颜色深浅表示观点冲突程度
- 实时更新，支持缩放和拖拽

### 3. 旁观者提问
- 旁观者可通过WebSocket实时提问
- 提问经审核后插入辩论流程
- 支持点赞、踩、回复

## 三、实施步骤

### 第一阶段：基础建设（1-2周）
1. 搭建WebSocket服务器，连接现有辩论引擎
2. 实现辩论室基础UI框架
3. 集成飞书用户认证

### 第二阶段：核心功能（2-3周）
1. 实现实时辩论展示组件
2. 开发碰撞热力图算法和可视化
3. 实现旁观者提问功能

### 第三阶段：优化集成（1-2周）
1. 连接2601块知识库，提供辩论参考
2. 性能优化和压力测试
3. 飞书Webhook集成，推送辩论动态

## 四、关键设计

- **状态管理**: Redis维护辩论状态，支持断线重连
- **热力图算法**: 基于观点向量余弦相似度计算碰撞强度
- **提问队列**: 采用优先级队列，保证辩论流畅性

## Phase 1: 技术调研 (Agent R1)
好的，作为技术调研专家，我将基于您提供的任务书，对推荐的“前端框架+图表库+部署方案”进行深度分析和优化建议，并输出一份专业的Markdown文档。

---

## Web辩论室技术栈深度调研与优化建议

### 一、 核心结论与总体评价

您推荐的技术栈（React + D3.js + WebSocket + Node.js + Redis）是构建此类实时、高交互性Web应用的**黄金标准组合**。它成熟、生态丰富、社区支持强大，能够完美覆盖“实时辩论展示”、“复杂数据可视化（热力图）”和“高并发状态管理”三大核心需求。

本报告将在此基础上，提供更细化的选型建议、潜在风险提示及优化方案，以确保项目的成功实施。

### 二、 前端框架：React

**1. 为何选择React？**
-   **组件化与状态管理**：辩论室UI（聊天框、热力图、用户列表、提问面板）可以拆分为独立的、可复用的React组件。结合`useState`、`useReducer`或更强大的状态管理库（如Zustand、Redux Toolkit），可以轻松管理复杂的辩论状态（当前发言人、观点列表、投票数等）。
-   **虚拟DOM与性能**：辩论过程中，观点列表和热力图会高频更新。React的虚拟DOM机制能最小化实际DOM操作，保证UI的流畅性。
-   **丰富的生态系统**：有大量成熟的UI组件库（Ant Design、Material-UI）和工具库，可加速开发。

**2. 优化与补充建议：**
-   **状态管理库**：推荐使用 **[Zustand](https://github.com/pmndrs/zustand)**。它比Redux更轻量、API更简洁，非常适合管理WebSocket驱动的实时状态。对于更复杂的场景，可以考虑`Redux Toolkit`。
-   **构建工具**：使用 **[Vite](https://vitejs.dev/)** 替代Create React App。Vite的开发服务器启动速度极快，热更新（HMR）几乎是即时的，能显著提升开发体验。
-   **UI组件库**：推荐 **[Ant Design](https://ant.design/)** 或 **[shadcn/ui](https://ui.shadcn.com/)**。Ant Design功能全面，开箱即用；shadcn/ui更现代、高度可定制，且不引入额外的CSS框架。

### 三、 图表库：D3.js 与 备选方案

**1. 为何选择D3.js？**
-   **极致灵活性**：D3.js直接操作DOM和SVG，允许你创建任何你能想象到的、高度定制的可视化效果。对于“碰撞热力图”这种需要精确控制坐标轴、颜色映射、动画和交互（缩放、拖拽）的图表，D3.js是理想选择。
-   **强大的数据处理能力**：D3.js内置了强大的数据绑定、比例尺、布局和地理映射功能，能轻松将“观点向量余弦相似度”这类数据映射为视觉元素。

**2. 潜在挑战与优化建议：**
-   **学习曲线陡峭**：D3.js的API相对底层，开发效率可能不如高级图表库。
-   **与React的集成**：直接操作DOM与React的声明式渲染理念存在冲突。需要谨慎管理D3的DOM操作，避免React的Re-render破坏D3的更新。
-   **推荐方案：使用React封装库**
    -   **首选：`@nivo/core` + `@nivo/heatmap`**：[Nivo](https://nivo.rocks/) 是一套基于D3.js构建的、专为React设计的图表库。它提供了声明式的React组件，让你无需直接操作D3的DOM，同时保留了D3的灵活性和强大功能。`@nivo/heatmap` 组件可以快速实现一个功能完备的热力图。
    -   **备选：`recharts`**：如果热力图需求相对标准（如矩形块、颜色渐变），[Recharts](https://recharts.org/) 是一个更易上手、API更简洁的React图表库。它基于D3.js，但封装程度更高。
    -   **保底方案：`react-d3-library`**：如果需要完全自定义，可以使用这个库将D3代码封装成React组件，但需要开发者具备较强的D3和React集成能力。

**结论**：**强烈建议优先评估 `@nivo/heatmap`**。它能在不牺牲太多灵活性的前提下，大幅提升开发效率和代码可维护性。只有在Nivo无法满足特定、复杂的交互需求时，再考虑直接使用D3.js。

### 四、 部署方案：从开发到生产

**1. 推荐架构：**
-   **前端**：静态文件（HTML, CSS, JS），部署到CDN或对象存储。
-   **后端**：Node.js应用，部署到云服务器或容器平台。
-   **数据库**：Redis，可托管或自建。

**2. 具体部署方案对比：**

| 方案 | 适用场景 | 优点 | 缺点 |
| :--- | :--- | :--- | :--- |
| **Vercel / Netlify** | 前端静态站点 | 免费额度高、部署简单（Git集成）、自动HTTPS、全球CDN | 不适合后端应用 |
| **云服务器（ECS/EC2）** | 全栈应用，需要完全控制 | 高度可定制、可运行任何软件 | 需要运维能力、成本较高 |
| **容器平台（K8s / Docker）** | 微服务架构、高可用、自动扩缩容 | 环境一致、易于扩展、管理方便 | 学习曲线陡峭、运维复杂 |
| **Serverless (AWS Lambda / 阿里云函数计算)** | 后端逻辑简单、事件驱动 | 无需管理服务器、按需付费、自动扩缩容 | 冷启动延迟、不适合长连接（WebSocket） |

**3. 推荐方案：**
-   **前端**：**Vercel** (如果项目开源或团队熟悉) 或 **阿里云OSS/CDN** (国内部署)。将React构建产物（`dist` 或 `build` 文件夹）部署上去。
-   **后端**：**Docker + 云服务器**。将Node.js应用打包成Docker镜像，部署到一台云服务器上。使用`pm2`或`docker-compose`进行进程管理。配置Nginx反向代理，处理WebSocket升级请求和静态文件服务（可选）。
-   **Redis**：使用云服务商提供的托管Redis服务（如阿里云Redis、AWS ElastiCache），省去自建和运维的麻烦。

**4. 关键部署配置：**
-   **WebSocket**：确保反向代理（如Nginx）正确配置了`Upgrade`和`Connection`头，以支持WebSocket连接。
-   **SSL证书**：为域名配置HTTPS，

## Phase 1: UX分析 (Agent R2)
好的，作为UX分析专家，我将基于您提供的“Web辩论室方案”任务书，并结合“多Agent辩论界面”的通用最佳实践，为您提供一份详细的UX分析与设计建议。

这份分析将围绕**布局、配色、交互、沉浸感**四个核心维度展开，并针对您提到的“3个哲学家角色视觉区分”和“辩论以卡片形式逐轮展示”等关键点进行深入剖析。

---

### **UX分析与设计建议：多Agent辩论室**

#### **一、 布局 (Layout)**

**核心目标：** 清晰展示多线程辩论进程，平衡信息密度与可读性，引导用户视线流动。

**最佳实践与建议：**

1.  **主辩论区 (核心焦点)：**
    *   **布局：** 采用**三栏式或中心聚焦式**布局。
        *   **三栏式：** 左侧、中间、右侧分别对应Agent A、B、C的发言流。优点是对比清晰，缺点是横向空间占用大，不适合长文本。
        *   **中心聚焦式 (推荐)：** 将辩论过程放在屏幕中央，以**时间线**或**轮次卡片**的形式垂直排列。每个轮次内，三个Agent的发言卡片水平并排或呈“品”字形排列。这种布局更符合阅读习惯，且能有效利用纵向空间。
    *   **元素：**
        *   **轮次指示器：** 在辩论流顶部或侧边，清晰显示当前是第几轮辩论。
        *   **发言卡片：** 每个Agent的发言使用独立的、视觉上可区分的卡片。卡片内包含：Agent头像/标识、发言文本、时间戳、观点强度指示器（可选）。
        *   **当前发言高亮：** 正在发言的Agent卡片应有明显的动效或高亮边框，引导用户视线。

2.  **辅助功能区：**
    *   **碰撞热力图 (右上/右下)：** 作为实时分析工具，建议放置在辩论主区的**右侧或右下角**，不干扰主要阅读流。可折叠或缩放。
    *   **旁观者互动区 (右侧/底部)：**
        *   **提问区：** 固定在页面底部或右侧面板，方便旁观者随时输入。
        *   **实时聊天/评论流：** 显示点赞、回复等互动信息，可置于提问区上方或作为独立侧边栏。
    *   **控制与信息面板 (顶部/左侧)：**
        *   **顶部导航栏：** 辩论主题、状态（进行中/暂停/结束）、计时器、用户信息、设置入口。
        *   **左侧边栏 (可选)：** 辩论参与者列表、历史回放控制、知识库入口。

**布局原则：**
*   **F型或Z型浏览模式：** 将最重要的元素（当前辩论轮次、核心观点）放在用户视线最先触及的左上到中间区域。
*   **信息层级：** 主辩论区 > 碰撞热力图 > 旁观者互动区 > 控制面板。
*   **一致性：** 所有页面和组件的布局逻辑保持一致，降低学习成本。

#### **二、 配色 (Color)**

**核心目标：** 快速区分三个Agent，传递情绪和观点强度，营造专注的辩论氛围。

**最佳实践与建议：**

1.  **Agent角色配色 (核心区分)：**
    *   **原则：** 使用**高对比度、色相差异大**的颜色，确保色盲用户也能区分（如使用纹理或图标辅助）。
    *   **推荐方案：**
        *   **Agent A (正方/理性)：** **蓝色系** (如 `#007BFF` 或 `#4A90E2`)。蓝色代表理性、逻辑、冷静。
        *   **Agent B (反方/批判)：** **红色系** (如 `#DC3545` 或 `#E74C3C`)。红色代表批判、激情、对立。
        *   **Agent C (中立/综合)：** **绿色系** (如 `#28A745` 或 `#2ECC71`)。绿色代表平衡、中立、生长。
    *   **应用：** 将颜色应用于Agent的头像边框、发言卡片的**左侧色条**、名字标签、观点强度指示器等。

2.  **碰撞热力图配色：**
    *   **原则：** 使用**单色渐变或双色渐变**，直观表达冲突强度。
    *   **推荐方案：**
        *   **从冷到暖：** 低冲突用蓝色/绿色，高冲突用黄色/红色。例如：`#1A237E` (低) -> `#FFC107` (中) -> `#D32F2F` (高)。
        *   **背景：** 使用深色背景（如 `#1E1E1E`）或半透明背景，让热力图数据点更突出。

3.  **整体界面配色：**
    *   **背景：** 使用**深色模式** (Dark Mode) 为主，如 `#121212` 或 `#1A1A2E`。深色背景能减少视觉疲劳，突出色彩鲜明的Agent卡片和热力图，营造沉浸感。
    *   **文本：** 主要文本使用高对比度的白色或浅灰色 (`#E0E0E0`)，辅助文本使用中灰色 (`#9E9E9E`)。
    *   **强调色：** 使用一种中性色（如金色 `#FFD700` 或紫色 `#9C27B0`）用于高亮当前发言、按钮、链接等交互元素。

**配色原则：**
*   **功能性优先：** 颜色首要服务于信息传达（区分角色、表达强度），而非单纯装饰。
*   **可访问性：** 确保文本与背景的对比度符合WCAG AA标准。
*   **一致性：** 整个界面遵循统一的色彩系统。

#### **三、 交互 (Interaction)**

**核心目标：** 流畅、直观、可控，支持实时观察、深度参与和历史回溯。

**最佳实践与建议：**

1.  **核心辩论交互：**
    *   **实时滚动与暂停：** 辩论自动滚动，但用户可随时**暂停**以仔细阅读当前轮次。暂停时，新内容在后台继续生成，并显示“有N条新消息”的提示。
    *   **卡片交互：**
        *   **点击卡片：** 展开显示完整发言内容（如果卡片默认有截断）。
        *   **悬停卡片：** 显示“观点来源”、“相关论据”或“知识库引用”的浮窗。
        *   **拖拽卡片：** (高级功能) 允许用户拖拽一个Agent的论点卡片到另一个Agent的论点卡上，手动触发“观点碰撞”分析。
    *   **轮次导航：** 提供“上一轮”、“下一

## Phase 1.5: 项目骨架
好的，作为项目骨架设计师，我将基于您提供的“Web辩论室”技术栈（React + D3.js + WebSocket + Node.js + Redis）生成一套完整的项目文件结构、依赖清单以及核心文件说明。

---

## 项目名称：`debate-arena`

### 一、 目录树结构

```
debate-arena/
├── client/                      # 前端 (React + Vite)
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/                 # API 请求封装
│   │   │   └── index.ts
│   │   ├── components/          # 通用组件
│   │   │   ├── ChatBox/         # 聊天框组件
│   │   │   │   ├── index.tsx
│   │   │   │   └── styles.css
│   │   │   ├── Heatmap/         # 热力图组件 (D3.js)
│   │   │   │   ├── index.tsx
│   │   │   │   ├── D3Heatmap.ts # D3 核心逻辑
│   │   │   │   └── styles.css
│   │   │   ├── UserList/        # 用户列表
│   │   │   │   ├── index.tsx
│   │   │   │   └── styles.css
│   │   │   └── ...
│   │   ├── hooks/               # 自定义 Hooks
│   │   │   ├── useWebSocket.ts  # WebSocket 连接管理
│   │   │   └── useDebateState.ts # 辩论状态管理
│   │   ├── store/               # 状态管理 (Zustand)
│   │   │   └── debateStore.ts
│   │   ├── types/               # TypeScript 类型定义
│   │   │   └── index.ts
│   │   ├── utils/               # 工具函数
│   │   │   └── helpers.ts
│   │   ├── App.tsx              # 根组件
│   │   ├── main.tsx             # 入口文件
│   │   └── index.css            # 全局样式
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── server/                      # 后端 (Node.js + Express + WebSocket)
│   ├── src/
│   │   ├── config/              # 配置文件
│   │   │   └── index.ts
│   │   ├── controllers/         # 控制器 (处理业务逻辑)
│   │   │   └── debateController.ts
│   │   ├── middleware/          # 中间件
│   │   │   └── auth.ts
│   │   ├── models/              # 数据模型 (Mongoose)
│   │   │   └── Debate.ts
│   │   ├── routes/              # 路由定义
│   │   │   └── api.ts
│   │   ├── services/            # 服务层 (业务逻辑)
│   │   │   ├── debateService.ts
│   │   │   └── redisService.ts  # Redis 服务
│   │   ├── socket/              # WebSocket 处理
│   │   │   ├── index.ts         # WebSocket 服务器初始化
│   │   │   └── handlers/        # 消息处理器
│   │   │       ├── debateHandler.ts
│   │   │       └── userHandler.ts
│   │   ├── utils/               # 工具函数
│   │   │   └── helpers.ts
│   │   ├── app.ts               # Express 应用
│   │   └── server.ts            # 服务器入口
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml           # Docker 编排 (可选)
├── .gitignore
└── README.md
```

### 二、 核心依赖清单

#### 1. 前端 (`client/package.json`)

```json
{
  "name": "debate-arena-client",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.5.0",                // 状态管理
    "d3": "^7.9.0",                    // 核心 D3 库
    "@nivo/core": "^0.85.0",           // Nivo 核心 (用于热力图)
    "@nivo/heatmap": "^0.85.0",        // Nivo 热力图组件 (推荐)
    "axios": "^1.7.0",                 // HTTP 请求
    "socket.io-client": "^4.7.0",      // WebSocket 客户端
    "antd": "^5.15.0",                 // UI 组件库
    "dayjs": "^1.11.10"               // 日期处理
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/d3": "^7.4.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0"
  }
}
```

#### 2. 后端 (`server/package.json`)

```json
{
  "name": "debate-arena-server",
  "version": "1.0.0",
  "description": "Web Debate Backend",
  "main": "dist/server.js",
  "scripts": {
    "dev": "ts-node-dev --respawn --transpile-only src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "socket.io": "^4.7.0",
    "redis": "^4.6.0",                 // Redis 客户端
    "mongoose": "^8.2.0",              // MongoDB ODM (可选)
    "cors": "^2.8.5",
    "dotenv": "^16.4.0",
    "uuid": "^9.

## Phase 2: 最终实施方案
好的，项目审核师。我已仔细审阅原始方案。

方案整体结构清晰，技术选型合理。但在集成性、接口设计和复杂度方面存在一些可优化点。以下是补充建议：

1.  **【集成性】增加飞书集成模块**：方案提到“与飞书集成”，但未设计如何集成。需要明确飞书登录后的身份同步、知识库引用方式。建议增加 `feishu-integration` 模块，包含飞书API调用封装、身份验证中间件、知识库数据获取与缓存逻辑。

2.  **【接口设计】明确WebSocket消息协议**：方案提到WebSocket，但未定义消息格式。缺乏统一协议会导致前后端对接混乱。建议定义标准的JSON消息结构，包括 `type`（如 `debate_message`, `user_join`, `heatmap_update`）、`payload`、`timestamp` 等字段，并在文档中列出所有消息类型。

3.  **【可行性】补充后端服务启动与配置**：方案未提及后端服务的启动入口、依赖管理、环境变量配置（如飞书App ID/Secret、Redis连接地址）。建议补充 `server/` 目录结构，包括 `index.js`（入口）、`config/`（配置文件）、`middleware/`（认证中间件）、`services/`（业务逻辑，如辩论引擎调用）、`ws/`（WebSocket处理）。

4.  **【复杂度】简化Socket.IO引入**：方案将Socket.IO列为“可选”，但原生WebSocket + Socket.IO并存会增加维护复杂度和学习成本。建议直接采用Socket.IO作为唯一实时通信方案，利用其自动重连、房间管理和事件广播能力，简化代码。

5.  **【接口设计】增加前端API层定义**：前端 `api/index.ts` 仅为空壳，未定义具体接口。建议预先定义所有HTTP接口，如 `POST /api/debate/start`（启动辩论）、`GET /api/debate/:id/status`（获取辩论状态）、`POST /api/spectator/question`（旁观者提问）。这有助于前后端并行开发。

---

### 最终版实施方案

# Web辩论室 - 完整实施方案（审核修订版）

## 1. 项目总览

本方案旨在将现有的3Agent辩论引擎v3与飞书集成，构建一个具备实时辩论展示、观点碰撞可视化、旁观者互动功能的Web辩论室。项目采用前后端分离架构，强调实时性、可扩展性和用户体验。

## 2. 技术栈详细说明

| 层级 | 技术 | 版本建议 | 用途 |
| :--- | :--- | :--- | :--- |
| **前端框架** | React | ^18.x | 构建UI组件，管理视图层 |
| **构建工具** | Vite | ^5.x | 提供极速开发体验和高效构建 |
| **状态管理** | Zustand | ^4.x | 管理WebSocket驱动的实时辩论状态 |
| **UI组件库** | Ant Design | ^5.x | 提供高质量UI组件（按钮、卡片、输入框等） |
| **图表库** | D3.js | ^7.x | 实现高度定制的碰撞热力图 |
| **实时通信** | Socket.IO | ^4.x | 前后端双向实时数据传输，提供自动重连和房间管理 |
| **后端框架** | Node.js + Express | ^20.x LTS / ^4.x | 提供HTTP API和WebSocket服务 |
| **状态/缓存** | Redis | ^7.x | 维护辩论状态、会话管理、消息队列 |
| **数据层** | 飞书API | - | 用户认证、获取知识库数据 |

## 3. 项目文件结构

```
debate-arena/
├── client/                          # 前端项目
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/                     # HTTP API 调用封装
│   │   │   └── index.ts             # 定义所有HTTP接口：startDebate, getDebateStatus, postQuestion等
│   │   ├── components/              # 通用业务组件
│   │   │   ├── DebateCard/          # 单条辩论发言卡片
│   │   │   ├── DebateStream/        # 辩论流容器
│   │   │   ├── Heatmap/             # 碰撞热力图组件
│   │   │   │   ├── index.tsx        # React 封装
│   │   │   │   └── d3Heatmap.ts     # D3.js 核心逻辑
│   │   │   ├── SpectatorPanel/      # 旁观者面板（提问、互动）
│   │   │   └── UserList/            # 在线用户列表
│   │   ├── hooks/                   # 自定义 Hooks
│   │   │   ├── useSocket.ts         # Socket.IO 连接管理，监听/发送事件
│   │   │   └── useDebateStore.ts    # 绑定 Zustand store 的 hook
│   │   ├── store/                   # 状态管理 (Zustand)
│   │   │   └── debateStore.ts       # 辩论全局状态
│   │   ├── types/                   # TypeScript 类型定义
│   │   │   └── index.ts             # 定义 DebateMessage, Agent, User, SocketMessage等类型
│   │   ├── pages/                   # 页面级组件
│   │   │   ├── DebateRoom.tsx       # 辩论室主页面
│   │   │   └── Login.tsx            # 飞书登录页面
│   │   ├── App.tsx                  # 根组件，路由配置
│   │   └── main.tsx                 # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── server/                          # 后端项目
│   ├── config/                      # 配置文件
│   │   └── index.js                 # 环境变量：飞书AppID/Secret, Redis地址, 端口等
│   ├── middleware/                   # 中间件
│   │   └── auth.js                  # 飞书身份验证中间件
│   ├── services/                    # 业务逻辑层
│   │   ├── debateEngine.js          # 调用3Agent辩论引擎
│   │   ├── feishuService.js         # 飞书API封装（登录、知识库查询）
│   │   └── redisService.js          # Redis操作封装
│   ├── ws/                          # WebSocket处理
│   │   └── socketHandler.js         # Socket.IO事件处理（连接、辩论消息、热力图更新）
│   ├── routes/                      # HTTP路由
│   │   ├── debate.js                # POST /api/debate/start, GET /api/debate/:id/status
│   │   ├── auth.js                  # POST /api/auth/feishu (飞书登录回调)
│   │   └── spectator.js             # POST /api/spectator/question
│   ├── index.js                     # 服务入口，启动Express和Socket.IO
│   └── package.json
├── .env.example                     # 环境变量模板
└── README.md
```

## 4. 核心接口与协议定义

### 4.1 HTTP API

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| POST | /api/auth/feishu | 飞书登录回调，返回JWT token |
| POST | /api/debate/start | 启动辩论，返回辩论ID |
| GET | /api/debate/:id/status | 获取辩论当前状态 |
| POST | /api/spectator/question | 旁观者提问 |

### 4.2 WebSocket消息协议

所有消息采用JSON格式，包含以下字段：

```json
{
  "type": "string",        // 消息类型
  "payload": {},           // 消息数据
  "timestamp": 1234567890  // Unix时间戳
}
```

**消息类型定义：**

| type | 方向 | payload说明 |
| :--- | :--- | :--- |
| `debate_message` | 服务端→客户端 | `{ agentId, content, round }` |
| `heatmap_update` | 服务端→客户端 | `{ matrix: [[score, ...], ...] }` |
| `user_join` | 客户端→服务端 | `{ userId, userName }` |
| `user_leave` | 客户端→服务端 | `{ userId }` |
| `spectator_question` | 客户端→服务端 | `{ questionText }` |
| `error` | 双向 | `{ code, message }` |

## 5. 核心功能模块

### 5.1 辩论实时展示
- 通过Socket.IO接收`debate_message`事件，更新Zustand store中的辩论流。
- 使用`DebateStream`组件按时间顺序
