#!/usr/bin/env python3
"""
生成打包所需的setup.py和README.md文件
"""
import os
import sys
import shutil

# 模板文件所在目录 (相对于本脚本)
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'package_templates')


def copy_template(template_name: str, target_dir: str, target_filename: str = None):
    """
    复制模板文件到目标目录
    :param template_name: 模板文件名 (在 package_templates 目录下)
    :param target_dir: 目标目录
    :param target_filename: 目标文件名 (如果为None则与模板名相同)
    """
    if target_filename is None:
        target_filename = template_name
        
    src_path = os.path.join(TEMPLATE_DIR, template_name)
    dst_path = os.path.join(target_dir, target_filename)
    
    if not os.path.exists(src_path):
        print(f"错误: 找不到模板文件: {src_path}")
        # 如果是关键文件缺失，可能需要退出，这里暂且打印错误
        return

    try:
        shutil.copy2(src_path, dst_path)
        print(f"✓ 创建 {target_filename}: {dst_path}")
    except Exception as e:
        print(f"错误: 复制文件失败 {src_path} -> {dst_path}: {e}")


def main():
    if len(sys.argv) != 2:
        print("用法: python generate_package_files.py <target_directory>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f"错误: 目标目录不存在: {target_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("生成打包文件")
    print("=" * 60)
    print(f"目标目录: {target_dir}\n")
    print(f"模板目录: {TEMPLATE_DIR}\n")
    
    # 复制各个模板文件
    copy_template('setup.py', target_dir)
    copy_template('README.md', target_dir)
    copy_template('MANIFEST.in', target_dir)
    
    print("\n✓ 所有文件生成完成!")


if __name__ == "__main__":
    main()
