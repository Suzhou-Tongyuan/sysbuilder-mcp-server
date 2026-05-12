import sys

if sys.platform == "win32":
    import winreg

def get_os_name():
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform == "linux":
        return "linux"
    else:
        raise ValueError(f"暂不支持该操作系统!: {sys}")

if sys.platform == "win32":
    def get_registry_value(key, subkey, value_name):
        try:
            with winreg.OpenKey(key, subkey) as registry_key:
                value, value_type = winreg.QueryValueEx(registry_key, value_name)
                return value
        except Exception as e:
            return str(e)