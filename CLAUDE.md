# Caicai Skills 项目规范

## 新增 Skill 检查清单

当添加新 skill 时，必须同步更新以下三个文件：

### 1. README.md（英文版）
- [ ] 在 Installation 部分的直接安装指令中添加新 skill
- [ ] 在 Available Skills 部分添加 skill 详细介绍，包括：
  - 功能描述
  - 使用示例
  - 功能特性
  - 输出结构示例

### 2. README_CN.md（中文版）
- [ ] 同步更新安装指令
- [ ] 同步添加中文详细介绍

### 3. .claude-plugin/marketplace.json
- [ ] 在 `plugins` 数组中添加新插件配置：
```json
{
  "name": "caicai-skill-name",
  "source": "./",
  "strict": false,
  "description": "Skill description here",
  "version": "1.0.0",
  "author": {
    "name": "Next蔡蔡"
  },
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "category": "productivity|utility|content",
  "skills": [
    "./skills/caicai-skill-name"
  ]
}
```

## Skill 目录结构

```
skills/
├── caicai-skill-name/
│   ├── SKILL.md          # 技能定义和使用说明
│   └── scripts/          # 实现脚本（如需要）
```

## 命名规范

- Skill 目录名：`caicai-<skill-name>`（小写，连字符分隔）
- Marketplace 中的 name 字段：与目录名一致
- Keywords：小写，与功能相关
