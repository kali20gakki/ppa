# 项目文件说明

## 核心文件

### 1. build_npu_profiler.sh
**主构建脚本** - 一键式构建工具

**功能**:
- 自动化整个构建流程
- Clone torch_npu仓库
- 协调各个Python脚本的执行
- 生成最终的whl包

**使用方法**:
```bash
./build_npu_profiler.sh
```

---

### 2. create_standalone_profiler.py
**代码提取脚本** - 从torch_npu提取profiler代码

**功能**:
- 从torch_npu仓库中复制profiler分析相关代码
- 修复导入路径,移除torch_npu依赖
- 创建独立的分析工具目录结构
- 生成analyse.py主入口文件

**配置**:
- `ROOT_DIR`: torch_npu源码路径
- `TARGET_DIR`: 输出目录路径

---

### 3. generate_package_files.py
**打包文件生成器** - 生成setup.py和README.md

**功能**:
- 生成符合setuptools规范的setup.py
- 生成包含使用说明的README.md
- 配置命令行入口点(npu-profiler-analyse)

**使用方法**:
```bash
python3 generate_package_files.py <target_directory>
```

**独立使用场景**:
- 更新包的版本号或依赖
- 修改README内容
- 调整包的元数据

---

## 文档文件

### BUILD_GUIDE.md
详细的构建和使用指南,包含:
- 完整的构建步骤
- 安装和使用说明
- 故障排查指南
- 高级配置选项

---

## 设计理念

### 模块化设计
每个脚本职责单一,便于维护和测试:
- **build_npu_profiler.sh**: 流程协调
- **create_standalone_profiler.py**: 代码提取
- **generate_package_files.py**: 打包配置

### 可复用性
- `generate_package_files.py`可独立使用
- `create_standalone_profiler.py`可单独运行
- 各脚本之间通过文件系统交互,耦合度低

### 易于维护
- setup.py和README.md集中在一个Python文件中
- 修改打包配置无需编辑shell脚本
- 清晰的步骤划分,便于调试

---

## 输出产物

### npu-profiler-analyser-1.0.0-py3-none-any.whl
最终的Python wheel包,包含:
- `npu_profiler/` - 核心分析代码
- `analyse.py` - 主入口文件
- 命令行工具: `npu-profiler-analyse`

**安装后提供**:
```bash
# 命令行接口
npu-profiler-analyse /path/to/profiling_data

# Python API
from analyse import analyse
analyse('/path/to/profiling_data')
```
