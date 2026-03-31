import datetime
import numpy as np
from osgeo import gdal, ogr
from .constants import CLOUD_VALUES, NODATA_VALUE

def get_ice_phenology_days(start_year):
    """定义冰物候年：从11月1日开始的242天"""
    start_date = datetime.date(start_year, 11, 1)
    return [start_date + datetime.timedelta(days=i) for i in range(242)]

def create_shp_mask(ref_tif_path, shp_path):
    """将 SHP 文件栅格化，生成布尔掩膜矩阵"""
    ref_ds = gdal.Open(str(ref_tif_path))
    if ref_ds is None: return None
    
    x_size = ref_ds.RasterXSize
    y_size = ref_ds.RasterYSize
    geo_transform = ref_ds.GetGeoTransform()
    projection = ref_ds.GetProjection()
    
    mem_driver = gdal.GetDriverByName('MEM')
    mask_ds = mem_driver.Create('', x_size, y_size, 1, gdal.GDT_Byte)
    mask_ds.SetGeoTransform(geo_transform)
    mask_ds.SetProjection(projection)
    
    shp_ds = ogr.Open(str(shp_path))
    if shp_ds is None: raise FileNotFoundError(f"无法打开 SHP: {shp_path}")
    layer = shp_ds.GetLayer()
    
    gdal.RasterizeLayer(mask_ds, [1], layer, burn_values=[1])
    mask_array = mask_ds.GetRasterBand(1).ReadAsArray()
    
    ref_ds, mask_ds, shp_ds = None, None, None
    return mask_array == 1 

def calculate_masked_cloud_fraction(file_path, lake_mask):
    """根据给定的 SHP 掩膜计算云占比"""
    if not file_path.exists(): return None
    try:
        ds = gdal.Open(str(file_path))
        if ds is None: return None
        b2 = ds.GetRasterBand(2).ReadAsArray()
        
        valid_pixels_mask = lake_mask & (b2 != NODATA_VALUE)
        valid_count = np.sum(valid_pixels_mask)
        if valid_count == 0: return 0.0
            
        cloud_pixels_mask = np.isin(b2, CLOUD_VALUES) & valid_pixels_mask
        cloud_count = np.sum(cloud_pixels_mask)
        
        return round((cloud_count / valid_count) * 100, 2)
    except Exception as e:
        print(f"读取异常 {file_path.name}: {e}")
        return None
