萌宠智伴

基于虚拟宠物养成与 AI 驱动的中小学生心理健康与行为管理平台

萌宠智伴将「虚拟宠物养成」游戏化机制引入校园教育场景，通过学生领养宠物、完成任务获取积分、与 AI 伙伴对话等互动方式，激发学习动力；同时为教师提供群体智能分析、异常预警与干预管理工具，帮助学校实现学生心理健康的早发现、早干预。

---

核心特性

- 虚拟宠物养成：学生领养专属宠物，通过完成任务、积分兑换喂养宠物，宠物等级反映学生综合表现
- AI 智能伙伴：基于大语言模型（DeepSeek）的年级自适应对话，提供 AI 通识课教学、出题测验、绘本生成、动画讲解
- 群体智能分析：基于 DeBERTa 情感分析模型与 MiroFish 群体模拟，构建学生角色网络、预测群体趋势
- 心理健康预警：自动识别异常行为学生（内向、注意力不集中等），支持教师记录干预过程并跟踪状态
- 三端协同：学生端、教师端、管理员端分别面向不同角色，覆盖教与学的完整闭环

---

技术栈

  层级      	技术                   	说明                             
  前端      	Vue 3 + TypeScript   	组合式 API，类型安全                   
  构建工具    	Vite 5               	快速热更新与打包                       
  UI 框架   	Element Plus         	企业级组件库                         
  状态管理    	Pinia                	轻量级状态管理                        
  图表库     	ECharts + vue-echarts	数据可视化                          
  HTTP 客户端	Axios                	统一请求拦截与 Token 注入               
  后端      	Python Flask         	轻量 Web 框架                      
  数据库     	MySQL 8.0            	关系型数据库（库名 teacher_psych_system）
  大语言模型   	DeepSeek API         	对话、出题、绘本生成、动画代码生成              
  AI 模型   	DeBERTa              	文本情感提取与分析                      
  AI 模型   	MiroFish             	群体行为模拟                         

---

目录结构

    萌宠智伴/
    ├── backend/                              # Flask 后端服务
    │   ├── app.py                            # 主应用（路由、接口实现）
    │   ├── llm_service.py                    # DeepSeek 大模型服务模块
    │   ├── config_local.py                   # 本地配置（API Key，不提交）
    │   └── __pycache__/
    │
    ├── 2026081247-萌宠智伴-前端代码/
    │   └── frontend/                         # Vue 3 前端项目
    │       ├── src/
    │       │   ├── api/                      # API 接口封装（auth/student/teacher/admin）
    │       │   ├── views/                    # 页面视图
    │       │   │   ├── auth/                 # 登录、注册
    │       │   │   ├── student/              # 学生端（8 个页面）
    │       │   │   ├── teacher/              # 教师端（9 个页面）
    │       │   │   └── admin/                # 管理员端（7 个页面）
    │       │   ├── stores/                   # Pinia 状态管理（app.ts / user.ts）
    │       │   ├── router/                   # Vue Router 路由配置
    │       │   ├── styles/                   # 全局样式
    │       │   └── utils/                    # 工具函数
    │       ├── public/                       # 静态资源
    │       ├── vite.config.ts                # Vite 配置
    │       └── package.json
    │
    ├── 2026081247-萌宠智伴-模型/              # AI 模型源码
    │   ├── DeBERTa-master/                   # DeBERTa 情感分析模型
    │   └── MiroFish-main(1)/                 # MiroFish 群体模拟框架
    │
    ├── 2026081247-萌宠智伴-数据库表/          # 数据库
    │   └── 2026081247-萌宠智伴-数据库表.sql   # 完整建表与初始数据（18 张表）
    │
    ├── 2026081247-萌宠智伴-前端素材/          # 图片素材
    │   ├── 宠物素材/  头像素材/  商品素材/
    │   ├── 图标素材/  当日情绪素材/
    │   └── 登陆注册界面素材/
    │
    ├── 2026081247-萌宠智伴-相关文档/          # 项目相关文档
    │
    ├── 后端接口清单分析报告.md                 # 接口清单（按页面维度分析）
    ├── 后端接口清单与数据结构分析报告.md        # 接口清单（按数据结构维度分析）
    │
    └── README.md                             # 本文件

---

功能模块

学生端

  页面    	路由                   	功能说明                 
  班级首页  	/student             	展示个人宠物、积分排名、班级宠物墙    
  我的宠物  	/student/my-pet      	宠物状态管理、积分商城购买食物、宠物商店 
  AI 学习 	/student/ai-learning 	AI 通识课学习、测验、绘本生成、动画讲解
  智能情感交流	/student/ai-companion	与 AI 宠物伙伴对话，支持年级自适应  
  成长日记  	/student/growth-diary	心情记录、目标管理、成就解锁、积分图表  
  当日任务  	/student/tasks       	查看并完成教师布置的日常/周任务     
  设置    	/student/settings    	修改个人信息与宠物信息          

教师端

  页面      	路由                       	功能说明                   
  工作台     	/teacher                 	数据概览、异常学生提醒、课表、班级概况    
  积分管理    	/teacher/points          	学生积分加减、积分规则、小组管理、学生评价  
  班级管理    	/teacher/classes         	班级增删改查、查看班级学生、导入班级     
  群体智能角色管理	/teacher/group-roles     	AI 特质分析、聊天活跃度、正向/负向情绪比率
  群体智能角色网络	/teacher/role-network    	可视化角色关系图谱、群体聚类         
  群体趋势预测  	/teacher/trend-prediction	基于模拟的群体行为趋势预测          
  干预管理    	/teacher/intervention    	异常学生记录、干预计划、跟踪状态       
  交流论坛    	/teacher/forum           	发帖、浏览、我的帖子、板块分类        

管理员端

  页面    	路由                  	功能说明                 
  数据看板  	/admin              	全校积分总览、班级排名、行为合规率    
  学生管理  	/admin/students     	学生 CRUD、按年级/班级/宠物等级筛选
  教师管理  	/admin/teachers     	教师 CRUD、按资历/教研组筛选    
  日常论坛管理	/admin/daily-forum  	帖子审核（通过/驳回）、置顶、公告发布  
  学科论坛管理	/admin/subject-forum	学科帖子审核与管理            
  积分概览  	/admin/points       	积分规则统计、班级积分对比、趋势图    

---

数据库设计

数据库名：teacher_psych_system，共 18 张表：

  表名                  	说明                         
  students            	学生信息（学号、密码 MD5、积分、心情指数、性格等）
  teachers            	教师信息（工号、密码明文、教研组、资历、所教班级）  
  classes             	班级信息（年级、班主任、总积分、心理状态）      
  pets                	宠物模板（类型、图片）                
  student_pets        	学生领养的宠物（经验值、等级、领养日期）       
  point_records       	积分变动记录（原因、分值、类型）           
  point_rules         	积分规则（加分/扣分项）               
  point_goods         	积分商城商品                     
  tasks               	教师布置的任务                    
  abnormal_students   	异常行为学生（类型、严重程度、状态）         
  intervention_records	干预记录                       
  evaluations         	教师对学生的评价                   
  study_groups        	学习小组                       
  group_members       	小组成员                       
  forums              	论坛板块                       
  posts               	论坛帖子（含审核状态、置顶）             
  replies             	帖子回复                       
  predictions         	群体趋势预测记录                   

---

快速开始

环境要求

- Node.js >= 18
- Python >= 3.9
- MySQL >= 8.0

1. 初始化数据库

    # 登录 MySQL，创建数据库
    mysql -u root -p
    CREATE DATABASE teacher_psych_system CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    
    # 导入建表与初始数据
    mysql -u root -p teacher_psych_system < 2026081247-萌宠智伴-数据库表/2026081247-萌宠智伴-数据库表.sql

2. 启动后端

    cd backend
    
    # 安装依赖
    pip install flask flask-cors pymysql requests
    
    # 配置 DeepSeek API Key（创建 config_local.py）
    echo 'DEEPSEEK_API_KEY = "your_api_key_here"' > config_local.py
    
    # 修改 app.py 中的数据库连接配置（host/user/password/port）
    # 默认配置: 127.0.0.1 / root / 092236 / 3306
    
    # 启动服务
    python app.py
    # 后端运行在 http://localhost:8000

3. 启动前端

    cd 2026081247-萌宠智伴-前端代码/frontend
    
    # 安装依赖
    npm install
    
    # 开发模式
    npm run dev
    # 前端运行在 http://localhost:5173
    
    # 生产构建
    npm run build

4. 访问系统

浏览器打开 http://localhost:5173，使用以下账号登录：

  角色  	用户名          	密码                     	说明          
  管理员 	admin        	admin / 092236 / 123456	均可登录        
  教师  	工号（如 T001）   	明文密码                   	见 teachers 表
  学生  	学号（如 2026001）	123456                 	数据库存储 MD5 值 

---

接口概览

后端提供 65+ 个 API 接口，统一前缀 /api，认证方式为 Authorization: Bearer {token}。

统一响应格式

    {
      "success": true,
      "data": {},
      "message": "操作成功"
    }

登录接口特殊：直接返回 { "token": "...", "user": {...} }，无外层包装。

接口分布

  模块  	接口数 	主要功能                   
  认证  	3   	登录、注册、获取当前用户           
  学生端 	18+ 	仪表盘、宠物、商城、AI 对话、任务、日记  
  教师端 	22+ 	仪表盘、积分、班级、角色网络、预测、干预、论坛
  管理员端	22+ 	仪表盘、学生/教师管理、论坛审核、积分概览  

详细的接口清单与数据结构请参阅：

- 后端接口清单分析报告.md
- 后端接口清单与数据结构分析报告.md

---

AI 能力

DeepSeek 大语言模型（llm_service.py）

  功能    	说明                          
  智能对话  	年级自适应（小学低/高年级、初中、高中），支持多轮上下文
  自动出题  	围绕知识点生成选择题，含答案与解析           
  测验批改  	自动评分，答对奖励积分                 
  绘本生成  	面向低龄学生，生成图文并茂的 SVG 绘本       
  动画讲解  	为抽象概念生成 SVG 动画演示            
  学习路径推荐	根据学习记录与测验成绩推荐下一步知识点         

DeBERTa 模型

用于学生文本（聊天记录、日记等）的情感提取与分析，为群体智能角色管理和异常预警提供数据支撑。

MiroFish 框架

群体行为模拟框架，用于构建学生角色网络、模拟群体互动、预测群体趋势。

---

前端对接状态

  模块  	对接状态	说明                                  
  认证  	已对接 	登录、注册已实际调用 API                      
  管理员端	部分对接	学生/教师管理、论坛审核已调用 API；数据看板、积分概览使用 Mock
  学生端 	待对接 	API 函数已定义，页面使用 Pinia Mock 数据        
  教师端 	待对接 	API 函数已定义，页面使用硬编码 Mock 数据           

---

开发说明

- 前端开发服务器默认端口 5173，后端默认端口 8000
- 前端通过 Vite 代理或直接请求 /api 前缀访问后端
- Token 存储在 localStorage 的 pet-education-storage 键中
- 学生密码统一为 123456（MD5 存储），教师密码为明文
- config_local.py 包含 API Key，不应提交到版本库

---

许可证

本项目为参赛作品，版权归原作者所有。
