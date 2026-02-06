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

# from scipy import stats
# from scipy.stats import t
# import scipy.signal as signal
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
# import cmaps
# from mpl_toolkits.basemap import Basemap, shiftgrid
# from cmaps import WhiteYellowOrangeRed
# import pandas as pd
# import math
# import glob
# # from pylab import *
# import subprocess

time_start = '2001-01'
time_end = '2010-12'

#region 开始作图
# 设置默认字体
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

titles = ["(a) Downward Longwave Radiation",
         "(b)  Downward Shortwave Radiation", 
         "(c) Precipitation", 
         "(d) Specific Humidity", 
         "(e) Air Temperature",
         "(f) Wind Speed"]
# titles = ["(a) dlwrf", "(b) dswrf", "(c) spfh", "(d) tprat", "(e) t2m", "(f) ws"]
# titles_line = ["LH", "SH", "Rn", "Tro"]
# names =["le","sh","rns","mrro"]
units =["W/m²","W/m²","mm/day","g/kg",'K','m/s']
vmax=[20,30,3,3,4,1]
vmin=[-20,-30,-3,-3,-4,-1]
ticks = [
    np.linspace(vmin[0], vmax[0], 11),
    np.linspace(vmin[1], vmax[1], 11),
    np.linspace(vmin[2], vmax[2], 11),
    np.linspace(vmin[3], vmax[3], 11),
    np.linspace(vmin[4], vmax[4], 11),
    np.linspace(vmin[5], vmax[5], 11),    
]
boundaries = [
    np.linspace(vmin[0], vmax[0], 21),
    np.linspace(vmin[1], vmax[1], 21),
    np.linspace(vmin[2], vmax[2], 21),
    np.linspace(vmin[3], vmax[3], 21),
    np.linspace(vmin[4], vmax[4], 21),
    np.linspace(vmin[5], vmax[5], 21), 
]

fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(40, 28), subplot_kw={'projection': ccrs.PlateCarree()})

for i, ax in enumerate(axs.flat):
    if i == 0:
        dlwrf_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/dlwrf.nc')['dlwrf1have-sfc-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        dlwrf_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/dlwrf.nc')['var205'].squeeze().sel(time=slice(time_start,time_end))
        dlwrf_std = np.nanstd(np.array([dlwrf_3q,dlwrf_55]),axis=0)
        dlwrf_std_mean = np.nanmean(dlwrf_std,axis=0)
        dlwrf_mean = np.nanmean(dlwrf_3q,axis=0)-np.nanmean(dlwrf_55,axis=0)
        data = np.flipud(dlwrf_mean)

    if i == 1:
        dswrf_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/dswrf.nc')['dswrf1have-sfc-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        dswrf_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/dswrf.nc')['var204'].squeeze().sel(time=slice(time_start,time_end))
        dswrf_std = np.nanstd(np.array([dswrf_3q,dswrf_55]),axis=0)
        dswrf_std_mean = np.nanmean(dswrf_std,axis=0)
        dswrf_mean = np.nanmean(dswrf_3q,axis=0)-np.nanmean(dswrf_55,axis=0)
        data = np.flipud(dswrf_mean)

    if i == 2:
        tprat_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/tprate.nc')['tprate1have-sfc-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))*86400
        tprat_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/tprate.nc')['var61'].squeeze().sel(time=slice(time_start,time_end))
        lon1 = tprat_55.lon
        lat1 = tprat_55.lat
        tprat_std = np.nanstd(np.array([tprat_3q,tprat_55]),axis=0)
        tprat_std_mean = np.nanmean(tprat_std,axis=0)
        tprat_mean = np.nanmean(tprat_3q,axis=0)-np.nanmean(tprat_55,axis=0)
        data = np.flipud(tprat_mean)


    if i == 3:
        #将spfh的单位从kg/kg转为g/kg
        spfh_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/spfh.nc')['spfh2m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))*1e3
        spfh_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/spfh.nc')['var51'].squeeze().sel(time=slice(time_start,time_end))*1e3
        lon1 = spfh_55.lon
        lat1 = spfh_55.lat
        spfh_std = np.nanstd(np.array([spfh_3q,spfh_55]),axis=0)
        spfh_std_mean = np.nanmean(spfh_std,axis=0)
        spfh_mean = np.nanmean(spfh_3q,axis=0)-np.nanmean(spfh_55,axis=0)
        data = np.flipud(spfh_mean)

    if i == 4:
        t2m_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/tmp.nc')['tmp2m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        t2m_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/tmp.nc')['var11'].squeeze().sel(time=slice(time_start,time_end))
        lon1 = t2m_55.lon
        lat1 = t2m_55.lat
        t2m_std = np.nanstd(np.array([t2m_3q,t2m_55]),axis=0)
        t2m_std_mean = np.nanmean(t2m_std,axis=0)
        t2m_mean = np.nanmean(t2m_3q,axis=0)-np.nanmean(t2m_55,axis=0)
        data = np.flipud(t2m_mean)

    if i == 5:
        u_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/u.nc')['ugrd10m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        u_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/u.nc')['var33'].squeeze().sel(time=slice(time_start,time_end))
        v_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/v.nc')['vgrd10m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        v_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/v.nc')['var34'].squeeze().sel(time=slice(time_start,time_end))
        ws_3q = np.sqrt(u_3q**2+v_3q**2)
        ws_55 = np.sqrt(u_55**2+v_55**2)
        lon1 = u_3q.lon
        lat1 = u_55.lat
        ws_std = np.nanstd(np.array([ws_3q,ws_55]),axis=0)
        ws_std_mean = np.nanmean(ws_std,axis=0)
        ws_mean = np.nanmean(ws_3q,axis=0)-np.nanmean(ws_55,axis=0)
        data = np.flipud(ws_mean)

    im = ax.imshow(data, cmap='RdBu_r', vmin=vmin[i], vmax=vmax[i], extent=[-180, 180, -60, 90])
    cbar = plt.colorbar(im, ticks=ticks[i][::2], boundaries=boundaries[i], orientation='vertical', pad=0.01, shrink=0.55, extend="both", ax=ax)
    cbar.ax.tick_params(labelsize=50, width=2, length=7)
    ax.set_title(f"{titles[i]}", fontsize=55, transform=ax.transAxes, loc="left")
    ax.coastlines(linewidth=2)
    ax.set_facecolor('white')
    # ax.text(0.003, 0.1, f"{titles[i]}", fontsize=60, transform=ax.transAxes, ha="left") 
    ax.text(1.037, 1.0, f'{units[i]}', fontsize=50, transform=ax.transAxes, ha="left")
    for spine in ax.spines.values():
        spine.set_linewidth(3)
plt.subplots_adjust(wspace=0.02, hspace=-0.15)
plt.savefig('/share/home/dq134/wzx/Datacomparison/figures/FigS3_meandif.jpg', format='jpg', dpi=300, bbox_inches='tight')