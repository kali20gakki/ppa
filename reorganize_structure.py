#!/usr/bin/env python3
"""
重组目录结构，将所有文件放到 ppa 包目录下
"""
import os
import sys
import shutil


def reorganize_structure(standalone_dir: str):
    """
    重组目录结构
    将 analyse.py, npu_profiler/, analysis/ 都移动到 ppa/ 目录下
    """
    print("=" * 60)
    print("重组目录结构")
    print("=" * 60)
    
    if not os.path.exists(standalone_dir):
        print(f"错误: 目标目录不存在: {standalone_dir}")
        return False
    
    # 创建 ppa 包目录
    ppa_dir = os.path.join(standalone_dir, "ppa")
    if os.path.exists(ppa_dir):
        print(f"清理已存在的 ppa 目录: {ppa_dir}")
        shutil.rmtree(ppa_dir)
    
    os.makedirs(ppa_dir)
    print(f"✓ 创建 ppa 目录: {ppa_dir}")
    
    # 移动 npu_profiler 目录
    src_npu_profiler = os.path.join(standalone_dir, "npu_profiler")
    dst_npu_profiler = os.path.join(ppa_dir, "npu_profiler")
    if os.path.exists(src_npu_profiler):
        shutil.move(src_npu_profiler, dst_npu_profiler)
        print(f"✓ 移动 npu_profiler/ -> ppa/npu_profiler/")
    else:
        print(f"⚠ npu_profiler 目录不存在，跳过")
    
    # 移动 analysis 目录
    src_analysis = os.path.join(standalone_dir, "analysis")
    dst_analysis = os.path.join(ppa_dir, "analysis")
    if os.path.exists(src_analysis):
        shutil.move(src_analysis, dst_analysis)
        print(f"✓ 移动 analysis/ -> ppa/analysis/")
    else:
        print(f"⚠ analysis 目录不存在，跳过")
    
    # 处理 analyse.py
    src_analyse = os.path.join(standalone_dir, "analyse.py")
    if os.path.exists(src_analyse):
        # 读取 analyse.py 内容
        with open(src_analyse, 'r', encoding='utf-8') as f:
            analyse_content = f.read()
        
        # 修正导入路径: from npu_profiler -> from ppa.npu_profiler
        analyse_content = analyse_content.replace(
            "from npu_profiler", 
            "from ppa.npu_profiler"
        )
        
        # 创建 __main__.py（作为包的入口点）
        main_py = os.path.join(ppa_dir, "__main__.py")
        with open(main_py, 'w', encoding='utf-8') as f:
            f.write(analyse_content)
        print(f"✓ 创建 ppa/__main__.py（从 analyse.py）")
        
        # 同时保留一份作为 cli.py（供 entry_points 使用）
        cli_py = os.path.join(ppa_dir, "cli.py")
        with open(cli_py, 'w', encoding='utf-8') as f:
            f.write(analyse_content)
        print(f"✓ 创建 ppa/cli.py（从 analyse.py）")
        
        # 删除原 analyse.py
        os.remove(src_analyse)
        print(f"✓ 删除原 analyse.py")
    else:
        print(f"⚠ analyse.py 不存在，跳过")
    
    # 创建 ppa/__init__.py
    init_py = os.path.join(ppa_dir, "__init__.py")
    with open(init_py, 'w', encoding='utf-8') as f:
        f.write('"""NPU Profiler 独立分析工具"""\n')
        f.write('__version__ = "1.0.0"\n')
    print(f"✓ 创建 ppa/__init__.py")
    
    print("\n✓ 目录结构重组完成!")
    print("\n新的目录结构:")
    print(f"{standalone_dir}/")
    print("└── ppa/")
    print("    ├── __init__.py")
    print("    ├── __main__.py")
    print("    ├── cli.py")
    print("    ├── npu_profiler/")
    print("    └── analysis/")
    
    return True


def main():
    if len(sys.argv) != 2:
        print("用法: python reorganize_structure.py <standalone_directory>")
        sys.exit(1)
    
    standalone_dir = sys.argv[1]
    
    if not reorganize_structure(standalone_dir):
        sys.exit(1)


if __name__ == "__main__":
    main()
