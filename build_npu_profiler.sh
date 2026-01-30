#!/bin/bash
set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/build_workspace"
TORCH_NPU_REPO="https://gitcode.com/Ascend/pytorch.git"
TORCH_NPU_DIR="${WORK_DIR}/pytorch"
MSPROF_REPO="https://gitcode.com/Ascend/msprof.git"
MSPROF_DIR="${WORK_DIR}/msprof"
STANDALONE_DIR="${WORK_DIR}/npu_profiler_standalone"
OUTPUT_DIR="${SCRIPT_DIR}/dist"

echo "================================================================"
echo "NPU Profiler 独立分析工具打包脚本"
echo "================================================================"
echo_info "工作目录: ${WORK_DIR}"
echo_info "输出目录: ${OUTPUT_DIR}"
echo ""

# 1. 创建工作目录
echo_info "[1/6] 创建工作目录..."
mkdir -p "${WORK_DIR}"
mkdir -p "${OUTPUT_DIR}"

# 2. Clone torch_npu仓库
echo_info "[2/6] Clone torch_npu仓库..."
if [ -d "${TORCH_NPU_DIR}" ]; then
    echo_warn "目录已存在,跳过clone: ${TORCH_NPU_DIR}"
    echo_warn "如需重新clone,请删除该目录"
else
    echo_info "正在从 ${TORCH_NPU_REPO} clone..."
    git clone --depth=1 "${TORCH_NPU_REPO}" "${TORCH_NPU_DIR}"
    echo_info "Clone完成"
fi

# 2.5. Clone msprof仓库并编译
echo_info "[2.5/6] Clone msprof仓库并编译..."
if [ -d "${MSPROF_DIR}" ]; then
    echo_warn "msprof目录已存在,跳过clone: ${MSPROF_DIR}"
    echo_warn "如需重新clone,请删除该目录"
else
    echo_info "正在从 ${MSPROF_REPO} clone..."
    git clone --depth=1 "${MSPROF_REPO}" "${MSPROF_DIR}"
    echo_info "Clone完成"
fi

# 下载三方依赖包
echo_info "下载msprof三方依赖包..."
cd "${MSPROF_DIR}"
bash scripts/download_thirdparty.sh

# 编译解析包
# 编译解析包
echo_info "编译msprof解析包..."
# Apply patch to avoid OOM or high load in QEMU
if [ -f "${SCRIPT_DIR}/patches/msprof_build.patch" ]; then
    echo_info "应用msprof构建补丁..."
    cd "${MSPROF_DIR}"
    git apply "${SCRIPT_DIR}/patches/msprof_build.patch"
fi
cd "${MSPROF_DIR}"
bash build/build.sh --mode=analysis

# 检查编译产物
MSPROF_ANALYSIS_DIR="${MSPROF_DIR}/build/analysis/build/lib/analysis"
if [ ! -d "${MSPROF_ANALYSIS_DIR}" ]; then
    echo_error "msprof编译失败,未找到产物目录: ${MSPROF_ANALYSIS_DIR}"
    exit 1
fi

echo_info "msprof编译完成"

# 3. 执行create_standalone_profiler.py
echo_info "[3/6] 执行create_standalone_profiler.py..."

# 修改脚本中的路径配置
TEMP_SCRIPT="${WORK_DIR}/create_standalone_profiler_temp.py"
cp "${SCRIPT_DIR}/create_standalone_profiler.py" "${TEMP_SCRIPT}"

# 复制模板目录到工作目录
cp -r "${SCRIPT_DIR}/package_templates" "${WORK_DIR}/"

# 使用sed替换路径
sed -i.bak "s|ROOT_DIR = \".*\"|ROOT_DIR = \"${TORCH_NPU_DIR}/torch_npu\"|g" "${TEMP_SCRIPT}"
sed -i.bak "s|TARGET_DIR = \".*\"|TARGET_DIR = \"${STANDALONE_DIR}\"|g" "${TEMP_SCRIPT}"

# 执行脚本
python3 "${TEMP_SCRIPT}"

if [ ! -d "${STANDALONE_DIR}" ]; then
    echo_error "独立工具目录创建失败: ${STANDALONE_DIR}"
    exit 1
fi

# 3.5. 复制msprof产物到standalone目录
echo_info "[3.5/6] 复制msprof产物到standalone目录..."
MSPROF_TARGET_DIR="${STANDALONE_DIR}/analysis"
mkdir -p "${MSPROF_TARGET_DIR}"

# 复制analysis文件夹
echo_info "复制 ${MSPROF_ANALYSIS_DIR} 到 ${MSPROF_TARGET_DIR}/"
cp -r "${MSPROF_ANALYSIS_DIR}" "${MSPROF_TARGET_DIR}/"

# 验证msprof.py是否存在
MSPROF_PY_PATH="${MSPROF_TARGET_DIR}/analysis/msprof/msprof.py"
if [ ! -f "${MSPROF_PY_PATH}" ]; then
    echo_error "msprof.py未找到: ${MSPROF_PY_PATH}"
    exit 1
fi

# 复制 prefix 目录 (包含 libc_sec.so)
echo_info "复制 ${MSPROF_DIR}/prefix 到 ${STANDALONE_DIR}/prefix"
if [ -d "${MSPROF_DIR}/prefix" ]; then
    cp -r "${MSPROF_DIR}/prefix" "${STANDALONE_DIR}/prefix"
    echo_info "prefix 复制完成"
else
    echo_warn "prefix 目录未找到: ${MSPROF_DIR}/prefix"
fi

# 应用补丁：修改_cann_export.py以支持打包的msprof
echo_info "应用补丁到 _cann_export.py..."
CANN_EXPORT_FILE="${STANDALONE_DIR}/npu_profiler/analysis/prof_view/cann_parse/_cann_export.py"
if [ -f "${CANN_EXPORT_FILE}" ]; then
    python3 "${SCRIPT_DIR}/patch_cann_export.py" "${CANN_EXPORT_FILE}"
    if [ $? -ne 0 ]; then
        echo_error "补丁应用失败"
        exit 1
    fi
else
    echo_error "_cann_export.py 未找到: ${CANN_EXPORT_FILE}"
    exit 1
fi

# 应用补丁到 _cann_analyze.py
echo_info "应用补丁到 _cann_analyze.py..."
CANN_ANALYZE_FILE="${STANDALONE_DIR}/npu_profiler/analysis/prof_view/cann_parse/_cann_analyze.py"
if [ -f "${CANN_ANALYZE_FILE}" ]; then
    python3 "${SCRIPT_DIR}/patch_cann_analyze.py" "${CANN_ANALYZE_FILE}"
    if [ $? -ne 0 ]; then
        echo_error "补丁应用失败"
        exit 1
    fi
else
    echo_error "_cann_analyze.py 未找到: ${CANN_ANALYZE_FILE}"
    exit 1
fi

# 处理 _memory_timeline_parser.py (移除 torch 依赖)
echo_info "处理 _memory_timeline_parser.py..."
MEMORY_TIMELINE_FILE="${STANDALONE_DIR}/npu_profiler/analysis/prof_view/_memory_timeline_parser.py"
if [ -f "${MEMORY_TIMELINE_FILE}" ]; then
    python3 "${SCRIPT_DIR}/patch_remove_memory_timeline.py" "${MEMORY_TIMELINE_FILE}"
    if [ $? -ne 0 ]; then
        echo_error "处理失败"
        exit 1
    fi
else
    echo_error "_memory_timeline_parser.py 未找到: ${MEMORY_TIMELINE_FILE}"
    exit 1
fi


# 3.6. 重组目录结构
echo_info "[3.6/6] 重组目录结构..."
python3 "${SCRIPT_DIR}/reorganize_structure.py" "${STANDALONE_DIR}"

# 4. 生成打包文件(setup.py和README.md)
echo_info "[4/6] 生成打包文件..."
python3 "${SCRIPT_DIR}/generate_package_files.py" "${STANDALONE_DIR}"

# 5. 打包成whl
echo_info "[5/6] 打包成whl文件..."
cd "${STANDALONE_DIR}"

# 清理旧的构建文件
rm -rf build dist *.egg-info

# 构建whl包
python3 setup.py bdist_wheel

# 复制到输出目录
if [ -d "${STANDALONE_DIR}/dist" ]; then
    cp ${STANDALONE_DIR}/dist/*.whl "${OUTPUT_DIR}/"
    echo_info "whl包已复制到: ${OUTPUT_DIR}"
else
    echo_error "打包失败,未找到dist目录"
    exit 1
fi

# 显示结果
echo ""
echo "================================================================"
echo_info "✓ 打包完成!"
echo "================================================================"
echo ""
echo_info "输出文件:"
ls -lh "${OUTPUT_DIR}"/*.whl
echo ""
echo_info "安装命令:"
echo "  pip install ${OUTPUT_DIR}/ppa-*.whl"
echo ""
echo_info "使用示例:"
echo "  ppa /path/to/profiling_data"
echo "  ppa /path/to/profiling_data --max_process_number 8"
echo ""
