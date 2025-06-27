# TENG Data Processor

**TENG Data Processor** 是一款用于信号处理的图形化可视化工具，支持批量导入、信号预处理与时频分析，适用于科研数据分析与算法开发。

## ✨ 功能特性

- 支持批量导入 CSV 格式的 TENG 信号数据
- 提供信号的基线矫正、去噪、滤波等预处理功能
- 可视化展示每个步骤处理后的信号效果
- 支持 FFT、STFT、CWT 等时频分析方法
- 可视化图形用户界面（GUI）友好易用

## 🛠 安装方法

```bash
git clone https://github.com/waytohill/TENG-data-processor.git
cd TENG-data-processor
pip install -r requirements.txt
python -m teng_data_processor.main

```

> 推荐使用 Python 3.8+ 环境运行本项目。

## 🚀 快速使用

1. 启动软件：`python -m teng_data_processor.main`
2. 加载 CSV 文件（需包含 Time 和 Data 两列）
3. 选择并应用处理流程，查看图形化处理效果

## 📁 项目结构说明

```bash
TENG-data-processor/
├── teng_data_processor/    # 核心程序包
├── examples/               # 示例数据与用法
├── tests/                  # 单元测试
├── README.md               # 项目说明
├── setup.py                # 安装脚本
├── requirements.txt        # 依赖列表
└── LICENSE                 # 开源许可证

```

## 📄 开源协议

本项目使用 MIT License。
