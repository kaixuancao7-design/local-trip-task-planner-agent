# Local Task Planner Agent

智能活动规划代理系统，采用"前后端分离 + 本地智能核心"架构。

## 技术栈

- **前端**：Vue.js 3.0 + Element Plus
- **后端**：Python 3.10 + FastAPI
- **大模型**：Qwen2.5-7B (via Ollama)
- **向量库**：ChromaDB (Persistent Mode)
- **应用框架**：LangChain

## 系统架构

1. **前端交互层**：负责可视化展示、地图交互、用户指令输入
2. **后端服务层**：API网关，负责任务分发、状态管理
3. **智能决策层**：系统的"大脑"，包含感知、规划、反思模块
4. **数据记忆层**：存储用户偏好和活动信息
5. **工具执行层**：地图API、天气API、模拟预订接口

## 核心功能

1. **感知阶段**：解析用户自然语言输入，提取关键实体
2. **记忆检索**：在ChromaDB中检索用户历史偏好
3. **规划与决策**：生成详细的活动计划
4. **展示与确认**：在前端展示计划，用户确认后执行
5. **执行与反馈**：执行预订动作，生成行程单

## 快速开始

1. **安装依赖**：
   - 后端：`pip install -r requirements.txt`
   - 前端：`cd frontend && npm install`

2. **启动服务**：
   - 后端：`python app.py`
   - 前端：`cd frontend && npm run dev`

3. **访问应用**：
   - 前端：http://localhost:3000
   - API文档：http://localhost:8000/docs

## 目录结构

```
local-task-planner-agent/
├── app.py                # FastAPI 启动入口
├── agent_core/           # 核心Agent逻辑
│   ├── planner.py        # 规划Agent
│   ├── memory.py         # Chroma 读写封装
│   └── tools.py          # 地图/天气工具函数
├── models/               # 数据模型 (Pydantic)
│   └── schemas.py
├── frontend/             # Vue.js 项目目录
│   ├── src/              # 前端源代码
│   ├── package.json      # 前端依赖
│   └── vite.config.js    # Vite配置
├── chroma_db/            # Chroma 本地数据持久化文件夹
└── requirements.txt      # Python依赖
```