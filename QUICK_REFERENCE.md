# NPU Profiler 打包工具 - 快速参考

## 🚀 快速开始

```bash
# 一键构建
./build_npu_profiler.sh

# 安装生成的包
pip install dist/npu-profiler-analyser-1.0.0-py3-none-any.whl

# 使用
npu-profiler-analyse /path/to/profiling_data
```

## 📁 项目结构

```
pta_profiler/
├── build_npu_profiler.sh          # 主构建脚本 (执行这个!)
├── create_standalone_profiler.py  # 代码提取
├── generate_package_files.py      # 生成setup.py/README
├── README.md                      # 项目说明
├── BUILD_GUIDE.md                 # 详细指南
└── dist/                          # 输出目录
    └── npu_profiler_analyser-*.whl
```

## 🔧 核心脚本

| 脚本 | 用途 | 独立使用 |
|------|------|----------|
| `build_npu_profiler.sh` | 主构建流程 | ✅ |
| `create_standalone_profiler.py` | 提取profiler代码 | ✅ |
| `generate_package_files.py` | 生成打包文件 | ✅ |

## 📝 常用命令

```bash
# 完整构建
./build_npu_profiler.sh

# 清理重建
rm -rf build_workspace dist
./build_npu_profiler.sh

# 只生成打包文件
python3 generate_package_files.py build_workspace/npu_profiler_standalone

# 测试whl包
pip install dist/npu_profiler_analyser-*.whl
npu-profiler-analyse --help
```

## 🎯 构建流程 (5步)

1. **创建工作目录** → `build_workspace/`
2. **Clone仓库** → `build_workspace/pytorch/`
3. **提取代码** → `build_workspace/npu_profiler_standalone/`
4. **生成打包文件** → `setup.py` + `README.md`
5. **打包whl** → `dist/npu_profiler_analyser-*.whl`

## ⚙️ 自定义配置

### 修改版本号
编辑 `generate_package_files.py`:
```python
version="1.0.0",  # 改为你的版本
```

### 添加依赖
编辑 `generate_package_files.py`:
```python
install_requires=[
    "numpy",
    "pandas",
    "your-package",  # 添加这里
],
```

### 修改命令名
编辑 `generate_package_files.py`:
```python
entry_points={
    'console_scripts': [
        'your-command=analyse:main',  # 改这里
    ],
},
```

## 🐛 故障排查

| 问题 | 解决方案 |
|------|----------|
| git clone失败 | 检查网络,或手动放置pytorch到`build_workspace/` |
| setuptools缺失 | `pip install setuptools wheel` |
| 重新构建 | `rm -rf build_workspace dist` |

## 📚 更多信息

- 详细指南: `BUILD_GUIDE.md`
- 项目说明: `README.md`
- 代码提取逻辑: `create_standalone_profiler.py`
- 打包配置: `generate_package_files.py`
