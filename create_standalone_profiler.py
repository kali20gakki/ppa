#!/usr/bin/env python3
"""
创建独立的NPU Profiler离线分析工具
只包含analyse接口所需的最小依赖
"""
import os
import shutil

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "package_templates")

ROOT_DIR = "/Users/a123/Project/pytorch/torch_npu"
TARGET_DIR = "/Users/a123/Project/npu_profiler_standalone"

def read_template(template_name):
    """读取模板文件内容"""
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def copy_file(src_rel, dst_rel):
    """复制单个文件"""
    src = os.path.join(ROOT_DIR, src_rel)
    dst = os.path.join(TARGET_DIR, dst_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"✓ Copied {src_rel}")

def copy_dir(src_rel, dst_rel, exclude_patterns=None):
    """复制目录"""
    src = os.path.join(ROOT_DIR, src_rel)
    dst = os.path.join(TARGET_DIR, dst_rel)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    
    def ignore_func(dir, files):
        ignored = []
        for f in files:
            if f.startswith('.'):
                ignored.append(f)
            if exclude_patterns:
                for pattern in exclude_patterns:
                    if pattern in f:
                        ignored.append(f)
                        break
        return ignored
    
    shutil.copytree(src, dst, ignore=ignore_func)
    print(f"✓ Copied directory {src_rel}")

def create_file(path_rel, content):
    """创建文件"""
    dst = os.path.join(TARGET_DIR, path_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {path_rel}")

def main():
    print("=" * 60)
    print("创建独立NPU Profiler离线分析工具")
    print("=" * 60)
    print(f"模板目录: {TEMPLATE_DIR}")
    
    # 清理并创建目标目录
    if os.path.exists(TARGET_DIR):
        shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DIR)
    
    # 1. 复制analysis目录(核心分析逻辑)
    print("\n[1/5] 复制分析核心代码...")
    copy_dir("profiler/analysis", "npu_profiler/analysis")
    
    # 2. 复制必要的utils文件
    print("\n[2/5] 复制工具函数...")
    copy_file("utils/_path_manager.py", "npu_profiler/utils/_path_manager.py")
    copy_file("utils/_error_code.py", "npu_profiler/utils/_error_code.py")
    
    # 3. 创建最小化的utils模块
    print("\n[3/5] 创建最小化工具模块...")
    utils_content = read_template("utils.py.tpl")
    create_file("npu_profiler/utils/utils.py", utils_content)
    
    # 4. 创建__init__.py文件
    print("\n[4/5] 创建包初始化文件...")
    create_file("npu_profiler/__init__.py", "")
    
    utils_init_content = read_template("utils_init.py.tpl")
    create_file("npu_profiler/utils/__init__.py", utils_init_content)
    
    # 5. 创建主入口文件
    print("\n[5/5] 创建主入口文件...")
    main_entry_content = read_template("analyse.py.tpl")
    create_file("analyse.py", main_entry_content)
    
    # 6. 自动修复所有导入路径
    print("\n[6/6] 修复导入路径...")
    fix_imports()
    
    print("\n" + "=" * 60)
    print("✓ 独立工具创建完成!")
    print("=" * 60)
    print(f"\n工具位置: {TARGET_DIR}")
    print("\n使用方法:")
    print(f"  cd {TARGET_DIR}")
    print("  python analyse.py /path/to/profiling_data")
    print()

def fix_imports():
    """修复所有Python文件中的导入路径"""
    import re
    
    fixed_count = 0
    npu_profiler_dir = os.path.join(TARGET_DIR, "npu_profiler")
    
    for root, dirs, files in os.walk(npu_profiler_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # 替换torch_npu.utils导入
                content = content.replace(
                    'from torch_npu.utils._error_code import',
                    'from npu_profiler.utils._error_code import'
                )
                content = content.replace(
                    'from torch_npu.utils._path_manager import',
                    'from npu_profiler.utils._path_manager import'
                )
                content = content.replace(
                    'from torch_npu.utils import _should_print_warning',
                    'from npu_profiler.utils import _should_print_warning'
                )
                
                # 修复相对导入 - 四个点
                content = re.sub(
                    r'from \.\.\.\.utils\._path_manager import',
                    'from npu_profiler.utils._path_manager import',
                    content
                )
                content = re.sub(
                    r'from \.\.\.\.utils\._error_code import',
                    'from npu_profiler.utils._error_code import',
                    content
                )
                
                # 修复相对导入 - 三个点
                content = re.sub(
                    r'from \.\.\.utils\._path_manager import',
                    'from npu_profiler.utils._path_manager import',
                    content
                )
                content = re.sub(
                    r'from \.\.\.utils\._error_code import',
                    'from npu_profiler.utils._error_code import',
                    content
                )
                
                # 特殊处理: 修复_host_info.py,移除torch_npu._C依赖
                if filename == '_host_info.py':
                    # 替换导入
                    content = re.sub(
                        r'from torch_npu\._C\._profiler import _get_host_uid',
                        'import uuid',
                        content
                    )
                    # 替换_get_host_uid()的使用
                    content = re.sub(
                        r'host_uid = str\(_get_host_uid\(\)\)',
                        'host_uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, host_name))',
                        content
                    )
                
                # 如果有修改,写回文件
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    rel_path = os.path.relpath(filepath, npu_profiler_dir)
                    print(f"  ✓ Fixed: {rel_path}")
                    fixed_count += 1
    
    if fixed_count > 0:
        print(f"  总共修复了 {fixed_count} 个文件")
    else:
        print(f"  无需修复")

if __name__ == "__main__":
    main()
