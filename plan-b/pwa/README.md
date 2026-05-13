# Debate Arena PWA — Plan B 前端应用包

## 文件清单

```
pwa/
├── sw.js                      # 通用 Service Worker (Cache-First)
├── manifest-liquid-glass.json  # 液态玻璃主题 manifest
├── manifest-river-of-light.json # 长河光影主题 manifest
├── manifest-epistolary.json    # 思想书简主题 manifest
├── manifest-frost-white.json   # 霜白臻简主题 manifest
├── manifest-anime-vn.json      # 次元绘卷主题 manifest
├── pwa-liquid-glass.html       # 液态玻璃·臻境 PWA
├── pwa-river-of-light.html     # 长河·光影 PWA
├── pwa-epistolary.html         # 思想书简 PWA
├── pwa-frost-white.html        # 霜白·臻简 PWA
├── pwa-anime-vn.html           # 次元·绘卷 PWA
└── README.md                   # 本文件
```

## 主题一览

| 文件 | 主题 | 视觉风格 | 主题色 |
|------|------|----------|--------|
| `pwa-liquid-glass.html` | 液态玻璃·臻境 | Apple Liquid Glass 半透明卡片 | `#ffffff` |
| `pwa-river-of-light.html` | 长河·光影 | Tenebrism 明暗对照法，单光源戏剧性 | `#000000` |
| `pwa-epistolary.html` | 思想书简 | 聊天流 UI，三种哲学家气泡 | `#f5f0e8` |
| `pwa-frost-white.html` | 霜白·臻简 | 极简白色 Frosted Glass | `#fafafa` |
| `pwa-anime-vn.html` | 次元·绘卷 | 日式视觉小说，集中线/速度线 | `#ffd1dc` |

## 启动方式

### 1. 启动辩论后端

```bash
cd debate-arena/plan-b/backend
node server.js   # 默认监听 localhost:3001
```

### 2. 启动 PWA 前端

```bash
# 任意静态文件服务器，例如:
npx serve E:\debate-arena\plan-b\pwa -p 3000

# 或者 Python:
cd E:\debate-arena\plan-b\pwa
python -m http.server 3000
```

### 3. 访问

打开浏览器访问 `http://localhost:3000/pwa-liquid-glass.html` 等任一文件。

## API 接口

PWA 前端连接后端以下端点：

- **Socket.IO** `ws://localhost:3001` — 实时消息通道
  - `debate_message` — 接收辩论消息 `{ speaker, text, round, type }`
  - `heatmap_update` — 碰撞热力图更新 `{ collisions, dots }`
  - `debate_ended` — 辩论结束报告 `{ score, debate_count, collision_avg }`

- **REST** `POST /api/debate/start`
  - Body: `{ topic: string, agents: string[] }`
  - Response: `{ debate_id, messages[] }`

## 离线模式

所有 PWA 均包含：
- Service Worker 缓存 (Cache-First 策略)
- Web App Manifest (可安装到主屏幕)
- Apple 移动端全屏支持
- 无后端时的 Demo 演示模式

## 设计稿源文件

PWA 文件源自 `design-proposals/` 目录，保留全部原始设计语言：
- `proposal-p-liquid-glass.html` → `pwa-liquid-glass.html`
- `scheme-i-river-of-light.html` → `pwa-river-of-light.html`
- `方案L-思想书简.html` → `pwa-epistolary.html`
- `scheme-h-frost-white.html` → `pwa-frost-white.html`
- `proposal-q-anime-vn.html` → `pwa-anime-vn.html`

## 特色功能

- 🔮 **次元绘卷**: 壹贰叁章节水晶指示器（毛笔字体，CSS clip-path 菱形，颜色渐变+脉动动画）
- 🌊 **长河光影**: 恢复 Tenebrism 黑暗感（文字降暗，光晕减弱 ~10%）
- ✉️ **思想书简**: 手机端全屏聊天流（去手机框，自适应气泡宽度 85%/60%）
