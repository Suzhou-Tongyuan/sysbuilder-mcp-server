"""定义各种过滤器"""
from functools import wraps
from .sysbuilder_connect import MwConnect
import inspect
import copy
import os

def mw_connect_decorator(process_path):
    def decorator(func):
        def to_camel_case(snake_str):
            """将下划线命名格式转换为带大写字母的驼峰式格式"""
            components = snake_str.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])

        @wraps(func)  # 保留func的签名
        def wrapper(*args, **kwargs):
            if not MwConnect().get_is_connected():
                print("[ERROR]: 请先启动或连接SysBuilder")
                return
            new_args = tuple(copy.deepcopy(arg) for arg in args)
            new_kwargs = {}
            for key, val in kwargs.items():
                new_key = to_camel_case(key)
                new_kwargs[new_key] = val
            try:
                return func(*new_args, **new_kwargs)
            except TypeError as e:
                print("发生异常：", e)
                print(f"使用 help({func.__name__}) 命令查看 {func.__name__} 的使用说明")
                return_type = inspect.signature(func).return_annotation
                if return_type == bool:
                    return False
            return None
        return wrapper
    return decorator

def path_resolver(param_names, is_read, work_dir, echo, check_empty=False):
    """
    给部分需要解析相对路径的函数添加的装饰器

    参数列表:
        param_names：需要解析相对路径的参数列表
        is_read：是否是读函数，读函数先从当前路径下寻找这个文件是否存在，不存在则去工作目录下寻找；而写函数则仅判断脚本所在路径是否存在
        work_dir：工作目录的获取函数
        check_empty：是否检查空路径，如果为True且路径为空则返回False
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            caller_dir = os.getcwd()
            # 获取函数参数的信息
            full_args_spec = inspect.getfullargspec(func)
            arg_names = full_args_spec.args
            default_values = full_args_spec.defaults if full_args_spec.defaults else []
            default_values = dict(zip(arg_names[-len(default_values):], default_values))

            # 获取传入的参数
            all_args = dict(zip(arg_names, args))
            all_args.update(kwargs)

            # 如果没有传入缺省参数值，从 default_values 中取值
            for param_name, default_value in default_values.items():
                if param_name not in all_args:
                    all_args[param_name] = default_value

            # 基础路径
            last_echo = echo()
            echo(False)
            base_path = work_dir()  # 将 base_path 替换成你的实际路径
            echo(last_echo)

            for param_name in param_names:
                if param_name in all_args:
                    path = all_args[param_name]
                    if type(path) != str and type(path) != bytes:
                        raise TypeError("%s() argument '%s' must be 'str' or 'bytes', not %r" %
                                        (func.__name__, param_name, path.__class__.__name__)) from None
                    # 检查空路径
                    if check_empty and path == "":
                        print("[ERROR]: %s() 参数 '%s' 不能为空" % (func.__name__, param_name))
                        return False
                    # SimulateModel 为空表示采用仿真结果目录，而不是相对路径
                    if func.__name__ == 'SimulateModel' and path == "":
                        return func(*args, **kwargs)
                    if is_read:
                        # 读操作：首先检查脚本路径下是否存在文件
                        if caller_dir:
                            abs_path = os.path.join(caller_dir, path)
                            if os.path.exists(abs_path):
                                all_args[param_name] = abs_path
                            else:
                                all_args[param_name] = os.path.join(base_path, path)
                        else:
                            all_args[param_name] = os.path.join(base_path, path)
                    else:
                        # 写操作：直接根据是否有脚本路径来拼接路径
                        if caller_dir:
                            all_args[param_name] = os.path.join(caller_dir, path)
                        else:
                            all_args[param_name] = os.path.join(base_path, path)

            # 用更新后的参数调用函数
            return func(**all_args)
        return wrapper
    return decorator