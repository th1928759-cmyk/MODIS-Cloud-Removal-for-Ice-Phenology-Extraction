#  🛰️☁️🧊 基于MODIS去云算法的湖冰物候提取

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![GDAL](https://img.shields.io/badge/GDAL-3.0%2B-green)
![Rasterio](https://img.shields.io/badge/Rasterio-1.2%2B-green)
![License](https://img.shields.io/badge/License-MIT-orange)

高纬度大型湖泊（例如贝加尔湖）在冬春季节经常被厚厚的云层遮挡，导致传统光学遥感（如 MODIS）很难获取连续、清晰的冰面观测数据，影响到时间精度要求高的物候提取。本项目通过对MODIS积雪产品进行去云处理，从而提取湖冰物候。

本项目提供了一套完整处理流程：从**原始影像的云量评估**，到**时空双向去云重构**，再到**时序/空间物候参数提取**，最后利用 Sentinel-1 微波雷达数据进行**高精度交叉验证**。整个流程高度模块化，数据与代码严格分离，开箱即用。

同时，请注意，**本项目的工程架构重构、部分代码与文档编写借助 AI 辅助完成**。请在使用或参考核心算法应用于其他研究区时，结合实际情况自行复核代码逻辑并进行参数微调。



## ✨ 核心内容

- **☁️ 递进式时空去云算法**：不依赖复杂的深度学习模型，直接结合“双星合成 (Terra+Aqua)”、严格的“双向时序平滑”与“ 3×3 空间滤波”，稳健重构连续无云的每日湖冰状态。
- **📈 稳健的时序物候提取**：结合季节性物理去噪、中值滤波与 Savitzky-Golay (SG) 平滑，应用不可逆阈值判定逻辑，精确提取全湖四大关键物候节点：FUS (Freeze Up Start)、FUE (Freeze Up End)、BUS (Break Up Start)、BUE (Break Up End)；以及四大物候时段：FUD (Freeze Up Duration)、BUD (Break Up Duration)、ICD (Ice Cover Duration)、CFD (Completely Frozen Duration)。
- **🗺️ 高效的空间格局制图**：抛弃了缓慢的循环遍历，底层全部采用 Numpy 矩阵向量化运算，几十秒内即可输出逐年及多年平均的 FU (Freeze-up) 和 BU (Break-up) 像素级空间分布图。
- **✅ 严谨的 SAR 交叉验证**：内置真值坐标投影转换与混淆矩阵评估模块，利用不受云层影响的 Sentinel-1 雷达数据，硬核验证光学去云算法的准确性。


## 🚀 处理流程
- **Step 0: 准备原始数据**
进入 data/2024/ (或其他年份文件夹)，阅读里面的 readme.txt。
使用提供的 GEE 脚本下载对应年份的 MOD10A1 和 MYD10A1 影像，并直接放在该年份文件夹下。
确保 data/range/ 下有贝加尔湖的 Shapefile 掩膜文件。

- **Step 1: 时空去云处理 (Cloud Removal)**
融合双星数据，并用时空平滑算法填补云层空缺。
输出: 连续无云的每日 .tif 重构影像将自动存入 data/result/{Year}/。

- **Step 2: 时序物候提取 (Temporal Phenology Extraction)**
提取全湖宏观的关键物候节点及持续时长 (ICD, CFD, FUD, BUD)，并生成平滑曲线。
(注：运行前请确保你已经统计出了每日覆盖率的 CSV 文件)
输出: 时序平滑曲线与物候节点散点图保存至 data/plots/。

- **Step 3: 空间物候制图 (Spatial Phenology Mapping)**
生成每个像素的结冰 (FU) 与融冰 (BU) 绝对日期及多年均态分布图。
输出: .tif 格式的地理空间产品保存至 data/result/spatial_products/。

- **Step 4: 精度评价与验证 (Validation & Assessment)**
评估原始影像到底有多少云，并基于 Sentinel-1 真值生成混淆矩阵。    
输出: 精度验证明细 CSV 与图表保存至 data/result/validation/ 与 data/plots/。

🌍 关于地面真值 (Ground Truth)
由于缺乏大范围的实地观测，我们在 Google Earth Engine (GEE) 设计了 Sentinel-1 SAR 交互式判读与均衡采样工具，用于人工目视解译获取可靠的冰水真值。

## 🛠 环境依赖
本项目主要基于 Python 构建。建议使用 conda 或 venv 创建独立环境，确保安装以下核心地理空间数据科学库：
- `numpy / scipy / pandas`
- `gdal / rasterio` (用于遥感影像的读写与处理)
- `geopandas / shapely` (用于矢量边界处理)
- `matplotlib` (用于时序曲线可视化)


## 📂 项目架构 

代码库采用了“主程序 + `core/` 核心工具箱”的结构，分为四大执行模块。所有数据流转均在 `data/` 目录中自动闭环。

```text
📦 MODIS-Cloud-Removal-for-Ice-Phenology-Extraction
├── 📂 Cloud Removal/                 # 核心去云与分类模块
│   ├── main.py                       # 去云处理流水线主入口
│   └── 📂 core/                      # 算法核心库
│       ├── classify.py               # 冰/水像元状态判别与分类逻辑
│       ├── constants.py              # 阈值与环境常量配置
│       ├── smooth.py                 # 时序平滑与噪声去除算法
│       └── utils.py                  # 基础辅助工具函数
│
├── 📂 Phenology Extraction/          # 湖冰物候时序提取模块
│   ├── main.py                       # 物候提取主入口
│   ├── phenology.py                  # 核心物候指标（FUS/FUE/BUS/BUE）计算算法
│   ├── plotting.py                   # 像元级时间序列曲线可视化与制图
│   └── processing.py                 # 时序数据的清洗与重组
│
├── 📂 Phenology Distribution Mapping/# 空间分布与制图模块
│   ├── generate_annual_maps.py       # 生成单年度的物候空间分布图
│   ├── calculate_average_maps.py     # 计算并生成多年平均物候分布图
│   └── 📂 core/                      
│       ├── algorithms.py             # 空间统计与制图算法
│       ├── constants.py              # 制图常量与样式配置
│       └── io_utils.py               # 栅格影像读写辅助工具
│
├── 📂 Validation & Assessment/       # 结果验证与精度评估模块
│   ├── accuracy_assessment.py        # 综合精度评估主入口
│   ├── eval_cloud_fraction.py        # 云量统计与去云效果评估程序
│   ├── project_ground_truth.py       # 真值数据的坐标投影转换与匹配
│   └── 📂 core/                      
│       ├── cloud_utils.py            # 云掩膜(Cloud Mask)处理工具
│       ├── constants.py              # 评估阈值与常量配置
│       └── validation_utils.py       # 评估指标（如RMSE, MAE等）计算算法
│
└── 📂 data/                          # 数据集与脚本存储
    ├── 📂 2024/                      # 样例年度(2024)数据与获取脚本
    │   ├── MOD10A1.js                # GEE平台获取 Terra MODIS 数据脚本
    │   └── MYD10A1.js                # GEE平台获取 Aqua MODIS 数据脚本
    ├── 📂 ground_truth/              # Sentinel-1 地面验证数据集
    │   ├── GEE_Sentinel1_Sampling.js # GEE平台 Sentinel-1 采样与导出脚本
    │   ├── S1_GroundTruth_Projected.csv # 投影后的 Sentinel-1 真值采样点数据
    │   └── 📂 raw_exports/           # 存放GEE原始导出的csv/shp结果
    └── 📂 range/                     # 空间范围与矢量边界
        └── Baikal_Lake_Boundary.*    # 贝加尔湖水体边界 Shapefile 集合 (shp, shx, dbf, prj 等)
```

## 🤝 贡献与反馈
如果你在复现过程中遇到任何路径解析或环境配置的问题，欢迎提交 Issue。如果你觉得这个项目对你的RS/GIS研究有启发，不妨点个STAR ⭐️ 鼓励支持一下！
