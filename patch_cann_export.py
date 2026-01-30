#!/usr/bin/env python3
"""
修补 _cann_export.py 文件，添加对打包 msprof 的支持
"""
import sys
import os


def patch_cann_export(file_path: str):
    """
    修补 _cann_export.py 文件
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
    old_class_vars = '    _MSPROF_PY_PATH = "tools/profiler/profiler_tool/analysis/msprof/msprof.py"'
    new_class_vars = '''    _MSPROF_PY_PATH = "tools/profiler/profiler_tool/analysis/msprof/msprof.py"
    # 打包进来的msprof.py相对路径（相对于包根目录）
    _BUNDLED_MSPROF_PATH = "analysis/analysis/msprof/msprof.py"'''
    
    content = content.replace(old_class_vars, new_class_vars)
    
    # 2. 修改 __init__ 方法
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
    
    # 3. 修改 run 方法中的 Db 导出部分
    old_db_export = '''            if Constant.Db in self._export_type:
                analyze_cmd_list = [self.msprof_path, "--export=on", "--type=db", f"--output={self._cann_path}"]
                completed_analysis = subprocess.run(analyze_cmd_list, capture_output=True, shell=False)'''
    
    new_db_export = '''            if Constant.Db in self._export_type:
                if self.use_bundled_msprof:
                    # 寻找并设置 libc_sec.so 的路径 (LD_LIBRARY_PATH)
                    msprof_dir = os.path.dirname(self.msprof_path)
                    lib_path = ""
                    p = msprof_dir
                    for _ in range(4): # 向上查找 prefix 目录
                        possible_lib = os.path.join(p, "prefix/securec_shared")
                        if os.path.exists(possible_lib):
                             lib_path = possible_lib
                             break
                        p = os.path.dirname(p)
                    
                    env = os.environ.copy()
                    if lib_path:
                         ld_path = env.get("LD_LIBRARY_PATH", "")
                         env["LD_LIBRARY_PATH"] = f"{lib_path}:{ld_path}"

                    # msprof.py 使用子命令格式
                    analyze_cmd_list = ["python3", self.msprof_path, "export", "db", "-dir", self._cann_path]
                    completed_analysis = subprocess.run(analyze_cmd_list, capture_output=True, shell=False, env=env)
                else:
                    analyze_cmd_list = [self.msprof_path, "--export=on", "--type=db", f"--output={self._cann_path}"]
                    completed_analysis = subprocess.run(analyze_cmd_list, capture_output=True, shell=False)'''
    
    content = content.replace(old_db_export, new_db_export)
    
    # 4. 修改 run 方法中的 Text 导出部分
    old_text_export = '''            if Constant.Text in self._export_type:
                # 避免老CANN包无type参数报错
                analyze_cmd_list = [self.msprof_path, "--export=on", f"--output={self._cann_path}"]
                completed_analysis = subprocess.run(analyze_cmd_list, capture_output=True, shell=False)'''
    
    new_text_export = '''            if Constant.Text in self._export_type:
                # 避免老CANN包无type参数报错
                if self.use_bundled_msprof:
                    # 寻找并设置 libc_sec.so 的路径 (LD_LIBRARY_PATH)
                    msprof_dir = os.path.dirname(self.msprof_path)
                    lib_path = ""
                    p = msprof_dir
                    for _ in range(4): # 向上查找 prefix 目录
                        possible_lib = os.path.join(p, "prefix/securec_shared")
                        if os.path.exists(possible_lib):
                             lib_path = possible_lib
                             break
                        p = os.path.dirname(p)
                    
                    env = os.environ.copy()
                    if lib_path:
                         ld_path = env.get("LD_LIBRARY_PATH", "")
                         env["LD_LIBRARY_PATH"] = f"{lib_path}:{ld_path}"

                    # msprof.py 使用子命令格式: 需要分别导出 timeline 和 summary
                    for export_type in ("timeline", "summary"):
                        analyze_cmd_list = ["python3", self.msprof_path, "export", export_type, "-dir", self._cann_path]
                        completed_analysis = subprocess.run(analyze_cmd_list, capture_output=True, shell=False, env=env)
                        if completed_analysis.returncode != self.COMMAND_SUCCESS:
                            print(f"[ERROR] msprof export {export_type} failed!")
                            if completed_analysis.stderr:
                                print(f"[ERROR] stderr: {completed_analysis.stderr.decode('utf-8', errors='ignore')}")
                            if completed_analysis.stdout:
                                print(f"[ERROR] stdout: {completed_analysis.stdout.decode('utf-8', errors='ignore')}")
                            raise RuntimeError(f"Failed to export CANN {export_type} Profiling data." + prof_error(ErrCode.INTERNAL))
                else:
                    analyze_cmd_list = [self.msprof_path, "--export=on", f"--output={self._cann_path}"]
                    completed_analysis = subprocess.run(analyze_cmd_list, capture_output=True, shell=False)
                    if completed_analysis.returncode != self.COMMAND_SUCCESS:
                        print(f"[ERROR] msprof export failed!")
                        if completed_analysis.stderr:
                            print(f"[ERROR] stderr: {completed_analysis.stderr.decode('utf-8', errors='ignore')}")
                        raise RuntimeError("Failed to export CANN TEXT Profiling data." + prof_error(ErrCode.INTERNAL))'''
    
    content = content.replace(old_text_export, new_text_export)
    
    # 5. 修改 _check_msprof_path 方法
    old_check_method = '''    def _check_msprof_path(self):
        error_message = ""
        if not self.msprof_path:
            error_message += "Export CANN Profiling data failed! 'msprof' command not found!" \\
                             + prof_error(ErrCode.NOT_FOUND) + "\\n"
        if not ProfilerPathManager.check_path_permission(self.msprof_path):'''
    
    new_check_method = '''    def _check_msprof_path(self):
        error_message = ""
        if not self.msprof_path:
            error_message += "Export CANN Profiling data failed! 'msprof' command not found!" \\
                             + prof_error(ErrCode.NOT_FOUND) + "\\n"
            raise RuntimeError(error_message)
        
        # 如果使用打包的msprof，只需要检查文件是否存在
        if self.use_bundled_msprof:
            if not os.path.exists(self.msprof_path):
                error_message += f"Bundled msprof.py not found at: {self.msprof_path}" \\
                                 + prof_error(ErrCode.NOT_FOUND) + "\\n"
            if error_message:
                raise RuntimeError(error_message)
            return
        
        # 使用系统msprof时的完整检查
        if not ProfilerPathManager.check_path_permission(self.msprof_path):'''
    
    content = content.replace(old_check_method, new_check_method)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 成功修补文件: {file_path}")
    return True


def main():
    if len(sys.argv) != 2:
        print("用法: python patch_cann_export.py <_cann_export.py文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not patch_cann_export(file_path):
        sys.exit(1)
    
    print("\n✓ 补丁应用完成!")


if __name__ == "__main__":
    main()
