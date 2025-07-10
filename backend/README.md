# 智能考勤系统 - 后端API

一个基于人脸识别和地理位置的智能考勤管理系统后端API，支持员工打卡、管理员管理、考勤统计等功能。

## 🚀 主要功能

### 👤 用户管理
- 用户注册/登录（手机号登录）
- JWT身份认证
- 用户角色管理（管理员/普通员工）
- 个人信息管理

### 🏢 部门管理
- 部门创建和管理
- 自定义考勤时间规则
- 灵活的打卡位置设置
- 距离阈值配置

### 📸 人脸识别
- 人脸照片上传
- 512维人脸特征提取
- 人脸相似度匹配
- 人脸照片审核流程

### ⏰ 考勤管理
- 智能打卡（人脸识别 + 地理位置）
- 考勤状态自动判断（正常/迟到/早退/缺勤/加班）
- 考勤记录查询
- 考勤统计分析

### 🔧 管理功能
- 员工管理
- 考勤记录管理
- 人脸照片审核
- 数据统计和报表

## 🛠 技术栈

- **Web框架**: Flask
- **数据库**: SQLite
- **身份认证**: JWT (Flask-JWT-Extended)
- **人脸识别**: FaceNet (facenet-pytorch)
- **图像处理**: OpenCV, Pillow
- **机器学习**: PyTorch, scikit-learn
- **其他**: Flask-CORS, Flask-SQLAlchemy

## 📦 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 依赖包说明
```
Flask                # Web框架
Flask-Cors           # 跨域支持
Flask-SQLAlchemy     # 数据库ORM
Flask-JWT-Extended   # JWT认证
PyJWT               # JWT处理
requests            # HTTP请求
pillow              # 图像处理
opencv-python       # 计算机视觉
facenet-pytorch     # 人脸识别模型
scikit-learn        # 机器学习工具
numpy               # 数值计算
torch               # PyTorch深度学习框架
torchvision         # 计算机视觉工具
schedule            # 定时任务
```

## 🚀 快速开始

### 1. 初始化数据库
```bash
# 创建数据库表
python migrate_db.py
```

### 2. 启动服务器
```bash
# 启动开发服务器
python run.py
```

服务器将在 `http://localhost:5000` 启动

### 3. 初始化数据（可选）
```bash
# 插入测试数据
python insert_data.py
```

## 📁 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用初始化
│   ├── models.py          # 数据模型
│   ├── face_service.py    # 人脸识别服务
│   ├── utils.py           # 工具函数
│   ├── routes/            # API路由
│   │   ├── auth.py        # 认证相关API
│   │   ├── user.py        # 用户管理API
│   │   ├── attendance.py  # 考勤相关API
│   │   ├── admin.py       # 管理员API
│   │   └── face.py        # 人脸识别API
│   └── uploads/           # 上传文件目录
├── instance/              # 实例配置
├── uploads/               # 文件上传目录
├── requirements.txt       # 依赖配置
├── run.py                # 启动脚本
├── migrate_db.py         # 数据库迁移
└── insert_data.py        # 测试数据插入
```

## 🔗 API接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/refresh` - 刷新Token

### 用户接口
- `GET /api/user/profile` - 获取用户信息
- `PUT /api/user/profile` - 更新用户信息

### 考勤接口
- `POST /api/attendance/check` - 打卡
- `GET /api/attendance/records` - 获取考勤记录
- `GET /api/attendance/calendar` - 日历视图

### 人脸识别接口
- `POST /api/face/upload` - 上传人脸照片
- `POST /api/face/recognize` - 人脸识别
- `POST /api/face/update_request` - 申请更新人脸照片

### 管理员接口
- `GET /api/admin/employees` - 员工管理
- `GET /api/admin/attendance` - 考勤管理
- `GET /api/admin/stats` - 统计数据
- `POST /api/admin/face_requests` - 人脸照片审核

## 🗄 数据库模型

### User (用户表)
- 存储用户基本信息、角色、部门关联

### Department (部门表)
- 部门信息、考勤规则、打卡位置配置

### Attendance (考勤表)
- 考勤记录、状态、位置、人脸特征

### FaceData (人脸数据表)
- 人脸照片、512维特征向量

### FaceUpdateRequest (人脸更新申请表)
- 人脸照片更新审核流程

## ⚙️ 配置说明

### 环境变量（推荐）
```bash
export JWT_SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///attendance.db"
```

### 应用配置
- 数据库：SQLite (开发) / PostgreSQL (生产)
- JWT过期时间：24小时
- 上传文件路径：`uploads/faces/`
- 人脸识别相似度阈值：0.8

## 🔒 安全特性

- JWT Token认证
- 密码加密存储
- CORS跨域配置
- 文件上传安全检查
- 人脸特征加密存储

## 🐛 故障排除

### 常见问题

1. **人脸识别模型加载失败**
   - 确保网络连接正常，首次运行会自动下载模型
   - 检查PyTorch和CUDA环境

2. **数据库初始化失败**
   - 检查数据库文件权限
   - 运行 `python migrate_db.py` 重新初始化

3. **图片上传失败**
   - 检查 `uploads/faces/` 目录权限
   - 确保图片格式为 jpg/png

## 📈 性能优化

- 人脸特征向量缓存
- 数据库查询优化
- 图片压缩处理
- 定期数据清理

## 🤝 开发指南

1. 遵循PEP 8代码规范
2. 添加适当的注释和文档
3. 编写单元测试
4. 使用版本控制管理代码

## 📄 许可证

本项目仅供学习和研究使用。

---

**注意**: 生产环境部署时，请修改JWT密钥、数据库配置等安全相关设置。 