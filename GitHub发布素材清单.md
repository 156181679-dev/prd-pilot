# PRD Pilot GitHub 发布素材清单

## 仓库一句话简介

`PRD Pilot is an AI workspace for product managers to turn vague ideas into reviewable PRDs, demo-ready HTML prototypes, and targeted iteration plans.`

## 仓库短描述

`AI PRD and Demo workspace for product managers.`

## 仓库长描述

`PRD Pilot 面向产品经理，帮助用户把模糊需求快速整理成 Requirement Spec、中文 PRD、可演示 Demo 和一致性检查结果，并支持定点迭代。`

## GitHub 首页截图建议

### 必拍 1：首页总览

- 展示顶部标题 `PRD Pilot`
- 左侧看到需求输入区
- 右侧看到 PRD / Demo / 一致性检查标签
- 目的：让访问者第一眼知道这是做什么的

### 必拍 2：Requirement Spec

- 输入一段真实需求后点击 `解析需求摘要`
- 截图展示结构化需求结果
- 目的：突出“不是直接乱生成，而是先做需求理解”

### 必拍 3：PRD 结果

- 展示完整 PRD 输出
- 最好能看到目录、目标用户、核心流程、功能模块
- 目的：证明它能产出可评审文档

### 必拍 4：Demo 预览

- 展示 Demo 实际页面
- 选一个视觉和交互都比较完整的案例
- 目的：证明它不只是写文档，也能快速做演示原型

### 必拍 5：一致性检查

- 展示评分、等级、问题列表、修复建议
- 目的：打出与普通 AI 生成器的差异化

### 必拍 6：定点修改

- 展示修改类型、影响页面、修改说明，以及更新后的结果
- 目的：说明它支持闭环迭代，不是整份重写

### 可选 7：模型配置弹窗

- 展示右上角 `配置模型`
- 看到模型平台、模型名、API Key、Base URL
- 目的：说明它支持用户自行切换模型

## 建议录屏顺序

1. 输入一句模糊需求
2. 解析 Requirement Spec
3. 生成 PRD
4. 生成 Demo 与原型说明
5. 运行一致性检查
6. 根据修复建议做一次定点修改

建议控制在 90 秒到 2 分钟内。

## 推荐案例

### 案例 1：校园二手交易平台

- 适合展示后台管理台风格
- 容易做出列表、详情、审核、状态流转

### 案例 2：AI 简历优化工具

- 适合展示移动端 H5 或 Web 工具风格
- 容易表现输入、生成、反馈、结果对比

## README 首屏建议顺序

1. 一句话定位
2. 主流程图
3. 核心功能
4. 截图/GIF
5. 快速启动
6. 技术栈
7. 案例

## 发布前自查

- 仓库里没有真实 `.env`
- 没有本地 API Key
- 没有 `node_modules`、`dist`、`__pycache__`
- README 路径都指向 `prd-pilot/`
- 默认启动命令可直接复制执行
