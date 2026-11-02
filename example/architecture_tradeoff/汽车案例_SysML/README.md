# 汽车案例架构权衡示例

本目录用于给 AI 客户端提供架构权衡脚本生成参考。

- `车辆案例.sybprojz`：Sysbuilder 汽车案例工程。
- `architect_test.py`：示例架构权衡分析脚本，演示如何使用模型对象属性生成雷达图和条形图。

推荐执行链路：

1. 打开目标 Sysbuilder 工程。
2. 调用 `ExportArchitectureTradeoffObjectCode(path)` 导出当前工程的 Python 对象代码。
3. 基于导出的对象代码编写新的分析脚本，复用对象变量和值属性。
4. 调用 `RunArchitectureTradeoff(scriptPath, imageDir)` 生成图片。
5. 返回图片截图，并给出基于指标的方案权衡结论。
