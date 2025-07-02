# 智慧考勤系统 - Web管理后台

基于Vue3 + Element Plus的管理后台，提供员工管理、考勤统计、数据分析等功能。

## 技术栈

- **前端框架**: Vue 3.3.4
- **UI组件库**: Element Plus 2.3.8
- **路由**: Vue Router 4.2.4
- **HTTP客户端**: Axios 1.4.0
- **图表库**: ECharts 5.4.3
- **构建工具**: Vite 4.4.5

## 功能模块

- 🔐 **管理员登录** - 安全的管理员身份验证
- 📊 **数据看板** - 考勤数据概览和统计
- 👥 **员工管理** - 员工信息的增删改查
- 📅 **考勤管理** - 考勤记录的查看和管理
- 📈 **统计分析** - 考勤数据的图表分析

## 快速开始

### 1. 安装依赖

```bash
cd web
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

开发服务器将在 `http://localhost:3000` 启动

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 项目结构

```
web/
├── src/
│   ├── views/           # 页面组件
│   │   ├── Login.vue    # 登录页面
│   │   ├── Dashboard.vue # 数据看板
│   │   ├── EmployeeList.vue # 员工列表
│   │   ├── EmployeeEdit.vue # 员工编辑
│   │   ├── AttendanceList.vue # 考勤列表
│   │   └── Stats.vue    # 统计分析
│   ├── api/             # API接口
│   │   └── index.js     # Axios配置
│   ├── App.vue          # 主应用组件
│   ├── main.js          # 应用入口
│   └── router.js        # 路由配置
├── index.html           # HTML模板
├── vite.config.js       # Vite配置
├── package.json         # 项目配置
└── README.md           # 项目说明
```

## 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0

## 开发配置

### 代理配置

项目已配置API代理，开发时请求 `/api/*` 会自动转发到后端服务：

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

### 环境变量

可以创建 `.env` 文件来配置环境变量：

```bash
# .env
VITE_API_BASE_URL=http://localhost:5000/api
```

## 页面说明

### 1. 登录页面 (`/login`)
- 管理员身份验证
- 用户名/密码登录
- 登录状态保持

### 2. 数据看板 (`/`)
- 考勤数据概览
- 今日考勤统计
- 快速操作入口

### 3. 员工管理 (`/employees`)
- 员工列表展示
- 员工信息编辑
- 员工状态管理

### 4. 考勤管理 (`/attendance`)
- 考勤记录列表
- 考勤状态筛选
- 考勤详情查看

### 5. 统计分析 (`/stats`)
- 考勤数据图表
- 趋势分析
- 数据导出

## API接口

### 认证相关
- `POST /api/login` - 管理员登录
- `POST /api/logout` - 退出登录

### 员工管理
- `GET /api/employees` - 获取员工列表
- `POST /api/employees` - 创建员工
- `PUT /api/employees/:id` - 更新员工信息
- `DELETE /api/employees/:id` - 删除员工

### 考勤管理
- `GET /api/attendance` - 获取考勤记录
- `GET /api/attendance/:id` - 获取考勤详情
- `PUT /api/attendance/:id` - 更新考勤状态

### 统计分析
- `GET /api/stats/overview` - 获取统计数据概览
- `GET /api/stats/trend` - 获取趋势数据
- `GET /api/stats/export` - 导出统计数据

## 开发指南

### 添加新页面

1. 在 `src/views/` 目录下创建新的Vue组件
2. 在 `src/router.js` 中添加路由配置
3. 在 `src/api/` 中添加相应的API接口

### 样式规范

- 使用Element Plus组件库
- 遵循Vue 3 Composition API
- 使用scoped样式避免样式冲突

### 代码规范

- 使用ESLint进行代码检查
- 遵循Vue 3官方风格指南
- 使用TypeScript类型注解（可选）

## 部署说明

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
npm run build
npm run preview
```

### Docker部署
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 常见问题

### 1. 依赖安装失败
```bash
# 清除缓存重新安装
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 2. 开发服务器启动失败
- 检查端口3000是否被占用
- 确认Node.js版本是否符合要求
- 检查vite.config.js配置是否正确

### 3. API请求失败
- 确认后端服务是否启动
- 检查代理配置是否正确
- 确认API接口地址是否正确

## 许可证

MIT License 