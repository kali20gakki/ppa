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
STANDALONE_DIR="${WORK_DIR}/npu_profiler_standalone"
OUTPUT_DIR="${SCRIPT_DIR}/dist"

echo "================================================================"
echo "NPU Profiler 独立分析工具打包脚本"
echo "================================================================"
echo_info "工作目录: ${WORK_DIR}"
echo_info "输出目录: ${OUTPUT_DIR}"
echo ""

# 1. 创建工作目录
echo_info "[1/5] 创建工作目录..."
mkdir -p "${WORK_DIR}"
mkdir -p "${OUTPUT_DIR}"

# 2. Clone torch_npu仓库
echo_info "[2/5] Clone torch_npu仓库..."
if [ -d "${TORCH_NPU_DIR}" ]; then
    echo_warn "目录已存在,跳过clone: ${TORCH_NPU_DIR}"
    echo_warn "如需重新clone,请删除该目录"
else
    echo_info "正在从 ${TORCH_NPU_REPO} clone..."
    git clone --depth=1 "${TORCH_NPU_REPO}" "${TORCH_NPU_DIR}"
    echo_info "Clone完成"
fi

# 3. 执行create_standalone_profiler.py
echo_info "[3/5] 执行create_standalone_profiler.py..."

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

# 4. 生成打包文件(setup.py和README.md)
echo_info "[4/5] 生成打包文件..."
python3 "${SCRIPT_DIR}/generate_package_files.py" "${STANDALONE_DIR}"

# 5. 打包成whl
echo_info "[5/5] 打包成whl文件..."
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
echo "  pip install ${OUTPUT_DIR}/npu-profiler-analyser-*.whl"
echo ""
echo_info "使用示例:"
echo "  npu-profiler-analyse /path/to/profiling_data"
echo "  npu-profiler-analyse /path/to/profiling_data --max_process_number 8"
echo ""
