import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
from matplotlib.colors import ListedColormap
from matplotlib import rcParams
import pandas as pd
import cmaps
from cmaps import WhiteBlueGreenYellowRed
import matplotlib

# 设置默认字体
plt.rcParams['font.family'] = 'Times New Roman'

# 定义变量、标题、单位和色条范围
titles = [
    "(a) Downward Longwave Radiation",
    "(b) Downward Shortwave Radiation",
    "(c) Precipitation",
    "(d) Specific Humidity",
    "(e) Air temperature",
    "(f) Wind Speed"
]
vars = ["dlwrf", "dswrf", "prec", "spfh", "tmp", "wind"]
units = ["W/m²", "W/m²", "mm/day", "g/kg", "K", "m/s"]
vmax = [450, 300, 10, 20, 300, 10]
vmin = [180, 0, 0, 0, 250, 0]
ticks = [
    np.linspace(vmin[0], vmax[0], 11),
    np.linspace(vmin[1], vmax[1], 11),
    np.linspace(vmin[2], vmax[2], 11),
    np.linspace(vmin[3], vmax[3], 11),
    np.linspace(vmin[4], vmax[4], 11),
    np.linspace(vmin[5], vmax[5], 11),
]
boundaries = [
    np.linspace(vmin[0], vmax[0], 11),
    np.linspace(vmin[1], vmax[1], 11),
    np.linspace(vmin[2], vmax[2], 11),
    np.linspace(vmin[3], vmax[3], 11),
    np.linspace(vmin[4], vmax[4], 11),
    np.linspace(vmin[5], vmax[5], 11),
]

# 读取 CSV 文件
csv_path = '/media/zhwei/data01/weizx/forcing_DAY/pvalue/ind/fdr/proportion_list.csv'
try:
    df = pd.read_csv(csv_path)
    # 创建变量到 proportion_passed_fdr 的映射（百分比）
    proportion_dict = dict(zip(df['variable'], df['proportion_passed_fdr'] * 100))
except FileNotFoundError:
    print(f"错误: CSV 文件未找到: {csv_path}")
    exit(1)
except Exception as e:
    print(f"读取 CSV 错误: {e}")
    exit(1)

# 检查 CSV 是否包含所有变量
missing_vars = [var for var in vars if var not in proportion_dict]
if missing_vars:
    print(f"警告: CSV 中缺少以下变量: {missing_vars}")
    # 为缺失变量设置默认值（0%）
    for var in missing_vars:
        proportion_dict[var] = 0

# 创建子图
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(40, 28), subplot_kw={'projection': ccrs.PlateCarree()})

for i, ax in enumerate(axs.flat):
    # 读取平均值的数据
    if i == 3:  # spfh 单位转换 kg/kg -> g/kg
        data_std = xr.open_dataset(f'/media/zhwei/data01/weizx/forcing_DAY/mean_mean/{vars[i]}.nc')['le'].squeeze() * 1000
    else:
        data_std = xr.open_dataset(f'/media/zhwei/data01/weizx/forcing_DAY/mean_mean/{vars[i]}.nc')['le'].squeeze()
    
    dif_std = np.flipud(data_std)
    lon = data_std.lon
    lat = data_std.lat

    # 绘制图像
    im = ax.imshow(dif_std, cmap=WhiteBlueGreenYellowRed, 
                   vmin=vmin[i], vmax=vmax[i],
                     extent=[-180, 180, -60, 90])  
    # 添加标题、比例和单位
    ax.set_title(f"{titles[i]}", fontsize=55, transform=ax.transAxes, loc="left")

    ax.text(1.02, 0.98, f'{units[i]}', fontsize=55, transform=ax.transAxes, ha="left")
    
    # 添加海岸线
    ax.coastlines(linewidth=2, color='k')
    
    # 添加色条
    cbar = plt.colorbar(im, 
                        ticks=ticks[i][::2], boundaries=boundaries[i], 
                        orientation='vertical', pad=0.01, shrink=0.6, extend="both", ax=ax)
    cbar.ax.tick_params(labelsize=50, width=2, length=7)
    
    # 设置边框线宽
    for spine in ax.spines.values():
        spine.set_linewidth(3)

# 调整子图间距
plt.subplots_adjust(wspace=0.02, hspace=-0.15)

# 保存图像
plt.savefig('/media/zhwei/data01/weizx/forcing_DAY/FigS1_fdr_mean.jpg', format='jpg', dpi=300, bbox_inches='tight')
print('出图完毕')