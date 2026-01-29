#!/usr/bin/env python3
"""
NPU Profiler 独立分析工具打包配置
"""
from setuptools import setup, find_packages
import os

# 读取README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "NPU Profiler 离线分析工具"

setup(
    name="npu-profiler-analyser",
    version="1.0.0",
    author="Ascend",
    author_email="",
    description="NPU Profiler 离线分析工具 - 独立运行,无需torch_npu环境",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://gitcode.com/Ascend/pytorch",
    packages=find_packages(),
    py_modules=['analyse'],  # 包含根目录的analyse.py
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.7",
    install_requires=[
        # 基础依赖
        "numpy",
        "pandas",
        # 可选:如果需要数据库导出功能
        # "sqlalchemy",
    ],
    entry_points={
        'console_scripts': [
            'npu-profiler-analyse=analyse:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
