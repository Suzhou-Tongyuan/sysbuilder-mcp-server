# Sysbuilder MCP Server

`Sysbuilder MCP Server` 用于把 Sysbuilder 对外开放的 Python API 封装成 MCP tools，供 Codex、Claude Code 以及其他支持 MCP 的客户端调用。

## 目录结构

- `sysbuilder_mcp_server/`：MCP 服务主包
- `resources/`：建模规则、参考资料和提示资源
- `example/`：示例文件
- `install_mcp.ps1`：安装脚本，自动写入 MCP 客户端配置

其中，MCP 服务启动时会自动读取 `resources/` 下的规则摘要与技能入口，并把它们注入 MCP instructions。
如果资源目录不在默认位置，请通过 `--resources-dir` 或环境变量 `MCP_RESOURCES_DIR` 显式指定。

## 系统要求

- Windows 10/11 64 位
- 已安装 Sysbuilder，或可直接访问 `Sysbuilder.exe`
- 推荐使用 Sysbuilder 自带的 `external\Python311\python.exe`

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

当前服务提供 10 个核心工具，聚焦 Sysbuilder 的模型构建、需求导入、API 查询、模型生成及文档导出，支撑复杂系统设计建模。

从用途上看，这些工具可以分为以下 4 类。

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
  </tbody>
</table>

## 说明

- 对建模任务，AI 客户端应优先按“`lookup_sysbuilder_api` -> 生成完整 Python 建模脚本 -> `run_script`”的顺序执行
- 如果使用开发版或自定义构建目录，可以直接在安装脚本里输入 `Sysbuilder.exe` 的完整路径

## 许可协议

本项目采用 MIT 许可证授权，有关详细信息，请参阅 [LICENSE](./LICENSE) 文件。
