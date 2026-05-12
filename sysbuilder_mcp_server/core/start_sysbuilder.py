from .sysbuilder_connect import MwConnect
import sys

def StartSysbuilder(processPath: str = None, ip: str = None, args: list = None, port = None) -> bool:
    """
    启动Sysbuilder，并连接

    Returns:
        bool: 连接成功返回 True，连接失败返回 False
    """
    return MwConnect().__StartSysbuilder__(ip = ip, port = port, processPath = processPath, argsParam = args)
    
def FindSysbuilder() -> list:
    """
    查找可以连接的Sysbuilder，并返回端口号
    """
    processName = "Sysbuilder"
    port_list = MwConnect().__FindSysbuilder__(processName)
    if len(port_list) != 0:
        print(f"可用端口列表为{port_list.ports}")
    return port_list
    
def ConnectSysbuilder(ip: str = None, port: int = None) -> bool:
    """
    连接到已打开的Sysbuilder

    Returns:
        bool: 连接成功返回 True，连接失败返回 False
    """
    try:
        if not port:
            process_ports = FindSysbuilder()
            if process_ports == [] or (port == 0 and sys.platform == "win32"):
                print("将启动一个新的Sysbuilder")
                return StartSysbuilder()
            else:
                port = process_ports[0]
        print(f"Connected: {ip}:{port}")
        return MwConnect().__ConnectorSysbuilder__(ip, port)
    except KeyboardInterrupt:
        return False
