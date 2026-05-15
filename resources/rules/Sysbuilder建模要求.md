> 强制要求：所有建模 Python 脚本必须使用 UTF-8 编码。

# 📘 Sysbuilder SysML 自动建模规范（标准版）

## 一、目标软件

- **软件名称**：Sysbuilder  
- **路径输入规则**：所有文件路径输入统一使用 `//`

### 必须：
- 必须使用 UTF-8 编码 Python 脚本，该要求为强制执行项
- 凡新增、修改、执行的 Sysbuilder 建模脚本，必须先确认脚本文件本身为 UTF-8 编码后再运行
- 凡涉及 Sysbuilder 的自动化建模、Modelica 生成、报告生成脚本，若不是 UTF-8 编码，必须先修正后执行，禁止跳过
---

## 二、总体执行原则

1. **必须执行优先，不停留解释**
   - 所有任务直接进入建模执行流程
   - 禁止只描述不操作
   - 禁止将“最小联通验证”作为独立前置步骤；除非为处理异常，否则应直接执行正式建模流程

2. **禁止反复迭代脚本，优先向下推进**
   - 正式建模执行过程中，若遇到局部步骤失败，应优先保持主线继续向下推进
   - 禁止围绕同一局部问题反复改脚本、反复从头重跑
   - 应优先完成主体模型、关键视图、Modelica 生成与报告生成，再对残留局部问题补充说明
   - 若某一步确实无法继续，需明确说明阻塞点，而不是进入无休止脚本迭代
3. **建模前必须先启动或连接 Sysbuilder**
  - 要进行建模，默认必须先调用 `StartSysbuilder` 打开软件并建立当前会话
  - `StartSysbuilder` 成功后，应直接继续建模；不要再额外调用 `FindSysbuilder` 或 `ConnectSysbuilder`
  - 只有当用户明确要求“连接已有实例”或“查看当前可用实例/端口”时，才允许调用 `FindSysbuilder` / `ConnectSysbuilder`
  - 若 `StartSysbuilder` 失败，可报告软件启动阻塞；不要默认退回到“先 find 再 connect”的旧流程
4. **所有命令必须串行执行**
   - 所有 Sysbuilder 相关命令、脚本语句与 MCP 工具调用必须逐条串行执行，上一条命令返回结果后才能继续下一条
   - 禁止并发发送多个建模命令，禁止在上一条命令尚未返回时继续创建元素、关系、视图或连线
   - 若某条命令执行失败，必须先根据返回结果处理失败原因，再决定是否继续后续步骤；不要在未知状态下继续向下执行
5. **建模失败，不保存，重新再建模**
6. **所有中间文件生成到output文件夹**
7. **不做联通检查，直接写脚本运行软件**
8. **模型没有根元素名，直接从包开始新建**
---

### 2.1 脚本导入与 API 使用前置检查

- 自动建模脚本默认不需要导入 `mworks.sysbuilder` 或 `mworks.sysbuilder.sysbuilder_api`。
- MCP 场景下，开始任何 Sysbuilder 建模任务前，必须先阅读 `resources/rules/Sysbuilder建模要求.md`；涉及脚本/API 时还必须阅读 `resources/quickref/sysbuilder_python_api.md`。
- 开始任何 Sysbuilder 自动建模任务前，必须先主动调用 `NewProject(...)` 新建模型工程，再继续包、图和元素创建；不要在未显式新建工程的前提下直接开始建模。
- 若本次任务明确要求生成 DoDAF 模型，则调用 `NewProject(...)` 新建工程时，`projectType` 必须显式指定为 `dodaf`。
- MCP 场景下应优先采用“先查 API，再写脚本”的流程：先调用 `lookup_sysbuilder_api` 确认本次要使用的 API 名称与签名，再一次性输出完整脚本。
- 命名规则需要先固定：元素全名使用 `.` 分层，且不要带工程名前缀。
- 在 MCP `run_script` 中，Sysbuilder API 已自动注入，可直接调用 `NewProject(...)`、`NewBlock(...)`、`NewActivity(...)`、`CreateRequirementSatisfyLine(...)` 等函数。
- 如需显式导入，只允许使用：`from sysbuilder_mcp_server.core import *`。
- 禁止使用未在 `resources/quickref/sysbuilder_python_api.md` 或 `sysbuilder_mcp_server/core/sysbuilder_api.py` 中出现的 API。
- 生成脚本前必须核对 API 名称和签名；不确定时查 quickref 或 `sysbuilder_mcp_server.core`，不要编造函数名。
- 写脚本时应先一次性确定本次建模要用的 API 集合，再输出完整脚本；不要反复进入“查 quickref -> 改一点 -> 再查 quickref -> 再重写”的循环。
- 若发现某个 API 未公开，必须立即改写为当前公开 API 的等价模式，而不是继续尝试相似命名函数。
- AI 生成脚本时应直接按 quickref 的命名和示例模式落地，不要输出“让我查阅参考文档”“让我重新编写脚本”“让我再试另一种 API”这类过程性自述。
- 常见错误示例：`NewObjectNode`、`CreateObjectNode`、`CreateActivityActionNode`、`NewActivityActionNode`、`CreateSwimlane`、`NewSwimlane`、`CreateActivityPartition`、`NewActivityPartition`、`CreateActivityParameterNode`、`NewActivityParameterNode` 等当前未公开接口不得直接使用。
- 当前没有公开的对象节点/活动参数节点 API；活动图需要对象流数据端点时，活动接口只使用 `NewInputPort(...)` 和 `NewOutputPort(...)`，再用 `CreateActivityObjectFlowLine(...)` 连接这些端点。
- 当前没有公开的泳道/活动分区 API；责任分配应通过包、命名、块或 allocate 关系表达，不要编造 swimlane/partition 函数。
- 若 `run_script` 返回 `api_preflight` 错误，必须先修正导入和 API 名称，再重新执行脚本。

## 三、工程管理规范

### 3.1 新建工程

- 新建模型前必须执行：
  - ✅ 新建工程
- 工程文件：
  - 后缀：`.sybprojz`
- 存储规则：
  - 若未指定路径 → 使用 Sysbuilder 工作目录
- 工程名与元素全名规则：
  - ❗ 元素全名必须从 **工程内顶层元素** 开始书写
  - ❌ 不要写成 `工程名.模型名.元素名`
  - ✅ 应写成 `模型名.元素名`
  - 例如：根包创建应使用 `固体发动机系统模型`
  - 例如：子元素创建应使用 `固体发动机系统模型.需求模型`

---

### 3.2 工程保存规则

| 操作类型 | 是否必须保存 |
|--------|-------------|
| 新建模型 | ✅ 必须保存 |

---

## 四、建模通用规范

### 4.1 命名规范

- 所有元素名称：
  - 建议使用 **中文**
- 同级目录：
  - ❗ 名称必须唯一

---

### 4.2 视图完整规范

1. SysML九张视图都必须生成

---

### 4.2 视图操作规范

1. 插入所有图块后执行自动布局

---

## 五、包图规范

### 5.1 包图要求

- 必须建立：
  - 📌 包之间的包含关系连线  

---

## 六、需求建模规范

### 6.1 需求分层结构

顶层需求建议包含：

- 功能需求  
- 性能需求  
- 集成接口需求  
- 通用质量特性需求  

- 需求必须形成层次结构，不能把所有需求都作为完全零散的平级元素创建
- 至少应存在“顶层需求 -> 子需求”的包含关系；功能、性能、接口、质量等需求应按语义归入对应父需求下
- 自动建模时，应优先先确定需求树，再创建后续 `Satisfy`、`Verify`、`Trace` 等关系

需求建议新建指标

---

### 6.2 子需求

- 每个顶层需求下：
  - 必须按语义创建子需求（分层）
- 创建方式要求：
  - ✅ 应直接按父需求路径创建子需求
  - ✅ 推荐写法：`模型名.需求模型.功能需求.点火功能需求`
  - ❌ 不要先创建为同级需求，再依赖后续 `Containment` 调整层级
- 原因说明：
  - 在 Sysbuilder 中，若先创建为平级需求，再建立 `Containment`，子需求的实际全名会变为 `父需求.子需求`
  - 若脚本仍使用旧路径创建 `Satisfy`、`Verify`、`Trace` 等关系，会出现“元素不存在”错误
- 执行约束：
  - 建立需求关系前，必须以最终层级路径作为需求全名

---

### 6.3 需求关系

必须建立：

- 包含关系（Containment）  
- 满足关系（Satisfy）：
  满足关系是活动或者块连接到需求
  每个需求建议都有满足连线
- 路径校验要求：
  - 在创建 `Satisfy` 前，必须确认需求元素路径已经是包含关系建立后的最终路径
  - 若需求存在父子分层，连线目标应写为完整分层路径，而不是创建前的平级路径

---

## 七、活动建模规范

### 7.1 活动分层

- 活动必须支持：
  - 子活动结构  
- 活动图挂载要求：
  - ✅ 活动图优先创建在顶层活动下，采用”顶层活动 + 子活动图”的方式组织
  - ✅ 推荐写法：先创建 `模型名.行为模型.固体发动机推进流程`，再创建 `模型名.行为模型.固体发动机推进流程.固体发动机推进活动图`
  - ❌ 不建议直接在行为包下创建活动图后再向图中插入活动
- 执行约束：
  - 自动建模时，必须先创建承载该图的顶层活动，再创建对应子活动图
  - 若活动图创建成功但无法插入活动元素，应优先检查活动图是否挂载在活动节点下，而不是继续重试插入

### 7.2 活动命名规范

- 活动名采用**”动词 + 宾语”**格式
- ✅ 正确：`识别目标位置`、`执行抓取动作`、`发送完成信号`
- ❌ 错误：`目标识别`（名词化）、`抓取`（缺少宾语）

### 7.3 活动图建模流程

- 活动图建模推荐顺序：
  1. ✅ `NewActivity(fullName)` 创建顶层活动
  2. ✅ `NewACTDiagram(fullName)` 创建活动图（挂在顶层活动下）
  3. ✅ `CreateActivityInitialNode(...)` 创建初始节点
  4. ✅ `InsertElementToDiagram(...)` 插入活动节点
  5. ✅ `CreateActivityDecisionNode(...)` 创建决策节点（条件分支）
  6. ✅ `CreateActivityForkNode(...)` 创建分叉节点（并发）
  7. ✅ `CreateActivityControlFlowLineByGraphName(...)` 连接控制流
  8. ✅ `CreateActivityMergeNode(...)` 创建合并节点
  9. ✅ `CreateActivityJoinNode(...)` 创建汇合节点
  10. ✅ `CreateActivityFinalNode(...)` 创建结束节点

- 非平凡业务流程的活动图不得只生成线性链路。除非用户明确要求“简单流程/线性流程”，自动建模时必须优先生成具备以下结构的可读活动图：
  - 至少 1 组“决策节点 + 合并节点”，用于表达条件分支或异常路径
  - 至少 1 组“分叉节点 + 汇合节点”，用于表达并发执行或并行检查
  - 仅当存在明确的外部触发、消息交互或定时等待语义时，才使用事件、信号或时间事件节点；不要为了凑复杂度随意创建
  - 回环应服务于明确的重试、轮询、等待恢复或闭环控制语义；不是很必要时，应减少活动图中的回环数量，避免仅为“看起来复杂”而制造往返路径
  - 能表达数据传递时，至少补充 1 条对象流；若当前 API 无法创建对象节点，可用活动节点之间的对象流表达主要数据交付
  - 所有控制节点连线优先使用 `CreateActivityControlFlowLineByGraphName(...)`
  - 建图完成后必须调用 `AutoLayoutDiagram(...)`

- 活动节点数量建议不少于 5 个，命名应体现真实动作；禁止只用 `步骤1`、`处理`、`执行` 这类弱语义名称。
- 普通活动节点不得作为活动图的起点或终点：
  - 每个插入活动图的普通活动必须至少有 1 条进入线和 1 条出线
  - 活动图起点必须使用 `CreateActivityInitialNode(...)`
  - 活动图终点必须使用 `CreateActivityFinalNode(...)` 或 `CreateActivityFlowFinalNode(...)`
  - 活动图中的每条流程路径都必须最终追踪到某个终止节点；不要留下无法到达 `CreateActivityFinalNode(...)` 或 `CreateActivityFlowFinalNode(...)` 的悬空路径
  - 活动节点之间可用控制流连接，也可通过对象流连接到接口、端口、参数或其他活动
  - 若活动通过接口/端口/参数传递数据，必须用 `CreateActivityObjectFlowLine(...)` 或 `CreateActivityObjectFlowLineByGraphName(...)` 表达
  - 禁止只给活动节点画进入线或只画出线；普通活动必须处于流程内部

### 7.4 控制节点使用规范

| 节点类型 | API | 使用场景 |
|----------|-----|----------|
| **决策节点** | `CreateActivityDecisionNode` | 条件分支：`if-else`、多路选择 |
| **合并节点** | `CreateActivityMergeNode` | 多个分支合并为一个流 |
| **分叉节点** | `CreateActivityForkNode` | 并发执行：多个流同时开始 |
| **汇合节点** | `CreateActivityJoinNode` | 并发结束：等待所有流完成 |
| **事件节点** | `CreateActivityEventNode` | 仅在确有外部事件触发语义时使用 |
| **信号节点** | `CreateActivitySignalNode` | 仅在确有发送/接收信号语义时使用 |
| **时间事件节点** | `CreateActivityTimeEventNode` | 仅在确有定时/延时语义时使用 |

- 禁止创建无连线的活动图逻辑节点：
  - 初始节点必须至少有 1 条 outgoing 控制流
  - 活动终止节点和流终止节点必须至少有 1 条 incoming 控制流或对象流
  - 决策、合并、分叉、汇合、事件、信号、时间事件节点必须至少有 1 条 incoming 和 1 条 outgoing 流
  - 逻辑节点没有 SysML 元素全名，连接时必须使用创建节点时传入的 `graphName`
  - 除决策/选择节点的唯一输入线外，逻辑节点连线优先使用 `CreateActivityControlFlowLineByGraphName(...)`；决策/选择节点的唯一输入线必须使用对象流
  - 决策/选择图块的每条 outgoing 控制流必须设置守卫，用于判断流程方向；调用格式为 `CreateActivityControlFlowLineByGraphName(diagram, "选择图块", "目标图块", "[条件]")`
  - 守卫必须使用方括号包裹，例如 `[参数有效]`、`[参数无效]`、`[else]`；不要只写普通连线名称
  - 不要创建仅表达判断结论的守卫文本，例如 `[目标有效]`、`[距离安全]`、`[距离过近]`、`[无目标]`；守卫必须显式引用进入该决策节点前的活动输出接口/输出端口/输出参数名，并写成可判断表达式，例如前置输出端口是 `speed_status`，守卫可写成 `[speed_status == 正常]`
  - 若使用 `CreateActivityObjectFlowLineByGraphName(...)`，同样必须使用准确的 `graphName`

### 7.5 决策与合并配对原则

- 决策节点后**必须**有对应的合并节点
- 每个决策分支必须在 outgoing 控制流上设置守卫条件，用于区分分支方向
- 守卫条件通过控制流 `lineName` 参数设置，格式必须是 `[guard]`，并且应显式引用前置输出端口/参数名，例如 `CreateActivityControlFlowLineByGraphName(diagram, "参数是否有效", "执行主任务", "[param_status == 有效]")`
- 活动图守卫中的逻辑与、逻辑或、逻辑非统一使用 `&&`、`||`、`!` 书写；不要使用 `and`、`or`、`not`，例如应写 `[target_valid == true && fault_flag == false]`
- 决策/选择节点前必须有明确的数据来源；前置活动的输出端口或输出参数必须通过对象流进入用于判断的接口，再基于该接口名书写守卫
- 决策/选择节点的直接前置节点必须为普通活动，而不是另一个控制节点；前置活动与选择节点之间必须使用对象流连接，禁止使用控制流直接进入决策/选择节点，也不要同时保留一条对象流和一条控制流
- 每个决策/选择节点只能有 1 条输入线；不要给同一个决策/选择节点连接多条 incoming 线
- 每个普通活动默认只允许 1 条输入线；若存在多路汇聚需求，应改用合并节点或汇合节点，不要把多条 incoming 线直接连接到同一个活动
- 不要在缺少前置数据端口的情况下随意创建选择节点和守卫；如果没有真实判断变量，就不要硬加决策分支
- 合并节点前的所有分支都应到达

### 7.6 分叉与汇合配对原则

- 分叉节点后**必须**有对应的汇合节点
- 分叉产生的所有并发流都必须汇合
- 汇合节点等待所有并发流完成后才继续

### 7.7 控制流与对象流

- **控制流**：表达执行顺序，使用 `CreateActivityControlFlowLine`
- **对象流**：表达数据传递，使用 `CreateActivityObjectFlowLine`
- 对象流应与接口定义保持一致
- 活动之间若传递数据、物料、参数、信号载荷或中间结果，必须使用对象流表达；不要用控制流代替数据传递
- 可使用 `CreateActivityObjectFlowLine(fullDiagramName, startElementName, endElementName)` 按元素全名连接活动、端口、参数或接口；该接口也支持 `"元素全名.端口名"` 形式，并可用于类似 `"活动1.out1" -> "DecisionNode"` 的对象流端点写法
- 优先使用 `CreateActivityObjectFlowLine(...)` 以完整元素名连接活动端口和活动接口；若脚本无法稳定解析逻辑节点端点，再改用 `CreateActivityObjectFlowLineByGraphName(...)`
- 若需要显式表达活动的数据输入/输出，活动接口只创建 `NewInputPort(...)` 和 `NewOutputPort(...)`，再使用对象流连接
- 创建活动输入/输出端口后，应按其实际语义立即设置对应的数值类型；涉及数值计算、判断或对象流传递的活动端口，不要保持未定型，应用 `SetType(...)` 显式设置为 `Real`、`Integer`、`Boolean`、`String` 或其它合适类型。除非用户明确要求自定义值类型，否则直接设置内置类型即可，不需要额外创建值类型。
- 不要给活动增加未参与连接的接口/端口；凡创建在活动下的输入/输出端口，都应参与至少 1 条对象流
- 凡创建在活动下的输出端口，其同名变量都必须在该父活动的脚本中显式赋值；不要只创建接口名而不在脚本中定值
- 与活动脚本变量相关的数据传递必须显式连接到对应名称的输入/输出端口，不要把对象流直接连到活动本身
- 若活动图中的活动端口需要向下游传递数据，必须为其父活动设置脚本，明确给出输出端口的值或计算表达式；这些计算表达式可以基于该父活动的输入端口名。
- 若对象流将前置活动的输出送入选择节点用于分支判断，则前置活动必须设置脚本，显式给出连接到该选择节点的输出端口的值或计算表达式，例如 `out = 1`、`distance_status = "safe"`、`score = speed / limit`
- 例如脚本活动 `...计算制动需求` 使用变量 `vehicle_speed`，应先创建 `...计算制动需求.vehicle_speed`，对象流终点也应写成 `...计算制动需求.vehicle_speed`，而不是 `...计算制动需求`
- 若对象流直接指向活动，Sysbuilder 可能自动创建新的接口用于连接，导致脚本变量名与对象流端点不再一一对应
- 若后续存在决策/选择节点，前置活动的输出判断值也应通过输出端口/输出参数显式建模，并通过对象流连接到判断所依赖的接口；不要只靠守卫文字口头描述条件

### 7.8 脚本规则（关键）

| 类型 | 规则 |
|------|------|
| 普通活动 | 可设置脚本 |
| 子活动图 | ❗ 与脚本互斥 |
| 不透明行为 | ✅ 必须设置脚本 |

- 当某个普通活动代表具体流程、算法、计算、控制逻辑或内部处理步骤时，可以调用 `SetActivityScript(fullName, script, language)` 为该活动设置脚本
- 所有脚本默认使用 Groovy；除非用户明确指定其他语言，否则调用 `SetActivityScript(...)`、`SetOpaqueBehaviorScript(...)` 等脚本设置接口时，语言参数都应传 `"Groovy"`
- 活动脚本只描述该活动内部如何处理数据；活动之间的数据传递仍必须通过对象流建模
- 活动脚本中不要使用说明性函数、伪函数、自定义函数或数学占位函数，例如 `integral(...)`、`derivative(...)`、`limit(...)`、`filter(...)`
- 活动脚本应展开为直接可执行的顺序赋值语句；需要积分、累加、限幅、状态更新时，直接写成显式变量更新表达式
- 活动脚本中的变量只能使用该活动自己的输入/输出端口名；不得直接引用其他活动的接口名、全局变量名或未建模的临时变量名
- 使用活动脚本变量前，必须先在该活动下创建同名输入/输出端口，例如脚本使用 `vehicle_speed` 和 `brake_force` 时，应先创建 `NewInputPort("...计算制动需求.vehicle_speed")` 和 `NewOutputPort("...计算制动需求.brake_force")`
- 反过来，凡在该活动下创建了输出端口，也必须在该活动脚本中出现同名赋值语句，例如创建了 `...检查车辆状态.out1` 后，脚本中必须显式写出 `out1 = ...`
- 脚本输入变量应由同名输入端口读取对象流另一端端口读取器名称对应的变量值；脚本输出变量应通过同名输出端口继续用对象流传递
- 当父活动承担数据汇总、判定或计算职责时，应在其脚本中显式写出输出端口/输出参数的赋值语句，例如 `distance_status = "安全"`、`target_speed = distance_value / dt`；若输出依赖输入，则表达式可直接基于输入端口/输入参数名书写。
- 因此涉及脚本变量的数据对象流必须以具体接口/端口/参数为端点，例如 `CreateActivityObjectFlowLine(diagram, "...采集车速.vehicle_speed", "...计算制动需求.vehicle_speed")`
- 设置脚本前应先创建对应活动，例如 `NewActivity("BehaviorModel.Flow.计算制动需求")` 后再调用 `SetActivityScript("BehaviorModel.Flow.计算制动需求", "...", "Groovy")`
- 不要同时把同一个活动建成子活动图入口又给它设置脚本；需要展开流程时用子活动图，需要表达内部实现时用脚本

---

### 7.3 状态机建模规范

#### 7.3.1 状态机创建流程

- 状态机建模必须遵循以下顺序：
  1. ✅ `NewStateMachine(fullName)` 创建状态机
  2. ✅ `NewSTMDiagram(fullName)` 创建状态机图
  3. ✅ `CreateStateInitialNode(...)` 创建初始节点
  4. ✅ `CreateState(...)` 创建各个状态节点
  5. ✅ `CreateStateChoiceNode(...)` 创建选择节点（条件分支）
  6. ✅ `CreateStateForkNode(...)` / `CreateStateJoinNode(...)` 创建并发分叉/汇合（如存在并发状态）
  7. ✅ `CreateCompositeState(...)` 或 `CreateOrthogonalState(...)` 表达复杂状态（如存在嵌套或并发区域）
  8. ✅ `CreateStateTransitionLineByGraphName(...)` 连接状态迁移
  9. ✅ `SetStateEntry/SetStateDoActivity/SetStateExit(...)` 设置状态行为（如已有活动/状态机/不透明行为）
  10. ✅ `CreateStateFinalNode(...)` 或 `CreateStateTerminateNode(...)` 创建结束/异常终止节点（如需要）

- 非平凡对象生命周期的状态机不得只生成 `Initial -> State -> Final`。除非用户明确要求简单状态机，自动建模时必须优先生成具备以下结构的状态机图：
  - 至少 4 个稳定状态节点，覆盖准备、运行、等待/暂停、故障/降级、完成等真实生命周期状态
  - 至少 1 个选择节点 `CreateStateChoiceNode(...)`，用于表达条件分支、异常判断或模式选择
  - 至少 1 组分叉/汇合节点，或至少 1 个组合状态/正交状态，用于表达并发区域、复合运行状态或多子状态管理
  - 至少 5 条状态迁移，迁移必须覆盖正常路径、异常路径、恢复/重试路径和结束路径
  - 至少 1 个状态应设置 entry、doActivity 或 exit 行为；行为元素必须先创建，再用 `SetStateEntry(...)`、`SetStateDoActivity(...)` 或 `SetStateExit(...)` 绑定
  - 回环/自循环只应在确有重试、等待条件变化、恢复重入或持续运行语义时使用；不是很必要时，应减少状态机图中的回环数量
  - 建图完成后必须调用 `AutoLayoutDiagram(...)`

#### 7.3.1.1 状态机变量与不透明行为

- 创建状态机图时，如需在整个状态机范围内共享“全局变量/状态变量”，可将相关值类型、值属性创建在该状态机下统一管理。
- 这些值属性必须显式设置默认值；默认值用于表达状态机启动时的初始变量状态。若有单位和基础数据类型，也应一并显式设置。
- 状态机下的值属性在创建后应尽快使用 `SetType(...)` 设置对应的数值类型；涉及计时、计数、模式、标志和测量值的变量，不要保持未定型，应显式设置为 `Real`、`Integer`、`Boolean`、`String` 或其它合适类型。除非用户明确要求自定义值类型，否则直接设置内置类型即可，不需要额外创建值类型。
- 状态迁移条件中使用的变量，必须先以同名值属性的形式创建在该状态机下；不要在迁移条件里直接使用未建模的临时变量名。
- 状态机下不要直接创建活动；若需要在状态机局部定义可供状态调用的动作逻辑，应在该状态机下创建 `OpaqueBehavior`，不要在该状态机下创建 `Activity` 代替。
- 如需对这些值属性进行赋值、更新或计算，可在状态机下创建不透明行为，并编辑脚本处理这些值属性。
- 不透明行为脚本中可直接使用这些值属性的元素名作为变量名，不必再额外发明未建模的临时变量名。
- 当状态需要执行某段变量处理逻辑时，可将该不透明行为作为状态动作绑定到状态上，使状态在 `entry`、`doActivity` 或 `exit` 阶段执行该不透明行为。
- 绑定状态动作时，状态的全名应写成“所属状态机全名 + `.` + 状态名”，例如状态机全名为 `AutoDoorV3.Behavior.DoorStateMachine`、状态名为 `Closed` 时，状态全名应写成 `AutoDoorV3.Behavior.DoorStateMachine.Closed`。
- 若状态机下已经创建了活动、不透明行为或其他可作为状态动作的行为元素，可直接按完整元素名绑定，例如 `SetStateDoActivity("AutoDoorV3.Behavior.DoorStateMachine.Closed", "AutoDoorV3.Behavior.DoorStateMachine.CloseDoorAction")`。
- 若状态动作脚本依赖多个状态机级值属性，应先在状态机下完成这些值属性的创建与默认值设置，再创建不透明行为并绑定到对应状态。

#### 7.3.2 状态命名规范

- 状态名必须是**稳定状态名词**，不是动作：
  - ✅ 正确：`空闲`、`运行中`、`已完成`、`故障`
  - ❌ 错误：`启动`、`处理`、`停止`
- 状态名建议使用中文

#### 7.3.3 状态行为设置

- 状态可设置三种行为：
  - `entry`：进入状态时执行的动作
  - `do`：在状态中持续执行的活动
  - `exit`：离开状态时执行的动作
- 设置方式：
  - 先创建状态：`CreateState('STM.Diagram', 'Running', [200, 200])`
  - 再设置行为：`SetStateEntry('STM.Running', 'ACT_EnterRunning')`

#### 7.3.4 组合状态与正交状态

- **组合状态**：包含子状态的复杂状态
  - 方式1：使用 `CreateCompositeState(...)` 创建，自动带1个区域
  - 方式2：使用 `SetStateSubMachine(stateName, subStateMachineName)` 设置子状态机
- **正交状态**：包含多个并发区域的状态
  - 使用 `CreateOrthogonalState(...)` 创建，自动带2个区域
  - 可使用 `CreateStateRegion(stateName)` 额外添加区域

#### 7.3.5 迁移连线规则

- 自动创建状态机图时，所有由 `CreateStateInitialNode(...)`、`CreateState(...)`、`CreateCompositeState(...)`、`CreateOrthogonalState(...)`、`CreateStateChoiceNode(...)`、`CreateStateForkNode(...)`、`CreateStateJoinNode(...)`、`CreateStateFinalNode(...)`、`CreateStateTerminateNode(...)` 创建的图块，迁移连线必须统一使用 `CreateStateTransitionLineByGraphName(...)`
- `CreateStateTransitionLineByGraphName(fullDiagramName, startGraphName, endGraphName, lineName="")` 的第二、第三参数必须是创建图块时传入的 `graphName`，只能是简单图形名，不要写完整元素名，不要包含 `.`
- 状态迁移可通过 `CreateStateTransitionLine(...)` 或 `CreateStateTransitionLineByGraphName(...)` 的第四个参数 `lineName` 设置迁移条件/守卫；自动建图时优先使用 `CreateStateTransitionLineByGraphName(diagram, startGraphName, endGraphName, condition)`。
- 状态迁移条件必须写成明确可判断的布尔表达式，例如 `time > 1`、`speed_status == 正常`、`retry_count < 3`；不要只写 `1`、`2`、`加速`、`减速`、`[停止运行]` 这类编号或标签式文本。
- 状态迁移条件中的逻辑与、逻辑或、逻辑非统一使用 `&&`、`||`、`!` 书写；不要使用 `and`、`or`、`not`，例如应写 `launch_ready == true && mission_abort == false`
- 迁移条件中出现的变量名必须与该状态机下已创建的值属性名一致；若条件为 `time > 1`，则必须先在状态机下创建名为 `time` 的值属性，并按需设置默认值。
- 当同一个状态或控制节点引出多条状态迁移时，最多只允许 1 条无条件迁移；其余迁移必须显式设置可判断的迁移条件，避免多条默认路径并存。
- 自动建模脚本中不要把 `CreateStateTransitionLine(...)` 作为失败后的替代方案；它只适合连接已存在且能确认完整元素名的状态元素，不适合连接刚用 `CreateState*` 创建的图块
- 若状态机迁移失败，应优先检查：目标状态机图是否创建成功、所有端点图块是否已创建、端点 `graphName` 是否完全一致、是否错误传入了完整路径
- 迁移应尽量明确事件、条件和动作；其中条件/守卫可通过迁移 API 的 `lineName` 参数显式设置，事件与动作如当前脚本未覆盖，可在 GUI 中补充。
- 选择节点出线必须语义可区分：目标状态名应能体现条件结果，例如 `运行中`、`故障`、`降级运行`、`等待恢复`
- 分叉节点后必须有对应汇合节点；并发分支不能悬空

---

## 八、块（Block）建模规范

### 8.1 块结构

- 每个块：
  - 建议包含 **代理端口**
  - 包含几何参数值属性
- 代理端口创建规则：
  - ❗ **不能直接创建在组成属性下面**
  - ✅ 必须先创建在 **块类型** 上
  - ✅ 再由部件实例在 **IBD** 中继承使用
- 值属性
  - 建议设置默认值、设置单位、设置基础数据类型（Real\Integer\String\Boolean）
- 新建组成属性有两种方式，优先考虑第一种
-   第一种是在模块定义图中建立组合连线
-   第二种是新建组成属性元素

---

### 8.2 分配关系

必须建立：

- 活动 → 块 分配关系 
- 每个块建议都有分配关系 

实现方式：

1. 模块定义图中建立分配关系   

---

## 九、IBD（内部模块图）规范

### 9.1 连接规则

- 连接对象：
  - ❗ 必须通过 **子代理端口连接**
  - 每个属性都需要连接
- 避免：
  - 直接连接属性  
- 若想为内部模块图中的组成属性增加接口/端口，不要直接在组成属性上创建；应先在该组成属性的**类型块**上创建对应接口/端口，再由 IBD 中的组成属性实例继承和使用。
- 使用 `CreateConnectorLine(...)` 在 IBD 中连接端口前，必须先将相关组成属性/部件实例插入到该 IBD；若端口所在组成属性未先插图，端口可能无法在图中解析，导致 connector 创建失败。
- 当 connector 端点写成 `partA.port1`、`partB.port2` 这类限定名时，应先确认 `partA`、`partB` 对应的组成属性已经通过 `InsertElementToDiagram(...)` 插入到同一个 IBD。

---

## 十、参数与约束规范

### 10.1 约束必须包含

| 内容 | 要求 |
|------|------|
| 表达式 | ✅ 必须 |
| 输入参数 | 右值 |
| 输出参数 | 左值 |

- 输入参数：
  - 建议设置默认值、设置单位、设置基础数据类型（Real\Integer\String\Boolean）

- 执行限制：
  - ❗ 输入参数和输出参数创建后，**不能再单独设置方向**
  - ❗ 约束属性下，**不能创建输入参数和输出参数**
  - ✅ 约束参数应创建在约束块下，而不是创建在约束属性下
  - ✅ 参数图中的参数、端口、值属性、约束属性之间可使用绑定连接器传递数据，优先用 `CreateBindingConnectorLine(...)` 建立明确连接关系
  - ❌ 不要创建完全零散的参数图；参数图应体现“参数源 -> 约束/计算 -> 输出参数”的结构，而不是只把元素散放在图上
  - ✅ 若参数图中存在端口、值属性、约束参数或约束属性之间的数据对应关系，应显式创建 binding connector，而不是仅靠名称暗示
  - ✅ 约束表达式是基于接口/端口/参数名称的表达式，表达式中的变量只能使用已创建的接口名、端口名或约束参数名
  - ✅ 使用到约束表达式的变量前，必须先创建同名接口/端口/参数，例如 `T_cycle_avg <= 10.0` 必须先创建名为 `T_cycle_avg` 的端口、值属性或约束参数
  - ❌ 禁止在 `SetConstraintExpression(...)` 中直接使用没有对应模型元素的临时变量名
  - ❌ 约束表达式中不要使用说明性函数、伪函数、自定义函数或数学占位函数，例如 `integral(...)`、`derivative(...)`、`limit(...)`、`filter(...)`
  - ✅ 约束表达式应写成直接的变量关系或代数/逻辑表达式，不要把算法过程、状态更新或函数调用写进 `SetConstraintExpression(...)`
  - ✅ 推荐顺序：先 `NewInputParam/NewOutputParam/NewReturnParam` 或 `NewProxyPort/NewInputPort/NewOutputPort/NewValueProperty`，再 `SetConstraintExpression`

---

### 10.2 示例结构

```
输出参数 = 表达式(输入参数)
```

---

## 十一、追踪与分析（必须）

系统必须创建：

1. 需求功能追溯矩阵  
2. 架构功能追溯矩阵  
3. 需求表格  
4. 架构表格  
5. 追溯分析图

👉 使用 Sysbuilder API 专用接口
- 创建规则：
  - ✅ 应先切换或定位到目标追踪分析包
  - ✅ 调用接口时只传图名，不传完整路径
  - ✅ 推荐做法：先创建独立追踪分析包，再在该包下创建表格/矩阵

### 11.2 执行约束

- 使用追踪分析专用接口前，必须先确认当前创建上下文已定位到目标包
- 若专用接口返回路径相关错误，应优先检查是否误传完整路径，而不是重复创建同名视图

---

## 十二、生成

- 生成几何参数文档必须调用API接口GenGeometricParam
- 生成Modelica仿真框架必须调用API接口GenerateModelicaSimulationFramework

---


## 十三、完成标准（验收条件）

任务完成必须满足：

- ✅ 软件成功启动  
- ✅ 已创建 SysML 工程  
- ✅ 工程已保存  
- ✅ 模型元素已生成  
- ✅ 关系已建立  
- ✅ 视图已生成  

---

## ✅ 总结

> 基于 Sysbuilder API，自动创建符合 SysML 规范的工程模型，包含完整需求、活动、块、参数与约束建模，建立追溯关系、分配关系与视图，并保证模型结构清晰、层级完整、元素命名规范、复杂度达标。
