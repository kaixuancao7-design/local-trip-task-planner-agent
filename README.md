# Local Task Planner Agent

智能活动规划代理系统，采用"感知-决策-执行-记忆"四层闭环架构，结合多Agent协作模式。

## 🌟 功能特性

- **智能规划**：用户只需输入自然语言指令，系统自动解析并生成完整行程
- **个性化体验**：通过Chroma向量数据库记忆用户历史偏好，形成个性化推荐
- **地图集成**：集成高德地图API，实现地图展示、路线规划、POI搜索
- **天气查询**：接入心知天气API，获取实时天气和天气预报
- **隐私保护**：所有数据处理在本地完成，敏感信息仅存储在本地数据库
- **流式输出**：采用SSE技术实现打字机效果，实时展示Agent思考过程

## 🛠️ 技术栈

| 模块 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Vue.js 3.0 + Element Plus | 负责地图交互和行程卡片展示 |
| 后端 | Python 3.10 + FastAPI | 高性能异步框架 |
| 大模型 | Qwen3.5-9B (via Ollama) | 本地运行，负责逻辑推理和文本生成 |
| 向量库 | ChromaDB (Persistent Mode) | 存储用户偏好向量 |
| 应用框架 | LangChain | 编排Agent逻辑 |
| 地图服务 | 高德地图API | 地图展示、地理编码、路线规划 |
| 天气服务 | 心知天气API | 实时天气和天气预报 |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端交互层 (Vue.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   地图展示    │  │   行程卡片    │  │   对话交互    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端服务层 (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   API网关    │  │   任务分发    │  │   状态管理    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │ 内部调用
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   智能决策层 (LangChain)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   感知模块    │  │   规划模块    │  │   反思模块    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │ 向量查询
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据记忆层 (ChromaDB)                    │
│              ┌──────────────────────────┐                 │
│              │   用户偏好向量存储        │                 │
│              └──────────────────────────┘                 │
└───────────────────────┬─────────────────────────────────────┘
                        │ 工具调用
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      工具执行层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   地图工具    │  │   天气工具    │  │   预订工具    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 📂 项目结构

```
local-task-planner-agent/
├── app.py                    # FastAPI 启动入口
├── api/                      # API层
│   └── v1/
│       ├── endpoints/        # API端点定义
│       │   ├── plan.py       # 行程规划端点
│       │   ├── tools.py      # 工具模块端点
│       │   └── preferences.py # 用户偏好端点
│       └── router.py         # 路由注册
├── config/                   # 配置层
│   ├── settings.py           # 配置管理
│   └── logging_config.py     # 日志配置
├── core/                     # 核心业务层
│   ├── planner.py            # 规划Agent
│   ├── parser.py             # 输入解析器
│   └── executor.py           # 执行Agent
├── data/                     # 数据访问层
│   └── memory_manager.py     # ChromaDB封装
├── tools/                    # 工具层
│   ├── map_tool.py           # 高德地图工具
│   └── weather_tool.py       # 心知天气工具
├── models/                   # 模型层
│   ├── domain.py             # 领域模型
│   └── schemas.py            # API Schema
├── frontend/                 # Vue.js 前端
│   ├── src/
│   │   ├── components/       # Vue组件
│   │   ├── api/              # API调用封装
│   │   ├── App.vue           # 主应用组件
│   │   └── main.js           # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── tests/                    # 测试模块
│   ├── test_api_config.py    # API配置测试
│   └── test_api_endpoints.py # API端点测试
├── logs/                     # 日志目录
├── requirements.txt          # Python依赖
├── .env.example             # 环境变量示例
└── .gitignore               # Git忽略配置
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend && npm install
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env` 并配置：

```env
# 高德地图API密钥
MAP_API_KEY=your_amap_api_key

# 心知天气API密钥
WEATHER_API_KEY=your_seniverse_api_key
```

### 3. 启动服务

```bash
# 启动后端服务 (端口: 8000)
python app.py

# 启动前端服务 (端口: 3000)
cd frontend && npm run dev
```

### 4. 访问应用

- **前端页面**：http://localhost:3000
- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/

## 🔌 API接口

### 工具模块

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/tools/weather` | GET | 获取实时天气 |
| `/api/v1/tools/forecast` | GET | 获取天气预报 |
| `/api/v1/tools/geocode` | GET | 地理编码 |
| `/api/v1/tools/route` | GET | 路线查询 |
| `/api/v1/tools/search` | GET | 地点搜索 |
| `/api/v1/tools/location` | GET | 获取用户位置 |
| `/api/v1/tools/map/config` | GET | 获取地图配置 |

### 示例请求

```bash
# 获取天气
curl "http://localhost:8000/api/v1/tools/weather?city=南京"

# 获取路线
curl "http://localhost:8000/api/v1/tools/route?origin=南京站&destination=紫金山"
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行配置测试
python tests/test_api_config.py

# 运行端点测试
python tests/test_api_endpoints.py
```

## 📝 日志

日志文件位于 `logs/app.log`，包含：
- 应用启动信息
- API请求记录
- 错误日志
- 调试信息

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和PR！
