# PTA Profiler Analyser (ppa)

独立的NPU Profiler数据分析工具,无需完整的torch_npu环境即可运行。

## 功能特性

- ✅ 离线分析NPU profiling数据
- ✅ 支持多进程并行分析
- ✅ 支持text和db两种导出格式
- ✅ 无需torch_npu运行时环境
- ✅ 提供命令行接口

## 安装

```bash
pip install ppa-1.0.0-py3-none-any.whl
```

## 使用方法

### 命令行使用

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
- `--export_type`: 导出类型,可选值为`text`或`db`,默认使用profiler_info.json中的配置

## 系统要求

- Python >= 3.7
- numpy
- pandas

## 许可证

BSD License

## 相关链接

- [torch_npu项目](https://gitcode.com/Ascend/pytorch)
