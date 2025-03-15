# 校园云宝项目架构说明

## 项目概述

校园云宝是一个面向大学生的校园规划助手，提供个人提升、校园规划、虚拟自习室和生活助手四大功能模块。项目使用Django 4.2作为后端框架，基于RESTful API设计原则实现所有接口功能。

## 技术栈

- **框架**：Django 4.2
- **API框架**：Django REST Framework
- **数据库**：PostgreSQL
- **认证**：JWT (JSON Web Token)
- **文档**：OpenAPI 3.0

## 项目结构

项目采用模块化设计，按功能划分为多个应用模块：

1. **认证模块 (authentication)**：负责用户注册、登录、登出等功能
2. **个人提升模块 (personal_growth)**：学习计划管理、任务拆解、资源推荐等
3. **校园规划模块 (campus_planning)**：日程规划、搭子匹配等
4. **虚拟自习室模块 (virtual_study_room)**：自习室管理、学习记录等
5. **生活助手模块 (life_assistant)**：天气查询、快递跟踪、宿舍任务管理等

## 核心设计原则

1. **分层架构**：
   - 模型层 (Models)：定义数据结构
   - 序列化层 (Serializers)：数据转换和验证
   - 视图层 (Views)：处理请求和响应
   - 路由层 (URLs)：定义API路由

2. **统一响应格式**：
   - 成功响应：`{"status": "success", "code": 200, "message": "请求成功", "data": {...}}`
   - 错误响应：`{"status": "error", "code": 404, "message": "未找到"}`

3. **认证机制**：
   - 使用JWT (JSON Web Token) 进行身份验证
   - 通过`Authorization: Bearer <token>`请求头传递token

4. **权限控制**：
   - 基于角色的访问控制
   - 自定义权限类处理特殊权限需求 