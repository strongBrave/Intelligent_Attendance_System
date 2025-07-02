# 考勤系统运行说明

本项目包含后端API服务和Vue前端界面，以下是运行步骤。

## 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

## 1. 运行后端服务

### 1.1 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 启动后端服务

```bash
python run.py
```

后端服务将在 `http://localhost:5000` 启动

## 2. 运行Vue前端

### 2.1 安装Node.js依赖

```bash
cd web
npm install
```

### 2.2 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动

## 3. 访问应用

- 前端界面：http://localhost:3000
- 后端API：http://localhost:5000

## 注意事项

- 确保后端服务先启动，前端才能正常访问API
- 前端已配置代理，API请求会自动转发到后端
- 首次运行时会自动创建SQLite数据库文件

## 常见问题

1. **端口被占用**：修改 `run.py` 中的端口号或 `vite.config.js` 中的端口配置
2. **依赖安装失败**：确保使用正确的Python和Node.js版本
3. **数据库问题**：删除 `backend/instance/attendance.db` 文件重新创建 