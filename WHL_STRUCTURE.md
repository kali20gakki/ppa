# WHL 包安装后的目录结构

## 概述

本文档详细说明 `ppa` whl 包安装后的目录结构，以及 `msprof.py` 的具体位置。
whl 包采用统一包结构，所有内容都位于 `ppa` 顶层包目录下。

## 安装位置

whl 包会被安装到 Python 的 site-packages 目录中。

## 完整目录结构

假设安装到 `/path/to/site-packages/`，完整结构如下：

```
/path/to/site-packages/
└── ppa/                            # 顶层包目录
    ├── __init__.py                # 包初始化
    ├── __main__.py                # 允许 python -m ppa 运行
    ├── cli.py                     # 命令行入口 (entry_points指向这里)
    ├── npu_profiler/               # 原始功能包
    │   ├── __init__.py
    │   ├── analysis/               # 分析模块
    │   │   ├── ...
    │   │   ...
    │   │   └── cann_parse/
    │   │       └── _cann_export.py # 被补丁修改的文件
    │   └── ...
    ├── analysis/                   # msprof 产物目录 ⭐
    │   └── analysis/               # msprof 编译产物
    │       ├── msprof/
    │       │   ├── msprof.py      # ⭐⭐⭐ msprof.py 的位置
    │       │   └── ...
    │       └── ...
    └── ...
└── ppa-1.0.0.dist-info/            # 包元数据
```

## msprof.py 的绝对路径

### 路径构成

```
<site-packages>/ppa/analysis/analysis/msprof/msprof.py
```

### 在代码中定位 msprof.py

在 `_cann_export.py` 中，通过向上查找 `cli.py` (包根目录标记) 来定位包根目录：

```python
def _get_bundled_msprof_path(self) -> str:
    """获取打包进来的msprof.py路径"""
    # 获取当前文件所在目录
    current_file = os.path.abspath(__file__)
    # 向上查找包根目录（包含cli.py的目录）
    package_root = current_file
    for _ in range(10):  # 最多向上查找10层
        package_root = os.path.dirname(package_root)
        # 查找根目录标记 cli.py
        root_marker = os.path.join(package_root, "cli.py")
        if os.path.exists(root_marker):
            # 找到包根目录，拼接相对路径
            bundled_path = os.path.join(package_root, "analysis/analysis/msprof/msprof.py")
            return bundled_path if os.path.exists(bundled_path) else ""
    return ""
```

## 目录层级关系

```
site-packages/
└── ppa/                          # 0 层 (包根目录, 包含 cli.py)
    ├── npu_profiler/             # 1 层
    │   └── analysis/             # 2 层
    │       └── prof_view/        # 3 层
    │           └── cann_parse/   # 4 层
    │               └── _cann_export.py # 5 层 (当前文件)
    └── analysis/                 # 1 层 (msprof 目录)
        └── analysis/             # 2 层
            └── msprof/           # 3 层
                └── msprof.py     # 4 层 (目标文件)
```

## 验证安装

```bash
# 验证 msprof.py 是否存在
python3 -c "
import os
import ppa
package_root = os.path.dirname(ppa.__file__) # 获取 ppa 包路径
msprof_path = os.path.join(package_root, 'analysis/analysis/msprof/msprof.py')
print('msprof.py 路径:', msprof_path)
print('文件存在:', os.path.exists(msprof_path))
"
```

## 运行时行为

1. **入口点**: `ppa` 命令指向 `ppa.cli:main`。
2. **执行流程**: 与之前相同，优先使用系统 msprof，否则使用打包版本。
3. **打包版本调用**: `subprocess.run(["python3", "/path/to/site-packages/ppa/analysis/analysis/msprof/msprof.py", ...])`
