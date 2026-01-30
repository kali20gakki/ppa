# PPA(Pytorch Profiler Analyzer)

PPA是基于Pytorch Profiler的离线分析工具, 目的是解耦torch_npu对npu环境的依赖, 支持在NPU Profiler生成的离线分析数据。

**使用方法**:
解耦torch_npu依赖，独立打包命令行ppa
```bash
./build_npu_profiler.sh
```

## 输出产物

### ppa-1.0.0-py3-none-any.whl
最终的Python wheel包,包含:
- `npu_profiler/` - 核心分析代码
- `analyse.py` - 主入口文件
- 命令行工具: `ppa`

**安装后提供**:
```bash
# 查看帮助
ppa --help

# 命令行接口
ppa /path/to/profiling_data
```