import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap
from matplotlib import rcParams
import subprocess
import cmaps
from cmaps import WhiteBlueGreenYellowRed
import matplotlib
import pandas as pd

# 设置默认字体
plt.rcParams['font.family'] = 'Times New Roman'
colorbar_ticklabel_size = 50
text_size = 50
unit_size = 50
title_size = 55

titles = ["(a) Net Radiation", "(b) Sensible Heat", "(c) Evapotranspiration", "(d) Surface Soil Moisture", "(e) Total Runoff","(f) Streamflow"]
vars = ['f_rnet','f_fsena','f_fevpa','f_wliq_soisno','f_rnof',]
units = ["W/m²", "W/m²",'mm/day','m³/m³', "mm/day","%"]

#region 0.25 degree
vmax = [20, 20, 1, 0.05, 4,100]
vmin = [0, 0, 0, 0, 0, -100]
ticks = [
    np.linspace(vmin[0], vmax[0], 21),
    np.linspace(vmin[1], vmax[1], 21),
    np.linspace(vmin[2], vmax[2], 21),
    np.linspace(vmin[3], vmax[3], 21),
    np.linspace(vmin[4], vmax[4], 21),
    np.linspace(vmin[5], vmax[5], 21),
]
boundaries = [
    np.linspace(vmin[0], vmax[0], 11),
    np.linspace(vmin[1], vmax[1], 11),
    np.linspace(vmin[2], vmax[2], 11),
    np.linspace(vmin[3], vmax[3], 11),
    np.linspace(vmin[4], vmax[4], 11),
    np.linspace(vmin[5], vmax[5], 11),
]
filepath='/media/zhwei/data01/weizx/colm_DAY/'
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(40, 28), subplot_kw={'projection': ccrs.PlateCarree()})
for i, ax in enumerate(axs.flat):
     #将runoff的单位从mm/s转为mm/day, 需要乘以86400
    if i == 4:
        data_std = xr.open_dataset(f'{filepath}/stdmean/'+vars[i]+'_stdmean.nc')['std_mean']*86400
        dif_std = np.flipud(data_std)
        lon = data_std.lon   
        lat = data_std.lat
        #读取pvalues
        data_sig = xr.open_dataset(f'{filepath}/pvalue/test/fdr/fdr_0p25_{vars[i]}.nc')
        significant_mask = data_sig['significant_mask']
        lon1 = data_sig.lon
        lat1 = data_sig.lat
        significant_coords = np.column_stack(np.where(significant_mask))
        data_pass = np.load(f'{filepath}/pvalue/test/fdr/0p25_proportion_list.npz',allow_pickle=True)['proportion_passed_fdr'][0]*100
        im = ax.imshow(dif_std,cmap=WhiteBlueGreenYellowRed,
                        vmin=vmin[i],vmax=vmax[i],
                        extent=[-180,180,-60,90])
        ax.contourf(lon1,lat1,significant_mask,levels=1,hatches=['','///'],alpha=0)
        ax.set_title(f"{titles[i]}", fontsize=50, transform=ax.transAxes, loc="left")
        ax.text(0, 0.007, f'{round(data_pass[i],2)}%',fontsize=text_size, transform=ax.transAxes)
        ax.text(1.02, 0.98, f'{units[i]}', fontsize=unit_size, transform=ax.transAxes, ha="left")
        ax.coastlines(linewidth=2,color='k')
        cbar = plt.colorbar(im, 
                                ticks=ticks[i][::5], 
                                boundaries=boundaries[i],
                                orientation='vertical', pad=0.01, shrink=0.55, extend="both", ax=ax)
        cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)
        for spine in ax.spines.values():
            spine.set_linewidth(3)
        continue
    if i == 5:
        #Streamflow 站点出图
        df_diffp = pd.read_csv('/media/zhwei/data01/weizx/colm_DAY/streamflow_diff_p.csv')
        df_p_values = pd.read_csv('/media/zhwei/data01/weizx/colm_DAY/streamflow_output_p_values.csv', header=0)
        # 读取站点信息数据
        df_stations = pd.read_csv('/media/zhwei/data01/weizx/colm_DAY/Streamflow_stn_GRDC_JRA3Q_cama_0.25_evaluations.csv', header=0)
        # 合并两个数据框，基于ID列
        df_merged_1 = pd.merge(df_p_values, df_stations, on='ID')
        df_merged = pd.merge(df_merged_1,df_diffp,on='ID')
        data_select = df_merged
        data_select['p_value'] = data_select['p_value'].apply(lambda x: 1 if x > 0.05 else -1)  #如果大于0.05认为是1，否则认为是-1，所以-1为显著的区域
        # print(data_select['p_value'] .shape)
        stn_lon = data_select['lon'].values
        stn_lat = data_select['lat'].values
        metric = data_select["p_value"].values
        diffp = data_select['diff_p']
        # print(f'metric is -1:{metric==-1}')
        #挑选出显著的区域
        lon_True = stn_lon[metric==-1]
        lat_True = stn_lat[metric==-1]
        data_True = diffp[metric==-1]
        passed_p = (len(data_True)/len(metric))*100
        # print(f'passed proporttion is {round(passed_p,2)}%')

        #——————————作图——————————————
        data_False = metric[metric==1]
        data_plt = data_False
        lon_plt = stn_lon[metric==1]
        lat_plt = stn_lat[metric==1]
        max_lat=90.0 
        min_lat=-60.0
        max_lon=180.0             
        min_lon=-180.0
        vmin=-1
        vmax= 1
        data_True_clipped = np.clip(data_True,-100,100)
        cs = ax.scatter(lon_plt, lat_plt, c='gray', s=150, marker='.', edgecolors='none', alpha=0.9,label='Not Significant', transform=ccrs.PlateCarree())
        # loc_lon_true, loc_lat_true = m(lon_True, lat_True)
        cs1 = ax.scatter(lon_True, lat_True, s=150, c=data_True_clipped, cmap='RdBu_r', marker='.', edgecolors='none', alpha=0.9,vmin=-100,vmax=100,label='Significant',transform=ccrs.PlateCarree() )
        ax.add_feature(cfeature.LAND, facecolor='0.8', edgecolor='0.6', linewidth=0.1)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.1, edgecolor='0.6')
        ax.add_feature(cfeature.LAKES, facecolor='white', edgecolor='0.6', linewidth=0.1)
        ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
        ax.set_title(f"{titles[i]}", fontsize=title_size, transform=ax.transAxes, loc="left")
        cbar = plt.colorbar(cs1, ticks=ticks[i][::5], 
                                boundaries=boundaries[i],
                                shrink=0.55, pad=0.01,orientation='vertical',extend='both')
        cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)
        ax.text(0, 0.007, f'{round(passed_p,2)}%',fontsize=text_size, transform=ax.transAxes)
        ax.text(1.02, 0.98, f'{units[i]}', fontsize=unit_size, transform=ax.transAxes, ha="left")
        for spine in ax.spines.values():
            spine.set_linewidth(3)
    else:
        data_std = xr.open_dataset(f'{filepath}/stdmean/'+vars[i]+'_stdmean.nc')['std_mean']
        dif_std = np.flipud(data_std)
        lon = data_std.lon   
        lat = data_std.lat
        #读取pvalues
        data_sig = xr.open_dataset(f'{filepath}/pvalue/test/fdr/fdr_0p25_{vars[i]}.nc')
        significant_mask = data_sig['significant_mask']
        lon1 = data_sig.lon
        lat1 = data_sig.lat
        significant_coords = np.column_stack(np.where(significant_mask))
        data_pass = np.load(f'{filepath}/pvalue/test/fdr/0p25_proportion_list.npz',allow_pickle=True)['proportion_passed_fdr'][0]*100
        im = ax.imshow(dif_std,cmap=WhiteBlueGreenYellowRed,
                        vmin=vmin[i],vmax=vmax[i],
                        extent=[-180,180,-60,90])
        ax.contourf(lon1,lat1,significant_mask,levels=1,hatches=['','///'],alpha=0)
        ax.set_title(f"{titles[i]}", fontsize=title_size, transform=ax.transAxes, loc="left")
        # ax.text(0.005, 0.1, f"{vars[i]}", fontsize=55, transform=ax.transAxes, ha="left")
        ax.text(0, 0.007, f'{round(data_pass[i],2)}%',fontsize=text_size, transform=ax.transAxes)
        ax.text(1.02, 0.98, f'{units[i]}', fontsize=unit_size, transform=ax.transAxes, ha="left")
        ax.coastlines(linewidth=2,color='k')
        cbar = plt.colorbar(im, ticks=ticks[i][::5], 
                                boundaries=boundaries[i],
                                orientation='vertical', pad=0.01, shrink=0.55, extend="both", ax=ax)
        cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)
        for spine in ax.spines.values():
            spine.set_linewidth(3)
    
plt.subplots_adjust(wspace=0.02, hspace=-0.15)
plt.savefig('/media/zhwei/data01/weizx/colm_DAY/Figure4_colm_fdr.jpg',format='jpg',dpi=300,bbox_inches='tight')
print(f'出图完毕')
#endregion
