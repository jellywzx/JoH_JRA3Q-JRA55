import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import rcParams
from cmaps import WhiteBlueGreenYellowRed
import pandas as pd

# ======== 基本设置 ========
plt.rcParams['font.family'] = 'Times New Roman'
colorbar_ticklabel_size = 50
text_size = 50
unit_size = 50
title_size = 55

titles = ["(a) Net Radiation", "(b) Sensible Heat", "(c) Evapotranspiration", "(d) Surface Soil Moisture", "(e) Total Runoff", "(f) Streamflow"]
vars = ['f_rnet', 'f_fsena', 'f_fevpa', 'f_wliq_soisno', 'f_rnof']
units = ["W/m²", "W/m²", 'mm/day', 'm³/m³', "mm/day", "%"]

vmax = [160, 120, 5, 0.3, 6, 100]
vmin = [0, 0, 0, 0, 0, -100]
ticks = [np.linspace(vmin[i], vmax[i], 21) for i in range(6)]
boundaries = [np.linspace(vmin[i], vmax[i], 11) for i in range(6)]

filepath = '/media/zhwei/data01/weizx/colm_DAY/'
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(40, 28), subplot_kw={'projection': ccrs.PlateCarree()})

# ======== 函数定义 ========
def draw_variable_map(ax, i, var, title, unit):
    if var == 'f_rnof':
        data = xr.open_dataset(f'{filepath}/mean_mean/{var}.nc')[var].squeeze() * 86400  # runoff转换单位
    else:
        data = xr.open_dataset(f'{filepath}/mean_mean/{var}.nc')[var].squeeze()
    data_plot = np.flipud(data)

    sigfile = f'{filepath}/pvalue/test/fdr/fdr_0p25_{var}.nc'
    sig_mask = xr.open_dataset(sigfile)['significant_mask']
    data_pass = np.load(f'{filepath}/pvalue/test/fdr/0p25_proportion_list.npz', allow_pickle=True)['proportion_passed_fdr'][0] * 100

    im = ax.imshow(data_plot, cmap=WhiteBlueGreenYellowRed,
                   vmin=vmin[i], vmax=vmax[i],
                   extent=[-180, 180, -60, 90])
    ax.set_title(title, fontsize=title_size, transform=ax.transAxes, loc="left")
    ax.text(1.02, 0.98, unit, fontsize=unit_size, transform=ax.transAxes, ha="left")
    ax.coastlines(linewidth=2, color='k')

    cbar = plt.colorbar(im,
                         ticks=ticks[i][::5], boundaries=boundaries[i],
                        orientation='vertical', pad=0.01, shrink=0.55, extend="both", ax=ax)
    cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)
    for spine in ax.spines.values():
        spine.set_linewidth(3)

def draw_streamflow_map(ax, i):
    df_diffp = pd.read_csv(f'{filepath}/streamflow_diff_p.csv')
    df_p_values = pd.read_csv(f'{filepath}/streamflow_output_p_values.csv')
    df_stations = pd.read_csv(f'{filepath}/Streamflow_stn_GRDC_JRA3Q_cama_0.25_evaluations.csv')
    df = pd.merge(pd.merge(df_p_values, df_stations, on='ID'), df_diffp, on='ID')

    df['p_value'] = df['p_value'].apply(lambda x: 1 if x > 0.05 else -1)
    lon = df['lon'].values
    lat = df['lat'].values
    diffp = np.clip(df['diff_p'], -100, 100)

    passed_p = round((df['p_value'] == -1).sum() / len(df) * 100, 2)
    ax.scatter(lon[df['p_value'] == 1], lat[df['p_value'] == 1], c='gray', s=150, marker='.', transform=ccrs.PlateCarree(), label='Not Significant')
    cs = ax.scatter(lon[df['p_value'] == -1], lat[df['p_value'] == -1], c=diffp[df['p_value'] == -1],
                    cmap='RdBu_r', s=150, marker='.', vmin=-100, vmax=100, transform=ccrs.PlateCarree(), label='Significant')

    ax.add_feature(cfeature.LAND, facecolor='0.8', edgecolor='0.6')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.1)
    ax.add_feature(cfeature.LAKES, facecolor='white', edgecolor='0.6')
    ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
    ax.set_title(titles[i], fontsize=title_size, transform=ax.transAxes, loc="left")
    ax.text(0, 0.007, f'{passed_p}%', fontsize=text_size, transform=ax.transAxes)
    ax.text(1.02, 0.98, units[i], fontsize=unit_size, transform=ax.transAxes, ha="left")

    cbar = plt.colorbar(cs, ticks=ticks[i][::5], boundaries=boundaries[i],
                        shrink=0.55, pad=0.01, orientation='vertical', extend='both')
    cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)
    for spine in ax.spines.values():
        spine.set_linewidth(3)

# ======== 主循环绘图 ========
for i, ax in enumerate(axs.flat):
    if i < 5:
        draw_variable_map(ax, i, vars[i], titles[i], units[i])
    else:
        ax.axis('off')  # 关闭最后一个空图

plt.subplots_adjust(wspace=0.02, hspace=-0.15)
plt.savefig(f'{filepath}/FigureS8_colm_fdr_mean.jpg', format='jpg', dpi=300, bbox_inches='tight')
print('✅ 出图完毕')
