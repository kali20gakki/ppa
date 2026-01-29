"""
最小化的工具函数,避免依赖torch_npu._C
"""
__all__ = ["_print_error_log", "_print_warn_log", "_print_info_log", "_should_print_warning"]

import os
import time

class _LogLevel:
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

def _print_log(level: str, msg: str):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    pid = os.getpid()
    print(f"{current_time}({pid})-[{level}] {msg}")

def _print_info_log(info_msg: str):
    _print_log(_LogLevel.INFO, info_msg)

def _print_warn_log(warn_msg: str):
    _print_log(_LogLevel.WARNING, warn_msg)

def _print_error_log(error_msg: str):
    _print_log(_LogLevel.ERROR, error_msg)

def _should_print_warning():
    """判断是否应该打印警告"""
    disabled_warning = os.environ.get("TORCH_NPU_DISABLED_WARNING", "0")
    if disabled_warning == "1":
        return False
    rank = os.environ.get("RANK", None)
    if rank is None or rank == "0":
        return True
    return False
