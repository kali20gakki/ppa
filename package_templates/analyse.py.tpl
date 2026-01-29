#!/usr/bin/env python3
"""
NPU Profiler 离线分析工具
独立运行,无需torch_npu环境

使用方法:
    python analyse.py <profiler_data_path> [--max_process_number N] [--export_type text|db]
    
示例:
    python analyse.py ./profiling_data
    python analyse.py ./profiling_data --max_process_number 8 --export_type text
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from npu_profiler.analysis._npu_profiler import NpuProfiler
from npu_profiler.analysis.prof_common_func._constant import Constant

def analyse(profiler_path: str, max_process_number: int = Constant.DEFAULT_PROCESS_NUMBER, 
            export_type=None):
    """
    离线分析NPU profiling数据
    
    参数:
        profiler_path: profiling数据路径
        max_process_number: 最大进程数,默认为CPU核心数的一半
        export_type: 导出类型,'text'或'db',默认为None(使用profiler_info.json中的配置)
    """
    NpuProfiler.analyse(
        profiler_path, 
        max_process_number=max_process_number, 
        export_type=export_type
    )

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='NPU Profiler 离线分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./profiling_data
  %(prog)s ./profiling_data --max_process_number 8
  %(prog)s ./profiling_data --export_type text
        """
    )
    
    parser.add_argument(
        'profiler_path',
        help='Profiling数据目录路径'
    )
    
    parser.add_argument(
        '--max_process_number',
        type=int,
        default=Constant.DEFAULT_PROCESS_NUMBER,
        help=f'最大并行进程数 (默认: {Constant.DEFAULT_PROCESS_NUMBER})'
    )
    
    parser.add_argument(
        '--export_type',
        choices=['text', 'db'],
        default=None,
        help='导出类型: text 或 db (默认: 使用profiler_info.json中的配置)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("NPU Profiler 离线分析工具")
    print("=" * 70)
    print(f"数据路径: {args.profiler_path}")
    print(f"最大进程数: {args.max_process_number}")
    print(f"导出类型: {args.export_type or '默认'}")
    print("=" * 70)
    
    try:
        analyse(
            args.profiler_path,
            max_process_number=args.max_process_number,
            export_type=args.export_type
        )
        print("\\n✓ 分析完成!")
    except Exception as e:
        print(f"\\n✗ 分析失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
