#!/usr/bin/env python3
"""
修补 _cann_analyze.py 文件，添加对打包 msprof 的支持
"""
import sys
import os


def patch_cann_analyze(file_path: str):
    """
    修补 _cann_analyze.py 文件
    """
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经打过补丁
    if '_BUNDLED_MSPROF_PATH' in content:
        print(f"文件已经打过补丁，跳过: {file_path}")
        return True
    
    # 1. 在类定义中添加 _BUNDLED_MSPROF_PATH
    old_class_vars = 'class CANNAnalyzeParser(BaseParser):\n    COMMAND_SUCCESS = 0'
    new_class_vars = '''class CANNAnalyzeParser(BaseParser):
    COMMAND_SUCCESS = 0
    # 打包进来的msprof.py相对路径（相对于包根目录）
    _BUNDLED_MSPROF_PATH = "analysis/analysis/msprof/msprof.py"'''
    
    content = content.replace(old_class_vars, new_class_vars)
    
    # 2. 修改 __init__ 方法，添加打包 msprof 检测逻辑
    old_init = '''    def __init__(self, name: str, param_dict: dict):
        super().__init__(name, param_dict)
        self._cann_path = ProfilerPathManager.get_cann_path(self._profiler_path)
        self.msprof_path = shutil.which("msprof")'''
    
    new_init = '''    def __init__(self, name: str, param_dict: dict):
        super().__init__(name, param_dict)
        self._cann_path = ProfilerPathManager.get_cann_path(self._profiler_path)
        self.msprof_path = shutil.which("msprof")
        self.use_bundled_msprof = False
        
        # 如果系统中没有msprof，尝试使用打包进来的msprof.py
        if not self.msprof_path:
            bundled_msprof = self._get_bundled_msprof_path()
            if bundled_msprof and os.path.exists(bundled_msprof):
                self.msprof_path = bundled_msprof
                self.use_bundled_msprof = True
    
    def _get_bundled_msprof_path(self) -> str:
        """获取打包进来的msprof.py路径"""
        # 获取当前文件所在目录
        current_file = os.path.abspath(__file__)
        # 向上查找包根目录（包含cli.py的目录，即ppa包目录）
        package_root = current_file
        for _ in range(10):  # 最多向上查找10层
            package_root = os.path.dirname(package_root)
            # 在新的结构中，根目录下会有 cli.py (由 analyse.py 重命名/复制而来)
            root_marker = os.path.join(package_root, "cli.py")
            if os.path.exists(root_marker):
                bundled_path = os.path.join(package_root, self._BUNDLED_MSPROF_PATH)
                return bundled_path if os.path.exists(bundled_path) else ""
        return ""'''
    
    content = content.replace(old_init, new_init)
    
    # 3. 修改 run 方法中的 Db 分析部分
    old_db_analyze = 'analyze_cmd_list = [self.msprof_path, "--analyze=on", "--type=db", f"--output={self._cann_path}"]'
    # 使用 python3 msprof.py analyze --type db --rule communication,communication_matrix -dir <dir>
    new_db_analyze = '''if self.use_bundled_msprof:
                    analyze_cmd_list = ["python3", self.msprof_path, "analyze", "--type", "db", "--rule", "communication,communication_matrix", "-dir", self._cann_path]
                else:
                    analyze_cmd_list = [self.msprof_path, "--analyze=on", "--type=db", f"--output={self._cann_path}"]'''
    
    content = content.replace(old_db_analyze, new_db_analyze)
    
    # 4. 修改 run 方法中的 Text 分析部分
    old_text_analyze = 'analyze_cmd_list = [self.msprof_path, "--analyze=on", f"--output={self._cann_path}"]'
    # 使用 python3 msprof.py analyze --rule communication,communication_matrix -dir <dir>
    new_text_analyze = '''if self.use_bundled_msprof:
                    analyze_cmd_list = ["python3", self.msprof_path, "analyze", "--rule", "communication,communication_matrix", "-dir", self._cann_path]
                else:
                    analyze_cmd_list = [self.msprof_path, "--analyze=on", f"--output={self._cann_path}"]'''
    
    content = content.replace(old_text_analyze, new_text_analyze)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 成功修补文件: {file_path}")
    return True


def main():
    if len(sys.argv) != 2:
        print("用法: python patch_cann_analyze.py <_cann_analyze.py文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not patch_cann_analyze(file_path):
        sys.exit(1)
    
    print("\n✓ 补丁应用完成!")


if __name__ == "__main__":
    main()
