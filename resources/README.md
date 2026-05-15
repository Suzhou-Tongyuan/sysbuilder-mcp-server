# sysbuilder-mcp-server Resources

本目录用于集中存放随 MCP 包一起分发的规则与技能资源，便于不同 AI 客户端以统一方式读取。

## 目录结构

- `rules/`
  - 存放执行约束、建模规范、流程规则等硬性规则文件
- `quickref/`
  - 存放按工具或 API 维度组织的速查文档
- `skills/`
  - 存放任务技能目录
  - 每个技能目录通常包含 `SKILL.md`，也可能包含 `references/`、`agents/` 等补充资料

## 文件说明

主要包括：

- `./resources/README.md`：`resources` 目录结构与推荐使用顺序说明
- `./resources/rules/default.rules`：默认工作区规则与执行约束补充说明
- `./resources/rules/Sysbuilder建模要求.md`：使用 Sysbuilder 建模时应遵守的强制要求
- `./resources/skills/sysml-modeling-standard/SKILL.md`：SysML 建模技能入口与执行流程说明
- `./resources/skills/sysml-modeling-standard/references/SysML建模规范.md`：SysML 建模参考规范
- `./resources/quickref/sysbuilder_python_api.md`：Sysbuilder Python 接口速查与自动建模实践
- `./resources/skills/sysml-modeling-standard/agents/openai.yaml`：该技能在 AI 客户端中的展示配置

## 提示 AI 先读资源

当用户使用 Sysbuilder 建模，并希望 AI 客户端先读取资源文件时，可将下面这段提示语直接输入给 AI 客户端：

```text
要使用 resources 里的资源，应先阅读一遍：

- ./resources/rules/Sysbuilder建模要求.md
- ./resources/skills/sysml-modeling-standard/SKILL.md

若技能文件引用了参考资料，再继续阅读：

- ./resources/skills/sysml-modeling-standard/references/SysML建模规范.md
- ./resources/quickref/sysbuilder_python_api.md
```
