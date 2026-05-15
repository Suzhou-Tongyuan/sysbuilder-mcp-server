# Sysbuilder Python 接口速查

> **渐进披露**：先在此表找到接口签名与适用图种，再按需查看 `sysbuilder_api.py` 原始 docstring 或补充示例。

> **建模前置**：开始 Sysbuilder 建模前，先阅读 `resources/rules/Sysbuilder建模要求.md`，再查本 quickref 选 API。

> **MCP 建议流程**：先调用 `lookup_sysbuilder_api` 查 API，再写完整脚本，最后调用 `run_script` 执行。

## ⛔ Script Rules（每次写脚本前必读）

1. 所有 Sysbuilder 建模脚本必须使用 `UTF-8` 编码。
2. 文件路径统一使用 `//`。
3. `NewProject(projectName=...)` 只决定工程文件名；后续元素全名**不要**带工程名前缀。
4. 元素全名统一使用 `.` 分层，例如：
   - `RequirementModel.Functions.REQ_FUN_001`
   - `ArchitectureModel.Scene`
5. 若名称段自身包含 `.`，使用单引号包裹该名称段。
6. 自动建模时优先一次性完成：工程创建 -> 包结构 -> 元素创建 -> 关系建立 -> 视图创建 -> 图块插入 -> 所有图块插入完成后自动布局。
7. 不要调用 quickref 或 `sysbuilder_api.py` 中不存在的 API；尤其禁止 `NewObjectNode`、`CreateObjectNode`、`CreateActivityActionNode`、`NewActivityActionNode`、`CreateSwimlane`、`CreateActivityPartition`、`CreateActivityParameterNode`。
8. 当前无对象节点/活动参数节点 API；活动图数据端点只用 `NewInputPort`、`NewOutputPort` 创建，再用 `CreateActivityObjectFlowLine` 连接。
9. 当前无泳道/活动分区 API；责任分配用包、命名、块或 allocate 关系表达。
10. 写脚本前先在 quickref 中一次性选定本次需要的 API，不要边写边反复改用其他命名。
11. 若某个 API 不存在，直接改写为 quickref 中已有的模式，不要输出”再查一下文档””再试另一种 API”这类过程性步骤。
12. 若本次任务明确要求生成 DoDAF 模型，则 `NewProject(...)` 的 `projectType` 必须显式传 `dodaf`，不要继续使用默认的 `sysml`。

---

## §1 文件与工程操作

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 获取工作目录 | `GetDirectory()` | `GetDirectory()` | 返回当前工作目录 |
| 设置工作目录 | `SetDirectory(path)` | `SetDirectory('C://work')` | 路径用 `//` |
| 打开工程 | `OpenProjectFile(path, autoReload=True)` | `OpenProjectFile('C://demo.sybprojz')` | 不弹保存提示 |
| 新建工程 | `NewProject(projectName, projectPath, projectFormat, projectType)` | `NewProject('Demo', 'C://work', 'sybprojz', 'sysml')` | 后续元素全名不要带工程名前缀；若明确要求生成 DoDAF 模型，则 `projectType` 必须传 `dodaf` |
| 保存工程 | `SaveProject()` | `SaveProject()` | 保存当前工程 |
| 另存为 | `SaveProjectAs(targetPath)` | `SaveProjectAs('C://backup//Demo.sybprojz')` | 用于显式落盘 |
| 退出软件 | `Exit()` | `Exit()` | 强制退出，不弹提示 |

---

## §2 视图创建

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 新建包图 | `NewPKGDiagram(fullName)` | `NewPKGDiagram('Context.PKG_ProjectOverview')` | 适合包组织总览 |
| 新建需求图 | `NewREQDiagram(fullName)` | `NewREQDiagram('RequirementModel.REQ_SystemRequirements')` | 需求与 `satisfy` 推荐落在这里 |
| 新建用例图 | `NewUCDiagram(fullName)` | `NewUCDiagram('UseCaseModel.UCD_MainScenarios')` | 参与者与用例 |
| 新建活动图 | `NewACTDiagram(fullName)` | `NewACTDiagram('BehaviorModel.ACT_Main.Flow')` | 行为流程 |
| 新建状态机图 | `NewSTMDiagram(fullName)` | `NewSTMDiagram('BehaviorModel.STM_Task.Diagram')` | 状态机骨架 |
| 新建模块定义图 | `NewBDDDiagram(fullName)` | `NewBDDDiagram('ArchitectureModel.BDD_SystemArchitecture')` | 结构、功能树、`allocate` 推荐落在这里 |
| 新建内部模块图 | `NewIBDDiagram(fullName)` | `NewIBDDiagram('ArchitectureModel.System.IBD')` | 组成属性与连接器 |
| 新建参数图 | `NewPARDiagram(fullName)` | `NewPARDiagram('ParametricModel.SystemParameters.PAR')` | 参数与约束 |
| 新建需求表 | `NewRequirementTable(fullName)` | `NewRequirementTable('TablesAndViews.RequirementTable')` | 需求列表 |
| 新建架构表 | `NewArchitectureTable(fullName)` | `NewArchitectureTable('TablesAndViews.ArchitectureTable')` | 架构表格 |
| 新建需求功能追溯矩阵 | `NewRequirementFunctionTraceabilityMatrix(fullName)` | `NewRequirementFunctionTraceabilityMatrix('TablesAndViews.RequirementFunctionTraceabilityMatrix')` | 自动配置矩阵筛选 |
| 新建架构功能追溯矩阵 | `NewArchitectureFunctionTraceabilityMatrix(fullName)` | `NewArchitectureFunctionTraceabilityMatrix('TablesAndViews.ArchitectureFunctionTraceabilityMatrix')` | 自动配置矩阵筛选 |
| 新建追溯分析图 | `NewRetrospectiveAnalysisDiagram(fullName)` | `NewRetrospectiveAnalysisDiagram('TraceabilityModel.TraceView')` | 不建议作为主追溯落线图 |

---

## §3 通用元素操作

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 新建包 | `NewPackage(fullName)` | `NewPackage('RequirementModel')` | 顶层包不带工程名前缀 |
| 新建块 | `NewBlock(fullName)` | `NewBlock('ArchitectureModel.Scene')` | 结构块、功能块都可用 |
| 新建活动 | `NewActivity(fullName)` | `NewActivity('BehaviorModel.ACT_SevenStage')` | 活动图主体 |
| 新建需求 | `NewRequirement(fullName)` | `NewRequirement('RequirementModel.Functions.REQ_FUN_001')` | 需配合 ID 和文本 |
| 新建状态机 | `NewStateMachine(fullName)` | `NewStateMachine('BehaviorModel.STM_TaskLifecycle')` | 当前无显式 `NewState` |
| 新建用例 | `NewUseCase(fullName)` | `NewUseCase('UseCaseModel.UC_01_SingleBallSorting')` | 用例建模 |
| 新建参与者 | `NewActor(fullName)` | `NewActor('UseCaseModel.Operator')` | 用例建模 |
| 新建值类型 | `NewValueType(fullName)` | `NewValueType('ParametricModel.Time_s')` | 参数模型 |
| 新建值属性 | `NewValueProperty(fullName)` | `NewValueProperty('ParametricModel.SystemParameters.cycleTimeTarget')` | 推荐挂在参数块下 |
| 新建组成属性 | `NewPartProperty(fullName)` | `NewPartProperty('ArchitectureModel.System.part_Scene')` | IBD 组成 |
| 新建代理端口 | `NewProxyPort(fullName)` | `NewProxyPort('ArchitectureModel.Scene.sceneOut')` | 推荐接口承载方式 |
| 新建接口块 | `NewInterfaceBlock(fullName)` | `NewInterfaceBlock('InterfaceModel.PerceptionIF')` | 接口定义名义载体 |
| 新建约束块 | `NewConstraintBlock(fullName)` | `NewConstraintBlock('ParametricModel.CycleTimeConstraint')` | 约束定义 |
| 新建约束属性 | `NewConstraintProperty(fullName)` | `NewConstraintProperty('ParametricModel.SystemParameters.cycleTimeConstraint')` | 参数图绑定 |
| 删除元素 | `DeleteElement(fullName)` | `DeleteElement('TmpPackage.Block1')` | 谨慎使用 |

---

## §4 需求操作

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 设置需求 ID | `SetRequirementId(fullName, newId)` | `SetRequirementId('RequirementModel.Functions.REQ_FUN_001', 'REQ-FUN-001')` | 推荐创建后立即设置 |
| 设置需求文本 | `SetRequirementText(fullName, newText)` | `SetRequirementText('RequirementModel.Functions.REQ_FUN_001', '系统应识别目标球位置...')` | 推荐创建后立即设置 |
| 新建需求指标 | `NewRequirementIndex(reqFullName, indexName, indexValue, indexUnit, indexDesc)` | `NewRequirementIndex('RequirementModel.Performance.REQ_PERF_001', 'T_cycle_avg', '<=10', 's', '单球平均节拍')` | 性能需求推荐显式挂指标 |
| 导出需求 Excel | `ExportReqExcel(path, fullName='')` | `ExportReqExcel('C://exports//requirements.xlsx', 'RequirementModel')` | 可导出某个包下全部需求 |
| 导出 ReqIF | `ExportReqIF(path, fullName='')` | `ExportReqIF('C://exports//requirements.reqif', 'RequirementModel')` | 按需使用 |

---

## §5 视图插入与布局

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 插入元素到视图 | `InsertElementToDiagram(fullElementName, fullDiagramName, position=None)` | `InsertElementToDiagram('ArchitectureModel.Scene', 'ArchitectureModel.BDD_SystemArchitecture', [120, 100])` | 许多关系要求两端先插图 |
| 打开视图 | `OpenDiagram(fullDiagramName)` | `OpenDiagram('ArchitectureModel.BDD_SystemArchitecture')` | 调试时有用 |
| 自动布局 | `AutoLayoutDiagram(fullDiagramName)` | `AutoLayoutDiagram('ArchitectureModel.BDD_SystemArchitecture')` | 建完图后建议调用 |
| 导出视图图片 | `ExportDiagramImage(path, fullDiagramName, includeBorder=True)` | `ExportDiagramImage('C://exports//bdd.png', 'ArchitectureModel.BDD_SystemArchitecture', True)` | 按需使用 |

---

## §6 用例图关系

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| Association | `CreateUseCaseAssociationLine(fullDiagramName, startElementName, endElementName)` | `CreateUseCaseAssociationLine('UseCaseModel.UCD_MainScenarios', 'UseCaseModel.Operator', 'UseCaseModel.UC_01_SingleBallSorting')` | 起点通常是参与者 |
| Include | `CreateUseCaseIncludeLine(fullDiagramName, startElementName, endElementName)` | `CreateUseCaseIncludeLine('UseCaseModel.UCD_MainScenarios', 'UseCaseModel.UC_02_BatchSorting', 'UseCaseModel.UC_01_SingleBallSorting')` | 用例到用例 |
| Extend | `CreateUseCaseExtendLine(fullDiagramName, startElementName, endElementName)` | `CreateUseCaseExtendLine('UseCaseModel.UCD_MainScenarios', 'UseCaseModel.UC_05_ExceptionRecoveryValidation', 'UseCaseModel.UC_02_BatchSorting')` | 按语义使用 |

---

## §7 需求图关系

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| Containment | `CreateRequirementContainmentLine(fullDiagramName, startElementName, endElementName)` | `CreateRequirementContainmentLine('RequirementModel.REQ_SystemRequirements', 'RequirementModel.Scenes.REQ_SCN_001', 'RequirementModel.Scenes.REQ_SCN_003')` | 父需求到子需求 |
| Derive | `CreateRequirementDeriveLine(...)` | `CreateRequirementDeriveLine(...)` | 派生关系 |
| Refine | `CreateRequirementRefineLine(...)` | `CreateRequirementRefineLine(...)` | 细化关系 |
| Trace | `CreateRequirementTraceLine(...)` | `CreateRequirementTraceLine(...)` | 泛追溯 |
| Verify | `CreateRequirementVerifyLine(...)` | `CreateRequirementVerifyLine(...)` | 验证关系 |
| Satisfy | `CreateRequirementSatisfyLine(fullDiagramName, startElementName, endElementName)` | `CreateRequirementSatisfyLine('RequirementModel.REQ_SystemRequirements', 'FunctionalModel.FUNC_PRD_FUN_03_PerceiveAndSelect', 'RequirementModel.Functions.REQ_FUN_001')` | **终点必须是需求** |

### `satisfy` 重要约束

- 需求不要全部散列为平级元素；应先建立顶层需求到子需求的 containment 层次，再继续 satisfy/verify/trace
- 创建子需求时优先直接按父需求路径新建，必要时再用 `CreateRequirementContainmentLine(...)` 补足图上层次关系
- 起点：功能块、活动块等实现元素
- 终点：需求元素
- 推荐落在 `REQ Diagram`
- 不要写成 `需求 -> 功能`，否则会报 `The end element must be a requirement`
- 在 MCP 工具可用时，优先调用高层工具 `create_satisfy_trace(...)`，它会自动插入两端元素、创建 satisfy 连线并执行布局。

---

## §8 活动图操作

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 创建初始节点 | `CreateActivityInitialNode(fullDiagramName, graphName='', position=None)` | `CreateActivityInitialNode('BehaviorModel.ACT_Main.Diagram', 'InitialNode', [60, 180])` | 流程起点 |
| 创建结束节点 | `CreateActivityFinalNode(fullDiagramName, graphName='', position=None)` | `CreateActivityFinalNode('BehaviorModel.ACT_Main.Diagram', 'FinalNode', [1600, 180])` | 流程终点 |
| 创建流终止节点 | `CreateActivityFlowFinalNode(...)` | `CreateActivityFlowFinalNode('BehaviorModel.ACT_Main.Diagram', 'FlowFinal', [1400, 300])` | 终止单个流 |
| **创建决策节点** | `CreateActivityDecisionNode(fullDiagramName, graphName='', position=None)` | `CreateActivityDecisionNode('BehaviorModel.ACT_Main.Diagram', 'DecisionCheck', [400, 200])` | **条件分支** |
| **创建合并节点** | `CreateActivityMergeNode(fullDiagramName, graphName='', position=None)` | `CreateActivityMergeNode('BehaviorModel.ACT_Main.Diagram', 'MergeResult', [800, 200])` | **分支合并** |
| **创建分叉节点** | `CreateActivityForkNode(fullDiagramName, graphName='', position=None)` | `CreateActivityForkNode('BehaviorModel.ACT_Main.Diagram', 'ForkParallel', [500, 200])` | **并发分叉（横向）** |
| **创建汇合节点** | `CreateActivityJoinNode(fullDiagramName, graphName='', position=None)` | `CreateActivityJoinNode('BehaviorModel.ACT_Main.Diagram', 'JoinParallel', [900, 200])` | **并发汇合（横向）** |
| 创建纵向分叉节点 | `CreateActivityForkVerticalNode(...)` | `CreateActivityForkVerticalNode('ACT.Diagram', 'ForkV', [300, 200])` | 纵向布局 |
| 创建纵向汇合节点 | `CreateActivityJoinVerticalNode(...)` | `CreateActivityJoinVerticalNode('ACT.Diagram', 'JoinV', [700, 200])` | 纵向布局 |
| **创建事件节点** | `CreateActivityEventNode(fullDiagramName, graphName='', position=None)` | `CreateActivityEventNode('BehaviorModel.ACT_Main.Diagram', 'WaitEvent', [200, 200])` | **等待事件触发** |
| **创建信号节点** | `CreateActivitySignalNode(fullDiagramName, graphName='', position=None)` | `CreateActivitySignalNode('BehaviorModel.ACT_Main.Diagram', 'SendSignal', [600, 200])` | **发送/接收信号** |
| **创建时间事件节点** | `CreateActivityTimeEventNode(fullDiagramName, graphName='', position=None)` | `CreateActivityTimeEventNode('BehaviorModel.ACT_Main.Diagram', 'Timer', [300, 200])` | **时间触发** |
| 创建控制流 | `CreateActivityControlFlowLine(fullDiagramName, startElementName, endElementName, lineName='')` | `CreateActivityControlFlowLine('ACT.Diagram', 'ACT.StageA', 'ACT.StageB')` | 用元素全名；`lineName='[guard]'` 可设置守卫 |
| 按图形名创建控制流 | `CreateActivityControlFlowLineByGraphName(fullDiagramName, startGraphName, endGraphName, lineName='')` | `CreateActivityControlFlowLineByGraphName('ACT.Diagram', 'DecisionCheck', 'StageA', '[valid]')` | 用于控制节点；决策/选择出线必须带守卫 |
| 创建对象流 | `CreateActivityObjectFlowLine(fullDiagramName, startElementName, endElementName)` | `CreateActivityObjectFlowLine('ACT.Diagram', 'ACT.OutputA.out1', 'DecisionNode')` | 数据流；支持 `元素全名.端口名` |
| 按图形名创建对象流 | `CreateActivityObjectFlowLineByGraphName(fullDiagramName, startGraphName, endGraphName)` | `CreateActivityObjectFlowLineByGraphName('ACT.Diagram', 'ObjectA', 'ObjectB')` | 数据流 |
| 设置活动脚本 | `SetActivityScript(fullName, script, language='')` | `SetActivityScript('ACT.Calculate', 'force = mass * acc', 'Groovy')` | 活动内部处理逻辑 |

### 活动图建模推荐流程

1. `NewActivity(fullName)` 创建顶层活动
2. `NewACTDiagram(fullName)` 创建活动图（挂在顶层活动下）
3. `CreateActivityInitialNode(...)` 创建初始节点
4. `InsertElementToDiagram(...)` 插入活动节点（或使用已有的子活动）
5. `CreateActivityDecisionNode(...)` 创建决策节点（条件分支）
6. `CreateActivityForkNode(...)` 创建分叉节点（并发）
7. `CreateActivityControlFlowLineByGraphName(...)` 连接控制流
8. `CreateActivityMergeNode(...)` 创建合并节点
9. `CreateActivityJoinNode(...)` 创建汇合节点
10. `CreateActivityFinalNode(...)` 创建结束节点
11. `AutoLayoutDiagram(...)` 自动布局

### 非线性活动图最低标准

除非用户明确要求线性流程，自动生成活动图时不要只画 `Initial -> A -> B -> Final`。建议至少包含：

- 5 个以上动宾短语活动节点
- 1 组决策/合并节点，表达正常分支、异常分支或多路选择
- 1 组分叉/汇合节点，表达并发检查、并行准备或同步
- 仅当存在真实的外部触发、消息或定时语义时，才使用事件、信号或时间事件节点
- 1 条对象流，表达关键数据或工件传递
- 控制节点连线使用 `CreateActivityControlFlowLineByGraphName(...)`
- 普通活动节点必须有进入线和出线；不要把普通活动当作活动图起点或终点

### 非线性活动图脚本片段

```python
from sysbuilder_mcp_server.core import *

root = "BehaviorModel"
parent = f"{root}.执行任务流程"
diagram = f"{parent}.任务活动图"

NewActivity(parent)
NewACTDiagram(diagram)

actions = [
    ("接收任务指令", [180, 180]),
    ("解析任务参数", [360, 180]),
    ("执行主任务", [760, 120]),
    ("记录异常信息", [760, 280]),
    ("准备执行资源", [1040, 100]),
    ("校验安全条件", [1040, 240]),
    ("发送完成信号", [1320, 180]),
]
for name, pos in actions:
    full_name = f"{parent}.{name}"
    NewActivity(full_name)
    InsertElementToDiagram(full_name, diagram, pos)

CreateActivityInitialNode(diagram, "开始", [60, 180])
CreateActivityDecisionNode(diagram, "参数是否有效", [560, 180])
CreateActivityMergeNode(diagram, "分支汇合", [900, 180])
CreateActivityForkNode(diagram, "并行准备", [980, 180])
CreateActivityJoinNode(diagram, "准备完成", [1200, 180])
CreateActivityFinalNode(diagram, "结束", [1600, 180])

CreateActivityControlFlowLineByGraphName(diagram, "开始", "接收任务指令")
CreateActivityControlFlowLineByGraphName(diagram, "接收任务指令", "解析任务参数")
CreateActivityControlFlowLineByGraphName(diagram, "解析任务参数", "参数是否有效")
CreateActivityControlFlowLineByGraphName(diagram, "参数是否有效", "执行主任务", "[有效]")
CreateActivityControlFlowLineByGraphName(diagram, "参数是否有效", "记录异常信息", "[无效]")
CreateActivityControlFlowLineByGraphName(diagram, "执行主任务", "分支汇合")
CreateActivityControlFlowLineByGraphName(diagram, "记录异常信息", "分支汇合")
CreateActivityControlFlowLineByGraphName(diagram, "分支汇合", "并行准备")
CreateActivityControlFlowLineByGraphName(diagram, "并行准备", "准备执行资源")
CreateActivityControlFlowLineByGraphName(diagram, "并行准备", "校验安全条件")
CreateActivityControlFlowLineByGraphName(diagram, "准备执行资源", "准备完成")
CreateActivityControlFlowLineByGraphName(diagram, "校验安全条件", "准备完成")
CreateActivityControlFlowLineByGraphName(diagram, "准备完成", "发送完成信号")
CreateActivityControlFlowLineByGraphName(diagram, "发送完成信号", "结束")

CreateActivityObjectFlowLine(diagram, f"{parent}.解析任务参数", f"{parent}.执行主任务")
AutoLayoutDiagram(diagram)
```

### 活动命名规范

- 活动名采用**"动词 + 宾语"**格式
- ✅ 正确：`识别目标位置`、`执行抓取动作`、`发送完成信号`
- ❌ 错误：`目标识别`（名词化）、`抓取`（缺少宾语）

### 控制节点使用场景

| 节点类型 | 使用场景 |
|----------|----------|
| **决策节点** | 条件分支：`if-else`、多路选择 |
| **合并节点** | 多个分支合并为一个流 |
| **分叉节点** | 并发执行：多个流同时开始 |
| **汇合节点** | 并发结束：等待所有流完成 |
| **事件节点** | 仅在确有外部事件触发语义时使用 |
| **信号节点** | 仅在确有发送/接收信号语义时使用 |
| **时间事件节点** | 仅在确有定时/延时语义时使用 |

### 逻辑节点连线检查

活动图逻辑节点没有稳定的元素全名，必须用创建时的 `graphName` 连线：

- 初始节点：至少 1 条 outgoing 流
- 活动终止/流终止节点：至少 1 条 incoming 流
- 决策、合并、分叉、汇合、事件、信号、时间事件节点：至少 1 条 incoming 和 1 条 outgoing 流
- 除决策/选择节点的唯一输入线外，使用 `CreateActivityControlFlowLineByGraphName(diagram, startGraphName, endGraphName)` 连接控制节点；决策/选择节点的唯一输入线必须使用对象流
- 决策/选择图块的每条 outgoing 控制流必须设置守卫，格式为 `CreateActivityControlFlowLineByGraphName(diagram, "选择图块", "目标图块", "[条件]")`
- 守卫必须使用方括号包裹，例如 `[有效]`、`[无效]`、`[else]`
- 不要写无意义守卫；守卫应基于前置活动输出接口/输出端口名，例如前置端口 `speed_status` 可写成 `[speed_status == 正常]`
- 禁止创建后不连线的逻辑节点，否则活动图会出现孤立节点

### 活动节点连线检查

- 插入活动图的普通活动节点必须至少有 1 条进入线和 1 条出线。
- 起点使用 `CreateActivityInitialNode(...)`，终点使用 `CreateActivityFinalNode(...)` 或 `CreateActivityFlowFinalNode(...)`。
- 活动图中的每条流程路径都必须最终追踪到某个终止节点，不要留下无法到达 `CreateActivityFinalNode(...)` 或 `CreateActivityFlowFinalNode(...)` 的悬空路径。
- 活动节点可以通过控制流连接到其他活动，也可以通过对象流连接到活动输入/输出端口或其他活动。
- 若活动通过输入/输出端口传递数据，使用 `CreateActivityObjectFlowLine(...)` 或 `CreateActivityObjectFlowLineByGraphName(...)`。
- 优先使用 `CreateActivityObjectFlowLine(...)` 按完整元素名连接活动输入/输出端口；该接口也支持 `"元素全名.端口名"` 形式，并可写成类似 `"活动1.out1" -> "DecisionNode"`。
- 禁止只创建进入线或只创建出线的普通活动节点。
- 每个普通活动默认只允许 1 条输入线；若存在多路汇聚需求，应改用合并节点或汇合节点，不要把多条 incoming 线直接接到同一个活动。
- 决策/选择节点前必须由前置活动通过对象流提供判断数据，再基于该接口名设置守卫。
- 决策/选择节点的直接前置节点必须为普通活动，且前置活动与选择节点之间必须使用对象流连接，禁止使用控制流直接进入决策/选择节点，也不要同时保留对象流和控制流。
- 每个决策/选择节点只能有 1 条输入线。

### 活动脚本与对象流

- 当活动代表具体流程、算法、计算、控制逻辑或内部处理步骤时，可用 `SetActivityScript(fullName, script, language)` 设置脚本。
- 所有脚本默认使用 Groovy；除非用户明确指定其他语言，否则 `SetActivityScript(...)`、`SetOpaqueBehaviorScript(...)` 等脚本设置接口的语言参数固定传 `"Groovy"`。
- 脚本只表达活动内部处理；活动之间的数据、物料、参数、信号载荷或中间结果必须使用对象流表达。
- 脚本中不要写说明性函数、伪函数或自定义函数，例如 `integral(...)`、`derivative(...)`、`limit(...)`；直接展开成顺序赋值语句。
- 脚本相关数据的对象流必须显式连接到对应名称的输入/输出端口；不要把对象流直接连到脚本活动本身，否则 Sysbuilder 可能自动新建接口，破坏变量名对应关系。
- 对象流可连接活动的输入/输出端口；需要显式数据口时只创建 `NewInputPort(...)` 和 `NewOutputPort(...)`。
- 创建活动输入/输出端口后，应使用 `SetType(...)` 为其设置对应的数值类型；涉及数值计算、判断或对象流传递的端口不要保持未定型。除非用户明确要求自定义值类型，否则直接设置 `Real`、`Integer`、`Boolean`、`String` 等内置类型即可。
- 不要给活动增加未参与连接的接口/端口；凡创建在活动下的输入/输出端口，都应参与至少 1 条对象流。
- 凡创建在活动下的输出端口，都必须在该活动脚本中对同名变量显式赋值，例如 `out1 = 1`。
- 活动脚本中的变量只能使用该活动自己的输入/输出端口名；脚本变量出现前必须先在该活动下创建同名输入/输出端口。
- 输入端口读取对象流另一端端口读取器名称对应的变量值；输出端口把脚本同名变量继续通过对象流传出。
- 若对象流将前置活动输出送入选择节点用于判断，则前置活动脚本必须显式给出该输出值或计算表达式，例如 `out = 1`。
- 子活动图和活动脚本互斥：展开为流程用子活动图，表达内部实现用脚本。

```python
parent = "BehaviorModel.BrakeFlow"
diagram = f"{parent}.BrakeActivityDiagram"

NewActivity(parent)
NewACTDiagram(diagram)

NewActivity(f"{parent}.采集车速")
NewActivity(f"{parent}.计算制动需求")
NewActivity(f"{parent}.输出制动力")
NewOutputPort(f"{parent}.采集车速.vehicle_mass")
NewOutputPort(f"{parent}.采集车速.target_deceleration")
NewInputPort(f"{parent}.计算制动需求.vehicle_mass")
NewInputPort(f"{parent}.计算制动需求.target_deceleration")
NewOutputPort(f"{parent}.计算制动需求.brake_force")
NewInputPort(f"{parent}.输出制动力.brake_force")

InsertElementToDiagram(f"{parent}.采集车速", diagram, [160, 160])
InsertElementToDiagram(f"{parent}.计算制动需求", diagram, [420, 160])
InsertElementToDiagram(f"{parent}.输出制动力", diagram, [700, 160])

SetActivityScript(
    f"{parent}.计算制动需求",
    "integral_error = integral_error + speed_error * dt\nbrake_force = vehicle_mass * target_deceleration",
    "Groovy",
)

CreateActivityControlFlowLine(diagram, f"{parent}.采集车速", f"{parent}.计算制动需求")
CreateActivityControlFlowLine(diagram, f"{parent}.计算制动需求", f"{parent}.输出制动力")
CreateActivityObjectFlowLine(diagram, f"{parent}.采集车速.vehicle_mass", f"{parent}.计算制动需求.vehicle_mass")
CreateActivityObjectFlowLine(diagram, f"{parent}.采集车速.target_deceleration", f"{parent}.计算制动需求.target_deceleration")
CreateActivityObjectFlowLine(diagram, f"{parent}.计算制动需求.brake_force", f"{parent}.输出制动力.brake_force")
```

### 控制流与对象流区别

| 流类型 | 用途 | 连接对象 |
|--------|------|----------|
| **控制流** | 表达执行顺序 | 活动节点、控制节点 |
| **对象流** | 表达数据传递 | 对象节点、活动节点 |

控制流可通过第四个参数设置连线名称；当名称格式为 `[guard]` 时，Sysbuilder 会把它识别为控制流守卫。决策/选择图块的出线必须使用守卫判断方向。
活动图守卫中的逻辑与、逻辑或、逻辑非统一使用 `&&`、`||`、`!` 书写；不要使用 `and`、`or`、`not`，例如应写 `[target_valid == true && fault_flag == false]`。

---

## §9 状态机操作

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 创建初始节点 | `CreateStateInitialNode(fullDiagramName, graphName='', position=None)` | `CreateStateInitialNode('BehaviorModel.STM_Task.Diagram', 'InitialState', [100, 220])` | 骨架节点 |
| 创建结束节点 | `CreateStateFinalNode(...)` | `CreateStateFinalNode('BehaviorModel.STM_Task.Diagram', 'Completed', [1040, 220])` | 骨架节点 |
| 创建终止节点 | `CreateStateTerminateNode(...)` | `CreateStateTerminateNode('BehaviorModel.STM_Task.Diagram', 'Abort', [1040, 380])` | 异常终止 |
| 创建选择节点 | `CreateStateChoiceNode(...)` | `CreateStateChoiceNode('BehaviorModel.STM_Task.Diagram', 'DecisionNode', [340, 220])` | 条件分支 |
| 创建分叉节点 | `CreateStateForkNode(...)` | `CreateStateForkNode('BehaviorModel.STM_Task.Diagram', 'ParallelCheck', [560, 220])` | 并发 |
| 创建汇合节点 | `CreateStateJoinNode(...)` | `CreateStateJoinNode('BehaviorModel.STM_Task.Diagram', 'FeedbackJoin', [800, 220])` | 并发汇合 |
| **创建状态** | `CreateState(fullDiagramName, graphName='', position=None)` | `CreateState('BehaviorModel.STM_Task.Diagram', 'Idle', [200, 220])` | **核心：创建状态元素** |
| **创建组合状态** | `CreateCompositeState(fullDiagramName, graphName='', position=None)` | `CreateCompositeState('BehaviorModel.STM_Task.Diagram', 'Running', [300, 220])` | **自动创建1个区域** |
| **创建正交状态** | `CreateOrthogonalState(fullDiagramName, graphName='', position=None)` | `CreateOrthogonalState('BehaviorModel.STM_Task.Diagram', 'Processing', [400, 220])` | **自动创建2个区域** |
| 按图形名创建迁移 | `CreateStateTransitionLineByGraphName(fullDiagramName, startGraphName, endGraphName, lineName='')` | `CreateStateTransitionLineByGraphName('BehaviorModel.STM_Task.Diagram', 'InitialState', 'Idle', 'start_ok == true')` | **自动建图首选且必须使用 graphName；`lineName` 可设置迁移条件/守卫；若写条件变量，必须先在该状态机下创建同名值属性并设置类型与默认值** |
| 按元素名创建迁移 | `CreateStateTransitionLine(fullDiagramName, startElementName, endElementName, lineName='')` | `CreateStateTransitionLine('BehaviorModel.STM_Task.Diagram', 'BehaviorModel.STM_Task.Idle', 'BehaviorModel.STM_Task.Running', 'retry_count < 3')` | 仅用于已存在且确认完整名的状态元素；不要作为 ByGraphName 失败后的替代；若写条件变量，也必须先创建同名值属性 |
| 设置 Entry | `SetStateEntry(fullName, behaviorFullName)` | `SetStateEntry('AutoDoorV3.Behavior.DoorStateMachine.Closed', 'AutoDoorV3.Behavior.DoorStateMachine.EnterClosedAction')` | `fullName` 必须是状态完整元素名：状态机全名 + `.` + 状态名 |
| 设置 DoActivity | `SetStateDoActivity(fullName, behaviorFullName)` | `SetStateDoActivity('AutoDoorV3.Behavior.DoorStateMachine.Closed', 'AutoDoorV3.Behavior.DoorStateMachine.CloseDoorAction')` | `fullName` 必须是状态完整元素名；`behaviorFullName` 可直接传 `OpaqueBehavior` 全名 |
| 设置 Exit | `SetStateExit(fullName, behaviorFullName)` | `SetStateExit('AutoDoorV3.Behavior.DoorStateMachine.Closed', 'AutoDoorV3.Behavior.DoorStateMachine.ExitClosedAction')` | 不要传图名、graphName 或猜测别名 |
| 设置子状态机 | `SetStateSubMachine(fullName, subStateMachineFullName)` | `SetStateSubMachine('BehaviorModel.STM_Task.Running', 'BehaviorModel.STM_RunningDetail')` | 组合状态 |
| 创建区域 | `CreateStateRegion(fullName)` | `CreateStateRegion('BehaviorModel.STM_Task.Running')` | 正交状态 |

- 开始任何 Sysbuilder 自动建模任务前，先调用 `NewProject(...)` 新建模型工程，再继续后续元素和视图创建。
- 状态机下不要直接创建 `Activity` 作为状态局部动作；应在状态机下创建 `NewOpaqueBehavior(...)`，再用 `SetStateEntry/DoActivity/Exit(...)` 绑定。
- 绑定状态动作时，`fullName` 应写成“所属状态机全名 + `.` + 状态名”。
- 例如状态机全名为 `AutoDoorV3.Behavior.DoorStateMachine`、状态名为 `Closed` 时，应写成 `AutoDoorV3.Behavior.DoorStateMachine.Closed`。
- 若状态机下已经创建了行为元素，可直接按完整元素名绑定，例如 `SetStateDoActivity("AutoDoorV3.Behavior.DoorStateMachine.Closed", "AutoDoorV3.Behavior.DoorStateMachine.CloseDoorAction")`。

### 状态机建模推荐流程

1. `NewStateMachine(fullName)` 创建状态机
2. `NewSTMDiagram(fullName)` 创建状态机图
3. `CreateStateInitialNode(...)` 创建初始节点
4. `CreateState(...)` 创建各个状态节点
5. `CreateStateChoiceNode(...)` 创建选择节点
6. `CreateStateForkNode(...)` / `CreateStateJoinNode(...)` 创建并发分叉/汇合（如适用）
7. `CreateCompositeState(...)` 或 `CreateOrthogonalState(...)` 表达复合/并发状态（如适用）
8. `CreateStateTransitionLineByGraphName(...)` 连接状态迁移
9. `SetStateEntry/DoActivity/Exit(...)` 设置状态行为（可选但推荐至少一个）
10. `CreateStateFinalNode(...)` 或 `CreateStateTerminateNode(...)` 创建结束/异常终止节点
11. `AutoLayoutDiagram(...)` 自动布局

### 非线性状态机最低标准

除非用户明确要求简单状态机，自动生成状态机时不要只画 `Initial -> State -> Final`。建议至少包含：

- 4 个以上稳定状态节点，覆盖准备、运行、等待/暂停、故障/降级、完成等生命周期
- 1 个选择节点，表达条件分支、异常判断或模式选择
- 1 组分叉/汇合节点，或 1 个组合状态/正交状态，表达并发或复合状态
- 5 条以上迁移，覆盖正常路径、异常路径、恢复/重试路径和结束路径
- 至少 1 个状态绑定 entry、doActivity 或 exit 行为
- 建图完成后调用 `AutoLayoutDiagram(...)`

### 状态机连线强制规则

- 自动创建的状态机图块一律用 `CreateStateTransitionLineByGraphName(...)` 连线。
- `startGraphName` / `endGraphName` 必须和创建图块时的 `graphName` 完全一致，例如先 `CreateState(diagram, "空闲", ...)`，再 `CreateStateTransitionLineByGraphName(diagram, "初始", "空闲")`。
- 状态迁移可通过第四个参数 `lineName` 设置迁移条件/守卫，例如 `CreateStateTransitionLineByGraphName(diagram, "条件判断", "执行中", "target_detected == true")`。
- 迁移条件必须写成明确可判断的表达式，例如 `time > 1`、`target_detected == true`、`retry_count < 3`；不要只写 `1`、`2`、`加速`、`减速` 这类编号或标签。
- 状态迁移条件中的逻辑与、逻辑或、逻辑非统一使用 `&&`、`||`、`!` 书写；不要使用 `and`、`or`、`not`，例如应写 `launch_ready == true && mission_abort == false`。
- 迁移条件中的变量必须先以同名值属性创建在该状态机下，再在条件表达式中直接使用该值属性名。
- 状态机下的值属性必须设置默认值，再作为迁移条件变量或状态动作变量使用。
- 状态机下的值属性创建后，应使用 `SetType(...)` 设置对应的数值类型，例如 `Real`、`Integer`、`Boolean`、`String`。除非用户明确要求自定义值类型，否则直接设置内置类型即可，不需要额外创建值类型。
- 不要把完整元素名传给 `CreateStateTransitionLineByGraphName(...)`，例如禁止 `"BehaviorModel.STM.空闲"`。
- 不要在 `CreateStateTransitionLineByGraphName(...)` 失败后改用 `CreateStateTransitionLine(...)` 猜完整元素名；应检查图名、端点图块创建顺序和 `graphName` 拼写。

### 复杂状态机脚本片段

```python
root = "BehaviorModel"
stm = f"{root}.任务生命周期状态机"
diagram = f"{stm}.任务生命周期图"

NewStateMachine(stm)
NewSTMDiagram(diagram)

CreateStateInitialNode(diagram, "初始", [80, 220])
CreateState(diagram, "空闲", [220, 220])
CreateState(diagram, "准备中", [420, 220])
CreateStateChoiceNode(diagram, "条件判断", [620, 220])
CreateCompositeState(diagram, "执行中", [820, 160])
CreateState(diagram, "等待恢复", [820, 340])
CreateStateForkNode(diagram, "并发检查", [1040, 160])
CreateState(diagram, "监测中", [1220, 90])
CreateState(diagram, "记录中", [1220, 230])
CreateStateJoinNode(diagram, "检查完成", [1420, 160])
CreateState(diagram, "故障", [1220, 380])
CreateStateFinalNode(diagram, "完成", [1620, 160])
CreateStateTerminateNode(diagram, "终止", [1620, 380])

NewActivity(f"{root}.进入执行状态")
SetStateEntry(f"{stm}.执行中", f"{root}.进入执行状态")

CreateStateTransitionLineByGraphName(diagram, "初始", "空闲")
CreateStateTransitionLineByGraphName(diagram, "空闲", "准备中")
CreateStateTransitionLineByGraphName(diagram, "准备中", "条件判断")
CreateStateTransitionLineByGraphName(diagram, "条件判断", "执行中", "condition_ok == true")
CreateStateTransitionLineByGraphName(diagram, "条件判断", "故障", "condition_ok == false")
CreateStateTransitionLineByGraphName(diagram, "执行中", "并发检查")
CreateStateTransitionLineByGraphName(diagram, "并发检查", "监测中")
CreateStateTransitionLineByGraphName(diagram, "并发检查", "记录中")
CreateStateTransitionLineByGraphName(diagram, "监测中", "检查完成")
CreateStateTransitionLineByGraphName(diagram, "记录中", "检查完成")
CreateStateTransitionLineByGraphName(diagram, "检查完成", "完成")
CreateStateTransitionLineByGraphName(diagram, "故障", "等待恢复")
CreateStateTransitionLineByGraphName(diagram, "等待恢复", "准备中")
CreateStateTransitionLineByGraphName(diagram, "故障", "终止")

AutoLayoutDiagram(diagram)
```

### 状态命名规范

- 状态名必须是**稳定状态名词**，不是动作
- ✅ 正确：`Idle`（空闲）、`Running`（运行中）、`Completed`（已完成）
- ❌ 错误：`Start`（启动）、`Process`（处理）

---

## §10 BDD / IBD 结构建模

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| Composition | `CreateCompositionLine(fullDiagramName, startElementName, endElementName)` | `CreateCompositionLine('ArchitectureModel.BDD_SystemArchitecture', 'ArchitectureModel.ColorSortingSystem', 'ArchitectureModel.Scene')` | 推荐用于功能树和结构分解 |
| Aggregation | `CreateAggregationLine(...)` | `CreateAggregationLine(...)` | 按语义使用 |
| Directed Association | `CreateDirectedAssociationLine(...)` | `CreateDirectedAssociationLine(...)` | 按语义使用 |
| Connector | `CreateConnectorLine(fullDiagramName, startElementName, endElementName)` | `CreateConnectorLine('ArchitectureModel.ColorSortingSystem.IBD_SystemIntegration', 'ArchitectureModel.ColorSortingSystem.part_Scene', 'ArchitectureModel.ColorSortingSystem.part_Perception')` | 推荐用于 IBD |
| Allocate | `CreateAllocateLine(fullDiagramName, startElementName, endElementName)` | `CreateAllocateLine('TraceabilityModel.BDD_FunctionArchitectureTrace', 'FunctionalModel.FUNC_PRD_FUN_05_PlanSevenStageMotion', 'ArchitectureModel.Planning')` | 推荐只在 BDD 中使用 |
| 设置类型 | `SetType(fullName, newTypeName)` | `SetType('ArchitectureModel.ColorSortingSystem.part_Scene', 'ArchitectureModel.Scene')` | PartProperty / Port / ValueProperty 常用 |

### `allocate` 重要约束

- 推荐在 `BDD` 中使用
- 连线前先把两端元素都插入该 BDD
- 推荐端点方向：`功能块 -> 架构块`
- 在 MCP 工具可用时，优先调用高层工具 `create_allocate_trace(...)`，它会自动插入两端元素、创建 allocate 连线并执行布局。

### `connector` 重要约束

- 在 IBD 中创建 `CreateConnectorLine(...)` 前，先把相关组成属性/部件实例插入到同一个 IBD。
- 若端点写成 `partA.port1`、`partB.port2`，则 `partA`、`partB` 必须已经通过 `InsertElementToDiagram(...)` 插入到该 IBD。
- 不要假设仅凭端口限定名就能在图中解析 connector 端点；很多失败场景本质上是“组成属性未先插图”。

---

## §11 参数与约束

| 接口中文名 | 接口调用 | 调用示例 | 强制性说明 |
| --- | --- | --- | --- |
| 设置单位 | `SetUnit(fullName, newUnit)` | `SetUnit('ParametricModel.SystemParameters.cycleTimeTarget', 's')` | 值属性常用 |
| 设置默认值 | `SetDefaultValue(fullName, newValue)` | `SetDefaultValue('ParametricModel.SystemParameters.cycleTimeTarget', '10.0')` | 默认值建议显式设置 |
| 设置元类型 | `SetMetaType(fullName, metaClassName)` | `SetMetaType('ArchitectureModel.Scene', 'SysML.Block')` | 按需使用 |
| 设置约束表达式 | `SetConstraintExpression(fullName, expression)` | `SetConstraintExpression('ParametricModel.CycleTimeConstraint', 'T_cycle_avg <= 10.0')` | 约束块或约束属性 |
| 创建绑定连接器 | `CreateBindingConnectorLine(fullDiagramName, startElementName, endElementName)` | `CreateBindingConnectorLine('ParametricModel.SystemParameters.PAR', 'ParametricModel.SystemParameters.mass', 'ParametricModel.SystemParameters.cycleTimeConstraint.T_mass')` | 参数图/IBD 数据绑定 |

### 约束表达式变量规则

- 约束表达式中的变量只能使用已创建的接口名、端口名、值属性名或约束参数名。
- 调用 `SetConstraintExpression(...)` 前，必须先创建表达式中同名的模型元素。
- 约束表达式中不要写说明性函数、伪函数或自定义函数，例如 `integral(...)`、`derivative(...)`、`limit(...)`；只保留直接变量关系和代数/逻辑表达式。
- 参数图不要把参数、值属性、约束属性零散地摆放在图上；若存在数据传递或数值绑定关系，优先使用 `CreateBindingConnectorLine(...)` 显式连接。
- 例如表达式 `T_cycle_avg <= 10.0` 需要先创建 `T_cycle_avg`：

```python
NewConstraintBlock('ParametricModel.CycleTimeConstraint')
NewInputParam('ParametricModel.CycleTimeConstraint.T_cycle_avg')
SetConstraintExpression('ParametricModel.CycleTimeConstraint', 'T_cycle_avg <= 10.0')
```

- 禁止直接在表达式里使用未建模的临时变量。

### 推荐参数建模模式

1. `NewValueType`
2. `NewBlock('ParametricModel.SystemParameters')`
3. `NewValueProperty`
4. `SetType`
5. `SetUnit`
6. `SetDefaultValue`
7. `NewConstraintBlock`
8. `NewConstraintProperty`
9. `SetConstraintExpression`
10. `NewPARDiagram`
11. `CreateBindingConnectorLine(...)` 连接参数、端口、值属性和约束参数
