# 贡献指南

感谢您考虑为酒店业BI报告平台做出贡献！这份文档提供了参与项目开发的指导方针。

## 开发流程

1. Fork 这个仓库
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个 Pull Request

## 代码风格

- 遵循 Vue 3 的 [风格指南](https://v3.cn.vuejs.org/style-guide/)
- 使用 TypeScript 类型注解
- 使用 Composition API 风格编写组件
- 保持代码简洁、可读性高
- 使用有意义的变量和函数命名

## 提交规范

提交信息应该遵循以下格式：

```
<类型>: <描述>

[可选的详细描述]

[可选的关闭问题引用]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码风格修改（不影响代码运行的变动）
- `refactor`: 重构（既不是新增功能，也不是修改bug的代码变动）
- `perf`: 性能优化
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动

例如：
```
feat: 添加用户权限管理功能

- 增加角色选择器
- 实现权限分配界面
- 添加权限验证逻辑

Closes #123
```

## 分支管理

- `main`: 主分支，保持稳定可发布状态
- `develop`: 开发分支，新功能合并到此分支
- `feature/*`: 功能分支，从develop分支创建
- `fix/*`: 修复分支，用于修复bug
- `release/*`: 发布分支，准备版本发布

## 测试

在提交PR前，请确保：

1. 所有单元测试通过 (`npm run test:unit`)
2. 端到端测试通过 (`npm run test:e2e`)
3. 代码符合项目的风格指南 (`npm run lint`)

## 问题报告

创建问题报告时，请包含：

1. 问题的简要描述
2. 复现步骤
3. 预期行为
4. 实际行为
5. 截图（如适用）
6. 环境信息（浏览器、操作系统等）

## 功能请求

提出新功能时，请描述：

1. 功能的目的和价值
2. 功能的具体行为
3. 可能的实现方式
4. 相关的用例或场景

## 代码审查

所有的PR都会经过代码审查。审查者会关注：

1. 代码质量和风格
2. 功能完整性
3. 测试覆盖率
4. 文档更新

## 许可证

通过贡献代码，您同意您的贡献将在项目的许可证下发布。

---

再次感谢您的贡献！ 