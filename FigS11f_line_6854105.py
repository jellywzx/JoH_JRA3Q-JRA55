import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.font_manager import FontProperties

# 设置默认字体和绘图参数
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.sans-serif': ['Times New Roman', 'SimHei'],
    'font.size': 15,
    'axes.labelsize': 12,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'legend.frameon': False,
    'axes.unicode_minus': False,
    'grid.linewidth': 0.2,
    'savefig.bbox': 'tight'
})

folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/streamflow_stnplot/'
# 定义文件路径和标签
file_paths = [
   folder_path+'/JRA3Q/Streamflow_ref_6854105_2001_2010.nc',
   folder_path+'/JRA3Q/Streamflow_sim_6854105_2001_2010.nc',
   folder_path+'/JRA55/Streamflow_sim_6854105_2001_2010.nc',
]
names = ['ref','JRA3Q', 'JRA55',]
titles = names  # 图例使用 names
markers = ['o', 's','^']
colors = ['black', 'steelblue', 'palevioletred']

x_values = range(1, 121)  # 120 个月
xtick_positions = [1 + i * 12 for i in range(10)] + [121]  # 每年的第一个月（2001-2010）加 2011
xtick_labels = [str(year) for year in range(2001, 2011)] + ['2011']
# 创建图形和轴
fig, ax = plt.subplots(figsize=(22, 10.5))

# 绘制折线图
for i in range(3):
    # 读取 NetCDF 文件
    if i == 0:
        data = xr.open_dataset(file_paths[i])['discharge'][:, 0, 0]
        ax.plot(x_values, data, 
                marker=markers[i], 
                linestyle='dashed', 
                markersize=10, label=names[i], linewidth=3, color=colors[i])

    else:
        data = xr.open_dataset(file_paths[i])['outflw'][:, 0, 0]
        ax.plot(x_values, data, 
                marker=markers[i],
                linestyle='solid', 
                markersize=10, label=names[i], linewidth=3, color=colors[i])

# 设置轴样式
ax.set_xticks(xtick_positions)
ax.set_xticklabels(xtick_labels, fontsize=50, rotation=30)
ax.set_yticks(np.linspace(0,150,11)[::2])
ax.tick_params(axis='both', labelsize=50, which='both', direction='out', length=6, width=1.5)
ax.set_ylabel('Discharge (m³/s)', fontproperties=FontProperties(size=50))

for spine in ax.spines.values():
    spine.set_linewidth(1.5)

ax.grid(True, linestyle='--', alpha=0.4, color='gray', linewidth=0.5)
ax.legend(bbox_to_anchor=(0, 1), loc='upper left', fontsize=50, ncol=3)

# 添加文本
ax.text(0, 1.05, '(f) Station ID: 6854105 (Lat: 60.88°N, Lon: 22.88°E)', fontsize=50, ha='left', transform=ax.transAxes)
ax.text(0.23, 0.7, 'RMSE: 11.53\nR: 0.85\nKGESS: 0.83', fontsize=40, ha="left", color = 'steelblue',  transform=ax.transAxes)
ax.text(0.55, 0.7, 'RMSE: 16.09\nR: 0.80\nKGESS: 0.68', fontsize=40, ha="left", color = 'palevioletred',  transform=ax.transAxes)
ax.text(0.85, 0.8, 'Europe',fontsize=60, ha="left",color = 'black', transform=ax.transAxes)
# 调整布局并保存
plt.subplots_adjust( right=0.95, top=0.95, bottom=0.05)
plt.savefig(folder_path+'/6854105.jpg', format='jpg', dpi=300)
