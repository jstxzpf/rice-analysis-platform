### **江苏泰兴水稻长势智能分析平台 - 系统设计方案 (AI-Dev Ready v1.0)**

#### **0. 面向AI编程的指导原则**

本方案遵循以下原则，以最大化与AI编程工具的协同效率：

  * **明确的边界**: 清晰划分后端、前端、数据库和分析引擎的职责。
  * **契约式设计**: 通过Pydantic模型定义API的请求和响应“契约”，AI可以精确理解数据结构。
  * **组件化指令**: 将复杂功能拆解为具体的函数和类，并提供清晰的输入、输出和核心逻辑描述。
  * **标准化的项目结构**: 提供一个标准的项目目录结构，便于AI在正确的未知生成代码。
  * **逐步构建**: 方案按逻辑顺序组织，您可以从数据库模型开始，依次构建API、异步任务，直至前端界面。

#### **1. 系统概述与架构**

  * **项目名称**: 江苏泰兴水稻长势智能分析平台

  * **核心目标**: 构建一个B/S架构的网络平台，实现水稻长势图像的自动化分析、数据可视化和趋势追踪。

  * **系统架构**: 现代化、高内聚、低耦合的微服务思想架构。

    ```mermaid
    graph TD
        A[用户浏览器 - Vue.js] -->|HTTP/S API请求| B(Nginx - 反向代理/静态文件服务);
        B -->|uWSGI| C{后端: FastAPI};
        C -->|CRUD操作| D[数据库: PostgreSQL];
        C -->|提交分析任务| E[消息队列: Redis];
        F[任务处理器: Celery Worker] -->|获取任务| E;
        F -->|执行图像分析| G[图像分析引擎 - OpenCV/Scikit-image];
        G -->|读取/写入| H[对象存储/文件系统 - MinIO/S3/本地];
        F -->|写入结果| D;
        A -->|WebSocket实时更新| C;

        subgraph "服务器环境 (Docker Compose)"
            B; C; D; E; F; H;
        end
        subgraph "核心算法库"
            G
        end
    ```

#### **2. 技术栈选型**

| 类别 | 技术 | 备注 |
| :--- | :--- | :--- |
| **后端** | Python 3.10+, FastAPI | 高性能异步Web框架，自带API文档。 |
| **前端** | Vue 3 + Vite + TypeScript | 现代、高效的前端框架，提供类型安全。 |
| **UI库** | Element Plus | 丰富、高质量的Vue 3组件库。 |
| **图表库** | Apache ECharts | 功能强大的数据可视化库。 |
| **数据库** | PostgreSQL 15+ | 稳定、开源的关系型数据库。 |
| **ORM** | SQLAlchemy 2.0 (Async) | Python的数据库工具包，支持异步操作。 |
| **数据校验** | Pydantic V2 | 用于API数据接口的定义与校验。 |
| **异步任务** | Celery 5+ | 分布式任务队列。 |
| **消息中间件**| Redis | 作为Celery的Broker和Backend。 |
| **图像处理** | OpenCV-Python, Scikit-image, Pillow | 核心图像算法库。 |
| **部署** | Docker, Docker Compose, Nginx | 容器化部署，便于环境隔离与管理。 |

#### **3. 标准化项目结构**

```
/rice-analysis-platform
|-- /backend                  # FastAPI 后端项目
|   |-- /app
|   |   |-- /api
|   |   |   |-- /v1
|   |   |   |   |-- __init__.py
|   |   |   |   |-- endpoints.py      # 集合所有API路由
|   |   |-- /core
|   |   |   |   |-- __init__.py
|   |   |   |   |-- config.py         # 配置管理 (环境变量)
|   |   |   |   |-- security.py       # 密码哈希、JWT令牌
|   |   |-- /crud                 # 数据库增删改查操作
|   |   |   |   |-- __init__.py
|   |   |   |   |-- crud_user.py
|   |   |   |   |-- crud_field.py
|   |   |-- /db
|   |   |   |   |-- __init__.py
|   |   |   |   |-- base.py           # SQLAlchemy Base 和 session
|   |   |   |   |-- models.py         # 数据库模型 (ORM类)
|   |   |-- /schemas              # Pydantic 数据模型
|   |   |   |   |-- __init__.py
|   |   |   |   |-- user.py
|   |   |   |   |-- field.py
|   |   |   |   |-- photogroup.py
|   |   |   |   |-- analysis_result.py
|   |   |-- /analysis             # 图像分析引擎核心代码
|   |   |   |   |-- __init__.py
|   |   |   |   |-- main_processor.py # 分析任务主入口
|   |   |   |   |-- steps_preprocess.py
|   |   |   |   |-- steps_analyze.py
|   |   |-- /worker               # Celery Worker 相关
|   |   |   |   |-- __init__.py
|   |   |   |   |-- celery_app.py     # Celery实例配置
|   |   |   |   |-- tasks.py          # Celery异步任务定义
|   |   |-- __init__.py
|   |   |-- main.py               # FastAPI 应用主入口
|   |-- requirements.txt
|   |-- Dockerfile
|   |-- .env                    # 环境变量配置文件
|
|-- /frontend                 # Vue.js 前端项目
|   |-- /src
|   |   |-- /api                # API请求封装
|   |   |-- /assets             # 静态资源
|   |   |-- /components         # 可复用UI组件
|   |   |-- /router             # 路由配置
|   |   |-- /store              # 状态管理 (Pinia)
|   |   |-- /views              # 页面级组件
|   |-- package.json
|   |-- Dockerfile
|
|-- docker-compose.yml          # Docker编排文件
```

#### **4. 数据库模型设计 (SQLAlchemy ORM)**

**AI编程指令**: "请在 `backend/app/db/models.py` 文件中，使用SQLAlchemy 2.0语法，根据以下定义创建数据库模型类。"

<details>
<summary>点击展开 `models.py` 的详细定义</summary>

```python
# backend/app/db/models.py
from sqlalchemy import (Column, Integer, String, Float, DateTime, Date,
                        ForeignKey, Enum as SQLAlchemyEnum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base

class AnalysisStatusEnum(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    fields = relationship("Field", back_populates="owner")

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    area = Column(Float) # 面积（亩）
    rice_variety = Column(String(100))
    planting_date = Column(Date)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="fields")
    photo_groups = relationship("PhotoGroup", back_populates="field", cascade="all, delete-orphan")

class PhotoGroup(Base):
    __tablename__ = "photo_groups"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    capture_date = Column(Date, nullable=False)
    growth_stage = Column(String(50)) # 生育期
    drone_photo_path = Column(String(512), nullable=False)
    side_photo_05m_path = Column(String(512), nullable=False)
    side_photo_3m_path = Column(String(512), nullable=False)
    analysis_status = Column(SQLAlchemyEnum(AnalysisStatusEnum), default=AnalysisStatusEnum.PENDING)
    celery_task_id = Column(String(255), index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", back_populates="photo_groups")
    analysis_result = relationship("AnalysisResult", back_populates="photo_group", uselist=False, cascade="all, delete-orphan")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    photo_group_id = Column(Integer, ForeignKey("photo_groups.id"), unique=True, nullable=False)
    coverage = Column(Float) # 冠层覆盖度 (%)
    avg_plant_height = Column(Float) # 平均株高 (cm)
    height_std_dev = Column(Float) # 株高标准差，反映整齐度
    canopy_color_index = Column(Float) # 冠层颜色指标 (如G/R比)
    uniformity_index = Column(Float) # 均匀度指数 (如CV)
    tiller_density_estimate = Column(Float) # 分蘖密度估算 (株/m²)
    notes = Column(String(1000)) # 分析备注或异常
    analysis_time = Column(DateTime(timezone=True), server_default=func.now())

    photo_group = relationship("PhotoGroup", back_populates="analysis_result")

```

</details>

#### **5. API接口设计 (FastAPI & Pydantic)**

**AI编程指令**: "请在 `backend/app/schemas/` 目录下创建对应模块文件，定义以下Pydantic模型。然后在 `backend/app/api/v1/endpoints.py` 中，使用FastAPI的APIRouter，实现下列API端点，并使用依赖注入获取数据库会话。"

<details>
<summary>点击展开API端点详细定义</summary>

| 模块 | 端点 | 方法 | 描述 | 请求体/参数 | 成功响应 (200) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **用户认证** | `/api/v1/token` | `POST` | 用户登录，获取JWT令牌 | `OAuth2PasswordRequestForm` | `Token` (含 `access_token`) |
| | `/api/v1/users/me` | `GET` | 获取当前用户信息 | Header: `Authorization` | `User` (公共信息) |
| **田块管理** | `/api/v1/fields` | `POST` | 新增田块 | `FieldCreate` | `Field` |
| | `/api/v1/fields` | `GET` | 获取当前用户所有田块列表| Header: `Authorization` | `List[Field]` |
| | `/api/v1/fields/{id}` | `GET` | 获取单个田块详情 | Path: `id` | `Field` |
| | `/api/v1/fields/{id}` | `PUT` | 更新田块信息 | Path: `id`, Body: `FieldUpdate`| `Field` |
| | `/api/v1/fields/{id}` | `DELETE`| 删除田块 | Path: `id` | `{"message": "Field deleted"}` |
| **数据上传与分析** | `/api/v1/photogroups/upload` | `POST` | 上传一组三张照片 | Form-Data: `field_id`, `capture_date`, `growth_stage`, `drone_photo`, `side_photo_05m`, `side_photo_3m` | `PhotoGroup` (状态为PENDING)|
| | `/api/v1/photogroups/status/{task_id}` | `GET` | 查询分析任务状态 | Path: `celery_task_id` | `{"task_id": ..., "status": ...}` |
| **结果查看** | `/api/v1/fields/{field_id}/results`| `GET` | 获取某田块所有历史分析结果 | Path: `field_id` | `List[AnalysisResultWithPhotos]`|
| | `/api/v1/results/{result_id}` | `GET` | 获取单次分析的详细结果 | Path: `result_id` | `AnalysisResultWithPhotos` |
| | `/api/v1/fields/{field_id}/trends` | `GET` | 获取某田块关键指标趋势 | Path: `field_id`, Query: `indicator` (e.g., coverage) | `List[{"date": ..., "value": ...}]` |

</details>

#### **6. 图像分析引擎设计**

**AI编程指令**: "在 `backend/app/analysis/` 目录下创建相应文件，并实现以下函数。主入口函数 `process_photo_group` 将被Celery任务调用。"

**主处理流程 (`main_processor.py`)**

```python
# def process_photo_group(photo_group_id: int):
# 1. 从数据库中获取 PhotoGroup 实例及其路径。
# 2. 调用 `steps_preprocess.py` 中的函数进行预处理（如色彩校正、尺寸标准化）。
# 3. **并行或串行**调用 `steps_analyze.py` 中的各个分析函数：
#    - coverage = analyze_drone_view(drone_photo_path)
#    - height, height_std = analyze_side_view_height(side_photo_3m_path)
#    - ...
# 4. 汇总所有分析结果，创建一个 AnalysisResult 对象。
# 5. 将结果存入数据库，并更新 PhotoGroup 的状态为 COMPLETED。
# 6. 设计完善的try...except块，若失败则更新状态为 FAILED 并记录错误。
```

**核心分析函数 (`steps_analyze.py`)**

  * **`analyze_drone_view(image_path: str) -> dict`**:
      * **输入**: 无人机俯拍图路径。
      * **逻辑**:
        1.  图像读取。
        2.  转换为HSV或LAB色彩空间。
        3.  使用颜色阈值法或ExG（超绿指数）分割出植被区域，生成二值化掩码。
        4.  计算`覆盖度` = (植被像素数 / 总像素数) * 100。
        5.  在植被区域内，计算颜色均值，得到`冠层颜色指标`。
        6.  将图像划分为N x M网格，计算每个网格的覆盖度，再计算所有网格覆盖度的变异系数（CV），得到`均匀度指数`。
      * **输出**: `{"coverage": float, "canopy_color_index": float, "uniformity_index": float}`
  * **`analyze_side_view_height(image_path_3m: str, whiteboard_actual_height_m: float = 2.0) -> dict`**:
      * **输入**: 3米侧拍图路径，白板实际高度。
      * **逻辑**:
        1.  分割出白色背景板，确定其在图像中的像素高度 `pixel_height_board`。
        2.  计算`比例尺` (cm/pixel) = (whiteboard_actual_height_m * 100) / pixel_height_board。
        3.  分割出水稻植株轮廓。
        4.  遍历所有植株轮廓，找到每个轮廓的最高点，计算其像素高度。
        5.  将所有植株的像素高度转换为实际高度（cm）。
        6.  计算所有实际高度的`平均值 (avg_plant_height)`和`标准差 (height_std_dev)`。
      * **输出**: `{"avg_plant_height": float, "height_std_dev": float}`
  * **`estimate_tiller_density(image_path_05m: str, whiteboard_actual_width_m: float = 1.0) -> dict`**:
      * **输入**: 0.5米精细侧拍图路径，白板实际宽度。
      * **逻辑**: (这是一个研究性问题，初期可以简化)
        1.  类似株高测量，先获取比例尺。
        2.  在分割出的植株基部区域，使用形态学操作（腐蚀、骨架化）尝试分离独立的茎秆。
        3.  使用轮廓检测或霍夫变换等方法计数。
        4.  `密度` = 计数值 / whiteboard_actual_width_m。
      * **输出**: `{"tiller_density_estimate": float}`

#### **7. 异步任务处理 (Celery)**

**AI编程指令**: "在 `backend/app/worker/tasks.py` 中，使用Celery装饰器定义一个异步任务，该任务调用 `analysis.main_processor.process_photo_group` 函数。"

```python
# backend/app/worker/tasks.py
from .celery_app import celery_app
from app.analysis.main_processor import process_photo_group

 @celery_app.task(name="tasks.run_analysis")
def run_analysis(photo_group_id: int):
    """
    Celery task to run the full image analysis pipeline for a photo group.
    """
    # 这里是调用实际处理逻辑的地方
    process_photo_group(photo_group_id)
```

**触发逻辑**: 在 `/api/v1/photogroups/upload` 端点中，成功保存图片和`PhotoGroup`记录到数据库后，调用 `.delay()` 或 `.apply_async()` 来触发此任务。
`task = run_analysis.delay(new_photo_group.id)`
`new_photo_group.celery_task_id = task.id`
`db.commit()`

#### **8. 前端界面设计 (Vue.js)**

**AI编程指令**: "请使用Vue 3、Vite和Element Plus，创建以下页面和组件。状态管理使用Pinia，API请求使用Axios封装。"

  * **Views (页面)**:
      * `Login.vue`: 登录页。
      * `Dashboard.vue`: 主仪表盘，地图展示所有田块及其最新状态，关键指标总览。
      * `FieldManagement.vue`: 田块列表、新增、编辑、删除的CRUD操作界面。
      * `FieldDetail.vue`: 单个田块的详细信息页面，包含一个历史分析记录列表。
      * `AnalysisReport.vue`: 展示单次分析的详细报告，包括三张原始图、分析结果数据和可视化图表（如长势热力图）。
      * `TrendAnalysis.vue`: 某个田块关键指标（株高、覆盖度等）的时间序列折线图，支持多指标对比。
  * **Components (组件)**:
      * `PhotoUploader.vue`: 封装了三个图片上传框、田块选择、日期选择的组件，上传后能显示进度和任务状态。
      * `FieldMap.vue`: 在Dashboard中使用的地图组件（可使用高德/百度地图JS API）。
      * `IndicatorChart.vue`: 可复用的ECharts图表组件，接收数据和配置，渲染趋势图。

---

## 项目实施任务列表 (Development Task List)

### **Sprint 1: 环境搭建与用户核心**
- [ ] **环境搭建**:
  - [ ] 编写 `docker-compose.yml` 文件，定义 `db` (PostgreSQL) 和 `redis` 服务。
  - [ ] 验证 `docker-compose up` 可以成功启动数据库和Redis。
- [ ] **后端 - 核心框架与用户认证**:
  - [ ] 初始化FastAPI后端项目结构。
  - [ ] 在 `app/db/models.py` 中创建所有数据库模型 (User, Field, PhotoGroup, AnalysisResult)。
  - [ ] 实现用户认证API (`/token`, `/users/me`)，包括密码哈希和JWT令牌生成/验证逻辑。
- [ ] **前端 - 项目初始化与登录**:
  - [ ] 初始化Vue 3 + Vite + TS 前端项目。
  - [ ] 集成 Element Plus UI 库。
  - [ ] 创建登录页面 `Login.vue`。
  - [ ] 实现调用登录API、获取并存储Token的逻辑。
  - [ ] 创建基本的主应用布局（包含导航栏和内容区域）。

### **Sprint 2: 核心功能贯通 (MVP)**
- [ ] **后端 - 田块管理**:
  - [ ] 在 `endpoints.py` 中实现田块管理的全部CRUD API (`/fields/...`)。
  - [ ] 在 `crud_field.py` 中编写对应的数据库操作函数。
- [ ] **前端 - 田块管理**:
  - [ ] 创建 `FieldManagement.vue` 页面，用于展示田块列表。
  - [ ] 实现新增、编辑、删除田块的表单和对话框组件。
  - [ ] 对接后端的田块管理API。
- [ ] **后端 - 图像上传与任务触发**:
  - [ ] 实现 `/photogroups/upload` API，用于接收三张图片和元数据。
  - [ ] 实现文件存储逻辑（初期可存放在本地文件系统）。
  - [ ] 在 `tasks.py` 中定义 `run_analysis` Celery任务。
  - [ ] 在上传API成功后，调用 `run_analysis.delay()` 触发异步任务，并将 `task_id` 保存到数据库。
- [ ] **后端 - 核心图像分析**:
  - [ ] 在 `analysis/` 目录下，实现 `analyze_drone_view` (计算覆盖度) 和 `analyze_side_view_height` (计算株高) 的基本版本。
  - [ ] 实现主处理函数 `process_photo_group`，能够调用上述分析函数并将结果存入 `AnalysisResult` 表。
- [ ] **前端 - 结果展示**:
  - [ ] 创建 `FieldDetail.vue` 页面，展示某个田块的历史分析记录。
  - [ ] 创建 `AnalysisReport.vue` 页面，用于展示单次分析的详细结果（包括图片和数据）。
  - [ ] 对接后端的分析结果查询API。

### **Sprint 3: 可视化与体验优化**
- [ ] **前端 - 数据可视化**:
  - [ ] 创建 `Dashboard.vue` 页面。
  - [ ] 开发 `TrendAnalysis.vue` 页面，集成 ECharts 渲染关键指标的时间序列折线图。
  - [ ] 对接后端的趋势分析API (`/fields/{field_id}/trends`)。
- [ ] **前端 - 用户体验**:
  - [ ] 在上传组件中，实现任务状态的轮询或WebSocket更新，向用户实时反馈分析进度（PENDING -> PROCESSING -> COMPLETED）。
  - [ ] 对接任务状态查询API (`/photogroups/status/{task_id}`)。
- [ ] **后端 - 算法优化**:
  - [ ] 收集测试图片，对覆盖度和株高计算的准确性进行初步验证和参数调优。
  - [ ] 完善分析过程中的错误处理和日志记录。

### **Sprint 4: 高级功能与部署**
- [ ] **后端 - 高级分析**:
  - [ ] 实现 `uniformity_index` (均匀度指数) 的计算逻辑。
  - [ ] 尝试实现 `tiller_density_estimate` (分蘖密度估算) 的简化版本。
- [ ] **部署准备**:
  - [ ] 编写 `backend/Dockerfile` 和 `frontend/Dockerfile`。
  - [ ] 在 `docker-compose.yml` 中完善 `backend` 和 `frontend` 服务配置。
  - [ ] 添加 `nginx` 服务作为反向代理和前端静态文件服务器。
- [ ] **测试与部署**:
  - [ ] 在本地使用 `docker-compose` 完整构建并运行所有服务。
  - [ ] 执行端到端的功能测试（从登录、上传到查看报告）。
  - [ ] （可选）将项目部署到云服务器。
