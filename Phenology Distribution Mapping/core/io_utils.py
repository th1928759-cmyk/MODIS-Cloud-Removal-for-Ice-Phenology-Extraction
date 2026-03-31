import os
import glob
import re
import rasterio
import numpy as np

def get_sorted_tif_files(year_dir):
    """获取指定年份文件夹下按时间排序的 TIF 文件"""
    if not os.path.exists(year_dir):
        return []
    files = glob.glob(os.path.join(year_dir, "*.tif"))
    def get_date(f):
        match = re.search(r'(\d{8})', os.path.basename(f))
        return match.group(1) if match else "00000000"
    files.sort(key=get_date)
    return files

def load_data_cube(files, nodata_val):
    """读取所有 TIF 构建 3D 矩阵"""
    if not files: return None, None, None
    with rasterio.open(files[0]) as src:
        profile = src.profile.copy()
        h, w = src.height, src.width
        valid_mask = (src.read(1) != nodata_val)

    stack = np.zeros((len(files), h, w), dtype=np.uint8)
    for i, f in enumerate(files):
        with rasterio.open(f) as src:
            stack[i] = src.read(1)
            
    return stack, profile, valid_mask

def save_geotiff(data, out_path, profile, dtype='int16', nodata=-9999):
    """保存为 GeoTIFF"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    meta = profile.copy()
    meta.update({
        'dtype': dtype,
        'nodata': nodata,
        'count': 1,
        'compress': 'lzw'
    })
    with rasterio.open(out_path, 'w', **meta) as dst:
        dst.write(data, 1)
