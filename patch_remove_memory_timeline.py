#!/usr/bin/env python3
"""
将 _memory_timeline_parser.py 替换为空实现，移除 torch 依赖
"""
import sys
import os


def patch_memory_timeline(file_path: str):
    """
    将 _memory_timeline_parser.py 替换为空实现
    """
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return False
    
    print(f"正在修改: {file_path}")
    
    # 新的内容：只保留基本结构和空实现，移除 torch 依赖
    new_content = '''
from ._base_parser import BaseParser
from ..prof_common_func._constant import Constant
from ..prof_common_func._log import ProfilerLogger

__all__ = []

class MemoryTimelineParser(BaseParser):
    """
    MemoryTimelineParser 空实现，移除 torch 依赖
    """
    def __init__(self, name: str, param_dict: dict):
        super().__init__(name, param_dict)
        ProfilerLogger.init(self._profiler_path, "MemoryTimelineParser")
        self.logger = ProfilerLogger.get_instance()

    def run(self, deps_data: dict):
        self.logger.warning("MemoryTimelineParser is disabled in standalone mode due to torch dependency.")
        return Constant.SUCCESS, None
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ 成功保留 MemoryTimelineParser 空实现，已移除依赖")
    return True


def main():
    if len(sys.argv) != 2:
        print("用法: python patch_remove_memory_timeline.py <_memory_timeline_parser.py文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not patch_memory_timeline(file_path):
        sys.exit(1)


if __name__ == "__main__":
    main()
