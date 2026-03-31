# 原始遥感影像获取指南 (Raw Data Acquisition)

**这是一个示例文件夹！**本文件夹用于存放贝加尔湖冰情物候提取项目所需的原始 MODIS 每日积雪产品数据（Terra 卫星的 `MOD10A1` 与 Aqua 卫星的 `MYD10A1`）。

由于原始遥感影像体积庞大，我们未将 `.tif` 影像文件直接上传至 GitHub 仓库。请使用本目录下提供的 Google Earth Engine (GEE) 脚本自行下载所需年份的数据。

## 📁 目录内容
- `readme.md`：本数据获取说明文档。
- `MOD10A1.js`：用于下载 Terra 卫星每日数据的 GEE 脚本。
- `MYD10A1.js`：用于下载 Aqua 卫星每日数据的 GEE 脚本。
- `*.tif` (待下载)：由 GEE 导出的每日原始影像。

## ⚙️ 影像规格说明
本仓库的去云算法（Cloud Removal）依赖于特定的波段和坐标系，GEE 脚本已为您自动配置好以下参数：
- **波段组合**：
  - Band 1: `NDSI_Snow_Cover` (用于提取冰/水)
  - Band 2: `NDSI_Snow_Cover_Class` (用于提取云掩膜)
- **空间分辨率**：500 米
- **坐标系**：EPSG:32648 (WGS 84 / UTM zone 48N)
- **命名规范**：`MOD10A1_YYYYMMDD.tif` 和 `MYD10A1_YYYYMMDD.tif`

## 🚀 下载步骤

### 1. 准备工作
请确保您拥有访问 [Google Earth Engine Code Editor](https://code.earthengine.google.com/) 的权限，以及足够的 Google Drive 存储空间。

### 2. 修改目标日期
使用文本编辑器打开 `MOD10A1.js` 和 `MYD10A1.js`。
找到代码中的时间过滤条件（默认可能为 `2019-10-24` 到 `2019-11-01`）：
```javascript
.filter(ee.Filter.date('2019-10-24', '2019-11-01'))
