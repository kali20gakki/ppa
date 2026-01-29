# NPU Profiler 独立分析工具构建指南

## 概述

本项目提供了一键式构建脚本,用于创建NPU Profiler的独立离线分析工具whl包。

## 构建步骤

### 1. 执行构建脚本

```bash
cd /Users/a123/Project/pta_profiler
./build_npu_profiler.sh
```

### 2. 构建流程说明

脚本会自动完成以下步骤:

1. **创建工作目录** - 在`build_workspace`目录下进行构建
2. **Clone torch_npu仓库** - 从 https://gitcode.com/Ascend/pytorch.git 克隆代码
3. **执行提取脚本** - 运行`create_standalone_profiler.py`提取必要的代码
4. **生成打包文件** - 调用`generate_package_files.py`创建setup.py和README.md
5. **打包成whl** - 使用setuptools构建wheel包

### 3. 输出文件

构建完成后,whl包将输出到 `dist/` 目录:

```
dist/
└── ppa-1.0.0-py3-none-any.whl
```

## 安装和使用

### 安装whl包

```bash
pip install dist/ppa-1.0.0-py3-none-any.whl
```

### 使用命令行接口

安装后会提供 `ppa` 命令:

```bash
# 基本用法
ppa /path/to/profiling_data

# 指定最大进程数
ppa /path/to/profiling_data --max_process_number 8

# 指定导出类型
ppa /path/to/profiling_data --export_type text
```

### Python API使用

```python
from analyse import analyse

# 分析profiling数据
analyse('/path/to/profiling_data')

# 自定义参数
analyse(
    '/path/to/profiling_data',
    max_process_number=8,
    export_type='text'
)
```

## 参数说明

- `profiler_path`: Profiling数据目录路径(必需)
- `--max_process_number`: 最大并行进程数,默认为CPU核心数的一半
- `--export_type`: 导出类型
  - `text`: 导出为文本格式
  - `db`: 导出为数据库格式
  - 不指定则使用profiler_info.json中的配置

## 依赖要求

### 构建依赖

- Python >= 3.7
- git
- setuptools
- wheel

### 运行依赖

- Python >= 3.7
- numpy
- pandas

## 目录结构

```
pta_profiler/
├── build_npu_profiler.sh          # 主构建脚本
├── create_standalone_profiler.py  # 代码提取脚本
├── generate_package_files.py      # 生成setup.py和README.md
├── BUILD_GUIDE.md                 # 本文档
├── build_workspace/               # 构建工作目录(自动创建)
│   ├── pytorch/                   # clone的torch_npu仓库
│   └── npu_profiler_standalone/   # 提取的独立工具
└── dist/                          # 输出目录
    └── ppa-*.whl
```

## 脚本说明

### build_npu_profiler.sh
主构建脚本,协调整个构建流程:
1. 创建工作目录
2. Clone torch_npu仓库
3. 执行create_standalone_profiler.py提取代码
4. 调用generate_package_files.py生成打包文件
5. 打包成whl文件

### create_standalone_profiler.py
从torch_npu仓库中提取profiler分析相关代码,创建独立的分析工具。

### generate_package_files.py
生成打包所需的setup.py和README.md文件。可以独立使用:
```bash
python3 generate_package_files.py <target_directory>
```

## 故障排查

### 问题1: git clone失败

**原因**: 网络问题或仓库地址不可达

**解决方案**:
- 检查网络连接
- 如果已经有pytorch仓库,可以手动放置到`build_workspace/pytorch`目录

### 问题2: Python依赖缺失

**错误信息**: `ModuleNotFoundError: No module named 'setuptools'`

**解决方案**:
```bash
pip install setuptools wheel
```

### 问题3: 重新构建

如需完全重新构建,删除工作目录:

```bash
rm -rf build_workspace dist
./build_npu_profiler.sh
```

## 高级配置

### 修改版本号

编辑 `build_npu_profiler.sh` 中setup.py的version字段:

```python
version="1.0.0",  # 修改为你需要的版本号
```

### 添加额外依赖

在setup.py的`install_requires`中添加:

```python
install_requires=[
    "numpy",
    "pandas",
    "your-package",  # 添加新依赖
],
```

## 许可证

BSD License

## 相关链接

- [torch_npu项目](https://gitcode.com/Ascend/pytorch)
