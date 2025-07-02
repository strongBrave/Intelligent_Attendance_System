# 考勤系统后端API文档

## 概述

本文档描述了考勤系统后端的所有API接口，包括用户认证、考勤管理、人脸识别、管理员功能等模块。

### 基础信息

- **基础URL**: `http://localhost:5000`
- **认证方式**: JWT Token (Bearer Token)
- **数据格式**: JSON
- **字符编码**: UTF-8

### 响应格式

所有API响应都遵循以下格式：

```json
{
  "code": 0,           // 状态码：0表示成功，1表示失败
  "msg": "操作成功",    // 响应消息
  "data": {}           // 响应数据（可选）
}
```

## 1. 认证模块 (Auth)

### 1.1 获取验证码

**接口**: `GET /api/captcha`

**描述**: 获取图形验证码

**请求参数**: 无

**响应示例**:
```json
{
  "captcha_id": "abc123def456",
  "captcha_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### 1.2 用户注册

**接口**: `POST /api/register`

**描述**: 用户注册

**请求参数**:
```json
{
  "name": "张三",
  "phone": "13800138000",
  "password": "123456",
  "captcha_id": "abc123def456",
  "captcha_text": "ABCD"
}
```

**响应示例**:
```json
{
  "msg": "注册成功",
  "user": {
    "id": 1,
    "name": "张三",
    "phone": "13800138000"
  }
}
```

### 1.3 用户登录

**接口**: `POST /api/login`

**描述**: 用户登录

**请求参数**:
```json
{
  "phone": "13800138000",
  "password": "123456"
}
```

**响应示例**:
```json
{
  "msg": "登录成功",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "name": "张三",
    "phone": "13800138000",
    "role": "user"
  }
}
```

### 1.4 验证原密码

**接口**: `POST /api/verify-old-password`

**描述**: 验证用户原密码（用于找回密码）

**请求参数**:
```json
{
  "phone": "13800138000",
  "old_password": "123456"
}
```

**响应示例**:
```json
{
  "msg": "验证成功",
  "phone": "13800138000",
  "user_name": "张三"
}
```

### 1.5 重置密码

**接口**: `POST /api/reset-password`

**描述**: 重置用户密码

**请求参数**:
```json
{
  "phone": "13800138000",
  "new_password": "newpass123",
  "confirm_password": "newpass123"
}
```

**响应示例**:
```json
{
  "msg": "密码重置成功"
}
```

### 1.6 获取用户信息

**接口**: `GET /api/profile`

**描述**: 获取当前登录用户信息

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "id": 1,
  "name": "张三",
  "phone": "13800138000",
  "role": "user",
  "department": "技术部"
}
```

## 2. 考勤模块 (Attendance)

### 2.1 用户签到

**接口**: `POST /api/attendance/check_in`

**描述**: 用户签到打卡

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "latitude": 39.9042,
  "longitude": 116.4074,
  "location": "北京市朝阳区"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "签到成功",
  "data": {
    "time": "2024-01-15 09:00:00",
    "status": "normal",
    "location": "北京市朝阳区"
  }
}
```

### 2.2 用户签退

**接口**: `POST /api/attendance/check_out`

**描述**: 用户签退打卡

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "latitude": 39.9042,
  "longitude": 116.4074,
  "location": "北京市朝阳区"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "签退成功",
  "data": {
    "time": "2024-01-15 18:00:00",
    "status": "normal",
    "location": "北京市朝阳区"
  }
}
```

### 2.3 获取考勤记录

**接口**: `GET /api/attendance/records`

**描述**: 获取用户的考勤记录

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**查询参数**:
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `page`: 页码 (默认1)
- `per_page`: 每页数量 (默认20)

**响应示例**:
```json
{
  "records": [
    {
      "id": 1,
      "date": "2024-01-15",
      "check_type": "sign_in",
      "status": "normal",
      "time": "2024-01-15 09:00:00",
      "location": "北京市朝阳区"
    }
  ],
  "total": 100,
  "pages": 5,
  "current_page": 1
}
```

### 2.4 获取今日考勤状态

**接口**: `GET /api/attendance/today`

**描述**: 获取今天的考勤状态

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "today": "2024-01-15",
  "check_in": {
    "time": "2024-01-15 09:00:00",
    "status": "normal",
    "location": "北京市朝阳区"
  },
  "check_out": {
    "time": "2024-01-15 18:00:00",
    "status": "normal",
    "location": "北京市朝阳区"
  }
}
```

### 2.5 获取用户今日考勤

**接口**: `GET /api/user/today`

**描述**: 获取用户今日考勤详情

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "today": "2024-01-15",
  "check_in": {
    "time": "2024-01-15 09:00:00",
    "status": "normal"
  },
  "check_out": {
    "time": "2024-01-15 18:00:00",
    "status": "normal"
  },
  "work_hours": 9.0
}
```

### 2.6 获取月度考勤统计

**接口**: `GET /api/user/month`

**描述**: 获取用户月度考勤统计

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**查询参数**:
- `year`: 年份 (默认当前年)
- `month`: 月份 (默认当前月)

**响应示例**:
```json
{
  "year": 2024,
  "month": 1,
  "total_days": 22,
  "work_days": 20,
  "attendance_days": 18,
  "late_days": 2,
  "absent_days": 0,
  "overtime_hours": 5.5
}
```

### 2.7 检查打卡距离

**接口**: `POST /api/attendance/check_distance`

**描述**: 检查用户当前位置是否在允许的打卡范围内

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "latitude": 39.9042,
  "longitude": 116.4074
}
```

**响应示例**:
```json
{
  "within_range": true,
  "distance": 50.5,
  "threshold": 100.0,
  "message": "位置在允许范围内"
}
```

### 2.8 人脸验证

**接口**: `POST /api/attendance/verify_face`

**描述**: 使用人脸识别验证用户身份

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "face_image": "base64编码的图片数据"
}
```

**响应示例**:
```json
{
  "verified": true,
  "similarity_score": 0.95,
  "threshold": 0.8,
  "message": "人脸验证成功"
}
```

## 3. 人脸识别模块 (Face)

### 3.1 获取模型信息

**接口**: `GET /model_info`

**描述**: 获取人脸识别模型信息

**响应示例**:
```json
{
  "code": 0,
  "msg": "获取成功",
  "data": {
    "model_name": "face_recognition",
    "feature_dim": 512,
    "version": "1.0.0"
  }
}
```

### 3.2 注册人脸（单张图片）

**接口**: `POST /register_face`

**描述**: 使用单张图片注册用户人脸

**请求参数**:
- `user_id`: 用户ID
- `face_image`: 人脸图片文件

**响应示例**:
```json
{
  "code": 0,
  "msg": "人脸注册成功",
  "data": {
    "face_data_id": 1,
    "feature_dim": 512,
    "model_info": {
      "model_name": "face_recognition",
      "version": "1.0.0"
    }
  }
}
```

### 3.3 注册人脸（多张图片）

**接口**: `POST /register_multiple_faces`

**描述**: 使用多张图片注册用户人脸，计算平均特征向量

**请求参数**:
- `user_id`: 用户ID
- `face_images`: 多个人脸图片文件（最多5张）

**响应示例**:
```json
{
  "code": 0,
  "msg": "人脸注册成功，处理了 3 张图片",
  "data": {
    "face_data_id": 1,
    "feature_dim": 512,
    "processed_images": 3,
    "valid_images": 3,
    "model_info": {
      "model_name": "face_recognition",
      "version": "1.0.0"
    }
  }
}
```

### 3.4 获取用户人脸信息

**接口**: `GET /user_face_info/<user_id>`

**描述**: 获取指定用户的人脸信息

**响应示例**:
```json
{
  "code": 0,
  "msg": "获取成功",
  "data": {
    "user_id": 1,
    "has_face_data": true,
    "face_data_id": 1,
    "feature_dim": 512,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

### 3.5 删除用户人脸

**接口**: `DELETE /delete_face/<user_id>`

**描述**: 删除指定用户的人脸数据

**响应示例**:
```json
{
  "code": 0,
  "msg": "人脸数据删除成功"
}
```

## 4. 用户模块 (User)

### 4.1 获取用户信息

**接口**: `GET /api/user/profile`

**描述**: 获取当前用户信息

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "id": 1,
  "username": "张三",
  "phone": "13800138000",
  "role": "user",
  "department": "技术部"
}
```

### 4.2 更新用户信息

**接口**: `PUT /api/user/update_profile`

**描述**: 更新当前用户信息

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "phone": "13800138001"
}
```

**响应示例**:
```json
{
  "message": "信息更新成功"
}
```

## 5. 管理员模块 (Admin)

### 5.1 获取所有用户

**接口**: `GET /api/admin/users`

**描述**: 获取所有用户列表

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "users": [
    {
      "id": 1,
      "name": "张三",
      "phone": "13800138000",
      "role": "user",
      "department": "技术部",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### 5.2 创建用户

**接口**: `POST /api/admin/users`

**描述**: 创建新用户

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "name": "李四",
  "password": "123456",
  "phone": "13800138001",
  "role": "user",
  "department_id": 1
}
```

**响应示例**:
```json
{
  "message": "用户创建成功",
  "user": {
    "id": 2,
    "name": "李四",
    "phone": "13800138001",
    "role": "user"
  }
}
```

### 5.3 更新用户

**接口**: `PUT /api/admin/users/<user_id>`

**描述**: 更新指定用户信息

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "name": "李四",
  "phone": "13800138002",
  "role": "admin",
  "department_id": 1
}
```

**响应示例**:
```json
{
  "message": "用户信息更新成功"
}
```

### 5.4 删除用户

**接口**: `DELETE /api/admin/users/<user_id>`

**描述**: 删除指定用户

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "message": "用户删除成功"
}
```

### 5.5 获取所有部门

**接口**: `GET /api/admin/departments`

**描述**: 获取所有部门列表

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "departments": [
    {
      "id": 1,
      "name": "技术部",
      "sign_in_time": "09:00",
      "sign_out_time": "18:00",
      "location": "北京市朝阳区",
      "user_count": 10
    }
  ]
}
```

### 5.6 创建部门

**接口**: `POST /api/admin/departments`

**描述**: 创建新部门

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "name": "市场部",
  "sign_in_time": "09:00",
  "sign_out_time": "18:00",
  "late_threshold": "09:30",
  "absent_threshold": "10:00",
  "early_leave_threshold": "17:30",
  "location": "北京市朝阳区",
  "distance_threshold": 100.0
}
```

**响应示例**:
```json
{
  "message": "部门创建成功",
  "department": {
    "id": 2,
    "name": "市场部",
    "sign_in_time": "09:00",
    "sign_out_time": "18:00"
  }
}
```

### 5.7 更新部门

**接口**: `PUT /api/admin/departments/<department_id>`

**描述**: 更新指定部门信息

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "name": "市场部",
  "sign_in_time": "08:30",
  "sign_out_time": "17:30"
}
```

**响应示例**:
```json
{
  "message": "部门信息更新成功"
}
```

### 5.8 删除部门

**接口**: `DELETE /api/admin/departments/<department_id>`

**描述**: 删除指定部门

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "message": "部门删除成功"
}
```

### 5.9 获取部门用户

**接口**: `GET /api/admin/departments/<department_id>/users`

**描述**: 获取指定部门的所有用户

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "users": [
    {
      "id": 1,
      "name": "张三",
      "phone": "13800138000",
      "role": "user"
    }
  ]
}
```

### 5.10 获取考勤统计

**接口**: `GET /api/admin/attendance/stats`

**描述**: 获取考勤统计数据

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**查询参数**:
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `department_id`: 部门ID (可选)

**响应示例**:
```json
{
  "total_users": 100,
  "total_attendance": 1800,
  "normal_attendance": 1600,
  "late_attendance": 150,
  "absent_attendance": 50,
  "attendance_rate": 0.89
}
```

### 5.11 获取考勤记录

**接口**: `GET /api/admin/attendance/records`

**描述**: 获取所有用户的考勤记录

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**查询参数**:
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `user_id`: 用户ID (可选)
- `department_id`: 部门ID (可选)
- `page`: 页码 (默认1)
- `per_page`: 每页数量 (默认20)

**响应示例**:
```json
{
  "records": [
    {
      "id": 1,
      "user_name": "张三",
      "department": "技术部",
      "date": "2024-01-15",
      "check_type": "sign_in",
      "status": "normal",
      "time": "2024-01-15 09:00:00",
      "location": "北京市朝阳区"
    }
  ],
  "total": 1000,
  "pages": 50,
  "current_page": 1
}
```

### 5.12 获取部门考勤设置

**接口**: `GET /api/admin/departments/<department_id>/attendance-settings`

**描述**: 获取指定部门的考勤设置

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "id": 1,
  "name": "技术部",
  "sign_in_time": "09:00",
  "sign_out_time": "18:00",
  "late_threshold": "09:30",
  "absent_threshold": "10:00",
  "early_leave_threshold": "17:30",
  "location": "北京市朝阳区",
  "distance_threshold": 100.0
}
```

### 5.13 更新部门考勤设置

**接口**: `PUT /api/admin/departments/<department_id>/attendance-settings`

**描述**: 更新指定部门的考勤设置

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "sign_in_time": "09:00",
  "sign_out_time": "18:00",
  "late_threshold": "09:30",
  "absent_threshold": "10:00",
  "early_leave_threshold": "17:30",
  "location": "北京市朝阳区",
  "distance_threshold": 100.0
}
```

**响应示例**:
```json
{
  "message": "考勤设置更新成功"
}
```

### 5.14 获取仪表板统计

**接口**: `GET /api/admin/dashboard/stats`

**描述**: 获取管理员仪表板统计数据

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**响应示例**:
```json
{
  "total_users": 100,
  "total_departments": 5,
  "today_attendance": 85,
  "today_late": 5,
  "today_absent": 10,
  "monthly_stats": {
    "total_days": 22,
    "attendance_days": 18,
    "late_days": 3,
    "absent_days": 1
  }
}
```

### 5.15 更新考勤状态

**接口**: `PUT /api/admin/attendance/<attendance_id>/status`

**描述**: 管理员手动更新考勤状态

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "status": "normal"
}
```

**响应示例**:
```json
{
  "message": "考勤状态更新成功"
}
```

### 5.16 补签考勤

**接口**: `POST /api/admin/attendance/makeup`

**描述**: 管理员为用户补签考勤

**请求头**: 
```
Authorization: Bearer <jwt_token>
```

**请求参数**:
```json
{
  "user_id": 1,
  "date": "2024-01-15",
  "check_type": "sign_in",
  "time": "2024-01-15 09:00:00",
  "status": "normal",
  "location": "北京市朝阳区"
}
```

**响应示例**:
```json
{
  "message": "补签成功"
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录） |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 认证说明

### JWT Token 使用

1. 用户登录后获取 `access_token`
2. 在后续请求中，在请求头中添加：
   ```
   Authorization: Bearer <access_token>
   ```
3. Token 有效期为24小时

### 权限说明

- `user`: 普通用户，只能访问自己的数据
- `admin`: 管理员，可以访问所有数据和管理功能

## 数据模型

### User (用户)
- `id`: 用户ID
- `name`: 姓名
- `password`: 密码（加密存储）
- `phone`: 手机号
- `role`: 角色 (user/admin)
- `department_id`: 部门ID
- `created_at`: 创建时间

### Department (部门)
- `id`: 部门ID
- `name`: 部门名称
- `sign_in_time`: 签到时间
- `sign_out_time`: 签退时间
- `late_threshold`: 迟到阈值
- `absent_threshold`: 缺勤阈值
- `early_leave_threshold`: 早退阈值
- `location`: 打卡位置
- `distance_threshold`: 距离阈值

### Attendance (考勤记录)
- `id`: 考勤ID
- `user_id`: 用户ID
- `date`: 考勤日期
- `check_type`: 打卡类型 (sign_in/sign_out)
- `status`: 状态 (normal/late/absent/overtime)
- `time`: 打卡时间
- `location`: 打卡位置
- `latitude`: 纬度
- `longitude`: 经度

### FaceData (人脸数据)
- `id`: 人脸数据ID
- `face_url`: 人脸图片路径
- `face_features`: 人脸特征向量（JSON格式）
- `user_id`: 用户ID

## 部署说明

### 环境要求
- Python 3.7+
- Flask
- SQLite/MySQL
- 相关依赖包（见 requirements.txt）

### 启动步骤
1. 安装依赖：`pip install -r requirements.txt`
2. 初始化数据库：`python init_db.py`
3. 启动服务：`python run.py`

### 配置文件
主要配置在 `app/__init__.py` 中，包括：
- 数据库连接
- JWT 密钥
- 文件上传路径
- 日志配置 