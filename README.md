# Sysbuilder MCP Server

> 内置 AI 模式使用 `SYSML_V1_API_HOST`、`SYSML_V1_API_PORT` 和 `SYSML_V1_INSTALL_DIR`，并通过
> `SYSBUILDER_WORKSPACE_DIR` 传递两代产品共用的工程目录。只要设置了 `SYSML_V1_API_PORT`，
> MCP 就只连接该端口，失败时不会启动或选择其他 Sysbuilder 实例。

`Sysbuilder MCP Server` 用于把 Sysbuilder 对外开放的 Python API 封装成 MCP tools，供 Codex、Claude Code 以及其他支持 MCP 的客户端调用。

## 目录结构

- `sysbuilder_mcp_server/`：MCP 服务主包
- `resources/`：建模规则、参考资料和提示资源
- `example/`：示例文件
- `install_mcp.ps1`：安装脚本，自动写入 MCP 客户端配置

其中，MCP 服务启动时会自动读取 `resources/` 下的规则摘要与技能入口，并把它们注入 MCP instructions。
如果资源目录不在默认位置，请通过 `--resources-dir` 或环境变量 `MCP_RESOURCES_DIR` 显式指定。

建模脚本、语义 JSON、架构权衡对象代码和分析图片等中间数据默认写入用户目录下的 `Sysbuilder/SysMLAIOutput`（Windows 下通常为 `%USERPROFILE%\Sysbuilder\SysMLAIOutput`）。可通过 `--output-dir` 或环境变量 `MCP_OUTPUT_DIR` 显式覆盖。

## 系统要求

- Windows 10/11 64 位
- 已安装 Sysbuilder，或可直接访问 `Sysbuilder.exe`
- 推荐使用 Sysbuilder 自带的 `external\Python311\python.exe`

## 单文件 EXE 与源码维护

`main` 分支维护 SysML v1 MCP；SysML v2 MCP 在独立分支中维护。开发源码、资源、测试和构建脚本应保留，EXE 是发布产物。
单文件 EXE 内嵌 Python、MCP、API 和建模资源，运行时不需要同目录中的 MCP 源码或资源目录。
修改 API、MCP 工具或建模规则后必须重新构建 EXE；外置文件变化不会自动更新已有 EXE。
产品原有的 `mworks.sysbuilder` Python API 属于 Sysbuilder 软件，不应作为 MCP 开发源码删除。

构建命令：

```powershell
.\scripts\build-onefile.ps1 -PythonPath "<Sysbuilder运行目录>\external\Python311\python.exe"
```

默认产物为仓库根目录的 `sysbuilder-mcp-server-win64.exe`。构建使用仓库中同步维护的
`sysbuilder_mcp_server/core/sysbuilder_api.py`、MCP 源码和 `resources/`。
现有 `install_mcp.ps1` 仍保留源码部署方式；使用单文件部署时，应将客户端启动命令配置为该 EXE。

## 安装

在当前目录执行：

```powershell
.\install_mcp.ps1
```

脚本会提示输入 Sysbuilder 安装目录或 `Sysbuilder.exe` 路径，然后自动写入 MCP 客户端配置。
如果 Sysbuilder 目录下没有自带 Python，也可以显式指定：

```powershell
.\install_mcp.ps1 -PythonPath E:\Python311\python.exe
```

当前会处理这些配置文件：

- Codex：`%USERPROFILE%\.codex\config.toml`
- Claude Desktop：`%USERPROFILE%\.claude.json`
- OpenCode：`%USERPROFILE%\.config\opencode\opencode.json`

安装脚本还会在当前目录生成一份通用示例：

```text
mcp_server_config.json
```

## MCP Tools

### 工具列表

当前服务提供 24 个核心工具，包括 2 个用户手册检索工具、4 个团队协同领域工具和 IBD 内部属性显示工具 `show_internal_properties`。

从用途上看，这些工具可以分为以下 7 类。

#### 1. 会话准备与生命周期

<table>
  <colgroup>
    <col style="width: 28%;" />
    <col style="width: 18%;" />
    <col style="width: 54%;" />
  </colgroup>
  <thead>
    <tr>
      <th>工具英文名</th>
      <th>工具中文描述</th>
      <th>工具具体功能描述</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>start</code></td>
      <td>启动 Sysbuilder 工具</td>
      <td>用于启动 Sysbuilder 并建立脚本连接。可直接传入 <code>process_path</code> 指向 <code>Sysbuilder.exe</code>，也可依赖安装脚本写入的默认路径。它通常是显式会话管理场景的第一步；在大多数建模工具调用里，服务也会自动尝试启动或连接。</td>
    </tr>
    <tr>
      <td><code>find</code></td>
      <td>查找会话工具</td>
      <td>用于发现当前可连接的 Sysbuilder 实例及端口信息。适合排查 MCP 服务已启动但尚未附着到目标 Sysbuilder 进程时的连接问题，也可用于多实例场景下确定可用端口。</td>
    </tr>
    <tr>
      <td><code>connect</code></td>
      <td>连接 Sysbuilder 工具</td>
      <td>用于连接已启动的 Sysbuilder 实例。若未显式传入 <code>port</code>，会优先查找可连接实例并自动选择第一个可用端口，适合在手工启动了 Sysbuilder 之后再接入 MCP 服务。</td>
    </tr>
    <tr>
      <td><code>exit</code></td>
      <td>关闭 Sysbuilder 工具</td>
      <td>用于调用底层 <code>Exit()</code> 关闭当前已连接的 Sysbuilder。这个工具只处理已建立连接的会话，不会在未连接时隐式启动或连接软件，适合在批处理完成后主动释放建模会话。</td>
    </tr>
  </tbody>
</table>

#### 2. API 查询与脚本化建模

<table>
  <colgroup>
    <col style="width: 28%;" />
    <col style="width: 18%;" />
    <col style="width: 54%;" />
  </colgroup>
  <thead>
    <tr>
      <th>工具英文名</th>
      <th>工具中文描述</th>
      <th>工具具体功能描述</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>lookup_sysbuilder_api</code></td>
      <td>API 查询工具</td>
      <td>用于查询 MCP 内置的 <code>sysbuilder_api.py</code> 接口清单，支持按 API 名称或关键词查找签名，适合在自然语言转脚本前先确认可用接口，减少“先猜 API 再返工”的情况。</td>
    </tr>
    <tr>
      <td><code>run_script</code></td>
      <td>建模脚本执行工具</td>
      <td>用于执行完整的 Sysbuilder Python 建模脚本，是自动化建模、需求建模、功能建模、架构建模、关系创建、视图生成等任务的核心入口。推荐先调用 <code>lookup_sysbuilder_api</code> 确认本次所需 API，再一次性生成完整建模脚本并传给本工具执行。</td>
    </tr>
  </tbody>
</table>

#### 3. 外部模型与需求导入

<table>
  <colgroup>
    <col style="width: 28%;" />
    <col style="width: 18%;" />
    <col style="width: 54%;" />
  </colgroup>
  <thead>
    <tr>
      <th>工具英文名</th>
      <th>工具中文描述</th>
      <th>工具具体功能描述</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>import_model</code></td>
      <td>模型导入工具</td>
      <td>用于将外部需求或模型文件导入到 Sysbuilder，当前支持需求 Excel、ReqIF 和 XML。可通过 <code>import_type=auto</code> 自动识别，也可显式指定导入类型，适合承担需求基线导入、第三方需求交换和既有模型迁移等任务。</td>
    </tr>
  </tbody>
</table>

#### 4. 模型生成与文档导出

<table>
  <colgroup>
    <col style="width: 28%;" />
    <col style="width: 18%;" />
    <col style="width: 54%;" />
  </colgroup>
  <thead>
    <tr>
      <th>工具英文名</th>
      <th>工具中文描述</th>
      <th>工具具体功能描述</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>generate_modelica_framework</code></td>
      <td>Modelica 框架生成工具</td>
      <td>用于调用 <code>GenerateModelicaSimulationFramework</code>，根据目标元素的完整名称生成 Modelica 仿真框架。适合在 SysML 模型已经具备一定结构后，向仿真侧继续推进模型落地和接口衔接。</td>
    </tr>
    <tr>
      <td><code>generate_system_design_report</code></td>
      <td>系统设计报告生成工具</td>
      <td>用于调用 <code>GenerateSystemDesignReport</code>，按 Sysbuilder 内置固定模板直接生成系统方案设计报告。适合在需求、结构和关系模型相对稳定后，快速输出正式设计报告用于评审、归档和方案沟通。</td>
    </tr>
    <tr>
      <td><code>generate_geometric_param_doc</code></td>
      <td>几何参数文档生成工具</td>
      <td>用于调用 <code>GenGeometricParam</code>，从模块定义图中提取目标模块的几何参数并生成 Markdown 文档。适合在结构模型稳定后输出参数说明和设计接口说明，并为后续 CAD 模型提供几何参数输入。</td>
    </tr>
    <tr>
      <td><code>export_semantic_json</code></td>
      <td>语义 JSON 导出工具</td>
      <td>用于调用 <code>ExportSemanticJson</code>，把当前工程或指定元素子树导出为 SysML2 语义树 JSON 文件。适合做模型语义检查、外部分析和数据归档。</td>
    </tr>
    <tr>
      <td><code>run_architecture_tradeoff</code></td>
      <td>架构权衡分析工具</td>
      <td>用于调用 <code>RunArchitectureTradeoff</code>，运行外部 Python 权衡脚本并导出分析图片。适合在架构方案比较、参数敏感性分析和评审材料生成时使用。</td>
    </tr>
  </tbody>
</table>

#### 5. 参数映射与约束验证

<table>
  <colgroup>
    <col style="width: 28%;" />
    <col style="width: 18%;" />
    <col style="width: 54%;" />
  </colgroup>
  <thead>
    <tr>
      <th>工具英文名</th>
      <th>工具中文描述</th>
      <th>工具具体功能描述</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>create_relation_mapping</code></td>
      <td>关系映射工具</td>
      <td>用于调用 <code>CreateRelationMapping</code>，按源变量到目标变量建立映射。支持需求指标、活动输入/输出接口、块值属性和约束输入/输出参数等可映射变量；建立前应保证两端类型、单位和值语义兼容。</td>
    </tr>
    <tr>
      <td><code>calculate_parametric_diagram</code></td>
      <td>参数图计算工具</td>
      <td>用于调用 <code>CalculateParametricDiagram</code> 执行约束计算，并读取 <code>parameter_calculation.json</code>。验证需求指标时，应同时核对计算值、约束满足状态和错误信息。</td>
    </tr>
  </tbody>
</table>

参数验证的推荐顺序为：创建并配置映射端点 -> 完成参数图约束与 binding connector -> 建立全部关系映射 -> 计算参数图 -> 检查结果 JSON。

#### 6. 帮助与使用说明

| MCP 工具 | 说明 |
| --- | --- |
| `search_sysbuilder_help` | 按自然语言问题搜索《MWORKS.Sysbuilder 用户手册》，返回相关 PDF 页码和原文片段。 |
| `read_sysbuilder_help_pages` | 读取指定的连续手册页，一次最多 5 页，用于补充完整操作步骤。 |

回答 Sysbuilder 界面、菜单、快捷键和操作流程问题时，应先调用
`search_sysbuilder_help`，必要时再调用 `read_sysbuilder_help_pages`，并在回答中标注手册 PDF 页码。

#### 7. 团队协同与仓库版本管理

21 个软件协同 API 收敛为 4 个领域工具，通过 `action` 选择具体操作。这样既保留完整能力，也避免 MCP 工具列表过长。

| MCP 工具 | action |
| --- | --- |
| `team_session` | `login`、`logout`、`info` |
| `team_resources` | `list_remote`、`search_public`、`list_local`、`create_group`、`update_group`、`delete_group`、`create_repository`、`clone_repository`、`clone_group`、`publish_project` |
| `team_repository` | `status`、`commit`、`pull`、`push` |
| `team_history` | `list`、`details`、`restore_files`、`reset_version` |

推荐工作流：

1. `team_session(action="login", ...)` 登录后，用 `action="info"` 确认会话。
2. 用 `team_resources` 查询 `resourcePath`，再执行分类、克隆或发布操作。
3. 对当前团队工程先调用 `team_repository(action="status")`，再提交、拉取和推送。
4. 删除分类、还原文件或重置版本前必须获得用户明确确认，并传 `confirm=true`。

登录密码仅传给底层 `LoginTeam`，MCP 结果不会回显密码。

## 说明

- 对建模任务，AI 客户端应优先按“`lookup_sysbuilder_api` -> 生成完整 Python 建模脚本 -> `run_script`”的顺序执行
- 如果使用开发版或自定义构建目录，可以直接在安装脚本里输入 `Sysbuilder.exe` 的完整路径

## 许可协议

本项目采用 MIT 许可证授权，有关详细信息，请参阅 [LICENSE](./LICENSE) 文件。
