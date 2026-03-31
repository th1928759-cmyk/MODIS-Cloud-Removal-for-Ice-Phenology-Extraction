import numpy as np

def calculate_phenology_vectorized(ice_bool_stack, window, thresh_low, thresh_high):
    """
    核心向量化算法：寻找满足条件的第一天
    """
    cumsum = np.pad(np.cumsum(ice_bool_stack, axis=0), ((1,0), (0,0), (0,0)), mode='constant')
    
    # 前 window 天的总和与后 window 天的总和
    past_sums = cumsum[window : -window] - cumsum[0 : -2*window]
    future_sums = cumsum[2*window :] - cumsum[window : -window]
    
    condition = (past_sums <= thresh_low) & (future_sums >= thresh_high)
    
    has_event = np.any(condition, axis=0)
    first_occurrence_idx = np.argmax(condition, axis=0)
    
    result_days = first_occurrence_idx + window + 1
    final_map = np.where(has_event, result_days, -9999).astype(np.int16)
    
    return final_map

def calculate_average_map(tif_files):
    """
    计算多年平均分布图，忽略无效的负值
    """
    import rasterio
    with rasterio.open(tif_files[0]) as src:
        meta = src.meta.copy()
        shape = src.shape
        sum_array = np.zeros(shape, dtype=np.float32)
        count_array = np.zeros(shape, dtype=np.float32)

    for f in tif_files:
        with rasterio.open(f) as src:
            data = src.read(1).astype(np.float32)
            valid_mask = data >= 0
            sum_array[valid_mask] += data[valid_mask]
            count_array[valid_mask] += 1

    avg_array = np.full(shape, -9999.0, dtype=np.float32)
    valid_pixels = count_array > 0
    avg_array[valid_pixels] = sum_array[valid_pixels] / count_array[valid_pixels]
    
    return avg_array, meta
