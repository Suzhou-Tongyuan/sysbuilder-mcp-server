import json
import inspect
import websocket
import socket
from jsonrpcclient import request_json
from colorama import Fore
import subprocess
import threading
import time
import os
import sys
import logging
import psutil
import struct
from .os_utils import get_os_name
if sys.platform == "win32":
    from .os_utils import get_registry_value
    import winreg
import ast

try:
    # Python 3.8+内置importlib.metadata
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python 3.7需要从外部包importlib_metadata引入
    from importlib_metadata import version, PackageNotFoundError
from packaging.version import Version

def find_available_port(ip:str, start_port:int, end_port:int) -> int:
    for port in range (start_port, end_port + 1):
        with socket.socket (socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((ip, port))
                return port
            except socket.error:
                continue
# 单例装饰器
def singleton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper
    
def parsing_data_type(SysOptions, key, value):
    if SysOptions[key] == 'int':
        real_val = int(value)
    elif SysOptions[key] == 'bool':
        if value == 'True':
            real_val = True
        else:
            real_val = False
    elif SysOptions[key] == 'list' and value != '':
        cur_val = value.replace("\\", "/")
        real_val = eval (cur_val)
    else:
        real_val = value
    return real_val
    
def get_package_version():
    """
    自动获取mworks包版本号
    """
    try:
        return version("mworks-sysbuilder")
    except PackageNotFoundError:
        return "unknown"
    
class MwPortInfo:
    def __init__(self, ports, pids):
        self._pids = pids
        self._ports = ports
    def __iter__(self):
        """支持直接迭代,保持向后兼容"""
        return iter (self._ports)
    def __getitem__(self, index):
        """支持索引访问,保持向后兼容"""
        return self._ports[index]
    def __len__(self):
        return len(self._ports)
    @property
    def ports(self):
        return self._ports
    @property
    def pids(self):
        return self._pids
    def get_port_pid_pairs(self):
        """返回(port,pid)对的列表"""
        return list(zip(self._ports, self._pids))
        
@singleton
class MwConnect:
    def __init__(self) -> None:
        self.echoOn = False
        self.autoNavigateOn = True
        self.lastSysbuilderPort = None
        self._reset_connection()
        self.lastMessageType = 0
        self.sendHeartThread = None
        self.sendHeartThreadEvent = threading.Event()
        
    def _reset_connection(self) -> None:
        self.connected = False
        self.toReceive = True
        self.builtinFuncs = self._get_builtin_funcs()
    
    def _get_builtin_funcs(self):
        try:
            # PyInstall creates a temp folder and stores path in MEIPASS
            base_path = sys.MEIPASS  
            api_path = os.path.join (base_path, 'sysbuilder_api.py')
        except AttributeError:
            cur_file_path = os.path.abspath(__file__)
            api_path = os.path.dirname (cur_file_path) + '/../sysbuilder_api.py'
        if not os.path.exists (api_path):
            return ()
        with open (api_path, "r", encoding="utf-8") as source_file:
            source_code = source_file.read()
        parsed_code = ast.parse (source_code)
        functions = []
        for node in ast.walk(parsed_code):
            if isinstance(node, ast.FunctionDef):
                # 函数名
                func_name = node.name
                if func_name.startswith('_'):
                    functions.append(func_name.lstrip('_'))
        return functions
    def get_is_connected(self)-> bool:
        return self.connected
    def get_to_receive(self)-> bool:
        return self.toReceive
    def get_echo_on(self)-> bool:
        return self.echoOn
    def set_echo_on(self, flag:bool)-> None:
        self.echoOn = flag

    def get_auto_navigate_on(self)-> bool:
        return self.autoNavigateOn
    def set_auto_navigate_on(self, flag:bool)-> None:
        self.autoNavigateOn = flag
            
    def build_init(self, ip:str = None, port = None, processPath:str = None):
        self.connect_mode = "Default"
        if sys.platform == "win32":
            if processPath:
                self.processPath = os.path.abspath(processPath)
            else:
                regHKey = winreg.HKEY_LOCAL_MACHINE
                regSubKey = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\MWORKS.Sysbuilder.exe'
                regName = ""
                _process_path = get_registry_value(regHKey, regSubKey, regName)
                #对路径进行简单补全
                if not _process_path.replace ("\\","/").lower().endswith ("bin/sysbuilder.exe"):
                    self.processPath = os.path.join(_process_path, r"Bin/Sysbuilder.exe")
                else:
                    self.processPath = _process_path
        else:
            self.processPath = os.path.abspath(processPath) if processPath else processPath
        self.className = "SysbuilderScript"
        self.messageHead = "Content-Length:"
        self.messageText = ""
        self.sysbuilderProcess = None
        self.sysbuilderIP = ip if ip else "127.0.0.1"
        self.sysbuilderPort = port if port else find_available_port(self.sysbuilderIP, 49152, 65535)
        self.response = []
        self.eventKeyboardInterrupt = False
    
    def __StartSysbuilder__(self, ip = None, port = None, processPath = None, start_mode: str = "-gui", argsParam: list = None) -> bool:
        self.build_init(ip = ip, port = port, processPath = processPath)
        if not self.processPath:
            print("processPath Error!")
            return False
        if not os.path.exists(self.processPath):
            print("未找到软件路径:", self.processPath)
            return False
        if not os.path.isfile(self.processPath):
            print("软件路径校验失败:", self.processPath)
            return False
        self.processPath = os.path.abspath(self.processPath).replace ("\\","/")
        directory, _ = os.path.split(self.processPath)
        if start_mode == '-q':#无界面模式
            print("暂未支持无界面")
            return False
            file_name = "mols.exe" if get_os_name()=="windows" else "mols.sh"
        else:#有界面和其他
            file_name = "Sysbuilder.exe" if get_os_name() == "windows" else "Sysbuilder.sh"
        self.processPath = os.path.join(directory, file_name)

        args = [self.processPath, '--script_addr', self.sysbuilderIP + ':' + str(self.sysbuilderPort)]
        if argsParam != None:
            if len (argsParam) != 0:
                for i in argsParam:
                    args.append(i)
        print(f"DEBUG: 尝试启动的路径是 -> {self.processPath}")
        try:
            if sys.platform == "win32":
                self.sysbuilderProcess = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                self.sysbuilderProcess = subprocess.Popen(args, start_new_session=True)
            # 如果已建立连接则保持当前连接,并且当前端口和上一个端口不是同一个
            if self.get_is_connected() and self.lastSysbuilderPort != self.sysbuilderPort:
                return True
            # 启动成功将端口存储起来
            self.lastSysbuilderPort = self.sysbuilderPort
            if not self.__BuildConnect__():
                print("连接超时!")
                # 连接失败时重置状态
                self._reset_connection()
                return False
            return True
        except KeyboardInterrupt:
            print("\n启动被用户中断!")
            # 被打断时重置连接状态
            self._reset_connection()
            return False
        except Exception as e:
            print(f"启动异常: {e}")
            # 异常时重置连接状态
            self._reset_connection()
            return False
            
    #获取名为process_name 的后台进程号
    def __GetProcessPorts__(self, process_name:str) -> list:
        if sys.platform == "win32":
            process_name = process_name + '.exe'
        return [pid for pid in psutil.process_iter() if pid.name() == process_name]      

    #指定ip port 尝试成功
    def __EstablishConnection__(self, pid, ip, port) -> bool:
        if ip == '0.0.0.0':
            ip = '127.0.0.1'
        web_url = f"ws://{ip}:{port}"
        send_confirm_json = request_json(method = "WaitSysbuilderLoad", params = {"isTryConnect":True})
        send_confirm_message = "Content-Length:" + str(len(send_confirm_json)) + "\r\n\r\n" + send_confirm_json
        for _ in range(60):
            try:
                # 判断pid是否存在减少后续遍历
                if not self.__IsLive__(pid):
                    break
                ws = websocket.create_connection(web_url, skip_utf8_validation=True)
                res = ws.send(send_confirm_message)
                if res == 0:
                    break
                response = ws.recv()
                if not response.startswith ("Content-Length:"):
                    break
                recv_data_list = response.split("\r\n\r\n")
                if len(recv_data_list) != 2:
                    break
                recv_json_data = json.loads (recv_data_list[1])
                result_keys = recv_json_data["result"]["keys"]
                if len (result_keys) > 1:
                    result = {}
                    for k in result_keys:
                        result[k] = recv_json_data["result"][k]
                elif len(result_keys) == 1:
                    result = recv_json_data["result"][result_keys[0]]
                if result != True:
                    break
                ws.close()
                return True
            except Exception as e:
                time.sleep (0.01)
        return False        
  
    def __IsLive__(self, pid:int) -> bool:
        try:
            proc = psutil.Process (pid)
            return proc.is_running()
        except psutil.NoSuchProcess:
            return False
        
    # 查找可用的sysbuilder端口
    def __FindSysbuilder__(self, process_name: str) -> MwPortInfo:
        process_ports = []
        res_process_pids = []
        process_pids = self.__GetProcessPorts__(process_name = process_name)
        process_alive = False
        for pid in process_pids:
            process_alive = True
            net_con = psutil.net_connections()
            for con_info in net_con:
                if not self.__IsLive__(pid.pid):
                    process_alive = False
                    break
                if con_info.pid != pid.pid:
                    continue
                # 判断pid是否存在减少后续遍历
                if not self.__IsLive__(pid.pid):
                    process_alive = False
                    break
                pro_ip = con_info.laddr.ip
                if pro_ip == '0.0.0.0' or pro_ip == '::':
                    pro_ip = '127.0.0.1'
                if(self.__EstablishConnection__(pid = pid.pid, ip = pro_ip, port = con_info.laddr.port)):
                    process_ports.append(con_info.laddr.port)
                    res_process_pids.append (pid.pid)
                    break
                    
        if not process_alive:
            print("未找到端口,本地Sysbuilder未打开或已关闭")
        elif process_ports == []:
            print("未找到端口,本地Sysbuilder已打开无可连端口")
        return MwPortInfo(process_ports, res_process_pids)
        
    def __ConnectorSysbuilder__(self, ip: str, port: int) -> bool:
        # 先保存目标端口，但不设置到 self.sysbuilderPort
        target_port = port
        self.build_init(ip = ip, port = None)
        # 临时设置端口用于连接
        self.sysbuilderPort = target_port
        try:
            if not self.__BuildConnect__():
                print("连接超时!")
                # 连接失败，清除端口并重置连接状态
                self.sysbuilderPort = None
                self._reset_connection()
                return False
            # 连接成功
            return True
        except KeyboardInterrupt:
            print("\n连接被用户中断!")
            # 被打断时重置连接状态
            self.sysbuilderPort = None
            self._reset_connection()
            raise  # 重新抛出异常，让上层调用者知道被中断
        except Exception as e:
            print(f"连接异常: {e}")
            # 异常时重置连接状态
            self.sysbuilderPort = None
            self._reset_connection()
            return False
        
    def __BuildConnect__(self):
        web_url = f"ws://{'127.0.0.1'}:{self.sysbuilderPort}"#先处理本地
        send_confirm_json = request_json(method = "WaitSysbuilderLoad", params = {"isTryConnect":False})
        first_build_connect = True
        send_confirm_message = self.messageHead + str(len(send_confirm_json)) + "\r\n\r\n" + send_confirm_json
        self.toReceive = True
        try:
            for i in range(60):
                try:
                    if first_build_connect:
                        print("正在连接...")
                        first_build_connect = False
                    self.ws = websocket.create_connection(web_url, skip_utf8_validation=True)
                    self.ws.send(send_confirm_message)
                    response = self.ws.recv()
                    if not response.startswith("Content-Length:"):
                        break
                    recv_data_list = response.split("\r\n\r\n")
                    if len(recv_data_list) != 2:
                        break
                    recv_json_data = json.loads(recv_data_list[1])
                    result_keys = recv_json_data["result"]["keys"]
                    if len(result_keys) > 1:
                        result = {}
                        for k in result_keys:
                            result[k] = recv_json_data["result"][k]
                    elif len(result_keys) == 1:
                        result = recv_json_data["result"][result_keys[0]]
                    if result != True:
                        break
                    print("连接成功!")
                    self.toReceive = False
                    self.connected = True
                    self.sendHeartThreadEvent.clear()
                    self.sendHeartThread = threading.Thread(target=self.__send_heart_thread__, daemon=True)
                    self.sendHeartThread.start()
                    return True
                except KeyboardInterrupt:
                    # 直接抛出，不在这里处理
                    raise
                except Exception as e:
                    time.sleep(1)
        except KeyboardInterrupt:
            # 直接抛出，让上层处理
            self.connected = False
            self.toReceive = False
            raise
        self.connected = False
        return False
        
    def __send_heart_thread__(self):
        while not self.sendHeartThreadEvent.is_set():
            self.sendHeartThreadEvent.wait(60)
            if self.toReceive == True:
                continue
            self.toReceive = True
            if self.sendHeartThreadEvent.is_set():
                self.toReceive = False
                break
            send_json_data = request_json ("SendHeart", {})
            send_json_data = self.messageHead + str(len(send_json_data)) + "\r\n\r\n" + send_json_data
            send_json_data = send_json_data.encode ("utf-8")
            try:
                self.ws.send (send_json_data)
            except:
                print("发送心跳失败")
                self.toReceive = False
                break
            try:
                res = self.ws.recv()
                if not res.startswith("Content-Length:"):
                    print("接收心跳失败")
                    self.toReceive = False
                    break
                recv_data_list = res.split("\r\n\r\n")
                if len(recv_data_list) != 2:
                    print("接收心跳失败")
                    self.toReceive = False
                    break
                recv_json_data = json.loads (recv_data_list[1])
                result_keys = recv_json_data["result"]["keys"]
                if len(result_keys) > 1:
                    result = {}
                    for k in result_keys:
                        result[k] = recv_json_data["result"][k]
                elif len(result_keys) == 1:
                    result = recv_json_data["result"][result_keys[0]]
                if result != True:
                    print("接收心跳失败")
                    self.toReceive = False
                    break
            except:
                self.toReceive = False
                break
            self.toReceive = False      

    def __websocket_thread__(self):
        try:
            self.ws.send (self.sendJsonData)
        except:
            print("发送失败!")
            self.sendResult = False
        try:
            response = self.ws.recv()
            self.response.append (response)
            """
            if (self.eventKeyboardInterrupt):
                # 取消命令时,取消的应答先返回,被取消的命令后返回。判断先返回的取消命令是否成功
                cancel_success = '"success":true' in response
                if not cancel_success:
                    print("无法终止该命令")
                response = self.ws.recv()
                if cancel_success:
                    print("已终止")
                self.response.append (response)
            """
            self.sendResult = True
        except:
            print("接收失败！请检查服务是否已经停止")
            self.sendResult = False
            self.ws.close()
        return
        
    def __websocket_communication__(self):
        self.sendResult = False
        self.response.clear()
        self.eventKeyboardInterrupt = False

        ws_thread = threading.Thread(target=self.__websocket_thread__)
        ws_thread.start()

        # 使用带超时的 join 循环，以便能响应 KeyboardInterrupt
        try:
            while True:
                ws_thread.join(timeout=0.1)
                if not ws_thread.is_alive():
                    break
        except KeyboardInterrupt:
            # 被中断时，关闭 WebSocket 连接并重置状态
            print("[DEBUG] KeyboardInterrupt in __websocket_communication__")
            try:
                if hasattr(self, 'ws') and self.ws:
                    self.ws.close()
            except:
                pass
            ws_thread.join(timeout=0.5)
            self._reset_connection()
            self.sysbuilderPort = None
            print(f"[DEBUG] After reset: connected={self.connected}, port={self.sysbuilderPort}")
            raise

        return self.sendResult
        
    def __RunCurrentFunction__(self, func, args, kwargs, expected_types, get_response = True, plugin_mode = None):
        while True:
            if self.toReceive == True:
                time.sleep(1)
            else:
                break
        self.toReceive = True
        # 获取函数的参数名
        params = inspect.signature(func).parameters
        param_names = list(params.keys())
        func_name = func.__name__
        is_print_build_func = False
        if func_name == "GetVarTimes":#是否打印内置函数的结果
            is_print_build_func = True
        if func_name.startswith("_"):
            func_name = func_name[1:]
            
        #if func_name == "CreatePlot":  
        #    param_names[param_names.index('subPlot')] = "subPlotRow"
        #    param_names.append ("subPlotColumn")
        #     判断参数个数
        #total_args = len(args) + len(kwargs)
        # if total_args!=len(expected_types):
        #     print(f"{func_name}需要{len(expected_types)}个参数,而输入{total_args}个参数")
        #     self.toReceive=False
        #     return False
        param_dict = {}
        # 检查位置参数
        for i, (arg, expected_type) in enumerate(zip(args, expected_types)):
            if arg == None:
                continue
            if not isinstance(arg, expected_type) and arg != None:
                if func_name not in["Echo"]:
                    self.toReceive = False
                    raise TypeError("%s() argument '%s' must be %r, not %r" %
                        (func_name, param_names[i], expected_type.__name__, type(arg).__name__)) from None
            param_dict[param_names[i]] = arg
        ## 检查关键字参数
        #for key,value in kwargs.items():
        #    if key in param_names:
        #        expected_type = expected_types[param_names.index(key)]
        #        if not isinstance(value, expected_type):
        #            print(f"关键字参数'{key}'不一致,应该是{expected_type.__name__},而不是{type(value).__name__}")
        #            self.toReceive = False
        #            return
        #        else
         #       self.toReceive = False
         #       return
        #    else:
         #       print(f"未知的关键字参数:{key}")
         #       self.toReceive = False
         #       return
        # 构造json
        if plugin_mode:
            param_dict['moduleName'] = plugin_mode
            
        send_json_data = request_json(func_name, param_dict)
        self.sendJsonData = self.messageHead + str(len(send_json_data)) + "\r\n\r\n" + send_json_data
        self.sendJsonData = self.sendJsonData.encode("utf-8")
        # print(f"Send data: {send_json_data}")
        try:
            result = self.__websocket_communication__()
        finally:
            # 登录请求完成后立即移除连接对象中缓存的原始密码报文。
            if func_name == "LoginTeam":
                self.sendJsonData = b""
        # 连接失败
        if not get_response:
            self.toReceive = False
            return
        if not result:
            print("调用失败!")
            if(func_name == "SendHeart"):
                print(result)
                self.toReceive = False
                return False
            self.toReceive = False
            return False
        if len(self.response) == 0:
            print("接受数据错误!")
            self.toReceive = False
            return False
        """
        if func_name == "GetVarValues" or func_name == "GetVarsValues" or func_name == "GetWatchVarsValues" or func_name == "GetVarsValueAt":
            sub_byte = b'variable'
            index = self.response[-1].find(sub_byte)
            result_byte = self.response[-1][index:]
            var_result = vars_value_byte_to_double(result_byte, func_name == "GetVarValues" or func_name == "GetVarsValueAt")
            self.toReceive = False
            if self.echoOn:
                print(str(var_result))
            return var_result
            # 返回结果格式不对
        """
        
        if not self.response[-1].startswith(self.messageHead):
            # 取消一个命令时,取消的应答先返回,被取消的命令后返回。判断先返回的取消命令是否成功
            print("接受数据错误!")
            self.toReceive = False
            return False

        # response 包含 "Content-Length: \r\n\r\n{}"
        recv_data_list = self.response[-1].split("\r\n\r\n")

        if len(recv_data_list) != 2:
            print("接受数据错误!")
            self.toReceive = False
            return False
        try:
            recv_json_data = json.loads(recv_data_list[1])
            #print(f"Recv: {recv_json_data}")
            result_keys = recv_json_data["result"]["keys"]
        
            if len(result_keys) > 1:
                result = {}
                for k in result_keys:
                    result[k] = recv_json_data["result"][k]
            elif len(result_keys) == 1:
                result = recv_json_data["result"][result_keys[0]]
            if (func_name == 'GetCurrentSimTime' or func_name == 'GetLinearEstimateCurrentSimTime') and result >= 1.7976931348623157e+308:
                result = None
            if func_name not in self.builtinFuncs and func_name != 'GetModelCodeGenerationOptions':
                if self.echoOn:
                    print(result)
            else:
                if self.echoOn & is_print_build_func:
                    print(result)
            self.messageText = str(recv_json_data["result"]["message"])
            if recv_json_data["result"]["message"] != "" and recv_json_data["result"]["messageType"] != "":
                # print(recv_json_data["result"]["messageType"])
                self.lastMessageType = recv_json_data["result"]["messageType"]
                self.messageText = self.messageText.replace("Error", Fore.RED + "Error" + Fore.RESET)
                self.messageText = self.messageText.replace("错误", Fore.RED + "错误" + Fore.RESET)
                self.messageText = self.messageText.replace("Warning", Fore.YELLOW + "Warning" + Fore.RESET)
                self.messageText = self.messageText.replace("警告", Fore.YELLOW + "警告" + Fore.RESET)
                self.messageText = self.messageText.replace("Message", Fore.GREEN + "Message" + Fore.RESET)
                self.messageText = self.messageText.replace("信息", Fore.GREEN + "信息" + Fore.RESET)
                if recv_json_data["result"]["messageType"] == 1 or recv_json_data["result"]["messageType"] == 2:
                    print(self.messageText)
            self.toReceive = False
            if func_name == "Exit" and self.sysbuilderProcess != None:
                self._reset_connection()
                self.sendHeartThreadEvent.set()
                self.sysbuilderProcess.communicate(timeout=100)
                if self.sysbuilderProcess.returncode is None:
                    print('The process is running.')
                else:
                    print("The process has exited, and the return code is: ", self.sysbuilderProcess.returncode)
            return result
        except subprocess.TimeoutExpired:
            print("Python进程已退出，本地有尚未关闭的由Python API启动的Sysbuilder子进程，请及时清理！")
        except:
            print("抛出异常!")
            self.toReceive = False
            print(recv_data_list[1])
            return_type = inspect.signature(func)
            if return_type.return_annotation == bool:
                return False
            return None


    def _process_path(self):
        return self.processPath if self.processPath else None