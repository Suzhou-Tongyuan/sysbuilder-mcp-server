---
name: sysml-modeling-standard
description: Use when creating, refining, reviewing, or validating SysML models in this workspace, especially when the task involves Sysbuilder, requirements, behavior, structure, interfaces, parameters, traceability, naming, diagram selection, or model quality checks.
---

# SysML Modeling Standard

Apply this skill as the default entry point for SysML work in this workspace.

## When To Use

Use this skill when the user asks to:
- create a SysML model
- modify an existing SysML model
- review SysML model quality
- define requirements, behaviors, structures, interfaces, states, parameters, or traceability
- perform Sysbuilder-based modeling in this workspace

If the task will use Sysbuilder software, Sysbuilder APIs, Sysbuilder MCP tools, or Sysbuilder automation scripts, read [Sysbuilder建模要求.md](../../rules/Sysbuilder建模要求.md) before any such action and treat it as a hard execution constraint.

## Mandatory Workflow

1. Read [references/SysML建模规范.md](references/SysML建模规范.md) for the workspace modeling rules.
2. If the task will use Sysbuilder automation scripts, also read [../../quickref/sysbuilder_python_api.md](../../quickref/sysbuilder_python_api.md).
3. Clarify the current modeling goal:
   - requirement analysis
   - behavior analysis
   - architecture design
   - interface/parameter/verification traceability
4. Build the minimum sufficient model for the task. Do not add diagrams that do not answer an engineering question.
5. Keep naming consistent, unique, and searchable. Prefer Chinese names in this workspace unless the source standard explicitly requires otherwise.
6. Follow the standard package layering, element usage, diagram-selection rules, and API compatibility rules.
7. Build the core traceability chain where applicable:
   - source -> requirement -> behavior -> structure -> verification
8. Before finishing, check naming consistency, relation semantics, interface consistency, and modeling completeness against the requested scope.

## What To Output

When reporting results for a modeling task, provide:
- which modeling goal was addressed
- which standard rules were applied
- which key traceability links were created or checked
- any unsupported diagram/tool limitations and how they were handled
- any violations found and the corrective action taken

## References

- [references/SysML建模规范.md](references/SysML建模规范.md): Full workspace SysML modeling standard.
- [../../quickref/sysbuilder_python_api.md](../../quickref/sysbuilder_python_api.md): API-level quick reference for reliable Sysbuilder automation.
