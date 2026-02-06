
#使用openbench的环境
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import dates, ticker
import matplotlib.path as mpath
from matplotlib.colors import ListedColormap
from matplotlib import rcParams
import cartopy.crs as ccrs
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib
import matplotlib.pyplot as plt

time_start = '2001-01'
time_end = '2010-12'

# 设置绘图参数
plt.rcParams['font.family'] = 'Times New Roman'
colorbar_ticklabel_size = 40
text_size = 50
unit_size = 40
title_size = 50

titles = ['(a) Downward Longwave Radiation','(b) Downward Shortwave Radiation','(c) Precipitation','(d) Specific Humidity','(e) Air Temperature', '(f) Wind Speed']
# titles_line = ["LH", "SH", "Rn", "Tro"]
# names =["le","sh","rns","mrro"]
# units =["W/m²","W/m²","g/kg","mm/day",'K','m/s']
vmax=[0.4,0.8,1,0.4,0.6,0.6]
vmin=[-0.4,-0.8,-1,-0.4,-0.6,-0.6]
ticks = [
    np.linspace(vmin[0], vmax[0], 13),
    np.linspace(vmin[1], vmax[1], 13),
    np.linspace(vmin[2], vmax[2], 13),
    np.linspace(vmin[3], vmax[3], 13),
    np.linspace(vmin[4], vmax[4], 13),
    np.linspace(vmin[5], vmax[5], 13),

]
boundaries = [
    np.linspace(vmin[0], vmax[0], 13),
    np.linspace(vmin[1], vmax[1], 13),
    np.linspace(vmin[2], vmax[2], 13),
    np.linspace(vmin[3], vmax[3], 13),
    np.linspace(vmin[4], vmax[4], 13),
    np.linspace(vmin[5], vmax[5], 13),

]

fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(40, 27), subplot_kw={'projection': ccrs.PlateCarree()})

folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison//Evaluation_forcing/output/comparisons/Diff_Plot'
var = ['Surface_Downward_LW_Radiation','Surface_Downward_SW_Radiation','Precipitation','Surface_Specific_Humidity','Surface_Air_Temperature','Surface_Wind_Speed']
ref_data = ['CLARA_3', 'CLARA_3','MSWEP_0p25','MSWX_0p25','CRU-TS4.08','ERA5LAND_0p25']

for i, ax in enumerate(axs.flat):
    data1 = xr.open_dataset(f'{folder_path}/{var[i]}_ref_{ref_data[i]}_JRA3Q_0.25_vs_JRA55_0.25_KGESS_diff.nc')['KGESS_diff']
    data = np.flipud(data1)
    im = ax.imshow(data, cmap='RdBu_r',
                    vmin=vmin[i], vmax=vmax[i],
                      extent=[-180, 180, -60, 90])
    cbar = plt.colorbar(im, 
                        ticks=ticks[i][::3], boundaries=boundaries[i],
                          orientation='vertical', pad=0.01, shrink=0.7, extend="both", ax=ax)
    cbar.ax.tick_params(labelsize=50, width=2, length=7)
    ax.coastlines(linewidth=2)
    ax.set_facecolor('white')
    ax.set_title(f"{titles[i]}", fontsize=50, transform=ax.transAxes, loc="left")
    # ax.text(1.037, 1.0, f'{units[i]}', fontsize=50, transform=ax.transAxes, ha="left")
    for spine in ax.spines.values():
        spine.set_linewidth(3)
plt.subplots_adjust(wspace=-0.02, hspace=-0.15)
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Figure2_forcing_KGESS_diff.jpg', format='jpg', dpi=300, bbox_inches='tight')
