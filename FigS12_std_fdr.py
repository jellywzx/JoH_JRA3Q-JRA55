import numpy as np
import xarray as xr
import pandas as pd
import math
import glob
# from pylab import *
import matplotlib.dates as mdates
from matplotlib import dates, ticker
import matplotlib.pyplot as plt
import matplotlib.path as mpath
# from scipy import stats
# from scipy.stats import t
# import scipy.signal as signal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import cmaps
# from mpl_toolkits.basemap import Basemap, shiftgrid
from matplotlib.colors import ListedColormap
from matplotlib import rcParams
import subprocess
import cartopy.crs as ccrs
from cmaps import WhiteYellowOrangeRed
import matplotlib.font_manager as fm
import os
import shutil



time_start = '2001-01'
time_end = '2010-12'

cache_dir = os.path.expanduser('~/.cache/matplotlib')
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
plt.rcParams['font.family'] = 'Times New Roman'

# 设置绘图参数
params = {
    'backend': 'ps',
    'axes.labelsize': 12,
    'grid.linewidth': 0.2,
    'font.size': 15,
    'legend.fontsize': 40,
    'legend.frameon': False,
    'xtick.labelsize': 20,
    'xtick.direction': 'out',
    'ytick.labelsize': 20,
    'ytick.direction': 'out',
    'savefig.bbox': 'tight',
    'axes.unicode_minus': False,
    'text.usetex': False
}
rcParams.update(params)

titles = ["(a) Donward Longwave Radiation", "(b) Donward Shortwave Radiation", "(c) Precipitation", "(d) Vapor Pressure Deficit", ]
units =["W/m²","W/m²","mm/s",'hPa']
vmax=[15,20,4,4,]
# vmin=[-20,-20,-2,-4,-2,-3]
vmin=[0,0,0,0,]
ticks = [
    np.linspace(vmin[0], vmax[0], 11),
    np.linspace(vmin[1], vmax[1], 11),
    np.linspace(vmin[2], vmax[2], 11),
    np.linspace(vmin[3], vmax[3], 11),
    # np.linspace(vmin[4], vmax[4], 11),
    # np.linspace(vmin[5], vmax[5], 11),    
]
boundaries = [
    np.linspace(vmin[0], vmax[0], 21),
    np.linspace(vmin[1], vmax[1], 21),
    np.linspace(vmin[2], vmax[2], 21),
    np.linspace(vmin[3], vmax[3], 21),
    # np.linspace(vmin[4], vmax[4], 21),
    # np.linspace(vmin[5], vmax[5], 21), 
]

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(50, 20), subplot_kw={'projection': ccrs.PlateCarree()})

for i, ax in enumerate(axs.flat):

    if i == 0:
        dlwrf_std_mean = xr.open_dataset('/media/zhwei/data01/weizx/forcing_DAY/stdmean/dlwrf_stdmean.nc')['std_mean']
        data = np.flipud(dlwrf_std_mean)

    if i == 1:
        dswrf_std_mean = xr.open_dataset('/media/zhwei/data01/weizx/forcing_DAY/stdmean/dswrf_stdmean.nc')['std_mean']
        data = np.flipud(dswrf_std_mean)

    if i == 2:
        tprat_std_mean = xr.open_dataset('/media/zhwei/data01/weizx/forcing_DAY/stdmean/prec_stdmean.nc')['std_mean']
        data = np.flipud(tprat_std_mean)

    if i == 3:
        vpd_std_mean = xr.open_dataset('/media/zhwei/data01/weizx/forcing_DAY/stdmean/vpd_stdmean.nc')['std_mean']
        data = np.flipud(vpd_std_mean)

    im = ax.imshow(data, cmap=WhiteYellowOrangeRed, vmin=vmin[i], vmax=vmax[i], extent=[-180, 180, -60, 90])
    cbar = plt.colorbar(im, ticks=ticks[i][::2], boundaries=boundaries[i], orientation='vertical', pad=0.01, shrink=0.8, extend="both", ax=ax)
    cbar.ax.tick_params(labelsize=65, width=2, length=7)
    ax.coastlines(linewidth=2)
    ax.set_facecolor('white')
    ax.set_title(f"{titles[i]}", fontsize=60, transform=ax.transAxes, loc="left")
    # ax.text(0.003, 0.1, f"{titles[i]}", fontsize=60, transform=ax.transAxes, ha="left") 
    ax.text(1.037, 1.0, f'{units[i]}', fontsize=60, transform=ax.transAxes, ha="left")
    for spine in ax.spines.values():
        spine.set_linewidth(3)
plt.subplots_adjust(wspace=-0.02, hspace=0)
plt.savefig('/media/zhwei/data01/weizx/forcing_DAY/FigS12.jpg', dpi=300, bbox_inches='tight')
