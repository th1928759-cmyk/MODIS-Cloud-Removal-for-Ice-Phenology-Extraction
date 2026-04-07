import os
import re
import rasterio
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, cohen_kappa_score, f1_score # 新增 f1_score
from .constants import CLOUD_VALUES

# ... (保留前面的 build_result_index, build_raw_index, check_cloud_status, extract_prediction 函数不变) ...

def plot_cm(y_true, y_pred, title, ax=None):
    """绘制单幅混淆矩阵及精度指标 (新增 F1-score)"""
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    oa = accuracy_score(y_true, y_pred)
    kappa = cohen_kappa_score(y_true, y_pred)
    
    # === 新增：计算 F1-score ===
    # pos_label=0 代表水，pos_label=1 代表冰。zero_division=0 防止某类完全缺失时报错
    f1_water = f1_score(y_true, y_pred, pos_label=0, zero_division=0) 
    f1_ice = f1_score(y_true, y_pred, pos_label=1, zero_division=0)
    macro_f1 = (f1_water + f1_ice) / 2.0
    
    if ax is None:
        plt.figure(figsize=(6, 5))
        ax = plt.gca()
        
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Water', 'Ice'], yticklabels=['Water', 'Ice'])
    
    # 在标题中展示丰富的精度指标
    title_str = (f'{title}\n'
                 f'OA={oa:.1%} | Kappa={kappa:.3f}\n'
                 f'F1-Water={f1_water:.3f} | F1-Ice={f1_ice:.3f} | Macro={macro_f1:.3f}')
    
    ax.set_title(title_str, fontsize=10, pad=10)
    ax.set_xlabel('MODIS Prediction')
    ax.set_ylabel('Sentinel-1 Truth')
    
    # 将指标返回，以便主程序在控制台打印
    return oa, kappa, f1_water, f1_ice, macro_f1
