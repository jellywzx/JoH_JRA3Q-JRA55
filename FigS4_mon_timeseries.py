import numpy as np
import xarray as xr
import pandas as pd
import math
import glob
from pylab import *
import matplotlib.dates as mdates
from matplotlib import dates, ticker
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
# import cmaps
# from mpl_toolkits.basemap import Basemap, shiftgrid
from matplotlib.colors import ListedColormap
from matplotlib import rcParams
import subprocess
import cartopy.crs as ccrs
# from cmaps import WhiteYellowOrangeRed


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

# titles = ["(a) dlwrf", "(b) dswrf", "(c) spfh", "(d) tprat", "(e) t2m", "(f) ws"]
titles = ["(a) Downward Longwave Radiation", 
          "(b) Downward Shortwave Radiation",
          "(c) Precipitation",
          "(d) Specific Humidity", 
          "(e) Air Temperature",
          "(f) Wind Speed"]
units =["    W/m²","    W/m²","mm/day","    g/kg",'       K','    m/s']
vmax=[350,250,3.2,10,284,0.35]
# vmin=[-20,-20,-2,-4,-2,-3]
vmin=[270,150,2.1,6,266,0]

fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(50, 30))
for i, ax in enumerate(axs.flat):

    if i == 0:
        dlwrf_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/dlwrf_fldmean.nc')['dlwrf1have-sfc-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        dlwrf_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/dlwrf_fldmean.nc')['var205'].squeeze().sel(time=slice(time_start,time_end))
        data1 = dlwrf_3q
        data2 = dlwrf_55


    if i == 1:
        dswrf_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/dswrf_fldmean.nc')['dswrf1have-sfc-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        dswrf_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/dswrf_fldmean.nc')['var204'].squeeze().sel(time=slice(time_start,time_end))
        data1 = dswrf_3q
        data2 = dswrf_55

    if i == 2:
        tprat_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/tprate_fldmean.nc')['tprate1have-sfc-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))*86400
        tprat_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/tprate_fldmean.nc')['var61'].squeeze().sel(time=slice(time_start,time_end))
        data1 = tprat_3q
        data2 = tprat_55

    if i == 3:
        spfh_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/spfh_fldmean.nc')['spfh2m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))*1e3
        spfh_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/spfh_fldmean.nc')['var51'].squeeze().sel(time=slice(time_start,time_end))*1e3
        data1 = spfh_3q
        data2 = spfh_55

    if i == 4:
        t2m_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/tmp_fldmean.nc')['tmp2m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        t2m_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/tmp_fldmean.nc')['var11'].squeeze().sel(time=slice(time_start,time_end))
        data1 = t2m_3q
        data2 = t2m_55

    if i == 5:
        u_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/u_fldmean.nc')['ugrd10m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        u_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/u_fldmean.nc')['var33'].squeeze().sel(time=slice(time_start,time_end))
        v_3q = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA3Q/mon_0p25/v_fldmean.nc')['vgrd10m-hgt-fc-gauss'].squeeze().sel(time=slice(time_start,time_end))
        v_55 = xr.open_dataset('/share/home/dq134/wzx/Datacomparison/JRA55/mon_0p25/v_fldmean.nc')['var34'].squeeze().sel(time=slice(time_start,time_end))
        ws_3q = np.sqrt(u_3q**2+v_3q**2)
        ws_55 = np.sqrt(u_55**2+v_55**2)
        data1 = ws_3q
        data2 = ws_55
    period = pd.date_range('2001-01','2010-12',freq='MS')
    im = ax.plot(period, data1, 
                            # marker='^',markersize=15,
                            linewidth=4,color='darkcyan',label='JRA-3Q')
    im = ax.plot(period, data2, 
                            # marker='o',markersize=15, 
                            linewidth=4,color='palevioletred',label='JRA-55')
    ax.text(0.04, 1.05, f"{titles[i]}", fontsize=60, transform=ax.transAxes, ha="left") 
    ax.text(-0.12, 1.05, f'{units[i]}', fontsize=60, transform=ax.transAxes, ha="left")
    ax.xaxis.set_tick_params(labelsize=55)
    ax.yaxis.set_tick_params(labelsize=55)
    ax.yaxis.set_ticks(np.linspace(vmin[i],vmax[i],11)[::2])
    plt.legend(edgecolor='k',fontsize=50,loc='upper right')
    for spine in ax.spines.values():
        spine.set_linewidth(3)

plt.subplots_adjust(wspace=0.1, hspace=0.35)
plt.savefig('/share/home/dq134/wzx/Datacomparison/figures/FigS4_mon_timeseries.jpg', format='jpg', dpi=300, bbox_inches='tight')
