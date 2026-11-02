import json
import inspect
import sys
import os
import ast
from .sysbuilder_connect import MwConnect
from .decorator import mw_connect_decorator,path_resolver

_MwConnect = MwConnect()

def Help(cmd: str = None):
    if cmd == None or cmd == "":
        msg = " Help(): 显示本信息。 \n Help(String command_name): 显示指定命名的文档。 \n ListFunctions(): 列出所有函数。 \n"
        print(msg)
    elif isinstance(cmd, str):
        cur_global = globals()
        if inspect.isfunction(cur_global.get(cmd, None)):
            return help(cur_global.get(cmd, None))
        else:
            print(f"  未找到函数： {cmd}")
    elif inspect.isfunction(cmd):
        return help(cmd)

def ListFunctions(return_list: bool = False):
    """
    列出所有命令函数
    
    语法
        >>> ListFunctions()
    说明
        ListFunctions() 用于列出所有命令函数，结果每行每个元素表示函数的名字和描述。
    示例
    示例1：列出所有命令函数示例
        打印所有命令函数
        >>> print(ListFunctions())
        结果：

    输入参数
        无
    返回值
        `str`：每个元素表示函数的名字和描述，并使用'\\n'分割
    另请参阅
        无
    """
    
    # Use utf-8-sig to safely handle files saved with UTF-8 BOM.
    with open(os.path.abspath(__file__), "r", encoding="utf-8-sig") as source_file:
        source_code = source_file.read()
    parsed_code = ast.parse(source_code)
    functions = []
    for node in ast.walk(parsed_code):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            if not (f"{func_name}".startswith('_') or f"{func_name}" == "ListFunctions" or f"{func_name}" == "Echo"): #去除不显示的函数
                docstring = ast.get_docstring(node)
                if docstring != None:
                    docstring = docstring.split('\n', 1)[0]
                functions.append(f"{func_name}: {docstring}")
                print(f"{func_name}: {docstring}");
    if return_list:
        return functions
listfunctions = ListFunctions

def _run_func(func, locals_dict) -> str:
    params = inspect.signature(func).parameters
    args = tuple(locals_dict[k] for k in params.keys() if k in locals_dict)
    expected_types = [v.annotation for k, v in params.items()]
    return _MwConnect.__RunCurrentFunction__(func, args=args, kwargs={}, expected_types=expected_types)


@mw_connect_decorator(_MwConnect._process_path)
def GetDirectory():
    """
    获取工作目录
    
    语法
        >>> GetDirectory()
    说明
        GetDirectory() 用于获取工作目录。
    示例
    示例1：获取当前工作目录路径示例
        获取当前工作目录并打印
        >>> print(GetDirectory())
        结果：
        > C:/Users/TR/Documents/Sysbuilder
    输入参数
        无
    返回值
        `str` : 工作目录
    另请参阅
        无
    """
    return _run_func(GetDirectory, locals())
    
@mw_connect_decorator(_MwConnect._process_path)
def SetDirectory(path: str = ""):
    """
    设置工作目录
    
    语法
        >>> SetDirectory(path:str)
    说明
        SetDirectory(path) 用于设置当前的工作目录。执行成功后，后续的文件操作将默认在该路径下进行。
    示例
        示例1：设置工作目录为指定路径
        >>> print(SetDirectory("C:/Users/TR/Documents/NewProject"))
        结果：
        > True
    输入参数
        path - 目标工作目录的绝对路径
        数据类型：str
    返回值
        `str` : 设置结果（通常为成功/失败的状态信息）
    另请参阅
        无
    """
    return _run_func(SetDirectory, locals())   
    
@mw_connect_decorator(_MwConnect._process_path)
def SetLicensePath(path: str):
    """
    设置许可证路径
    
    语法
        >>> SetLicensePath(path:str)
    说明
        SetLicensePath(path) 用于设置许可证路径。多个路径之间以“ ; ”分割，许可证文件全路径中，不允许有 @ 符号，True表示应用成功。
    示例
    示例1：本地许可证文件格式示例
        加载本地许可证文件，path为file@ + 许可证路径
        >>> SetLicensePath("file@C:\Program Files\MWORKS\License.txt")
        结果：
        > True
    示例2：许可证服务器格式示例
        从服务器加载许可证，path为server@ + 许可证服务器地址
        >>> SetLicensePath("server@172.16.1.36")
        结果：
        > True
    输入参数
        path - 许可证文件的绝对路径
        数据类型：str
    返回值
        `bool` : 设置结果
    另请参阅
        无
    """
    return _run_func(SetLicensePath, locals())

@mw_connect_decorator(_MwConnect._process_path)
def GetVersion():
    """
    获取软件版本号
    
    语法
        >>> GetVersion()
    说明
        GetVersion() 用于获取当前 Sysbuilder 软件的具体版本号，并将其打印。
    示例
        示例1：查看当前软件版本
        >>> print(GetVersion())
        结果：
        > "1.2.0"
    返回值
        `str` : 软件版本号
    另请参阅
        无
    """
    return _run_func(GetVersion, locals())

@mw_connect_decorator(_MwConnect._process_path)
def GetLanguage():
    """
    获取当前系统语言
    
    语法
        >>> GetLanguage()
    说明
        GetLanguage() 用于获取 Sysbuilder 当前界面显示的语言设置，并将其打印。
    示例
        示例1：获取当前语言
        >>> print(GetLanguage())
        结果：
        > "Chinese"
    返回值
        `str` : 当前语言名称
    另请参阅
        无
    """
    return _run_func(GetLanguage, locals())

@mw_connect_decorator(_MwConnect._process_path)
def SetLanguage(language: str = "zh_CN"):
    """
    设置系统语言
    
    语法
        >>> SetLanguage(language:str)
    说明
        SetLanguage(language) 用于设置 Sysbuilder 的系统显示语言，目前支持Chinese(需输入zh_CN)和English（需输入en）。
    示例
        示例1：将语言切换为英文
        >>> print(SetLanguage("en"))
        结果：
        > True
    输入参数
        language - 目标语言标识（如 "zh_CN", "en"）
        数据类型：str
    返回值
        `bool` : 设置成功返回 True
    另请参阅
        无
    """
    return _run_func(SetLanguage, locals())
    
@mw_connect_decorator(_MwConnect._process_path)
def Exit():
    """
    退出Sysbuilder
    
    语法
        >>> Exit()
    说明
        Exit() 用于退出 Sysbuilder 程序。若存在未保存的修改，系统将直接强制退出，不弹出提示。
    示例
        示例1：退出软件
        >>> Exit()
    返回值
        无
    另请参阅
        无
    """
    return _run_func(Exit, locals())    
    
@mw_connect_decorator(_MwConnect._process_path)
def Echo(on : bool = None):
    """
    设置/获取是否打开“反馈每条语句的执行结果”功能，如果不传入参数，则返回当前状态
    
    语法
        >>> Echo(on="")
    说明
        Echo(on="") 用于设置/获取是否打开“反馈每条语句的执行结果”功能，打开则传入True，关闭则传入False，如果不传入参数，则返回当前状态。
    示例
    示例1：打开和关闭“反馈每条语句的执行结果”功能
        打开“反馈每条语句的执行结果”功能
        >>> print("打开“反馈每条语句的执行结果”功能")
        >>> Echo(on=True)
        >>> LoadLibrary("Projectica")
        >>> SimulateProject("Projectica.Mechanics.MultiBody.Examples.Elementary.DoublePendulum")
        >>> ClearAll()
        >>> print("关闭“反馈每条语句的执行结果”功能")
        >>> Echo(on=False)
        >>> LoadLibrary("Projectica")
        >>> SimulateProject("Projectica.Mechanics.MultiBody.Examples.Elementary.DoublePendulum")
        结果：
        > 打开“反馈每条语句的执行结果”功能
        >
        > True
        > True
        >
        > 关闭“反馈每条语句的执行结果”功能
    示例2：查询“反馈每条语句的执行结果”功能状态
        查询”反馈每条语句的执行结果”功能状态
        >>> print(Echo())
        >>> Echo(on=True)
        >>> print(Echo())
        结果：
        > False
        > True
    输入参数
        on - 设置状态
        数据类型：bool
    返回值
        `bool` : 表示该功能是否开启
    另请参阅
        无
    """
    if on is None:
        return _MwConnect.get_echo_on()
    else:
        _MwConnect.set_echo_on(on)
        return True

@mw_connect_decorator(_MwConnect._process_path)
@path_resolver(['path'], True, GetDirectory, Echo, check_empty=True)
def OpenProjectFile(path:str, autoReload:bool = True) -> bool:
    """
    打开模型文件,支持sybproj、sybprojx、sybprojz、sybprojxl、sybprojzl文件，不会有是否保存的提示

    语法
        >>> OpenProjectFile(path)
    说明
        OpenProjectFile(path) 加载指定的Project模型文件，支持sybproj、sybprojx、sybprojz、sybprojxl、sybprojzl文件。
        默认情况下，会自动重新加载模型。
    示例
    示例1：默认参数加载指定Projectica模型文件
        DoublePendulum.mo默认存储在%安装路径%/Docs/Samples/PythonAPI文件夹下
        加载指定的Projectica模型文件，支持.mol、.mef和.mo文件
        >>> OpenProjectFile(r"C:\\Program Files\\MWORKS\\example.sybprojz")
    输入参数
        path - 工程文件的全路径
        数据类型：str
    返回值
        `bool` : 表示模型是否成功打开
    另请参阅
        无
    """
    return _run_func(OpenProjectFile, locals())
    
@mw_connect_decorator(_MwConnect._process_path)
def NewProject(projectName:str = "", projectPath:str = "", projectFormat:str = "", projectType:str = "") -> str:
    """
    新建模型
    
    语法
        >>> NewProject(projectName:str = "", projectPath:str = "", projectFormat:str = "", projectType:str = "")
    说明
        NewProject(projectName, projectPath, projectFormat, projectType) 用于新建模型，函数返回`str`表示新建工程文件名。
        后缀仅由projectFormat决定；projectName中的`.`按名称字符处理，不参与后缀解析。
        当projectFormat为空时，默认使用`sybprojz`；当projectType为空时，默认按`sysml`处理。
    示例
    示例1：按默认配置新建一个模型
        不限定任何参数，按照默认配置新建一个模型。
        >>> print(NewProject())
        结果：
        > Project6
    示例2：设置参数新建一个模型
        指定名称、路径、格式和类型创建模型。
        >>> print(NewProject(projectName="NewProject", projectPath="C://Users//TR//Desktop", projectFormat="sybprojz", projectType="sysml"))
        结果：
        > NewProject.sybprojz
    输入参数
        projectName - 模型名称（不解析后缀，允许包含`.`），缺省时自动生成`SysbuilderN`
        数据类型：str
        projectPath - 模型路径，缺省时会使用工作目录
        数据类型：str
        projectFormat - 模型格式，支持sybproj、sybprojx、sybprojz、sybprojxl、sybprojzl，缺省时默认`sybprojz`
        数据类型：str
        projectType - 模型类型，请在sysml、dodaf和all中选择一个，缺省时按sysml处理
        数据类型：str
    返回值
        `str` : 返回新建工程文件名（包含后缀）
    另请参阅
        无    
    """
    return _run_func(NewProject, locals())
    
@mw_connect_decorator(_MwConnect._process_path)
def ImportXML(path: str = ""):
    """
    导入XML文件
    
    语法
        >>> ImportXML(path:str)
    说明
        ImportXML(path) 用于将外部 XML 格式的模型或数据文件导入到 Sysbuilder 当前环境中。
    示例
        示例1：导入指定的 XML 模型文件
        >>> print(ImportXML("C:/Users/TR/Documents/ModelData.xml"))
        结果：
        > True
    输入参数
        path - XML 文件的绝对路径
        数据类型：str
    返回值
        `bool` : 导入成功返回 True，否则返回 False
    另请参阅
        无
    """
    return _run_func(ImportXML, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ExportXML(path: str = "", modelName: str = "SysbuilderRootModel") -> str:
    """
    导出 UML 2.5 XMI/XML 文件

    语法
        >>> ExportXML(path:str = "", modelName:str = "SysbuilderRootModel")
    说明
        ExportXML(path, modelName) 用于将当前 Sysbuilder 工程导出为 UML 2.5 XMI XML 文件。
        当 path 为空时，默认导出到当前工程工作目录；当 path 为目录时，默认文件名为 SysBuilderUMLExport.xml。
        本接口复用文件菜单“导出 UML 2.5 XMI 文件”的全模型导出逻辑。
    示例
        示例1：导出到指定 XML 文件
        >>> print(ExportXML("C:/Users/TR/Documents/SysBuilderUMLExport.xml"))
        结果：
        > C:/Users/TR/Documents/SysBuilderUMLExport.xml
    输入参数
        path - XML 文件或目标目录的绝对路径，可为空
        数据类型：str
        modelName - 导出 XML 中的模型名称，默认 SysbuilderRootModel
        数据类型：str
    返回值
        `str` : 导出成功返回生成的 XML 文件绝对路径，失败返回空字符串
    另请参阅
        ImportXML
    """
    if path is None:
        path = ""
    if modelName in ("", None):
        modelName = "SysbuilderRootModel"
    return _run_func(ExportXML, locals())

ExportXMI = ExportXML

@mw_connect_decorator(_MwConnect._process_path)
def ImportReqExcel(path: str = ""):
    """
    导入需求Excel文件
    
    语法
        >>> ImportReqExcel(path:str)
    说明
        ImportReqExcel(path) 用于将外部 Excel 需求文件（.xlsx）导入到 Sysbuilder 当前工程中。
    示例
        示例1：导入指定的需求Excel文件
        >>> print(ImportReqExcel("C:/Users/TR/Documents/requirements.xlsx"))
        结果：
        > True
    输入参数
        path - 需求Excel文件的绝对路径
        数据类型：str
    返回值
        `bool` : 导入成功返回 True，否则返回 False
    另请参阅
        无
    """
    return _run_func(ImportReqExcel, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ImportReqIF(path: str = ""):
    """
    导入需求ReqIF文件
    
    语法
        >>> ImportReqIF(path:str)
    说明
        ImportReqIF(path) 用于将外部 ReqIF 需求文件（.reqif）导入到 Sysbuilder 当前工程中。
    示例
        示例1：导入指定的ReqIF文件
        >>> print(ImportReqIF("C:/Users/TR/Documents/requirements.reqif"))
        结果：
        > True
    输入参数
        path - ReqIF文件的绝对路径
        数据类型：str
    返回值
        `bool` : 导入成功返回 True，否则返回 False
    另请参阅
        无
    """
    return _run_func(ImportReqIF, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ExportReqExcel(path: str, fullName: str = "") -> str:
    """
    导出需求Excel文件

    语法
        >>> ExportReqExcel(path:str, fullName:str = "")
    说明
        ExportReqExcel(path, fullName) 用于将需求导出为 Excel 文件（.xlsx）。
        当 fullName 为空时，导出所有需求；当 fullName 为需求或包的全名时，导出该元素及其子需求。
    示例
        示例1：导出所有需求到指定路径
        >>> print(ExportReqExcel("C:/Users/TR/Documents/all_requirements.xlsx"))
        结果：
        > C:/Users/TR/Documents/all_requirements.xlsx

        示例2：导出指定包下的需求
        >>> print(ExportReqExcel("C:/Users/TR/Documents/requirements.xlsx", "Package1"))
        结果：
        > C:/Users/TR/Documents/requirements.xlsx
    输入参数
        path - 导出的Excel文件绝对路径（必须是.xlsx格式）
        数据类型：str
        fullName - 需求或包的全名（可选，为空时导出所有需求）
        数据类型：str
    返回值
        `str` : 导出成功返回生成的文件绝对路径，失败返回空字符串
    另请参阅
        ImportReqExcel
    """
    return _run_func(ExportReqExcel, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ExportReqIF(path: str, fullName: str = "") -> str:
    """
    导出需求ReqIF文件

    语法
        >>> ExportReqIF(path:str, fullName:str = "")
    说明
        ExportReqIF(path, fullName) 用于将需求导出为 ReqIF 文件（.reqif）。
        当 fullName 为空时，导出所有需求；当 fullName 为需求或包的全名时，导出该元素及其子需求。
    示例
        示例1：导出所有需求到指定路径
        >>> print(ExportReqIF("C:/Users/TR/Documents/all_requirements.reqif"))
        结果：
        > C:/Users/TR/Documents/all_requirements.reqif

        示例2：导出指定包下的需求
        >>> print(ExportReqIF("C:/Users/TR/Documents/requirements.reqif", "Package1"))
        结果：
        > C:/Users/TR/Documents/requirements.reqif
    输入参数
        path - 导出的ReqIF文件绝对路径（必须是.reqif格式）
        数据类型：str
        fullName - 需求或包的全名（可选，为空时导出所有需求）
        数据类型：str
    返回值
        `str` : 导出成功返回生成的文件绝对路径，失败返回空字符串
    另请参阅
        ImportReqIF
    """
    return _run_func(ExportReqIF, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ExportSemanticJson(path: str = "", fullName: str = "", includeHidden: bool = False) -> str:
    """
    导出 SysML2 语义 JSON 文件

    语法
        >>> ExportSemanticJson(path:str = "", fullName:str = "", includeHidden:bool = False)
    说明
        ExportSemanticJson(path, fullName, includeHidden) 用于将当前工程的 SysML2 语义树导出为 JSON 文件。
        本接口返回导出的 JSON 文件路径，不直接返回 JSON 内容。
        当 path 为空时，优先导出到工程工作目录下的 semantic_tree.json；若工程工作目录不可用，则导出到进程当前目录。
        当 fullName 为空时，导出整个工程语义树；当 fullName 不为空时，只导出该元素及其递归 owned 子元素。
        导出文件顶层的 root 只是 JSON 包装占位节点，不属于 SysML2 语义模型内容；真实语义元素从 root.children 开始。
        JSON 节点只包含 fullName、type、properties、children 四类核心字段。
        type 为字符串类型名，不导出数字枚举；图元素会带 Diagram 标识，便于直接看出该节点是图。
        properties 保留影响语义树显示和理解的属性，例如 ScalarValues.Real；内部 SysbuilderDefinition.* 默认不输出。
        需求指标节点的 type 为 RequirementIndex，properties 中包含非空的 indexValue、indexUnit 和 indexDescription。
        includeHidden=False 时按 SysML2 语义隐藏标记过滤，但用户可见的需求指标始终保留；不承诺与模型浏览器插件扩展显示状态完全一致。
    示例
        示例1：导出当前工程语义树
        >>> print(ExportSemanticJson("C:/Temp/semantic_tree.json"))
        结果：
        > C:/Temp/semantic_tree.json

        示例2：导出指定元素子树并包含隐藏元素
        >>> print(ExportSemanticJson("C:/Temp/semantic_subtree.json", "Package1.Block1", True))
        结果：
        > C:/Temp/semantic_subtree.json

        示例3：使用默认路径导出整个工程
        >>> print(ExportSemanticJson())
        结果：
        > 当前工作目录/semantic_tree.json
    输入参数
        path - 导出的 JSON 文件路径；允许为空，空值表示优先使用工程工作目录下的 semantic_tree.json
        数据类型：str
        fullName - 导出根元素全名；为空表示导出整个工程，不为空表示只导出指定元素及其子元素
        数据类型：str
        includeHidden - 是否包含 SysML2 语义隐藏元素，默认 False；该参数不追随插件扩展的模型浏览器显示状态
        数据类型：bool
    返回值
        `str` : 导出成功返回生成的 JSON 文件绝对路径，失败返回空字符串
    另请参阅
        OpenProjectFile
    """
    if path is None:
        path = ""
    if fullName is None:
        fullName = ""
    if includeHidden in ("", None):
        includeHidden = False
    return _run_func(ExportSemanticJson, locals())

@mw_connect_decorator(_MwConnect._process_path)
def RunArchitectureTradeoff(scriptPath: str, imageDir: str = "") -> str:
    """
    运行架构权衡计算并导出图片

    语法
        >>> RunArchitectureTradeoff(scriptPath:str, imageDir:str = "")
    说明
        RunArchitectureTradeoff(scriptPath, imageDir) 用于按当前工程模型运行架构权衡 Python 计算脚本。
        scriptPath 为外部应用生成的 Python 脚本路径，必须存在且可读取；脚本内容会在模型类和实例变量生成后执行。
        imageDir 为空时，自动在当前工程工作路径下创建一个 architecture_tradeoff_时间戳 目录；不为空时使用指定目录。
        计算过程中会自动保存 matplotlib 已创建的图片，不弹出图片窗口。
        返回值是实际图片输出目录，不直接返回图片内容。脚本执行失败时返回空字符串，并通过运行消息返回错误原因。
    示例
        示例1：运行架构权衡脚本并导出到默认目录
        >>> print(RunArchitectureTradeoff("C:/Project/python/architect_test.py"))
        结果：
        > C:/Project/architecture_tradeoff_20260707_153000_001

        示例2：运行脚本并指定图片目录
        >>> print(RunArchitectureTradeoff("C:/Project/python/architect_test.py", "C:/Temp/tradeoff_images"))
        结果：
        > C:/Temp/tradeoff_images
    输入参数
        scriptPath - 架构权衡 Python 脚本文件路径；不能为空
        数据类型：str
        imageDir - 图片输出目录；为空时自动在工作路径下创建目录
        数据类型：str
    返回值
        `str` : 成功返回图片输出目录绝对路径，失败返回空字符串
    另请参阅
        OpenProjectFile
    """
    if scriptPath is None:
        scriptPath = ""
    if imageDir is None:
        imageDir = ""
    return _run_func(RunArchitectureTradeoff, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ExportArchitectureTradeoffObjectCode(path: str = "") -> str:
    """
    导出架构权衡对象代码文本

    语法
        >>> ExportArchitectureTradeoffObjectCode(path:str = "")
    说明
        ExportArchitectureTradeoffObjectCode(path) 用于导出架构权衡窗口中“全选”架构方案时，
        “架构对象代码”区域生成的 Python 文本。导出内容包含模型定义类代码和实例初始化代码，
        与界面中全选架构方案后的对象代码显示保持一致。
        path 为空时，自动在当前工程工作路径下生成 architecture_tradeoff_object_code.py。
        path 为已存在文件夹时，在该文件夹下生成 architecture_tradeoff_object_code.py。
        path 为文件路径且没有扩展名时，自动补充 .py 扩展名；父文件夹不存在时会自动创建。
        返回值是实际导出的对象代码文件路径，不直接返回文件内容。执行失败时返回空字符串，并通过运行消息返回错误原因。
    示例
        示例1：导出到默认位置
        >>> print(ExportArchitectureTradeoffObjectCode())
        结果：
        > C:/Project/architecture_tradeoff_object_code.py

        示例2：导出到指定文件
        >>> print(ExportArchitectureTradeoffObjectCode("C:/Temp/tradeoff_object_code.py"))
        结果：
        > C:/Temp/tradeoff_object_code.py
    输入参数
        path - 对象代码输出文件或已存在文件夹路径；为空时使用默认输出文件
        数据类型：str
    返回值
        `str` : 成功返回对象代码文件绝对路径，失败返回空字符串
    另请参阅
        RunArchitectureTradeoff
    """
    if path is None:
        path = ""
    return _run_func(ExportArchitectureTradeoffObjectCode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def SaveProject():
    """
    保存当前项目
    
    语法
        >>> SaveProject()
    说明
        SaveProject() 用于保存 Sysbuilder 当前正在操作的项目。
    示例
        示例1：保存当前工程
        >>> print(SaveProject())
        结果：
        > True
    输入参数
        无
    返回值
        `bool` : 保存成功返回 True，否则返回 False
    另请参阅
        无
    """
    return _run_func(SaveProject, locals())

@mw_connect_decorator(_MwConnect._process_path)
def SaveProjectAs(targetPath: str):
    """
    项目另存为
    
    语法
        >>> SaveProjectAs(targetPath:str)
    说明
        SaveProjectAs(targetPath) 用于将当前 Sysbuilder 项目另存到新的绝对路径下。
    示例
        示例1：将项目另存为备份文件
        >>> print(SaveProjectAs("D:/ProjectBackup/Vehicle_V1.sybprojz"))
        结果：
        > True
    输入参数
        targetPath - 另存为的目标完整路径
        数据类型：str
    返回值
        `bool` : 另存为成功返回 True，否则返回 False
    另请参阅
        无
    """
    return _run_func(SaveProjectAs, locals())


# ---------------------------- 视图类 --------------------------------------

@mw_connect_decorator(_MwConnect._process_path)
def NewPKGDiagram(fullName: str = "") -> str:
    """
    新建包图
    
    语法
        >>>NewPKGDiagram(fullName:str)
    说明
        NewPKGDiagram(fullName)用于新建包图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建包图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewPKGDiagram("package1.pkgDiagram"))
    输入参数
        fullName - 包图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewPKGDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewREQDiagram(fullName: str = "") -> str:
    """
    新建需求图
    
    语法
        >>>NewREQDiagram(fullName:str)
    说明
        NewREQDiagram(fullName)用于新建需求图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建需求图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewREQDiagram("package1.reqDiagram"))
    输入参数
        fullName - 需求图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewREQDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewUCDiagram(fullName: str = "") -> str:
    """
    新建用例图
    
    语法
        >>>NewUCDiagram(fullName:str)
    说明
        NewUCDiagram(fullName)用于新建用例图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建用例图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewUCDiagram("package1.ucDiagram"))
    输入参数
        fullName - 用例图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewUCDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewACTDiagram(fullName: str = "") -> str:
    """
    新建活动图
    
    语法
        >>>NewACTDiagram(fullName:str)
    说明
        NewACTDiagram(fullName)用于新建活动图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建活动图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewACTDiagram("activity1.actDiagram"))
    输入参数
        fullName - 活动图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewACTDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSTMDiagram(fullName: str = "") -> str:
    """
    新建状态机图
    
    语法
        >>>NewSTMDiagram(fullName:str)
    说明
        NewSTMDiagram(fullName)用于新建状态机图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建状态机图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewSTMDiagram("package1.stmDiagram"))
    输入参数
        fullName - 状态机图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewSTMDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSDDiagram(fullName: str = "") -> str:
    """
    新建序列图
    
    语法
        >>>NewSDDiagram(fullName:str)
    说明
        NewSDDiagram(fullName)用于新建序列图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建序列图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewSDDiagram("package1.seqDiagram"))
    输入参数
        fullName - 序列图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewSDDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewBDDDiagram(fullName: str = "") -> str:
    """
    新建模块定义图
    
    语法
        >>>NewBDDDiagram(fullName:str)
    说明
        NewBDDDiagram(fullName)用于新建模块定义图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewBDDDiagram("package1.bddDiagram"))
    输入参数
        fullName - 模块定义图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewBDDDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewIBDDiagram(fullName: str = "") -> str:
    """
    新建内部模块图
    
    语法
        >>>NewIBDDiagram(fullName:str)
    说明
        NewIBDDiagram(fullName)用于新建内部模块图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewIBDDiagram("block1.ibdDiagram"))
    输入参数
        fullName - 内部模块图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewIBDDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewPARDiagram(fullName: str = "") -> str:
    """
    新建参数图
    
    语法
        >>>NewPARDiagram(fullName:str)
    说明
        NewPARDiagram(fullName)用于新建参数图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewPARDiagram("package1.parDiagram"))
    输入参数
        fullName - 参数图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewPARDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewMMDiagram(fullName: str = "") -> str:
    """
    新建思维导图
    
    语法
        >>>NewMMDiagram(fullName:str)
    说明
        NewMMDiagram(fullName)用于新建思维导图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewMMDiagram("package1.mmDiagram"))
    输入参数
        fullName - 思维导图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewMMDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewGenericTableDiagram(fullName: str = "") -> str:
    """
    新建表格视图
    
    语法
        >>>NewGenericTableDiagram(fullName:str)
    说明
        NewGenericTableDiagram(fullName)用于新建表格视图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewGenericTableDiagram("package1.table1"))
    输入参数
        fullName - 表格视图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewGenericTableDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewRequirementTable(fullName: str = "") -> str:
    """
    新建需求表格

    语法
        >>>NewRequirementTable(fullName:str)
    说明
        NewRequirementTable(fullName)用于新建“需求表格”。
        该接口等效于：先新建表格视图，再将筛选数据弹窗中的显示元素设置为需求并执行全选；整个过程不弹出弹窗。
        函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewRequirementTable("package1.req_table"))
    输入参数
        fullName - 表格视图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    另请参阅
        NewGenericTableDiagram
        NewArchitectureTable
    """
    return _run_func(NewRequirementTable, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewArchitectureTable(fullName: str = "") -> str:
    """
    新建架构表格

    语法
        >>>NewArchitectureTable(fullName:str)
    说明
        NewArchitectureTable(fullName)用于新建“架构表格”。
        该接口等效于：先新建表格视图，再将筛选数据弹窗中的显示元素设置为块、接口块、值类型并执行全选；整个过程不弹出弹窗。
        函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewArchitectureTable("package1.arch_table"))
    输入参数
        fullName - 表格视图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    另请参阅
        NewGenericTableDiagram
        NewRequirementTable
    """
    return _run_func(NewArchitectureTable, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewRelationMatrixDiagram(fullName: str = "") -> str:
    """
    新建关系矩阵图
    
    语法
        >>>NewRelationMatrixDiagram(fullName:str)
    说明
        NewRelationMatrixDiagram(fullName)用于新建关系矩阵图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewRelationMatrixDiagram("package1.matrix1"))
    输入参数
        fullName - 关系矩阵图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewRelationMatrixDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewRequirementFunctionTraceabilityMatrix(fullName: str = "") -> str:
    """
    新建需求功能追溯矩阵

    语法
        >>>NewRequirementFunctionTraceabilityMatrix(fullName:str)
    说明
        NewRequirementFunctionTraceabilityMatrix(fullName)用于新建“需求功能追溯矩阵”。
        该接口等效于：先新建关系矩阵，再将行数据筛选为需求并全选、列数据筛选为活动和块并全选、关系类型筛选为满足。
        函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewRequirementFunctionTraceabilityMatrix("package1.req_func_matrix"))
    输入参数
        fullName - 关系矩阵图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    另请参阅
        NewRelationMatrixDiagram
        NewArchitectureFunctionTraceabilityMatrix
    """
    return _run_func(NewRequirementFunctionTraceabilityMatrix, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewArchitectureFunctionTraceabilityMatrix(fullName: str = "") -> str:
    """
    新建架构功能追溯矩阵

    语法
        >>>NewArchitectureFunctionTraceabilityMatrix(fullName:str)
    说明
        NewArchitectureFunctionTraceabilityMatrix(fullName)用于新建“架构功能追溯矩阵”。
        该接口等效于：先新建关系矩阵，再将行数据筛选为块并全选、列数据筛选为活动并全选、关系类型筛选为分配。
        函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewArchitectureFunctionTraceabilityMatrix("package1.arch_func_matrix"))
    输入参数
        fullName - 关系矩阵图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    另请参阅
        NewRelationMatrixDiagram
        NewRequirementFunctionTraceabilityMatrix
    """
    return _run_func(NewArchitectureFunctionTraceabilityMatrix, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewRetrospectiveAnalysisDiagram(fullName: str = "") -> str:
    """
    新建追溯分析图
    
    语法
        >>>NewRetrospectiveAnalysisDiagram(fullName:str)
    说明
        NewRetrospectiveAnalysisDiagram(fullName)用于新建追溯分析图，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建图的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewRetrospectiveAnalysisDiagram("package1.retro1"))
    输入参数
        fullName - 追溯分析图的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewRetrospectiveAnalysisDiagram, locals())

# ============================== DODAF/UAF 体系视图 ==============================

@mw_connect_decorator(_MwConnect._process_path)
def NewAV1Diagram(diagramName: str = "") -> str:
    """
    新建AV-1全景视图

    语法
        >>>NewAV1Diagram(diagramName:str="")
    说明
        NewAV1Diagram(diagramName)用于新建AV-1全景视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如AV1Diagram1）；软件内部自动拼接固定父包路径AV.'AV-1'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        示例1：缺省参数，自动生成默认名
        >>>print(NewAV1Diagram())
        结果：
        > AV.'AV-1'.AV1Diagram1
        示例2：指定视图名称
        >>>print(NewAV1Diagram("myAV1Diagram"))
        结果：
        > AV.'AV-1'.myAV1Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewAV1Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewAV2Diagram(diagramName: str = "") -> str:
    """
    新建AV-2全景视图

    语法
        >>>NewAV2Diagram(diagramName:str="")
    说明
        NewAV2Diagram(diagramName)用于新建AV-2全景视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如AV2Diagram1）；软件内部自动拼接固定父包路径AV.'AV-2'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewAV2Diagram("myAV2Diagram"))
        结果：
        > AV.'AV-2'.myAV2Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewAV2Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewAV3Diagram(diagramName: str = "") -> str:
    """
    新建AV-3全景视图

    语法
        >>>NewAV3Diagram(diagramName:str="")
    说明
        NewAV3Diagram(diagramName)用于新建AV-3全景视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如AV3Diagram1）；软件内部自动拼接固定父包路径AV.'AV-3'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewAV3Diagram("myAV3Diagram"))
        结果：
        > AV.'AV-3'.myAV3Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewAV3Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewCV1aDiagram(diagramName: str = "") -> str:
    """
    新建CV-1a能力视图

    语法
        >>>NewCV1aDiagram(diagramName:str="")
    说明
        NewCV1aDiagram(diagramName)用于新建CV-1a能力视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如CV1aDiagram1）；软件内部自动拼接固定父包路径CV.'CV-1a'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewCV1aDiagram("myCV1aDiagram"))
        结果：
        > CV.'CV-1a'.myCV1aDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewCV1aDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewCV1bDiagram(diagramName: str = "") -> str:
    """
    新建CV-1b能力视图

    语法
        >>>NewCV1bDiagram(diagramName:str="")
    说明
        NewCV1bDiagram(diagramName)用于新建CV-1b能力视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如CV1bDiagram1）；软件内部自动拼接固定父包路径CV.'CV-1b'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewCV1bDiagram("myCV1bDiagram"))
        结果：
        > CV.'CV-1b'.myCV1bDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewCV1bDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewCV2Diagram(diagramName: str = "") -> str:
    """
    新建CV-2能力视图

    语法
        >>>NewCV2Diagram(diagramName:str="")
    说明
        NewCV2Diagram(diagramName)用于新建CV-2能力视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如CV2Diagram1）；软件内部自动拼接固定父包路径CV.'CV-2'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewCV2Diagram("myCV2Diagram"))
        结果：
        > CV.'CV-2'.myCV2Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewCV2Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewCV3Diagram(diagramName: str = "") -> str:
    """
    新建CV-3能力视图

    语法
        >>>NewCV3Diagram(diagramName:str="")
    说明
        NewCV3Diagram(diagramName)用于新建CV-3能力视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如CV3Diagram1）；软件内部自动拼接固定父包路径CV.'CV-3'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewCV3Diagram("myCV3Diagram"))
        结果：
        > CV.'CV-3'.myCV3Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewCV3Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewCV4Diagram(diagramName: str = "") -> str:
    """
    新建CV-4能力视图

    语法
        >>>NewCV4Diagram(diagramName:str="")
    说明
        NewCV4Diagram(diagramName)用于新建CV-4能力视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如CV4Diagram1）；软件内部自动拼接固定父包路径CV.'CV-4'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewCV4Diagram("myCV4Diagram"))
        结果：
        > CV.'CV-4'.myCV4Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewCV4Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewCV5Diagram(diagramName: str = "") -> str:
    """
    新建CV-5能力视图

    语法
        >>>NewCV5Diagram(diagramName:str="")
    说明
        NewCV5Diagram(diagramName)用于新建CV-5能力视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如CV5Diagram1）；软件内部自动拼接固定父包路径CV.'CV-5'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewCV5Diagram("myCV5Diagram"))
        结果：
        > CV.'CV-5'.myCV5Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewCV5Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV1aDiagram(diagramName: str = "") -> str:
    """
    新建OV-1a作战概念模型

    语法
        >>>NewOV1aDiagram(diagramName:str="")
    说明
        NewOV1aDiagram(diagramName)用于新建OV-1a作战概念模型，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如OV1aDiagram1）；软件内部自动拼接固定父包路径OV.'OV-1a'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewOV1aDiagram("myOV1aDiagram"))
        结果：
        > OV.'OV-1a'.myOV1aDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV1aDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV1bDiagram(diagramName: str = "") -> str:
    """
    新建OV-1b作战概念模型

    语法
        >>>NewOV1bDiagram(diagramName:str="")
    说明
        NewOV1bDiagram(diagramName)用于新建OV-1b作战概念模型，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如OV1bDiagram1）；软件内部自动拼接固定父包路径OV.'OV-1b'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewOV1bDiagram("myOV1bDiagram"))
        结果：
        > OV.'OV-1b'.myOV1bDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV1bDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV1cDiagram(diagramName: str = "") -> str:
    """
    新建OV-1c作战概念模型

    语法
        >>>NewOV1cDiagram(diagramName:str="")
    说明
        NewOV1cDiagram(diagramName)用于新建OV-1c作战概念模型，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如OV1cDiagram1）；软件内部自动拼接固定父包路径OV.'OV-1c'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewOV1cDiagram("myOV1cDiagram"))
        结果：
        > OV.'OV-1c'.myOV1cDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV1cDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV1dDiagram(diagramName: str = "") -> str:
    """
    新建OV-1d作战概念模型

    语法
        >>>NewOV1dDiagram(diagramName:str="")
    说明
        NewOV1dDiagram(diagramName)用于新建OV-1d作战概念模型，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如OV1dDiagram1）；软件内部自动拼接固定父包路径OV.'OV-1d'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewOV1dDiagram("myOV1dDiagram"))
        结果：
        > OV.'OV-1d'.myOV1dDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV1dDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV1fDiagram(diagramName: str = "") -> str:
    """
    新建OV-1f作战概念模型

    语法
        >>>NewOV1fDiagram(diagramName:str="")
    说明
        NewOV1fDiagram(diagramName)用于新建OV-1f作战概念模型，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如OV1fDiagram1）；软件内部自动拼接固定父包路径OV.'OV-1f'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewOV1fDiagram("myOV1fDiagram"))
        结果：
        > OV.'OV-1f'.myOV1fDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV1fDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV2Diagram(diagramName: str = "") -> str:
    """
    新建OV-2作战视图

    语法
        >>>NewOV2Diagram(diagramName:str="")
    说明
        NewOV2Diagram(diagramName)用于新建OV-2作战视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如OV2Diagram1）；软件内部自动拼接固定父包路径OV.'OV-2'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewOV2Diagram("myOV2Diagram"))
        结果：
        > OV.'OV-2'.myOV2Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV2Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV4Diagram(diagramName: str = "") -> str:
    """
    新建OV-4作战视图

    语法
        >>>NewOV4Diagram(diagramName:str="")
    说明
        NewOV4Diagram(diagramName)用于新建OV-4作战视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如OV4Diagram1）；软件内部自动拼接固定父包路径OV.'OV-4'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewOV4Diagram("myOV4Diagram"))
        结果：
        > OV.'OV-4'.myOV4Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV4Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV5aDiagram(diagramName: str = "") -> str:
    """
    新建OV-5a作战视图

    语法
        >>>NewOV5aDiagram(diagramName:str="")
    说明
        NewOV5aDiagram(diagramName)用于新建OV-5a作战视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName支持以下格式：
        - 空字符串：自动生成父元素名（作战活动）和图名（如OV5aDiagram1）。
        - 单个名称（如"myDiagram"）：自动生成父元素名，使用指定图名。
        - "父元素名.图名"格式（如"活动1.myDiagram"）：在指定父元素下创建图，若父元素不存在则新建。
        最多只接受一个分隔符（.），名称自身包含.时请用单引号包裹（如'活动.A'.myDiagram）。
        拆分后的父元素名和图名会按SysML2模型名规则自动规范化，例如"02_父元素.02_图名"会创建为"'02_父元素'.'02_图名'"。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        示例1：缺省参数，自动生成默认名
        >>>print(NewOV5aDiagram())
        结果：
        > OV.'OV-5a'.作战活动1.OV5aDiagram1
        示例2：指定图名
        >>>print(NewOV5aDiagram("myDiagram"))
        结果：
        > OV.'OV-5a'.作战活动1.myDiagram
        示例3：指定父元素和图名
        >>>print(NewOV5aDiagram("活动1.myDiagram"))
        结果：
        > OV.'OV-5a'.活动1.myDiagram
        示例4：名称需要规范化
        >>>print(NewOV5aDiagram("02_父元素.02_图名"))
        结果：
        > OV.'OV-5a'.'02_父元素'.'02_图名'
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV5aDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV5bDiagram(diagramName: str = "") -> str:
    """
    新建OV-5b作战视图

    语法
        >>>NewOV5bDiagram(diagramName:str="")
    说明
        NewOV5bDiagram(diagramName)用于新建OV-5b作战视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName支持以下格式：
        - 空字符串：自动生成父元素名（作战活动）和图名（如OV5bDiagram1）。
        - 单个名称（如"myDiagram"）：自动生成父元素名，使用指定图名。
        - "父元素名.图名"格式（如"活动1.myDiagram"）：在指定父元素下创建图，若父元素不存在则新建。
        最多只接受一个分隔符（.），名称自身包含.时请用单引号包裹（如'活动.A'.myDiagram）。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        示例1：缺省参数，自动生成默认名
        >>>print(NewOV5bDiagram())
        结果：
        > OV.'OV-5b'.作战活动1.OV5bDiagram1
        示例2：指定图名
        >>>print(NewOV5bDiagram("myDiagram"))
        结果：
        > OV.'OV-5b'.作战活动1.myDiagram
        示例3：指定父元素和图名
        >>>print(NewOV5bDiagram("活动1.myDiagram"))
        结果：
        > OV.'OV-5b'.活动1.myDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV5bDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV6bDiagram(diagramName: str = "") -> str:
    """
    新建OV-6b作战视图

    语法
        >>>NewOV6bDiagram(diagramName:str="")
    说明
        NewOV6bDiagram(diagramName)用于新建OV-6b作战视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName支持以下格式：
        - 空字符串：自动生成父元素名（作战状态机）和图名（如OV6bDiagram1）。
        - 单个名称（如"myDiagram"）：自动生成父元素名，使用指定图名。
        - "父元素名.图名"格式（如"状态机1.myDiagram"）：在指定父元素下创建图，若父元素不存在则新建。
        最多只接受一个分隔符（.），名称自身包含.时请用单引号包裹（如'状态.A'.myDiagram）。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        示例1：缺省参数，自动生成默认名
        >>>print(NewOV6bDiagram())
        结果：
        > OV.'OV-6b'.作战状态机1.OV6bDiagram1
        示例2：指定图名
        >>>print(NewOV6bDiagram("myDiagram"))
        结果：
        > OV.'OV-6b'.作战状态机1.myDiagram
        示例3：指定父元素和图名
        >>>print(NewOV6bDiagram("状态机1.myDiagram"))
        结果：
        > OV.'OV-6b'.状态机1.myDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV6bDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOV6cDiagram(diagramName: str = "") -> str:
    """
    新建OV-6c作战视图

    语法
        >>>NewOV6cDiagram(diagramName:str="")
    说明
        NewOV6cDiagram(diagramName)用于新建OV-6c作战视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName支持以下格式：
        - 空字符串：自动生成父元素名（作战交互）和图名（如OV6cDiagram1）。
        - 单个名称（如"myDiagram"）：自动生成父元素名，使用指定图名。
        - "父元素名.图名"格式（如"交互1.myDiagram"）：在指定父元素下创建图，若父元素不存在则新建。
        最多只接受一个分隔符（.），名称自身包含.时请用单引号包裹（如'交互.A'.myDiagram）。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        示例1：缺省参数，自动生成默认名
        >>>print(NewOV6cDiagram())
        结果：
        > OV.'OV-6c'.作战交互1.OV6cDiagram1
        示例2：指定图名
        >>>print(NewOV6cDiagram("myDiagram"))
        结果：
        > OV.'OV-6c'.作战交互1.myDiagram
        示例3：指定父元素和图名
        >>>print(NewOV6cDiagram("交互1.myDiagram"))
        结果：
        > OV.'OV-6c'.交互1.myDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewOV6cDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV1aDiagram(diagramName: str = "") -> str:
    """
    新建SV-1a系统视图

    语法
        >>>NewSV1aDiagram(diagramName:str="")
    说明
        NewSV1aDiagram(diagramName)用于新建SV-1a系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV1aDiagram1）；软件内部自动拼接固定父包路径SV.'SV-1a'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV1aDiagram("mySV1aDiagram"))
        结果：
        > SV.'SV-1a'.mySV1aDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV1aDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV1bDiagram(diagramName: str = "") -> str:
    """
    新建SV-1b系统视图

    语法
        >>>NewSV1bDiagram(diagramName:str="")
    说明
        NewSV1bDiagram(diagramName)用于新建SV-1b系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV1bDiagram1）；软件内部自动拼接固定父包路径SV.'SV-1b'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV1bDiagram("mySV1bDiagram"))
        结果：
        > SV.'SV-1b'.mySV1bDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV1bDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV2Diagram(diagramName: str = "") -> str:
    """
    新建SV-2系统视图

    语法
        >>>NewSV2Diagram(diagramName:str="")
    说明
        NewSV2Diagram(diagramName)用于新建SV-2系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV2Diagram1）；软件内部自动拼接固定父包路径SV.'SV-2'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV2Diagram("mySV2Diagram"))
        结果：
        > SV.'SV-2'.mySV2Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV2Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV3Diagram(diagramName: str = "") -> str:
    """
    新建SV-3系统视图

    语法
        >>>NewSV3Diagram(diagramName:str="")
    说明
        NewSV3Diagram(diagramName)用于新建SV-3系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV3Diagram1）；软件内部自动拼接固定父包路径SV.'SV-3'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV3Diagram("mySV3Diagram"))
        结果：
        > SV.'SV-3'.mySV3Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV3Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV4Diagram(diagramName: str = "") -> str:
    """
    新建SV-4系统视图

    语法
        >>>NewSV4Diagram(diagramName:str="")
    说明
        NewSV4Diagram(diagramName)用于新建SV-4系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV4Diagram1）；软件内部自动拼接固定父包路径SV.'SV-4'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV4Diagram("mySV4Diagram"))
        结果：
        > SV.'SV-4'.mySV4Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV4Diagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV4bDiagram(diagramName: str = "") -> str:
    """
    新建SV-4b系统视图

    语法
        >>>NewSV4bDiagram(diagramName:str="")
    说明
        NewSV4bDiagram(diagramName)用于新建SV-4b系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV4bDiagram1）；软件内部自动拼接固定父包路径SV.'SV-4b'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV4bDiagram("mySV4bDiagram"))
        结果：
        > SV.'SV-4b'.mySV4bDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV4bDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV5aDiagram(diagramName: str = "") -> str:
    """
    新建SV-5a系统视图

    语法
        >>>NewSV5aDiagram(diagramName:str="")
    说明
        NewSV5aDiagram(diagramName)用于新建SV-5a系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV5aDiagram1）；软件内部自动拼接固定父包路径SV.'SV-5a'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV5aDiagram("mySV5aDiagram"))
        结果：
        > SV.'SV-5a'.mySV5aDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV5aDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV5bDiagram(diagramName: str = "") -> str:
    """
    新建SV-5b系统视图

    语法
        >>>NewSV5bDiagram(diagramName:str="")
    说明
        NewSV5bDiagram(diagramName)用于新建SV-5b系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV5bDiagram1）；软件内部自动拼接固定父包路径SV.'SV-5b'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV5bDiagram("mySV5bDiagram"))
        结果：
        > SV.'SV-5b'.mySV5bDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV5bDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewSV5cDiagram(diagramName: str = "") -> str:
    """
    新建SV-5c系统视图

    语法
        >>>NewSV5cDiagram(diagramName:str="")
    说明
        NewSV5cDiagram(diagramName)用于新建SV-5c系统视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如SV5cDiagram1）；软件内部自动拼接固定父包路径SV.'SV-5c'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewSV5cDiagram("mySV5cDiagram"))
        结果：
        > SV.'SV-5c'.mySV5cDiagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewSV5cDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewDIV1Diagram(diagramName: str = "") -> str:
    """
    新建DIV-1信息与数据视图

    语法
        >>>NewDIV1Diagram(diagramName:str="")
    说明
        NewDIV1Diagram(diagramName)用于新建DIV-1信息与数据视图，函数返回的`str`表示新建视图的完整路径，新建失败时为空。
        diagramName表示视图名称，缺省时自动生成默认名称（如DIV1Diagram1）；软件内部自动拼接固定父包路径DIV.'DIV-1'。
        若父包不存在（如非DODAF工程），则报错返回空。
    示例
        >>>print(NewDIV1Diagram("myDIV1Diagram"))
        结果：
        > DIV.'DIV-1'.myDIV1Diagram
    输入参数
        diagramName - 视图名称（可选，缺省时自动生成）
        数据类型：str
    返回值
        `str` : 新建视图的完整路径
    """
    return _run_func(NewDIV1Diagram, locals())

# ------------------------------模型树元素---------------------------------------

@mw_connect_decorator(_MwConnect._process_path)
def NewPackage(fullName: str = "") -> str:
    """
    新建包
    
    语法
        >>>NewPackage(fullName:str)
    说明
        NewPackage(fullName)用于新建包，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建包的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewPackage("Root.package1"))
    输入参数
        fullName - 包的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewPackage, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewBlock(fullName: str = "") -> str:
    """
    新建块
    
    语法
        >>>NewBlock(fullName:str)
    说明
        NewBlock(fullName)用于新建块，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建块的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewBlock("package1.Engine"))
    输入参数
        fullName - 块的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewBlock, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewActivity(fullName: str = "") -> str:
    """
    新建活动
    
    语法
        >>>NewActivity(fullName:str)
    说明
        NewActivity(fullName)用于新建活动，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建活动的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewActivity("package1.Calculate"))
    输入参数
        fullName - 活动的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewActivity, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewValueType(fullName: str = "") -> str:
    """
    新建值类型
    
    语法
        >>>NewValueType(fullName:str)
    说明
        NewValueType(fullName)用于新建值类型，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建值类型的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewValueType("package1.Real"))
    输入参数
        fullName - 值类型的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewValueType, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewRequirement(fullName: str = "") -> str:
    """
    新建需求
    
    语法
        >>>NewRequirement(fullName:str)
    说明
        NewRequirement(fullName)用于新建需求，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建需求的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewRequirement("package1.Req_001"))
    输入参数
        fullName - 需求的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewRequirement, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewStateMachine(fullName: str = "") -> str:
    """
    新建状态机
    
    语法
        >>>NewStateMachine(fullName:str)
    说明
        NewStateMachine(fullName)用于新建状态机，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建状态机的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewStateMachine("package1.ControlLogic"))
    输入参数
        fullName - 状态机的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewStateMachine, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewUseCase(fullName: str = "") -> str:
    """
    新建用例
    
    语法
        >>>NewUseCase(fullName:str)
    说明
        NewUseCase(fullName)用于新建用例，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建用例的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewUseCase("package1.IdentifyUser"))
    输入参数
        fullName - 用例的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewUseCase, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewConstraintBlock(fullName: str = "") -> str:
    """
    新建约束块
    
    语法
        >>>NewConstraintBlock(fullName:str)
    说明
        NewConstraintBlock(fullName)用于新建约束块，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建约束块的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewConstraintBlock("package1.MathConstraint"))
    输入参数
        fullName - 约束块的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewConstraintBlock, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOpaqueBehavior(fullName: str = "") -> str:
    """
    新建不透明行为
    
    语法
        >>>NewOpaqueBehavior(fullName:str)
    说明
        NewOpaqueBehavior(fullName)用于新建不透明行为，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建不透明行为的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewOpaqueBehavior("package1.Script1"))
    输入参数
        fullName - 不透明行为的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewOpaqueBehavior, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewInteraction(fullName: str = "") -> str:
    """
    新建交互
    
    语法
        >>>NewInteraction(fullName:str)
    说明
        NewInteraction(fullName)用于新建交互，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建交互的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewInteraction("package1.Scenario1"))
    输入参数
        fullName - 交互的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewInteraction, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewInterfaceBlock(fullName: str = "") -> str:
    """
    新建接口块
    
    语法
        >>>NewInterfaceBlock(fullName:str)
    说明
        NewInterfaceBlock(fullName)用于新建接口块，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建接口块的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewInterfaceBlock("package1.DataInterface"))
    输入参数
        fullName - 接口块的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewInterfaceBlock, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewActor(fullName: str = "") -> str:
    """
    新建参与者
    
    语法
        >>>NewActor(fullName:str)
    说明
        NewActor(fullName)用于新建参与者，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建参与者的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewActor("package1.User"))
    输入参数
        fullName - 参与者的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewActor, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewInstance(fullName: str = "", definitionFullName: str = "") -> str:
    """
    新建实例

    语法
        >>>NewInstance(fullName:str, definitionFullName:str)
    说明
        NewInstance(fullName, definitionFullName) 用于按指定定义创建实例，函数返回的`str`表示新建实例的全名，新建失败时为空。
        fullName 表示实例的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`）。
        definitionFullName 表示实例对应定义的全名，也可传基础值类型短名（如 Real/Integer/Boolean/String）。
        接口会先校验 definitionFullName 是否存在，并按定义类型创建对应 usage，再设置实例类型定义。
    示例
        示例1：创建块实例
        >>>print(NewInstance("Package1.engine1", "Package1.EngineBlock"))
        示例2：创建 Real 值实例
        >>>print(NewInstance("Package1.mass", "Real"))
    输入参数
        fullName - 实例的全名
        数据类型：str
        definitionFullName - 实例定义的全名或基础值类型短名
        数据类型：str
    返回值
        `str` : 新建的实例全名
    """
    return _run_func(NewInstance, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewPartProperty(fullName: str = "") -> str:
    """
    新建组成属性
    
    语法
        >>>NewPartProperty(fullName:str)
    说明
        NewPartProperty(fullName)用于新建组成属性，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建组成属性的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewPartProperty("Engine.Piston"))
    输入参数
        fullName - 组成属性的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewPartProperty, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewProxyPort(fullName: str = "") -> str:
    """
    新建代理端口
    
    语法
        >>>NewProxyPort(fullName:str)
    说明
        NewProxyPort(fullName)用于新建代理端口，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建代理端口的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewProxyPort("Engine.FuelInlet"))
    输入参数
        fullName - 代理端口的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewProxyPort, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewValueProperty(fullName: str = "") -> str:
    """
    新建值属性
    
    语法
        >>>NewValueProperty(fullName:str)
    说明
        NewValueProperty(fullName)用于新建值属性，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建值属性的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewValueProperty("Engine.Mass"))
    输入参数
        fullName - 值属性的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewValueProperty, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewConstraintProperty(fullName: str = "") -> str:
    """
    新建约束属性
    
    语法
        >>>NewConstraintProperty(fullName:str)
    说明
        NewConstraintProperty(fullName)用于新建约束属性，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建约束属性的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewConstraintProperty("Engine.Limit"))
    输入参数
        fullName - 约束属性的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewConstraintProperty, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewInputPort(fullName: str = "") -> str:
    """
    新建输入端口
    
    语法
        >>>NewInputPort(fullName:str)
    说明
        NewInputPort(fullName)用于新建输入端口，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建输入端口的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewInputPort("Activity1.in_port"))
    输入参数
        fullName - 输入端口的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewInputPort, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOutputPort(fullName: str = "") -> str:
    """
    新建输出端口
    
    语法
        >>>NewOutputPort(fullName:str)
    说明
        NewOutputPort(fullName)用于新建输出端口，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建输出端口的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewOutputPort("Activity1.out_port"))
    输入参数
        fullName - 输出端口的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewOutputPort, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewInputParam(fullName: str = "") -> str:
    """
    新建输入参数
    
    语法
        >>>NewInputParam(fullName:str)
    说明
        NewInputParam(fullName)用于新建输入参数，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建输入参数的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewInputParam("Constraint1.x"))
    输入参数
        fullName - 输入参数的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewInputParam, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewOutputParam(fullName: str = "") -> str:
    """
    新建输出参数
    
    语法
        >>>NewOutputParam(fullName:str)
    说明
        NewOutputParam(fullName)用于新建输出参数，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建输出参数的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewOutputParam("Constraint1.y"))
    输入参数
        fullName - 输出参数的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewOutputParam, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewReturnParam(fullName: str = "") -> str:
    """
    新建返回参数
    
    语法
        >>>NewReturnParam(fullName:str)
    说明
        NewReturnParam(fullName)用于新建返回参数，函数返回的`str`表示新建的元素名，新建失败时为空。
        fullName表示新建返回参数的全名，与父级之间使用`.`进行分隔；若名称自身包含`.`，请使用单引号包裹该名称段（如 `A.'B.b'`，表示 A 下有个子元素 B.b）。
    示例
        >>>print(NewReturnParam("Constraint1.result"))
    输入参数
        fullName - 返回参数的全名
        数据类型：str
    返回值
        `str` : 新建的元素名
    """
    return _run_func(NewReturnParam, locals())
    
@mw_connect_decorator(_MwConnect._process_path)
def DeleteElement(fullName: str) -> str:
    """
    删除元素
    
    语法
        >>> DeleteElement(fullName:str)
    说明
        DeleteElement(fullName) 用于根据全名删除指定的模型元素、视图或属性。该操作将从模型树中永久移除该节点。
    示例
        示例1：删除指定路径下的块
        >>> print(DeleteElement("Package1.Engine"))
    输入参数
        fullName - 待删除元素的全名（包含路径）
        数据类型：str
    返回值
        `bool` : 删除结果
    另请参阅
        无
    """
    return _run_func(DeleteElement, locals())

@mw_connect_decorator(_MwConnect._process_path)
def OpenDiagram(fullDiagramName: str) -> bool:
    """
    打开视图

    语法
        >>> OpenDiagram(fullDiagramName:str)
    说明
        OpenDiagram(fullDiagramName) 用于模拟在模型树中双击视图进行打开。
        fullDiagramName 为不可缺省参数，表示目标视图的全名（包含路径）。
        名称分隔规则与模型树一致：仅未被单引号包裹的 '.' 作为层级分隔符；
        若名称本身包含 '.'，请使用单引号包裹该名称段（如 `A.'B.b'.IBD1`，表示 A 下有个子元素 B.b，其下有子图 IBD1）。
    示例
        示例1：打开指定路径下的视图
        >>> print(OpenDiagram("Package1.System.IBD1"))
    输入参数
        fullDiagramName - 目标视图全名（不可缺省）
        数据类型：str
    返回值
        `bool` : 打开成功返回 True，否则返回 False
    另请参阅
        InsertElementToDiagram
        NewBDDDiagram
        NewIBDDiagram
        NewPARDiagram
    """
    return _run_func(OpenDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ExportDiagramImage(path: str = "", fullDiagramName: str = "", includeBorder: bool = True) -> str:
    """
    导出视图图片

    语法
        >>> ExportDiagramImage(path:str, fullDiagramName:str = "", includeBorder:bool = True)
    说明
        ExportDiagramImage(path, fullDiagramName, includeBorder) 用于按指定路径导出图片。
        path 为导出路径，支持目录路径或文件路径；不弹出路径选择对话框。
        当 path 为空时，默认保存到工作路径。
        若目标文件同名已存在，将自动追加后缀 _1、_2... 避免覆盖。
        includeBorder 为 True 时执行“包括边框”，为 False 时执行“不包括边框”，行为与界面菜单一致。
    示例
        示例1：导出指定视图图片（包括边框）
        >>> print(ExportDiagramImage("C:/Temp/diagram.jpg", "Package1.System.IBD1"))
        示例2：导出指定视图图片（不包括边框）
        >>> print(ExportDiagramImage("C:/Temp", "Package1.System.IBD1", False))
    输入参数
        path - 图片保存路径（可缺省；缺省时使用工作路径）
        数据类型：str
        fullDiagramName - 目标视图全名（可缺省，缺省时使用当前视图）
        数据类型：str
        includeBorder - 是否包括边框，默认 True
        数据类型：bool
    返回值
        `str` : 导出成功时返回最终保存的图片绝对路径，失败返回空字符串
    另请参阅
        OpenDiagram
        AutoLayoutDiagram
    """
    # 入参归一化：支持把空值按默认行为处理。
    if path is None:
        path = ""
    if fullDiagramName is None:
        fullDiagramName = ""
    if includeBorder in ("", None):
        includeBorder = True
    return _run_func(ExportDiagramImage, locals())

@mw_connect_decorator(_MwConnect._process_path)
def AutoLayoutDiagram(fullDiagramName: str = "") -> bool:
    """
    自动布局视图

    语法
        >>> AutoLayoutDiagram(fullDiagramName:str = "")
    说明
        AutoLayoutDiagram(fullDiagramName) 用于执行视图自动布局。
        fullDiagramName 为可缺省参数：传入图全名时，若目标图未打开或不是当前视图，会先打开并切换为当前视图再执行自动布局；
        传空字符串时，对当前视图执行自动布局（当前视图为空时返回 False）。
    示例
        示例1：对指定视图执行自动布局
        >>> print(AutoLayoutDiagram("Package1.System.IBD1"))
        示例2：对当前视图执行自动布局
        >>> print(AutoLayoutDiagram())
    输入参数
        fullDiagramName - 目标视图全名，缺省时使用当前视图
        数据类型：str
    返回值
        `bool` : 自动布局成功返回 True，否则返回 False
    另请参阅
        OpenDiagram
        InsertElementToDiagram
    """
    return _run_func(AutoLayoutDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def AdjustDiagramFrameToOptimalSize(fullDiagramName: str) -> bool:
    """
    将视图画布边框调整到最佳尺寸

    语法
        >>> AdjustDiagramFrameToOptimalSize(fullDiagramName:str)
    说明
        根据目标视图中可见图元的范围调整画布边框，目标视图无需预先打开，也不会切换当前视图。
    示例
        >>> print(AdjustDiagramFrameToOptimalSize("Package1.System.IBD1"))
    输入参数
        fullDiagramName - 目标视图全名
        数据类型：str
    返回值
        `bool` : 调整成功返回 True；视图不存在、没有持久化边框或没有有效内容时返回 False
    另请参阅
        AutoLayoutDiagram
        ExportDiagramImage
    """
    return _run_func(AdjustDiagramFrameToOptimalSize, locals())

@mw_connect_decorator(_MwConnect._process_path)
def StartDiagramSimulation(fullDiagramName: str) -> bool:
    """
    开始视图仿真

    语法
        >>> StartDiagramSimulation(fullDiagramName:str)
    说明
        StartDiagramSimulation(fullDiagramName) 用于开始指定视图的仿真。
        当前支持活动图、状态机图、序列图。
        该接口等效于：先打开指定视图，再触发主窗口仿真命令，最后执行仿真面板的开始动作。
    示例
        >>> print(StartDiagramSimulation("Package1.Act1"))
    输入参数
        fullDiagramName - 视图全名
        数据类型：str
    返回值
        `bool` : 是否成功触发仿真开始
    另请参阅
        OpenDiagram
        GetSimulationInfo
    """
    return _run_func(StartDiagramSimulation, locals())

@mw_connect_decorator(_MwConnect._process_path)
def GetSimulationInfo(clear: bool = True) -> str:
    """
    获取仿真信息

    语法
        >>> GetSimulationInfo(clear:bool = True)
    说明
        GetSimulationInfo(clear) 用于获取最近收到的仿真信息。
        仿真信息来源于主窗口的仿真动画更新链路，返回原始文本内容。
        当clear为True时，读取后会清空当前缓存。
    示例
        >>> print(GetSimulationInfo())
    输入参数
        clear - 获取后是否清空缓存
        数据类型：bool
    返回值
        `str` : 仿真信息文本
    另请参阅
        StartDiagramSimulation
    """
    return _run_func(GetSimulationInfo, locals())

@mw_connect_decorator(_MwConnect._process_path)
def InsertElementToDiagram(fullElementName: str, fullDiagramName: str, position: list = None) -> bool:
    """
    插入元素到视图

    语法
        >>> InsertElementToDiagram(fullElementName:str, fullDiagramName:str, position:list=None)
    说明
        InsertElementToDiagram(fullElementName, fullDiagramName, position) 用于模拟从模型树拖拽元素到视图进行创建。
        fullElementName 与 fullDiagramName 均为不可缺省参数。
        position 为可缺省参数，格式为 [x, y]，坐标表示创建图块的左上角位置。
        目标视图未打开时也会直接写入底层图形数据，后续打开视图可见。
        接口会按模型树拖拽规则校验元素类型，不能拖入的类型会返回 False。
    示例
        示例1：将块插入模块定义图
        >>> print(InsertElementToDiagram("Package1.Block1", "Package1.BDD1"))
        示例2：指定插入位置
        >>> print(InsertElementToDiagram("Package1.Block1", "Package1.BDD1", [100, 200]))
    输入参数
        fullElementName - 待插入元素的全名（包含路径）
        数据类型：str
        fullDiagramName - 目标视图的全名（包含路径）
        数据类型：str
        position - 图块创建位置，格式为 [x, y]，可缺省
        数据类型：list
    返回值
        bool : 插入成功返回 True，否则返回 False
    另请参阅
        DeleteElement
        NewBDDDiagram
        NewIBDDiagram
        NewPARDiagram
    """
    if isinstance(position, tuple):
        position = list(position)
    if position is not None and len(position) != 2:
        raise ValueError("position must be [x, y].")
    return _run_func(InsertElementToDiagram, locals())

@mw_connect_decorator(_MwConnect._process_path)
def ShowInternalProperties(fullDiagramName: str, parentPropertyPath: str, propertyNames: list = None) -> bool:
    """在 IBD 组成属性中显示其类型的内部属性，支持多层嵌套。

    先 NewPartProperty、SetType 和 InsertElementToDiagram，再显示内部属性。
    parentPropertyPath 是图中的组成属性路径，如 "partA" 或 "partA.child"；
    唯一宿主也可用元素全名。同类型的不同宿主必须用各自的视图路径。
    propertyNames=None 显示全部非接口子属性；列表只增量显示指定子属性，[] 不新增。
    已有子图元和连线保留，重复调用不重复创建；子属性仍引用类型中的原元素。
    对嵌套组成属性再次调用即可继续展开，无须在组成属性下新建语义子元素。
    连接时使用 CreateConnectorLine / CreateBindingConnectorLine，端点可为
    "partA.child"、"partA.child.port"；带点的名称需用单引号包裹。

    >>> ShowInternalProperties("System.IBD", "partA", ["child"])
    >>> ShowInternalProperties("System.IBD", "partA.child")
    >>> CreateConnectorLine("System.IBD", "partA.child.out", "partB.child.in")
    >>> AutoLayoutDiagram("System.IBD")
    完成全部图元显示和连线后，调用现有 AutoLayoutDiagram 统一布局。
    返回 bool，目标不是 IBD、宿主无类型、属性不属于宿主类型或路径有歧义时失败。
    """
    if not isinstance(fullDiagramName, str) or not fullDiagramName.strip():
        raise ValueError("fullDiagramName must be a non-empty string.")
    if not isinstance(parentPropertyPath, str) or not parentPropertyPath.strip():
        raise ValueError("parentPropertyPath must be a non-empty string.")
    if propertyNames is not None:
        if not isinstance(propertyNames, (list, tuple)):
            raise TypeError("propertyNames must be a list of property names or None.")
        if any(not isinstance(name, str) or not name.strip() for name in propertyNames):
            raise ValueError("propertyNames must contain non-empty strings.")
    return _ShowInternalProperties(
        fullDiagramName, parentPropertyPath,
        list(propertyNames) if propertyNames is not None else [], propertyNames is None)


def _ShowInternalProperties(fullDiagramName: str, parentPropertyPath: str,
                            propertyNames: list, showAll: bool) -> bool:
    return _run_func(_ShowInternalProperties, locals())


def _check_graph_name_and_position(graphName: str, position):
    if isinstance(position, tuple):
        position = list(position)
    if position is not None and len(position) != 2:
        raise ValueError("position must be [x, y].")
    if graphName and "." in graphName:
        raise ValueError("graphName must not contain '.'.")
    return position

def _check_model_name_and_position(graphName: str, position):
    if isinstance(position, tuple):
        position = list(position)
    if position is not None and len(position) != 2:
        raise ValueError("position must be [x, y].")
    return position

@mw_connect_decorator(_MwConnect._process_path)
def CreateQuickPanelLine(lineKind: str, fullDiagramName: str, startElementName: str, endElementName: str, lineName: str = "") -> bool:
    """
    创建QuickPanel连线（通用入口）

    语法
        >>> CreateQuickPanelLine(lineKind:str, fullDiagramName:str, startElementName:str, endElementName:str, lineName:str = "")
    说明
        CreateQuickPanelLine(lineKind, fullDiagramName, startElementName, endElementName, lineName)用于按QuickPanel连线类型创建连线。
        lineKind支持以下关键字：`copy`、`satisfy`、`derive`、`dependency`、`containment`、`refine`、`trace`、`verify`、
        `import`、`control_flow`、`object_flow`、`connector`、`binding_connector`、`transition`、`include`、`extend`、
        `association`、`generalization`、`allocate`、`directed_association`、`aggregation`、`composition`。
        其中`control_flow`、`object_flow`和`transition`支持在找不到端点SysML元素时按图形名称兜底定位；
        `connector`和`binding_connector`除支持元素全名外，还支持以`组成属性名.端口名`形式传入图中的端口限定名。
        不同lineKind仅允许在对应视图中创建，且后端会同时校验端点类型、端点方向以及关系合法性；创建失败时返回False。

        lineName参数用于设置连线名称（可选，默认为空）：
        - 对于`control_flow`（控制流）：格式为 "[guard]" 时被视为守卫条件，例如 "[x > 0]"
        - 对于`transition`（转移）：作为守卫条件，例如 "x > 0"
        - 对于其他类型连线：作为普通连线名称
    示例
        >>> print(CreateQuickPanelLine("satisfy", "Package1.REQ1", "Package1.func1", "Package1.req1"))
        >>> print(CreateQuickPanelLine("control_flow", "Package1.ACT1", "Package1.actionA", "Package1.actionB", "[x > 10]"))
    输入参数
        lineKind - QuickPanel连线类型关键字
        数据类型：str
        fullDiagramName - 目标视图全名
        数据类型：str
        startElementName - 起点元素全名；部分线型也支持图形名称或端口限定名
        数据类型：str
        endElementName - 终点元素全名；部分线型也支持图形名称或端口限定名
        数据类型：str
        lineName - 连线名称/守卫条件（可选），控制流格式 "[guard]" 时被视为守卫
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateRequirementCopyLine
        CreateActivityControlFlowLineByGraphName
        CreateStateTransitionLineByGraphName
    """
    return _run_func(CreateQuickPanelLine, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementCopyLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在需求图中创建 copy 连线

    语法
        >>> CreateRequirementCopyLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementCopyLine(fullDiagramName, startElementName, endElementName)
        用于在目标需求图中创建 copy 连线，样式与快速面板创建一致。
    示例
        >>> print(CreateRequirementCopyLine("Package1.REQ1", "Package1.reqA", "Package1.reqB"))
    输入参数
        fullDiagramName - 目标需求图全名（包含路径）
        数据类型：str
        startElementName - 起始元素全名（包含路径）
        数据类型：str
        endElementName - 终点元素全名（包含路径）
        数据类型：str
    返回值
        `bool` : 创建成功返回 True，否则返回 False
    另请参阅
        InsertElementToDiagram
    """
    return CreateQuickPanelLine("copy", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementSatisfyLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    创建satisfy连线

    语法
        >>> CreateRequirementSatisfyLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementSatisfyLine(fullDiagramName, startElementName, endElementName)用于创建satisfy连线。
        目标视图支持需求图、模块定义图和活动图；终点元素必须为需求。
    示例
        >>> print(CreateRequirementSatisfyLine("Package1.REQ1", "Package1.func1", "Package1.req1"))
    输入参数
        fullDiagramName - 目标视图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点需求元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("satisfy", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementDeriveLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在需求图中创建derive连线

    语法
        >>> CreateRequirementDeriveLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementDeriveLine(fullDiagramName, startElementName, endElementName)用于在需求图中创建derive连线。
        起点和终点都必须是需求元素。
    示例
        >>> print(CreateRequirementDeriveLine("Package1.REQ1", "Package1.reqA", "Package1.reqB"))
    输入参数
        fullDiagramName - 目标需求图全名
        数据类型：str
        startElementName - 起点需求元素全名
        数据类型：str
        endElementName - 终点需求元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("derive", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementDependencyLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    创建dependency连线

    语法
        >>> CreateRequirementDependencyLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementDependencyLine(fullDiagramName, startElementName, endElementName)用于创建dependency连线。
        目标视图支持需求图和包图；端点需能在目标视图中解析到对应图块。
    示例
        >>> print(CreateRequirementDependencyLine("Package1.REQ1", "Package1.reqA", "Package1.reqB"))
    输入参数
        fullDiagramName - 目标视图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("dependency", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementContainmentLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    创建containment连线

    语法
        >>> CreateRequirementContainmentLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementContainmentLine(fullDiagramName, startElementName, endElementName)用于创建containment连线。
        目标视图支持需求图和包图；创建成功后会同步调整终点元素的父级，使其被起点元素包含。
    示例
        >>> print(CreateRequirementContainmentLine("Package1.REQ1", "Package1.reqParent", "Package1.reqChild"))
    输入参数
        fullDiagramName - 目标视图全名
        数据类型：str
        startElementName - 起点元素全名（包含者）
        数据类型：str
        endElementName - 终点元素全名（被包含者）
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("containment", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementRefineLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在需求图中创建refine连线

    语法
        >>> CreateRequirementRefineLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementRefineLine(fullDiagramName, startElementName, endElementName)用于创建refine连线。
        目标视图支持需求图和模块定义图；起点必须是需求，终点可为需求、活动或块。
    示例
        >>> print(CreateRequirementRefineLine("Package1.REQ1", "Package1.reqA", "Package1.reqB"))
    输入参数
        fullDiagramName - 目标视图全名
        数据类型：str
        startElementName - 起点需求元素全名
        数据类型：str
        endElementName - 终点需求、活动或块元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("refine", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementTraceLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在需求图中创建trace连线

    语法
        >>> CreateRequirementTraceLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementTraceLine(fullDiagramName, startElementName, endElementName)用于在需求图中创建trace连线。
        端点需能在目标需求图中解析到对应图块。
    示例
        >>> print(CreateRequirementTraceLine("Package1.REQ1", "Package1.reqA", "Package1.reqB"))
    输入参数
        fullDiagramName - 目标需求图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("trace", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateRequirementVerifyLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在需求图中创建verify连线

    语法
        >>> CreateRequirementVerifyLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateRequirementVerifyLine(fullDiagramName, startElementName, endElementName)用于在需求图中创建verify连线。
        终点元素必须为需求。
    示例
        >>> print(CreateRequirementVerifyLine("Package1.REQ1", "Package1.testCase1", "Package1.req1"))
    输入参数
        fullDiagramName - 目标需求图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点需求元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("verify", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreatePackageImportLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在包图中创建import连线

    语法
        >>> CreatePackageImportLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreatePackageImportLine(fullDiagramName, startElementName, endElementName)用于在包图中创建import连线。
        该接口仅支持包图。
    示例
        >>> print(CreatePackageImportLine("Package1.PKG1", "Package1.pkgA", "Package1.pkgB"))
    输入参数
        fullDiagramName - 目标包图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("import", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityControlFlowLine(fullDiagramName: str, startElementName: str, endElementName: str, lineName: str = "") -> bool:
    """
    在活动图中创建control flow连线

    语法
        >>> CreateActivityControlFlowLine(fullDiagramName:str, startElementName:str, endElementName:str, lineName:str = "")
    说明
        CreateActivityControlFlowLine(fullDiagramName, startElementName, endElementName, lineName)用于在活动图中创建control flow连线。
        默认按元素全名解析端点；若端点是无SysML数据的逻辑节点，请改用CreateActivityControlFlowLineByGraphName。
        初始节点只能作为起点，活动终止节点和流终止节点只能作为终点。

        lineName参数用于设置连线名称/守卫条件（可选，默认为空）：
        - 格式为 "[guard]" 时被视为守卫条件，例如 "[x > 0]"
        - 不带方括号时作为普通连线名称
    示例
        >>> print(CreateActivityControlFlowLine("Package1.ACT1", "Package1.actionA", "Package1.actionB"))
        >>> print(CreateActivityControlFlowLine("Package1.ACT1", "Package1.decision", "Package1.actionA", "[x > 10]"))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
        lineName - 连线名称/守卫条件（可选），格式 "[guard]" 时被视为守卫
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    return CreateQuickPanelLine("control_flow", fullDiagramName, startElementName, endElementName, lineName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityObjectFlowLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在活动图中创建object flow连线

    语法
        >>> CreateActivityObjectFlowLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateActivityObjectFlowLine(fullDiagramName, startElementName, endElementName)用于在活动图中创建object flow连线。
        默认按元素全名解析端点；若端点是无SysML数据的逻辑节点，请改用CreateActivityObjectFlowLineByGraphName。
        当活动端点缺少输入端口或输出端口时，后端会按QuickPanel行为自动补齐端口后再创建连线。
        初始节点只能作为起点，活动终止节点和流终止节点只能作为终点。
        支持以"元素全名.端口名"格式指定端点，如"活动1.out1"或"包1.活动1.out1"。
    示例
        >>> print(CreateActivityObjectFlowLine("Package1.ACT1", "Package1.actionA", "Package1.actionB"))
        >>> print(CreateActivityObjectFlowLine("活动1.活动图1", "活动1.out1", "DecisionNode"))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        startElementName - 起点元素全名或"元素全名.端口名"格式
        数据类型：str
        endElementName - 终点元素全名或"元素全名.端口名"格式
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityObjectFlowLineByGraphName
    """
    return CreateQuickPanelLine("object_flow", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityInitialNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建初始节点

    语法
        >>> CreateActivityInitialNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityInitialNode(fullDiagramName, graphName, position)用于在活动图中创建初始节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityInitialNode("Package1.ACT1", "initial_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityInitialNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityFinalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建活动终止节点

    语法
        >>> CreateActivityFinalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityFinalNode(fullDiagramName, graphName, position)用于在活动图中创建活动终止节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityFinalNode("Package1.ACT1", "activity_final_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityFinalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityFlowFinalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建流终止节点

    语法
        >>> CreateActivityFlowFinalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityFlowFinalNode(fullDiagramName, graphName, position)用于在活动图中创建流终止节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityFlowFinalNode("Package1.ACT1", "flow_final_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityObjectFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityFlowFinalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityDecisionNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建决策节点

    语法
        >>> CreateActivityDecisionNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityDecisionNode(fullDiagramName, graphName, position)用于在活动图中创建决策节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityDecisionNode("Package1.ACT1", "decision_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityDecisionNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityMergeNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建合并节点

    语法
        >>> CreateActivityMergeNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityMergeNode(fullDiagramName, graphName, position)用于在活动图中创建合并节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityMergeNode("Package1.ACT1", "merge_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityObjectFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityMergeNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityEventNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建事件节点

    语法
        >>> CreateActivityEventNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityEventNode(fullDiagramName, graphName, position)用于在活动图中创建事件节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityEventNode("Package1.ACT1", "event_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityEventNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivitySignalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建信号节点

    语法
        >>> CreateActivitySignalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivitySignalNode(fullDiagramName, graphName, position)用于在活动图中创建信号节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivitySignalNode("Package1.ACT1", "signal_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivitySignalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityTimeEventNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建时间事件节点

    语法
        >>> CreateActivityTimeEventNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityTimeEventNode(fullDiagramName, graphName, position)用于在活动图中创建时间事件节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityTimeEventNode("Package1.ACT1", "time_event_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityTimeEventNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityForkNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建分叉节点（横向）

    语法
        >>> CreateActivityForkNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityForkNode(fullDiagramName, graphName, position)用于在活动图中创建横向分叉节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityForkNode("Package1.ACT1", "fork_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityForkNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityForkVerticalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建分叉节点（纵向）

    语法
        >>> CreateActivityForkVerticalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityForkVerticalNode(fullDiagramName, graphName, position)用于在活动图中创建纵向分叉节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityForkVerticalNode("Package1.ACT1", "fork_vertical_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityForkVerticalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityJoinNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建汇合节点（横向）

    语法
        >>> CreateActivityJoinNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityJoinNode(fullDiagramName, graphName, position)用于在活动图中创建横向汇合节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityJoinNode("Package1.ACT1", "join_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityJoinNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityJoinVerticalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在活动图中创建汇合节点（纵向）

    语法
        >>> CreateActivityJoinVerticalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateActivityJoinVerticalNode(fullDiagramName, graphName, position)用于在活动图中创建纵向汇合节点。
        该接口仅创建图形节点，不创建新的SysML元素；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateActivityJoinVerticalNode("Package1.ACT1", "join_vertical_node", [100, 200]))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateActivityJoinVerticalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateInitialNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建初始状态节点

    语法
        >>> CreateStateInitialNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateInitialNode(fullDiagramName, graphName, position)用于在状态机图中创建初始状态节点。
        该接口会同时创建状态机中的SysML初始节点及其图形节点；同一父级层次下仅允许存在一个初始状态。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateInitialNode("Package1.STM1", "state_initial", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateInitialNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateFinalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建结束状态节点

    语法
        >>> CreateStateFinalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateFinalNode(fullDiagramName, graphName, position)用于在状态机图中创建结束状态节点。
        该接口会同时创建对应的SysML节点及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateFinalNode("Package1.STM1", "state_final", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateFinalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateTerminateNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建终止状态节点

    语法
        >>> CreateStateTerminateNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateTerminateNode(fullDiagramName, graphName, position)用于在状态机图中创建终止状态节点。
        该接口会同时创建对应的SysML节点及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateTerminateNode("Package1.STM1", "state_terminate", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateTerminateNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateChoiceNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建选择节点

    语法
        >>> CreateStateChoiceNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateChoiceNode(fullDiagramName, graphName, position)用于在状态机图中创建选择节点。
        该接口会同时创建对应的SysML节点及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateChoiceNode("Package1.STM1", "state_choice", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateChoiceNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateForkNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建分叉节点（横向）

    语法
        >>> CreateStateForkNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateForkNode(fullDiagramName, graphName, position)用于在状态机图中创建横向分叉节点。
        该接口会同时创建对应的SysML节点及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateForkNode("Package1.STM1", "state_fork", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateForkNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateForkVerticalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建分叉节点（纵向）

    语法
        >>> CreateStateForkVerticalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateForkVerticalNode(fullDiagramName, graphName, position)用于在状态机图中创建纵向分叉节点。
        该接口会同时创建对应的SysML节点及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateForkVerticalNode("Package1.STM1", "state_fork_vertical", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateForkVerticalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateJoinNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建汇合节点（横向）

    语法
        >>> CreateStateJoinNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateJoinNode(fullDiagramName, graphName, position)用于在状态机图中创建横向汇合节点。
        该接口会同时创建对应的SysML节点及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateJoinNode("Package1.STM1", "state_join", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateJoinNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateJoinVerticalNode(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建汇合节点（纵向）

    语法
        >>> CreateStateJoinVerticalNode(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateStateJoinVerticalNode(fullDiagramName, graphName, position)用于在状态机图中创建纵向汇合节点。
        该接口会同时创建对应的SysML节点及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateStateJoinVerticalNode("Package1.STM1", "state_join_vertical", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateStateJoinVerticalNode, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateState(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建状态

    语法
        >>> CreateState(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateState(fullDiagramName, graphName, position)用于在状态机图中创建状态。
        该接口会同时创建对应的SysML状态元素及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName按SysML2模型名规则处理，名称中包含`.`时会自动规范化为合法名称；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateState("Package1.STM1", "state1", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_model_name_and_position(graphName, position)
    return _run_func(CreateState, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateCompositeState(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建组合状态

    语法
        >>> CreateCompositeState(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateCompositeState(fullDiagramName, graphName, position)用于在状态机图中创建组合状态。
        该接口会同时创建对应的SysML状态元素及其图形节点，并自动创建1个区域；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName按SysML2模型名规则处理，名称中包含`.`时会自动规范化为合法名称；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateCompositeState("Package1.STM1", "composite_state1", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_model_name_and_position(graphName, position)
    return _run_func(CreateCompositeState, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateOrthogonalState(fullDiagramName: str, graphName: str = "", position: list = None) -> bool:
    """
    在状态机图中创建正交状态

    语法
        >>> CreateOrthogonalState(fullDiagramName:str, graphName:str = "", position:list = None)
    说明
        CreateOrthogonalState(fullDiagramName, graphName, position)用于在状态机图中创建正交状态。
        该接口会同时创建对应的SysML状态元素及其图形节点，并自动创建2个区域；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName按SysML2模型名规则处理，名称中包含`.`时会自动规范化为合法名称；position用于指定图中的放置坐标，格式为`[x, y]`。
    示例
        >>> print(CreateOrthogonalState("Package1.STM1", "orthogonal_state1", [100, 200]))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    position = _check_model_name_and_position(graphName, position)
    return _run_func(CreateOrthogonalState, locals())

@mw_connect_decorator(_MwConnect._process_path)
def CreateSubState(parentStateFullName: str, regionIndex: int = 0, graphName: str = "", position: list = None) -> bool:
    """
    在状态的指定区域中创建子状态

    语法
        >>> CreateSubState(parentStateFullName:str, regionIndex:int = 0, graphName:str = "", position:list = None)
    说明
        CreateSubState(parentStateFullName, regionIndex, graphName, position)用于在状态的指定区域中创建子状态。
        该接口会同时创建对应的SysML状态元素及其图形节点；未显式传入graphName时，系统会自动生成唯一图形名称。
        graphName必须是不包含`.`的简单名；position用于指定图中的放置坐标，格式为`[x, y]`。
        组合状态只有1个区域（索引0），正交状态有多个区域（索引0、1等）。
    示例
        >>> print(CreateSubState("statemachine.composite_state", 0, "sub_state1"))
        >>> print(CreateSubState("statemachine.orthogonal_state", 1, "sub_state2", [100, 200]))
    输入参数
        parentStateFullName - 父状态全名
        数据类型：str
        regionIndex - 区域索引，默认为0
        数据类型：int
        graphName - 图中的显示名称；为空时自动生成
        数据类型：str
        position - 图中坐标，格式为[x, y]；不传则使用系统默认位置
        数据类型：list
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateCompositeState, CreateOrthogonalState
    """
    position = _check_graph_name_and_position(graphName, position)
    return _run_func(CreateSubState, locals())

def _check_simple_graph_name(name: str, param_name: str):
    """
    校验图形名称是否有效。
    用于活动图中按图形名称创建连线，支持简单名和带”.”的限定名。
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{param_name} must be a non-empty str.")

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityControlFlowLineByGraphName(fullDiagramName: str, startGraphName: str, endGraphName: str, lineName: str = "") -> bool:
    """
    在活动图中按图形名称创建 control flow 连线

    语法
        >>> CreateActivityControlFlowLineByGraphName(fullDiagramName:str, startGraphName:str, endGraphName:str, lineName:str = "")
    说明
        CreateActivityControlFlowLineByGraphName(fullDiagramName, startGraphName, endGraphName, lineName)用于在活动图中按图形名称创建control flow连线。
        startGraphName和endGraphName支持简单名或带"."的限定名（如"活动1.out1"）。
        后端会优先按SysML全名解析，找不到时自动按图形名称兜底定位并创建图线。

        lineName参数用于设置连线名称/守卫条件（可选，默认为空）：
        - 格式为 "[guard]" 时被视为守卫条件，例如 "[x > 0]"
        - 不带方括号时作为普通连线名称
    示例
        >>> print(CreateActivityControlFlowLineByGraphName("Package1.ACT1", "initial_node", "decision_node"))
        >>> print(CreateActivityControlFlowLineByGraphName("Package1.ACT1", "decision_node", "actionA", "[x > 10]"))
        >>> print(CreateActivityControlFlowLineByGraphName("活动1.活动图1", "活动1.out1", "DecisionNode"))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        startGraphName - 起点图形名称，支持简单名或"元素全名.端口名"格式
        数据类型：str
        endGraphName - 终点图形名称，支持简单名或"元素全名.端口名"格式
        数据类型：str
        lineName - 连线名称/守卫条件（可选），格式 "[guard]" 时被视为守卫
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityControlFlowLine
    """
    _check_simple_graph_name(startGraphName, "startGraphName")
    _check_simple_graph_name(endGraphName, "endGraphName")
    return CreateQuickPanelLine("control_flow", fullDiagramName, startGraphName, endGraphName, lineName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateActivityObjectFlowLineByGraphName(fullDiagramName: str, startGraphName: str, endGraphName: str) -> bool:
    """
    在活动图中按图形名称创建 object flow 连线

    语法
        >>> CreateActivityObjectFlowLineByGraphName(fullDiagramName:str, startGraphName:str, endGraphName:str)
    说明
        CreateActivityObjectFlowLineByGraphName(fullDiagramName, startGraphName, endGraphName)用于在活动图中按图形名称创建object flow连线。
        startGraphName和endGraphName支持简单名或带"."的限定名（如"活动1.out1"）。
        后端会优先按SysML全名解析，找不到时自动按图形名称兜底定位并创建图线。
    示例
        >>> print(CreateActivityObjectFlowLineByGraphName("Package1.ACT1", "decision_node", "merge_node"))
        >>> print(CreateActivityObjectFlowLineByGraphName("活动1.活动图1", "活动1.活动1.out1", "DecisionNode"))
    输入参数
        fullDiagramName - 目标活动图全名
        数据类型：str
        startGraphName - 起点图形名称，支持简单名或"元素全名.端口名"格式
        数据类型：str
        endGraphName - 终点图形名称，支持简单名或"元素全名.端口名"格式
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateActivityObjectFlowLine
    """
    _check_simple_graph_name(startGraphName, "startGraphName")
    _check_simple_graph_name(endGraphName, "endGraphName")
    return CreateQuickPanelLine("object_flow", fullDiagramName, startGraphName, endGraphName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateTransitionLine(fullDiagramName: str, startElementName: str, endElementName: str, lineName: str = "") -> bool:
    """
    在状态机图中创建transition连线

    语法
        >>> CreateStateTransitionLine(fullDiagramName:str, startElementName:str, endElementName:str, lineName:str = "")
    说明
        CreateStateTransitionLine(fullDiagramName, startElementName, endElementName, lineName)用于在状态机图中创建transition连线。
        默认按元素全名解析端点；若端点是按图形名称创建的节点，请改用CreateStateTransitionLineByGraphName。
        lineName参数用于设置守卫条件（可选），例如 "x > 0"。
    示例
        >>> print(CreateStateTransitionLine("Package1.STM1", "Package1.stateA", "Package1.stateB"))
        >>> print(CreateStateTransitionLine("Package1.STM1", "Package1.stateA", "Package1.stateB", "x > 10"))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
        lineName - 守卫条件（可选）
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLineByGraphName
    """
    return CreateQuickPanelLine("transition", fullDiagramName, startElementName, endElementName, lineName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateTransitionLineByGraphName(fullDiagramName: str, startGraphName: str, endGraphName: str, lineName: str = "") -> bool:
    """
    在状态机图中按图形名称创建 transition 连线

    语法
        >>> CreateStateTransitionLineByGraphName(fullDiagramName:str, startGraphName:str, endGraphName:str, lineName:str = "")
    说明
        CreateStateTransitionLineByGraphName(fullDiagramName, startGraphName, endGraphName, lineName)用于在状态机图中按图形名称创建transition连线。
        startGraphName和endGraphName需传图中图块名称，必须为不包含`.`的简单名。
        lineName参数用于设置守卫条件（可选），例如 "x > 0"。
    示例
        >>> print(CreateStateTransitionLineByGraphName("Package1.STM1", "state_initial", "state_choice"))
        >>> print(CreateStateTransitionLineByGraphName("Package1.STM1", "state_initial", "state_choice", "x > 10"))
    输入参数
        fullDiagramName - 目标状态机图全名
        数据类型：str
        startGraphName - 起点图形名称，不含`.`
        数据类型：str
        endGraphName - 终点图形名称，支持简单名或"元素全名.端口名"格式
        数据类型：str
        lineName - 守卫条件（可选）
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateStateTransitionLine
    """
    _check_simple_graph_name(startGraphName, "startGraphName")
    _check_simple_graph_name(endGraphName, "endGraphName")
    return CreateQuickPanelLine("transition", fullDiagramName, startGraphName, endGraphName, lineName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateConnectorLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在内部模块图中创建connector连线

    语法
        >>> CreateConnectorLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateConnectorLine(fullDiagramName, startElementName, endElementName)用于在内部模块图中创建connector连线。
        除可直接传元素全名外，也支持传图中的端口限定名，格式为`组成属性名.端口名`。
    示例
        >>> print(CreateConnectorLine("Package1.IBD1", "partA.port1", "partB.port2"))
    输入参数
        fullDiagramName - 目标内部模块图全名
        数据类型：str
        startElementName - 起点元素全名；也支持端口限定名
        数据类型：str
        endElementName - 终点元素全名；也支持端口限定名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("connector", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateBindingConnectorLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在内部模块图或参数图中创建binding connector连线

    语法
        >>> CreateBindingConnectorLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateBindingConnectorLine(fullDiagramName, startElementName, endElementName)用于在内部模块图或参数图中创建binding connector连线。
        除可直接传元素全名外，也支持传图中的端口限定名，格式为`组成属性名.端口名`。
    示例
        >>> print(CreateBindingConnectorLine("Package1.IBD1", "partA.port1", "partB.port2"))
    输入参数
        fullDiagramName - 目标内部模块图或参数图全名
        数据类型：str
        startElementName - 起点元素全名；也支持端口限定名
        数据类型：str
        endElementName - 终点元素全名；也支持端口限定名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("binding_connector", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateUseCaseIncludeLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在用例图中创建include连线

    语法
        >>> CreateUseCaseIncludeLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateUseCaseIncludeLine(fullDiagramName, startElementName, endElementName)用于在用例图中创建include连线。
        起点和终点都必须是用例元素。
    示例
        >>> print(CreateUseCaseIncludeLine("Package1.UC1", "Package1.ucA", "Package1.ucB"))
    输入参数
        fullDiagramName - 目标用例图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("include", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateUseCaseExtendLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在用例图中创建extend连线

    语法
        >>> CreateUseCaseExtendLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateUseCaseExtendLine(fullDiagramName, startElementName, endElementName)用于在用例图中创建extend连线。
        起点和终点都必须是用例元素。
    示例
        >>> print(CreateUseCaseExtendLine("Package1.UC1", "Package1.ucA", "Package1.ucB"))
    输入参数
        fullDiagramName - 目标用例图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("extend", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateUseCaseAssociationLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在用例图中创建association连线

    语法
        >>> CreateUseCaseAssociationLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateUseCaseAssociationLine(fullDiagramName, startElementName, endElementName)用于在用例图中创建association连线。
        该接口仅支持用例图。
    示例
        >>> print(CreateUseCaseAssociationLine("Package1.UC1", "Package1.actor1", "Package1.ucA"))
    输入参数
        fullDiagramName - 目标用例图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("association", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateGeneralizationLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    创建generalization连线

    语法
        >>> CreateGeneralizationLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateGeneralizationLine(fullDiagramName, startElementName, endElementName)用于创建generalization连线。
        该接口依赖QuickPanel规则校验视图与端点，可用于支持泛化关系的视图。
    示例
        >>> print(CreateGeneralizationLine("Package1.BDD1", "Package1.blockA", "Package1.blockB"))
    输入参数
        fullDiagramName - 目标视图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("generalization", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateAllocateLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在模块定义图中创建allocate连线

    语法
        >>> CreateAllocateLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateAllocateLine(fullDiagramName, startElementName, endElementName)用于在模块定义图中创建allocate连线。
        该接口仅支持模块定义图。
    示例
        >>> print(CreateAllocateLine("Package1.BDD1", "Package1.blockA", "Package1.activity1"))
    输入参数
        fullDiagramName - 目标模块定义图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("allocate", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateDirectedAssociationLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在模块定义图中创建directed association连线

    语法
        >>> CreateDirectedAssociationLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateDirectedAssociationLine(fullDiagramName, startElementName, endElementName)用于在模块定义图中创建directed association连线。
        该接口仅支持模块定义图。
    示例
        >>> print(CreateDirectedAssociationLine("Package1.BDD1", "Package1.blockA", "Package1.blockB"))
    输入参数
        fullDiagramName - 目标模块定义图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("directed_association", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateAggregationLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在模块定义图中创建aggregation连线

    语法
        >>> CreateAggregationLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateAggregationLine(fullDiagramName, startElementName, endElementName)用于在模块定义图中创建aggregation连线。
        该接口仅支持模块定义图。
    示例
        >>> print(CreateAggregationLine("Package1.BDD1", "Package1.blockWhole", "Package1.blockPart"))
    输入参数
        fullDiagramName - 目标模块定义图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("aggregation", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateCompositionLine(fullDiagramName: str, startElementName: str, endElementName: str) -> bool:
    """
    在模块定义图中创建composition连线

    语法
        >>> CreateCompositionLine(fullDiagramName:str, startElementName:str, endElementName:str)
    说明
        CreateCompositionLine(fullDiagramName, startElementName, endElementName)用于在模块定义图中创建composition连线。
        该接口仅支持模块定义图。
    示例
        >>> print(CreateCompositionLine("Package1.BDD1", "Package1.blockWhole", "Package1.blockPart"))
    输入参数
        fullDiagramName - 目标模块定义图全名
        数据类型：str
        startElementName - 起点元素全名
        数据类型：str
        endElementName - 终点元素全名
        数据类型：str
    返回值
        `bool` : 创建成功返回True，否则返回False
    另请参阅
        CreateQuickPanelLine
    """
    return CreateQuickPanelLine("composition", fullDiagramName, startElementName, endElementName)

@mw_connect_decorator(_MwConnect._process_path)
def CreateStateRegion(fullName: str) -> bool:
    """
    给状态新建区域

    语法
        >>> CreateStateRegion(fullName:str)
    说明
        CreateStateRegion(fullName)用于在状态机中给状态新建区域，行为参考状态图块右键菜单“新建区域”。
        支持普通状态、组合状态、正交状态；若当前状态已设置子状态机则不允许新建区域。
    示例
        >>> print(CreateStateRegion("包1.状态机图1.状态1"))
    输入参数
        fullName - 目标状态元素全名
        数据类型：str
    返回值
        `bool` : 新建结果，True 表示成功
    另请参阅
        SetStateSubMachine
    """
    return _run_func(CreateStateRegion, locals())

@mw_connect_decorator(_MwConnect._process_path)
def GenerateSystemDesignReport() -> str:
    """
    生成系统方案设计报告

    语法
        >>> GenerateSystemDesignReport()
    说明
        GenerateSystemDesignReport() 用于按固定策略生成系统方案设计报告，不弹出报告选择窗口。
        生成逻辑等价于：
        1. 报告模板固定为“系统方案设计报告”；
        2. 系统方案设计章节逐项处理；
        3. 每个章节中的专项数据执行“全选”后确认生成。
    示例
        示例1：生成系统方案设计报告
        >>> print(GenerateSystemDesignReport())
    输入参数
        无
    返回值
        `str` : 生成成功返回报告文件路径；失败返回空字符串
    另请参阅
        GenerateModelicaSimulationFramework
    """
    return _run_func(GenerateSystemDesignReport, locals())

@mw_connect_decorator(_MwConnect._process_path)
def GenerateModelicaSimulationFramework(fullName: str) -> bool:
    """
    生成Modelica仿真框架

    语法
        >>> GenerateModelicaSimulationFramework(fullName:str)
    说明
        GenerateModelicaSimulationFramework(fullName) 用于对指定元素触发生成Modelica仿真框架流程。
        当前版本仅执行前置校验：fullName 必须对应内部模块图（IBD）元素。
    示例
        示例1：对指定内部模块图触发生成流程
        >>> print(GenerateModelicaSimulationFramework("Package1.SystemModel.IBD1"))
    输入参数
        fullName - 目标内部模块图元素的全名（不可缺省）
        数据类型：str
    返回值
        `bool` : 执行结果，True 表示通过前置校验
    另请参阅
        NewIBDDiagram
    """
    return _run_func(GenerateModelicaSimulationFramework, locals())
    
# ------------------------------设置参数---------------------------------------

@mw_connect_decorator(_MwConnect._process_path)
def CreateRelationMapping(sourceFullName: str, targetFullName: str) -> bool:
    """
    创建关系映射

    语法
        >>> CreateRelationMapping(sourceFullName:str, targetFullName:str)
    说明
        CreateRelationMapping(sourceFullName, targetFullName) 创建与“关系映射”窗口连线等价的映射，数据方向为源变量到目标变量。
        是否能够创建由关系映射窗口的连线规则决定；两端必须是支持映射的变量，且不能是同一变量。重复调用已有映射按成功处理。
        典型端点包括需求指标、活动输入/输出接口、块值属性和约束输入/输出参数；建立映射前应保证两端类型、单位和值语义兼容。
    示例
        示例1：把需求指标映射到任务场景参数
        >>> print(CreateRelationMapping("Requirements.targetOrbitAltitude", "Mission.targetOrbitAltitude"))
    输入参数
        sourceFullName - 源变量全名（箭头起点）
        数据类型：str
        targetFullName - 目标变量全名（箭头终点）
        数据类型：str
    返回值
        `bool` : 创建结果，True 表示映射已存在或创建成功
    另请参阅
        CalculateParametricDiagram
    """
    return _run_func(CreateRelationMapping, locals())


@mw_connect_decorator(_MwConnect._process_path)
def CalculateParametricDiagram(fullName: str) -> str:
    """
    计算参数图

    语法
        >>> CalculateParametricDiagram(fullName:str)
    说明
        CalculateParametricDiagram(fullName) 执行与参数图“仿真 → 约束计算 → 计算”相同的流程，但不会打开参数图、切换视图或显示计算及报错弹窗。
        结果写入工程工作目录下的 parameter_calculation.json，并返回该文件的绝对路径。
        计算成功时 JSON 的 values 保存右侧计算参数栏的层级、元素全名和数值；计算失败时 JSON 的 error 保存错误信息。
        执行前应完成约束表达式、参数图绑定和本场景需要的全部关系映射；验证需求指标时还应检查约束满足情况。
    示例
        示例1：计算指定参数图
        >>> print(CalculateParametricDiagram("Package1.ConstraintBlock1.ParametricDiagram1"))
        > 工程工作目录/parameter_calculation.json
    输入参数
        fullName - 参数图全名（不可缺省）
        数据类型：str
    返回值
        `str` : JSON 结果文件的绝对路径；参数图无效或文件无法写入时返回空字符串
    另请参阅
        CreateRelationMapping, ExportSemanticJson
    """
    return _run_func(CalculateParametricDiagram, locals())
    
@mw_connect_decorator(_MwConnect._process_path)
def SetName(fullName: str, newName: str) -> bool:
    """
    设置元素名称

    语法
        >>> SetName(fullName:str, newName:str)
    说明
        SetName(fullName, newName) 用于根据全名找到指定元素并重命名；命名限制与模型树重命名一致，可通过单引号包裹名称段来包含`.`（如 `'A.B'`），新名称与旧值相同时不执行任何操作。
    示例
        示例1：重命名指定元素
        >>> print(SetName("Package1.Engine", "NewEngine"))
    输入参数
        fullName - 目标元素的全名（包含路径）
        数据类型：str
        newName - 新名称
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetName, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetRequirementId(fullName: str, newId: str) -> bool:
    """
    设置需求ID

    语法
        >>> SetRequirementId(fullName:str, newId:str)
    说明
        SetRequirementId(fullName, newId) 用于设置指定需求元素的 ID。
    示例
        示例1：设置需求ID
        >>> print(SetRequirementId("Package1.Req1", "REQ-001"))
    输入参数
        fullName - 目标需求元素的全名（包含路径）
        数据类型：str
        newId - 新的需求 ID
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetRequirementText
    """
    return _run_func(SetRequirementId, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetRequirementText(fullName: str, newText: str) -> bool:
    """
    设置需求文本

    语法
        >>> SetRequirementText(fullName:str, newText:str)
    说明
        SetRequirementText(fullName, newText) 用于设置指定需求元素的文本内容。
    示例
        示例1：设置需求文本
        >>> print(SetRequirementText("Package1.Req1", "系统应支持最大100个并发用户"))
    输入参数
        fullName - 目标需求元素的全名（包含路径）
        数据类型：str
        newText - 新的需求文本内容
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetRequirementId
    """
    return _run_func(SetRequirementText, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetMultiplicity(fullName: str, multiplicity: str) -> bool:
    """
    设置多重性

    语法
        >>> SetMultiplicity(fullName:str, multiplicity:str)
    说明
        SetMultiplicity(fullName, multiplicity) 用于设置指定元素的多重性范围。
        支持格式：单值（"1"）、范围（"0..1"）、无上限（"1..*" 或 "*"）。
    示例
        示例1：设置单值多重性
        >>> print(SetMultiplicity("Package1.Block1.parts", "1"))
        示例2：设置范围多重性
        >>> print(SetMultiplicity("Package1.Block1.parts", "0..1"))
        示例3：设置无上限多重性
        >>> print(SetMultiplicity("Package1.Block1.parts", "1..*"))
    输入参数
        fullName - 目标元素的全名（包含路径）
        数据类型：str
        multiplicity - 多重性字符串
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetMultiplicity, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetDefaultValue(fullName: str, newValue: str) -> bool:
    """
    设置属性默认值

    语法
        >>> SetDefaultValue(fullName:str, newValue:str)
    说明
        SetDefaultValue(fullName, newValue) 用于设置指定属性 usage 的默认值。
        仅支持定义为数据类型或值类型的 AttributeUsage 或 ConstraintParameter；若属性定义不是值定义，应通过实例设置逻辑处理。
        当 fullName 指向实例继承的值属性且 newValue 非空时，会先在实例下创建该值属性的重定义，再写入默认值。
        当 newValue 为空字符串时，若目标重定义值属性没有保留实例、绑定关系或非空子属性，会按实例属性对话框逻辑删除该重定义节点；否则仅清空默认值。
        本接口不负责新建顶层实例；设置实例继承值属性前，目标实例本身需要已存在。
    示例
        示例1：设置属性默认值
        >>> print(SetDefaultValue("Package1.Block1.speed", "100"))
    输入参数
        fullName - 目标属性元素的全名（包含路径）
        数据类型：str
        newValue - 新的默认值
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetDefaultValue, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetUnit(fullName: str, newUnit: str) -> bool:
    """
    设置属性单位

    语法
        >>> SetUnit(fullName:str, newUnit:str)
    说明
        SetUnit(fullName, newUnit) 用于设置指定属性的计量单位。
        仅支持定义为基础数据类型的 AttributeUsage 或 ConstraintParameter；若属性定义不是基础数据类型，应通过实例设置逻辑处理。
    示例
        示例1：设置属性单位
        >>> print(SetUnit("Package1.Block1.speed", "km/h"))
    输入参数
        fullName - 目标属性元素的全名（包含路径）
        数据类型：str
        newUnit - 新的计量单位字符串
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetUnit, locals())

@mw_connect_decorator(_MwConnect._process_path)
def SetType(fullName: str, newTypeName: str) -> bool:
    """
    设置元素类型

    语法
        >>> SetType(fullName:str, newTypeName:str)
    说明
        SetType(fullName, newTypeName) 用于设置 Usage 元素的类型定义（Type）。
        规则与属性面板“类型”一致：仅支持允许设置类型的元素；实例与重定义元素不允许设置。
        newTypeName 可传类型全名，或基础类型短名（如 Real/Integer/Boolean/String）；
        传空字符串或 \"Untyped\" 表示清空类型（设为未定型）。
    示例
        示例1：设置值属性为 Real
        >>> print(SetType("Package1.Block1.value1", "Real"))
        示例2：设置零件属性为某个块类型
        >>> print(SetType("Package1.System.partA", "Package1.BlockA"))
        示例3：清空类型
        >>> print(SetType("Package1.System.partA", "Untyped"))
    输入参数
        fullName - 目标元素全名（包含路径）
        数据类型：str
        newTypeName - 新类型名称（全名或基础类型短名）
        数据类型：str
    返回值
        `bool` : 设置成功返回 True，否则返回 False
    另请参阅
        SetDefaultValue
        SetUnit
    """
    return _run_func(SetType, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetDirection(fullName: str, direction: int) -> bool:
    """
    设置参数方向

    语法
        >>> SetDirection(fullName:str, direction:int)
    说明
        SetDirection(fullName, direction) 用于设置指定参数的方向。
    示例
        示例1：设置参数方向
        >>> print(SetDirection("Package1.Activity1.param1", 1))
    输入参数
        fullName - 目标参数元素的全名（包含路径）
        数据类型：str
        direction - 方向枚举值（SysML2DirectionKind 对应的整数）
        数据类型：int
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetConjugate
    """
    return _run_func(SetDirection, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetConjugate(fullName: str, conjugated: bool) -> bool:
    """
    设置端口共轭

    语法
        >>> SetConjugate(fullName:str, conjugated:bool)
    说明
        SetConjugate(fullName, conjugated) 用于设置指定端口的共轭标志，同时自动翻转方向。
    示例
        示例1：设置端口为共轭
        >>> print(SetConjugate("Package1.Block1.port1", True))
    输入参数
        fullName - 目标端口元素的全名（包含路径）
        数据类型：str
        conjugated - True 表示共轭，False 表示非共轭
        数据类型：bool
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetDirection
    """
    return _run_func(SetConjugate, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetStateSubMachine(fullName: str, subStateMachineFullName: str) -> bool:
    """
    设置状态的子状态机

    语法
        >>> SetStateSubMachine(fullName:str, subStateMachineFullName:str)
    说明
        SetStateSubMachine(fullName, subStateMachineFullName) 用于设置状态（包含普通状态、组合状态、正交状态）的子状态机定义。
        subStateMachineFullName 传空字符串可清空当前设置。
    示例
        示例1：设置子状态机
        >>> print(SetStateSubMachine("包1.状态机1.状态1", "包1.状态机定义1"))
        示例2：清空子状态机
        >>> print(SetStateSubMachine("包1.状态机1.状态1", ""))
    输入参数
        fullName - 目标状态元素全名
        数据类型：str
        subStateMachineFullName - 子状态机定义全名（可传空清空）
        数据类型：str
    返回值
        `bool` : 设置成功返回 True，否则返回 False
    另请参阅
        SetStateEntry
        SetStateDoActivity
        SetStateExit
    """
    return _run_func(SetStateSubMachine, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetStateEntry(fullName: str, behaviorFullName: str) -> bool:
    """
    设置状态入口动作

    语法
        >>> SetStateEntry(fullName:str, behaviorFullName:str)
    说明
        SetStateEntry(fullName, behaviorFullName) 用于设置状态（包含普通状态、组合状态、正交状态）的入口动作。
        behaviorFullName 传空字符串可清空当前设置。
    示例
        示例1：设置入口动作
        >>> print(SetStateEntry("包1.状态机1.状态1", "包1.活动1"))
        示例2：清空入口动作
        >>> print(SetStateEntry("包1.状态机1.状态1", ""))
    输入参数
        fullName - 目标状态元素全名
        数据类型：str
        behaviorFullName - 行为元素全名（支持状态机/活动/不透明行为，可传空清空）
        数据类型：str
    返回值
        `bool` : 设置成功返回 True，否则返回 False
    另请参阅
        SetStateDoActivity
        SetStateExit
    """
    return _run_func(SetStateEntry, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetStateDoActivity(fullName: str, behaviorFullName: str) -> bool:
    """
    设置状态执行活动

    语法
        >>> SetStateDoActivity(fullName:str, behaviorFullName:str)
    说明
        SetStateDoActivity(fullName, behaviorFullName) 用于设置状态（包含普通状态、组合状态、正交状态）的执行活动。
        behaviorFullName 传空字符串可清空当前设置。
    示例
        示例1：设置执行活动
        >>> print(SetStateDoActivity("包1.状态机1.状态1", "包1.不透明行为1"))
        示例2：清空执行活动
        >>> print(SetStateDoActivity("包1.状态机1.状态1", ""))
    输入参数
        fullName - 目标状态元素全名
        数据类型：str
        behaviorFullName - 行为元素全名（支持状态机/活动/不透明行为，可传空清空）
        数据类型：str
    返回值
        `bool` : 设置成功返回 True，否则返回 False
    另请参阅
        SetStateEntry
        SetStateExit
    """
    return _run_func(SetStateDoActivity, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetStateExit(fullName: str, behaviorFullName: str) -> bool:
    """
    设置状态出口动作

    语法
        >>> SetStateExit(fullName:str, behaviorFullName:str)
    说明
        SetStateExit(fullName, behaviorFullName) 用于设置状态（包含普通状态、组合状态、正交状态）的出口动作。
        behaviorFullName 传空字符串可清空当前设置。
    示例
        示例1：设置出口动作
        >>> print(SetStateExit("包1.状态机1.状态1", "包1.状态机定义2"))
        示例2：清空出口动作
        >>> print(SetStateExit("包1.状态机1.状态1", ""))
    输入参数
        fullName - 目标状态元素全名
        数据类型：str
        behaviorFullName - 行为元素全名（支持状态机/活动/不透明行为，可传空清空）
        数据类型：str
    返回值
        `bool` : 设置成功返回 True，否则返回 False
    另请参阅
        SetStateEntry
        SetStateDoActivity
    """
    return _run_func(SetStateExit, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetActivityScript(fullName: str, script: str, language: str = "") -> bool:
    """
    设置活动脚本与脚本语言

    语法
        >>> SetActivityScript(fullName:str, script:str, language:str = "")
    说明
        SetActivityScript(fullName, script, language) 用于设置活动（ActionType）的脚本内容与脚本语言。
        language 可缺省；language 传空字符串时表示不修改当前脚本语言，仅修改脚本内容。
        仅当 fullName 指向活动类型元素时可设置。
    示例
        示例1：设置活动脚本
        >>> print(SetActivityScript("Package1.Activity1", "print('hello')", "Python"))
        示例2：仅更新脚本内容，不修改当前语言
        >>> print(SetActivityScript("Package1.Activity1", "print('hello v2')"))
    输入参数
        fullName - 目标活动元素的全名（包含路径）
        数据类型：str
        script - 脚本文本内容
        数据类型：str
        language - 脚本语言名称，可缺省，缺省值为空字符串
        数据类型：str
    返回值
        `bool` : 设置成功返回 True，否则返回 False
    另请参阅
        SetOpaqueBehaviorScript
    """
    return _run_func(SetActivityScript, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetOpaqueBehaviorScript(fullName: str, script: str, language: str = "") -> bool:
    """
    设置不透明行为脚本与脚本语言

    语法
        >>> SetOpaqueBehaviorScript(fullName:str, script:str, language:str = "")
    说明
        SetOpaqueBehaviorScript(fullName, script, language) 用于设置不透明行为（OpaqueBehavior）的脚本内容与脚本语言。
        language 可缺省；language 传空字符串时表示不修改当前脚本语言，仅修改脚本内容。
        仅当 fullName 指向不透明行为元素时可设置。
    示例
        示例1：设置不透明行为脚本
        >>> print(SetOpaqueBehaviorScript("Package1.Behavior1", "return x + y;", "C"))
        示例2：仅更新脚本内容，不修改当前语言
        >>> print(SetOpaqueBehaviorScript("Package1.Behavior1", "return x + y + z;"))
    输入参数
        fullName - 目标不透明行为元素的全名（包含路径）
        数据类型：str
        script - 脚本文本内容
        数据类型：str
        language - 脚本语言名称，可缺省，缺省值为空字符串
        数据类型：str
    返回值
        `bool` : 设置成功返回 True，否则返回 False
    另请参阅
        SetActivityScript
    """
    return _run_func(SetOpaqueBehaviorScript, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetConstraintExpression(fullName: str, expression: str) -> bool:
    """
    设置约束表达式

    语法
        >>> SetConstraintExpression(fullName:str, expression:str)
    说明
        SetConstraintExpression(fullName, expression) 用于设置指定约束元素（ConstraintType 或 ConstraintUsage）的表达式内容。
    示例
        示例1：设置约束表达式
        >>> print(SetConstraintExpression("Package1.Constraint1", "x > 0 && x < 100"))
    输入参数
        fullName - 目标约束元素的全名（包含路径）
        数据类型：str
        expression - 约束表达式字符串
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetConstraintExpression, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetMetaType(fullName: str, metaClassName: str) -> bool:
    """
    设置元类型

    语法
        >>> SetMetaType(fullName:str, metaClassName:str)
    说明
        SetMetaType(fullName, metaClassName) 用于设置指定元素的元类型，元类名称为空时不执行任何操作。
    示例
        示例1：设置元类型
        >>> print(SetMetaType("Package1.Block1", "SysML.Block"))
    输入参数
        fullName - 目标元素的全名（包含路径）
        数据类型：str
        metaClassName - 元类名称字符串
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetMetaType, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetIcon(fullName: str, iconPath: str) -> bool:
    """
    设置图标

    语法
        >>> SetIcon(fullName:str, iconPath:str)
    说明
        SetIcon(fullName, iconPath) 用于设置指定构造型或用户自定义图的图标，路径为空时不执行任何操作。
    示例
        示例1：设置图标
        >>> print(SetIcon("Package1.Stereotype1", "C:/icons/my_icon.png"))
    输入参数
        fullName - 目标元素的全名（包含路径）
        数据类型：str
        iconPath - 图标文件路径
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetIcon, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetSourceType(fullName: str, sourceTypes: list) -> bool:
    """
    设置关系源端类型

    语法
        >>> SetSourceType(fullName:str, sourceTypes:list)
    说明
        SetSourceType(fullName, sourceTypes) 用于设置用户自定义关系的源端对象类型列表。
    示例
        示例1：设置源端类型
        >>> print(SetSourceType("Package1.Relation1", ["Block", "PartUsage"]))
    输入参数
        fullName - 目标关系元素的全名（包含路径）
        数据类型：str
        sourceTypes - 源端类型名称列表
        数据类型：list
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetTargetType
    """
    return _run_func(SetSourceType, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetTargetType(fullName: str, targetTypes: list) -> bool:
    """
    设置关系目标端类型

    语法
        >>> SetTargetType(fullName:str, targetTypes:list)
    说明
        SetTargetType(fullName, targetTypes) 用于设置用户自定义关系的目标端对象类型列表。
    示例
        示例1：设置目标端类型
        >>> print(SetTargetType("Package1.Relation1", ["Block", "PartUsage"]))
    输入参数
        fullName - 目标关系元素的全名（包含路径）
        数据类型：str
        targetTypes - 目标端类型名称列表
        数据类型：list
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetSourceType
    """
    return _run_func(SetTargetType, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetLineColor(fullName: str, color: str) -> bool:
    """
    设置关系线条颜色

    语法
        >>> SetLineColor(fullName:str, color:str)
    说明
        SetLineColor(fullName, color) 用于设置用户自定义关系的线条颜色，颜色以十六进制字符串表示。
    示例
        示例1：设置线条颜色为红色
        >>> print(SetLineColor("Package1.Relation1", "#ff0000"))
    输入参数
        fullName - 目标关系元素的全名（包含路径）
        数据类型：str
        color - 颜色十六进制字符串（如 "#ff0000"）
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetLineType
        SetLineWidth
    """
    return _run_func(SetLineColor, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetLineType(fullName: str, lineTypeIndex: int) -> bool:
    """
    设置关系线型

    语法
        >>> SetLineType(fullName:str, lineTypeIndex:int)
    说明
        SetLineType(fullName, lineTypeIndex) 用于设置用户自定义关系的线型。
    示例
        示例1：设置线型
        >>> print(SetLineType("Package1.Relation1", 0))
    输入参数
        fullName - 目标关系元素的全名（包含路径）
        数据类型：str
        lineTypeIndex - 线型编号
        数据类型：int
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetLineColor
        SetLineWidth
    """
    return _run_func(SetLineType, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetLineWidth(fullName: str, width: float) -> bool:
    """
    设置关系线宽

    语法
        >>> SetLineWidth(fullName:str, width:float)
    说明
        SetLineWidth(fullName, width) 用于设置用户自定义关系的线宽。
    示例
        示例1：设置线宽
        >>> print(SetLineWidth("Package1.Relation1", 1.5))
    输入参数
        fullName - 目标关系元素的全名（包含路径）
        数据类型：str
        width - 线宽数值
        数据类型：float
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetLineColor
        SetLineType
    """
    return _run_func(SetLineWidth, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetArrowType(fullName: str, arrowMacro: str) -> bool:
    """
    设置关系箭头类型

    语法
        >>> SetArrowType(fullName:str, arrowMacro:str)
    说明
        SetArrowType(fullName, arrowMacro) 用于设置用户自定义关系的箭头类型。
    示例
        示例1：设置箭头类型
        >>> print(SetArrowType("Package1.Relation1", "ARROW_OPEN"))
    输入参数
        fullName - 目标关系元素的全名（包含路径）
        数据类型：str
        arrowMacro - 箭头类型宏字符串
        数据类型：str
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        SetLineType
    """
    return _run_func(SetArrowType, locals())


@mw_connect_decorator(_MwConnect._process_path)
def SetElementSelect(fullName: str, elements: list) -> bool:
    """
    设置图支持的元素类型

    语法
        >>> SetElementSelect(fullName:str, elements:list)
    说明
        SetElementSelect(fullName, elements) 用于设置用户自定义图支持的元素类型列表。
    示例
        示例1：设置图支持的元素类型
        >>> print(SetElementSelect("Package1.Diagram1", ["Block", "PartUsage", "PortUsage"]))
    输入参数
        fullName - 目标图元素的全名（包含路径）
        数据类型：str
        elements - 元素类型字符串列表
        数据类型：list
    返回值
        `bool` : 设置结果，True 表示设置成功
    另请参阅
        无
    """
    return _run_func(SetElementSelect, locals())

@mw_connect_decorator(_MwConnect._process_path)
def NewRequirementIndex(reqFullName: str, indexName: str = "", indexValue: str = "", indexUnit: str = "", indexDesc: str = "") -> str:
    """
    新建需求指标

    语法
        >>> NewRequirementIndex(reqFullName:str, indexName:str = "", indexValue:str = "", indexUnit:str = "", indexDesc:str = "")
    说明
        NewRequirementIndex(reqFullName, indexName, indexValue, indexUnit, indexDesc) 用于在指定需求下创建指标。
        参数1：需求全名（必填），例如"需求1.需求1"
        参数2：指标名（可选），为空时自动生成唯一默认名（如Index1）；非空时会按SysML2模型名规则自动规范化。
        参数3：指标的值（可选）
        参数4：指标的单位（可选）
        参数5：指标的描述（可选）
    示例
        示例1：在需求下创建指标
        >>> result = NewRequirementIndex("需求1.需求1", "指标1", "100", "km/h", "速度指标")
        >>> print(result)
        示例2：使用默认名称创建指标
        >>> result = NewRequirementIndex("需求1.需求1")
        >>> print(result)
        示例3：指标名需要规范化
        >>> result = NewRequirementIndex("需求1.需求1", "02_ 指标")
        >>> print(result)
        > '02_ 指标'
    输入参数
        reqFullName - 需求全名
        数据类型：str
        indexName - 指标名，可为空；非空时会按SysML2模型名规则自动规范化
        数据类型：str
        indexValue - 指标的值，可为空
        数据类型：str
        indexUnit - 指标的单位，可为空
        数据类型：str
        indexDesc - 指标的描述，可为空
        数据类型：str
    返回值
        `str` : 新建的指标名
    另请参阅
        NewRequirement
    """
    return _run_func(NewRequirementIndex, locals())

@mw_connect_decorator(_MwConnect._process_path)
def GenGeometricParam(diagramFullName: str, moduleName: str, outputPath: str = "") -> str:
    """
    生成几何参数文档

    语法
        >>> GenGeometricParam(diagramFullName:str, moduleName:str, outputPath:str = "")
    说明
        GenGeometricParam(diagramFullName, moduleName, outputPath) 用于从模块定义图中提取模块的组成属性和值属性信息，并输出到Markdown文件。
    示例
        示例1：生成几何参数文档
        >>> result = GenGeometricParam("2系统设计.'2.3架构设计'.'2.3.1组成设计'.系统组合", "固体发动机系统")
        >>> print(result)
    输入参数
        diagramFullName - 模块定义图的全名（包含路径）
        数据类型：str
        moduleName - 模块名称，在图中查找
        数据类型：str
        outputPath - 输出路径名，可以为空，默认为工作目录/GeometricParam.md
        数据类型：str
    返回值
        `str` : 生成的文档文件路径
    另请参阅
        无
    """
    return _run_func(GenGeometricParam, locals())


@mw_connect_decorator(_MwConnect._process_path)
def LoginTeam(serverAddress: str, userName: str, password: str) -> bool:
    """
    登录团队资源服务器

    语法
        >>> LoginTeam(serverAddress:str, userName:str, password:str)
    说明
        LoginTeam(serverAddress, userName, password) 使用与软件登录窗口相同的服务器地址、用户名和密码登录团队资源服务器。
        登录成功后可调用团队分类、远程仓库和当前团队工程相关接口；不需要传仓库ID。
    示例
        示例1：登录团队资源服务器
        >>> result = LoginTeam("172.16.1.35:9999", "user", "password")
        >>> print(result)
        > True
    输入参数
        serverAddress - 团队资源服务器地址，格式为“主机:端口”
        数据类型：str
        userName - 团队资源服务器用户名
        数据类型：str
        password - 团队资源服务器密码
        数据类型：str
    返回值
        `bool` : 登录成功返回 True，登录失败返回 False
    另请参阅
        LogoutTeam
        GetTeamSessionInfo
    """
    return _run_func(LoginTeam, locals())


@mw_connect_decorator(_MwConnect._process_path)
def LogoutTeam() -> bool:
    """
    退出团队资源账号

    语法
        >>> LogoutTeam()
    说明
        LogoutTeam() 退出当前团队资源登录会话，不退出 Sysbuilder 程序，也不删除本地仓库。
    示例
        示例1：退出团队资源账号
        >>> print(LogoutTeam())
        > True
    输入参数
        无
    返回值
        `bool` : 退出成功返回 True，退出失败返回 False
    另请参阅
        LoginTeam
        GetTeamSessionInfo
    """
    return _run_func(LogoutTeam, locals())


@mw_connect_decorator(_MwConnect._process_path)
def GetTeamSessionInfo() -> dict:
    """
    获取团队资源会话信息

    语法
        >>> GetTeamSessionInfo()
    说明
        GetTeamSessionInfo() 获取当前团队资源登录状态以及本地团队仓库根目录。
        返回字典字段：
        loggedIn - 是否已通过 LoginTeam 登录，数据类型为 bool
        userName - 当前或最近一次登录的用户名，数据类型为 str
        serverAddress - 当前或最近一次连接的服务器地址，数据类型为 str
        localRepositoryRoot - 团队仓库在本机的存放根目录，数据类型为 str
    示例
        示例1：查询当前会话
        >>> info = GetTeamSessionInfo()
        >>> print(info["loggedIn"], info["serverAddress"])
        > True 172.16.1.35:9999
    输入参数
        无
    返回值
        `dict` : 会话信息字典；读取失败时返回空字典
    另请参阅
        LoginTeam
        LogoutTeam
    """
    result = _run_func(GetTeamSessionInfo, locals())
    return json.loads(result or "{}")


@mw_connect_decorator(_MwConnect._process_path)
def ListTeamResources() -> list:
    """
    获取远程团队资源树

    语法
        >>> ListTeamResources()
    说明
        ListTeamResources() 获取团队资源管理器“我的仓库”下的分类和仓库树。
        顶层返回列表，分类通过 children 递归包含下级分类或仓库，因此支持多级分类。
        每个资源字典字段：
        name - 界面显示名称，不包含“（协同）”后缀，数据类型为 str
        resourcePath - 云端可见完整路径，不含虚拟根“我的仓库”，数据类型为 str
        description - 分类或仓库描述，未设置时为空字符串，数据类型为 str
        type - 资源类型；group 表示分类，repository 表示仓库，数据类型为 str
        isCollaborative - 是否显示为协同资源，数据类型为 bool；不表示公开/私有或是否正在同时编辑
        children - 下级资源列表，仅分类包含，数据类型为 list
    示例
        示例1：列出远程团队资源
        >>> resources = ListTeamResources()
        >>> print(resources[0]["name"], resources[0]["resourcePath"])
        > 总体工程 总体工程
    输入参数
        无
    返回值
        `list` : 远程团队资源字典列表；未登录、没有资源或读取失败时返回空列表
    另请参阅
        SearchPublicTeamRepositories
        ListLocalTeamRepositories
        CloneTeamRepository
    """
    result = _run_func(ListTeamResources, locals())
    return json.loads(result or "[]")


@mw_connect_decorator(_MwConnect._process_path)
def SearchPublicTeamRepositories(keyword: str = "") -> list:
    """
    搜索公共团队仓库

    语法
        >>> SearchPublicTeamRepositories(keyword:str = "")
    说明
        SearchPublicTeamRepositories(keyword) 按仓库名称关键字搜索当前账号可见的公共团队仓库。
        keyword 为空字符串时查询全部可见公共仓库。
        每个返回字典包含 name、resourcePath、description、type 和 isCollaborative 字段；
        type 固定为 repository，公共仓库的 isCollaborative 固定为 False，不用于判断所有权或公开范围。
    示例
        示例1：搜索名称包含“模型”的公共仓库
        >>> repositories = SearchPublicTeamRepositories("模型")
        >>> print(repositories)
    输入参数
        keyword - 仓库名称关键字，可以为空
        数据类型：str
    返回值
        `list` : 公共仓库字典列表；没有匹配项、未登录或查询失败时返回空列表
    另请参阅
        ListTeamResources
        CloneTeamRepository
    """
    result = _run_func(SearchPublicTeamRepositories, locals())
    return json.loads(result or "[]")


@mw_connect_decorator(_MwConnect._process_path)
def ListLocalTeamRepositories() -> list:
    """
    获取本地团队仓库列表

    语法
        >>> ListLocalTeamRepositories()
    说明
        ListLocalTeamRepositories() 获取团队资源管理器“本地仓库”区域中的有效 Git 仓库。
        每个返回字典字段：
        name - 本地仓库目录名称，与界面“仓库名”一致，数据类型为 str
        resourcePath - 本地元数据记录的云端完整路径，元数据缺失时为空，数据类型为 str
        localPath - 界面显示的本地仓库绝对路径，使用“/”分隔，数据类型为 str
        projectFile - 仓库内可打开工程文件的绝对路径，没有时为空，数据类型为 str
        isEmpty - 仓库内没有可打开工程文件时为 True，数据类型为 bool
        description - 本地元数据记录的描述，数据类型为 str
        name 是本地目录名，projectFile 是目录内工程文件，两者名称允许不同。
    示例
        示例1：列出本地团队仓库
        >>> repositories = ListLocalTeamRepositories()
        >>> print(repositories[0]["name"], repositories[0]["localPath"])
    输入参数
        无
    返回值
        `list` : 本地团队仓库字典列表；没有有效仓库时返回空列表
    另请参阅
        ListTeamResources
        CloneTeamRepository
    """
    result = _run_func(ListLocalTeamRepositories, locals())
    return json.loads(result or "[]")


@mw_connect_decorator(_MwConnect._process_path)
def CreateTeamGroup(parentGroupPath: str, name: str, description: str) -> bool:
    """
    创建团队分类

    语法
        >>> CreateTeamGroup(parentGroupPath:str, name:str, description:str)
    说明
        CreateTeamGroup(parentGroupPath, name, description) 在指定云端父分类下创建子分类。
        parentGroupPath 使用 ListTeamResources() 返回的 resourcePath；传空字符串表示在“我的仓库”下创建顶层分类。
        支持多级分类，例如父路径“总体工程/子分类”表示在二级分类下继续创建。
    示例
        示例1：创建顶层分类
        >>> print(CreateTeamGroup("", "临时分类", "API创建的分类"))
        > True
        示例2：创建非顶层分类
        >>> print(CreateTeamGroup("临时分类", "子分类", "二级分类"))
        > True
    输入参数
        parentGroupPath - 云端父分类完整路径；创建顶层分类时传空字符串
        数据类型：str
        name - 新分类名称
        数据类型：str
        description - 新分类描述；界面资源树默认不直接显示描述
        数据类型：str
    返回值
        `bool` : 创建成功返回 True，创建失败返回 False
    另请参阅
        ListTeamResources
        UpdateTeamGroup
        DeleteTeamGroup
    """
    return _run_func(CreateTeamGroup, locals())


@mw_connect_decorator(_MwConnect._process_path)
def CloneTeamRepository(resourcePath: str) -> bool:
    """
    克隆团队仓库

    语法
        >>> CloneTeamRepository(resourcePath:str)
    说明
        CloneTeamRepository(resourcePath) 将指定云端团队仓库克隆到当前账号的本地团队仓库根目录。
        resourcePath 是界面可见的云端完整路径，不需要仓库ID；克隆后可通过 ListLocalTeamRepositories() 查看本地路径。
    示例
        示例1：克隆指定仓库
        >>> print(CloneTeamRepository("总体工程/test2"))
        > True
    输入参数
        resourcePath - 云端仓库完整路径，可使用 ListTeamResources() 返回的 resourcePath
        数据类型：str
    返回值
        `bool` : 克隆成功返回 True，克隆失败返回 False
    另请参阅
        ListTeamResources
        ListLocalTeamRepositories
        CloneTeamGroup
    """
    return _run_func(CloneTeamRepository, locals())


@mw_connect_decorator(_MwConnect._process_path)
def GetTeamRepositoryStatus() -> dict:
    """
    获取当前团队工程状态

    语法
        >>> GetTeamRepositoryStatus()
    说明
        GetTeamRepositoryStatus() 获取当前打开团队工程的 Git 分支和文件变更状态。
        所有文件路径均相对于仓库根目录。返回字典字段：
        branch - 当前分支名；无法读取时为空，分离头状态可能为 HEAD，数据类型为 str
        isDirty - 工作区或暂存区是否存在变更，数据类型为 bool
        modifiedFiles - 已修改文件路径列表，数据类型为 list
        addedFiles - 已加入版本控制或已暂存新增的文件路径列表，数据类型为 list
        deletedFiles - 已删除文件路径列表，数据类型为 list
        untrackedFiles - 尚未加入版本控制的文件路径列表，数据类型为 list
        conflictedFiles - 存在合并冲突的文件路径列表，数据类型为 list
        renamedFiles - 重命名或复制记录列表，每项包含 from 和 to，数据类型为 list
    示例
        示例1：查看当前团队工程变更
        >>> status = GetTeamRepositoryStatus()
        >>> print(status["branch"], status["modifiedFiles"])
    输入参数
        无；接口自动使用当前打开的团队工程
    返回值
        `dict` : 当前团队工程状态字典；当前工程不是团队仓库或读取失败时返回空字典
    另请参阅
        CommitTeamRepository
        PullTeamRepository
        PushTeamRepository
    """
    result = _run_func(GetTeamRepositoryStatus, locals())
    return json.loads(result or "{}")


def _CommitTeamRepository(message: str, files: str) -> bool:
    """向 RPC 层发送已经序列化的提交文件列表。"""
    return _run_func(_CommitTeamRepository, locals())


@mw_connect_decorator(_MwConnect._process_path)
def CommitTeamRepository(message: str, files: list = None) -> bool:
    """
    提交当前团队工程

    语法
        >>> CommitTeamRepository(message:str, files:list = None)
    说明
        CommitTeamRepository(message, files) 提交当前打开团队工程中的本地变更。
        files 为可选的仓库相对路径列表，可直接使用 GetTeamRepositoryStatus() 返回的
        modifiedFiles、addedFiles、deletedFiles 或 untrackedFiles 中的路径字符串。
        files 缺省、传入 None 或空列表时提交全部变更；传非空列表时仅提交指定文件。
    示例
        示例1：提交全部变更
        >>> print(CommitTeamRepository("更新需求模型"))
        > True
        示例2：只提交指定文件
        >>> print(CommitTeamRepository("更新工程文件", ["Project1.sybproj"]))
        > True
    输入参数
        message - Git 提交说明，不能为空
        数据类型：str
        files - 要提交的仓库相对路径列表，可以缺省
        数据类型：list
    返回值
        `bool` : 提交成功返回 True，提交失败返回 False
    另请参阅
        GetTeamRepositoryStatus
        PushTeamRepository
        GetTeamRepositoryHistory
    """
    files_json = json.dumps(files or [], ensure_ascii=False)
    return _CommitTeamRepository(message, files_json)


@mw_connect_decorator(_MwConnect._process_path)
def PullTeamRepository() -> bool:
    """
    拉取当前团队工程

    语法
        >>> PullTeamRepository()
    说明
        PullTeamRepository() 从远程仓库拉取更新并合并到当前打开的团队工程。
        接口自动确定当前工程所属仓库，不需要传仓库路径或仓库ID。
    示例
        示例1：拉取远程更新
        >>> print(PullTeamRepository())
        > True
    输入参数
        无；接口自动使用当前打开的团队工程
    返回值
        `bool` : 拉取成功返回 True，拉取失败或发生冲突返回 False
    另请参阅
        PushTeamRepository
        GetTeamRepositoryStatus
    """
    return _run_func(PullTeamRepository, locals())


@mw_connect_decorator(_MwConnect._process_path)
def PushTeamRepository() -> bool:
    """
    推送当前团队工程

    语法
        >>> PushTeamRepository()
    说明
        PushTeamRepository() 将当前打开团队工程中已经提交的本地提交推送到远程仓库。
        未提交的工作区变更不会被推送；接口不需要传仓库路径或仓库ID。
    示例
        示例1：推送当前工程的本地提交
        >>> print(PushTeamRepository())
        > True
    输入参数
        无；接口自动使用当前打开的团队工程
    返回值
        `bool` : 推送成功返回 True，推送失败返回 False
    另请参阅
        CommitTeamRepository
        PullTeamRepository
    """
    return _run_func(PushTeamRepository, locals())


@mw_connect_decorator(_MwConnect._process_path)
def PublishProjectToTeam(targetGroupPath: str, repositoryName: str, description: str = "") -> bool:
    """
    发布当前工程到团队仓库

    语法
        >>> PublishProjectToTeam(targetGroupPath:str, repositoryName:str, description:str = "")
    说明
        PublishProjectToTeam(targetGroupPath, repositoryName, description) 将当前打开的本地工程发布到指定云端分类，
        并创建对应的团队仓库。该接口用于发布已有工程，不用于创建空远程仓库。
    示例
        示例1：将当前工程发布到临时团队分类
        >>> print(PublishProjectToTeam("临时团队分类", "需求模型", "需求模型工程"))
        > True
    输入参数
        targetGroupPath - 目标云端分类完整路径，可使用 ListTeamResources() 返回的 resourcePath
        数据类型：str
        repositoryName - 发布后显示的远程仓库名称
        数据类型：str
        description - 远程仓库描述，可以缺省
        数据类型：str
    返回值
        `bool` : 发布成功返回 True，发布失败返回 False
    另请参阅
        CreateTeamRepository
        ListTeamResources
        PushTeamRepository
    """
    return _run_func(PublishProjectToTeam, locals())


@mw_connect_decorator(_MwConnect._process_path)
def UpdateTeamGroup(targetGroupPath: str, newName: str, newDescription: str) -> bool:
    """
    编辑团队分类

    语法
        >>> UpdateTeamGroup(targetGroupPath:str, newName:str, newDescription:str)
    说明
        UpdateTeamGroup(targetGroupPath, newName, newDescription) 修改指定云端分类的名称和描述。
        targetGroupPath 是修改前的完整路径，用它确定编辑哪个分类；不需要分类ID。
    示例
        示例1：编辑顶层分类
        >>> print(UpdateTeamGroup("临时分类", "正式分类", "已调整分类名称"))
        > True
        示例2：编辑非顶层分类
        >>> print(UpdateTeamGroup("正式分类/子分类", "新子分类", "二级分类描述"))
        > True
    输入参数
        targetGroupPath - 修改前的云端分类完整路径
        数据类型：str
        newName - 修改后的分类名称
        数据类型：str
        newDescription - 修改后的分类描述；需要清空描述时传空字符串
        数据类型：str
    返回值
        `bool` : 编辑成功返回 True，编辑失败返回 False
    另请参阅
        CreateTeamGroup
        ListTeamResources
        DeleteTeamGroup
    """
    return _run_func(UpdateTeamGroup, locals())


@mw_connect_decorator(_MwConnect._process_path)
def DeleteTeamGroup(groupPath: str) -> bool:
    """
    删除团队分类

    语法
        >>> DeleteTeamGroup(groupPath:str)
    说明
        DeleteTeamGroup(groupPath) 删除指定云端分类。groupPath 使用界面可见完整路径，不需要分类ID。
        该操作影响远程团队资源；分类非空、没有权限或登录失效时删除失败。
    示例
        示例1：删除非顶层分类
        >>> print(DeleteTeamGroup("临时分类/子分类"))
        > True
    输入参数
        groupPath - 要删除的云端分类完整路径
        数据类型：str
    返回值
        `bool` : 删除成功返回 True，删除失败返回 False
    另请参阅
        CreateTeamGroup
        UpdateTeamGroup
        ListTeamResources
    """
    return _run_func(DeleteTeamGroup, locals())


@mw_connect_decorator(_MwConnect._process_path)
def CreateTeamRepository(groupPath: str, name: str, description: str = "") -> bool:
    """
    创建空的远程团队仓库

    语法
        >>> CreateTeamRepository(groupPath:str, name:str, description:str = "")
    说明
        CreateTeamRepository(groupPath, name, description) 在指定云端分类下创建一个不包含 Sysbuilder 工程的空远程仓库。
        这是 Python API 的补充能力，当前软件界面没有独立的“新建空仓库”入口。
        若要把当前工程上传为团队仓库，应使用 PublishProjectToTeam()。
    示例
        示例1：创建空远程仓库
        >>> print(CreateTeamRepository("临时分类", "空仓库", "用于后续导入"))
        > True
    输入参数
        groupPath - 目标云端分类完整路径
        数据类型：str
        name - 新远程仓库名称
        数据类型：str
        description - 新远程仓库描述，可以缺省
        数据类型：str
    返回值
        `bool` : 创建成功返回 True，创建失败返回 False
    另请参阅
        PublishProjectToTeam
        CloneTeamRepository
        ListTeamResources
    """
    return _run_func(CreateTeamRepository, locals())


@mw_connect_decorator(_MwConnect._process_path)
def CloneTeamGroup(groupPath: str) -> bool:
    """
    批量克隆团队分类

    语法
        >>> CloneTeamGroup(groupPath:str)
    说明
        CloneTeamGroup(groupPath) 递归查找指定云端分类下的仓库，并依次克隆到本地团队仓库根目录。
        该接口是对多次 CloneTeamRepository() 的批量封装；不需要分类ID或仓库ID。
    示例
        示例1：克隆分类下的全部仓库
        >>> print(CloneTeamGroup("总体工程"))
        > True
    输入参数
        groupPath - 要批量克隆的云端分类完整路径
        数据类型：str
    返回值
        `bool` : 分类下所有仓库均克隆成功返回 True；任一仓库失败返回 False
    另请参阅
        CloneTeamRepository
        ListTeamResources
        ListLocalTeamRepositories
    """
    return _run_func(CloneTeamGroup, locals())


@mw_connect_decorator(_MwConnect._process_path)
def GetTeamRepositoryHistory() -> list:
    """
    获取当前团队工程提交历史

    语法
        >>> GetTeamRepositoryHistory()
    说明
        GetTeamRepositoryHistory() 获取当前打开团队工程最近的非合并 Git 提交，最多返回 200 条，按新到旧排列。
        每个提交字典字段：
        commitId - 完整 Git 提交哈希，数据类型为 str
        author - 提交作者名称，数据类型为 str
        time - ISO 8601 格式的作者时间，数据类型为 str
        message - 提交说明首行，数据类型为 str
    示例
        示例1：获取最近一次提交
        >>> history = GetTeamRepositoryHistory()
        >>> print(history[0]["commitId"], history[0]["message"])
    输入参数
        无；接口自动使用当前打开的团队工程
    返回值
        `list` : 提交历史字典列表；当前工程不是团队仓库或读取失败时返回空列表
    另请参阅
        GetTeamCommitDetails
        ResetTeamRepositoryVersion
        CommitTeamRepository
    """
    result = _run_func(GetTeamRepositoryHistory, locals())
    return json.loads(result or "[]")


@mw_connect_decorator(_MwConnect._process_path)
def GetTeamCommitDetails(commitId: str) -> dict:
    """
    获取团队工程提交详情

    语法
        >>> GetTeamCommitDetails(commitId:str)
    说明
        GetTeamCommitDetails(commitId) 获取当前打开团队工程中指定 Git 提交的基本信息和文件变更。
        返回字典字段：
        commitId - 解析后的完整 Git 提交哈希，数据类型为 str
        author - 提交作者名称，数据类型为 str
        time - ISO 8601 格式的作者时间，数据类型为 str
        message - 提交说明首行，数据类型为 str
        files - 文件变更字典列表，数据类型为 list；每项包含 status 和 path
        status 为 A 表示该提交新增文件，M 表示该提交修改文件，D 表示该提交删除文件；
        path 为相对仓库根目录的路径。接口禁用重命名检测，因此重命名通常显示为一条 D 和一条 A。
    示例
        示例1：查看最近一次提交详情
        >>> history = GetTeamRepositoryHistory()
        >>> details = GetTeamCommitDetails(history[0]["commitId"])
        >>> print(details["files"])
    输入参数
        commitId - 完整或可唯一识别的十六进制 Git 提交哈希
        数据类型：str
    返回值
        `dict` : 提交详情字典；工程、提交编号无效或读取失败时返回空字典
    另请参阅
        GetTeamRepositoryHistory
        RestoreTeamRepositoryFiles
        ResetTeamRepositoryVersion
    """
    result = _run_func(GetTeamCommitDetails, locals())
    return json.loads(result or "{}")


def _RestoreTeamRepositoryFiles(files: str) -> bool:
    """向 RPC 层发送已经序列化的还原文件列表。"""
    return _run_func(_RestoreTeamRepositoryFiles, locals())


@mw_connect_decorator(_MwConnect._process_path)
def RestoreTeamRepositoryFiles(files: list = None) -> bool:
    """
    还原当前团队工程文件

    语法
        >>> RestoreTeamRepositoryFiles(files:list = None)
    说明
        RestoreTeamRepositoryFiles(files) 丢弃当前打开团队工程中指定文件的未提交本地变更。
        files 为仓库相对路径列表，可直接使用 GetTeamRepositoryStatus() 返回的各文件列表。
        files 缺省、传入 None 或空列表时还原全部未提交变更。
        该操作不能通过本接口撤销，请在调用前确认不再需要这些本地变更。
    示例
        示例1：还原指定文件
        >>> print(RestoreTeamRepositoryFiles(["Project1.sybproj"]))
        > True
        示例2：还原全部未提交变更
        >>> print(RestoreTeamRepositoryFiles())
        > True
    输入参数
        files - 要还原的仓库相对路径列表，可以缺省
        数据类型：list
    返回值
        `bool` : 还原成功返回 True，还原失败返回 False
    另请参阅
        GetTeamRepositoryStatus
        ResetTeamRepositoryVersion
    """
    files_json = json.dumps(files or [], ensure_ascii=False)
    return _RestoreTeamRepositoryFiles(files_json)


@mw_connect_decorator(_MwConnect._process_path)
def ResetTeamRepositoryVersion(commitId: str) -> bool:
    """
    重置当前团队工程版本

    语法
        >>> ResetTeamRepositoryVersion(commitId:str)
    说明
        ResetTeamRepositoryVersion(commitId) 将当前打开团队工程的本地仓库重置到指定 Git 提交。
        commitId 可从 GetTeamRepositoryHistory() 的 commitId 字段取得。
        该操作会改变当前工程版本并可能丢弃目标提交之后的本地状态，请谨慎调用。
    示例
        示例1：重置到指定历史版本
        >>> history = GetTeamRepositoryHistory()
        >>> print(ResetTeamRepositoryVersion(history[1]["commitId"]))
        > True
    输入参数
        commitId - 目标提交的完整或可唯一识别的十六进制 Git 提交哈希
        数据类型：str
    返回值
        `bool` : 重置成功返回 True，重置失败返回 False
    另请参阅
        GetTeamRepositoryHistory
        GetTeamCommitDetails
        RestoreTeamRepositoryFiles
    """
    return _run_func(ResetTeamRepositoryVersion, locals())

