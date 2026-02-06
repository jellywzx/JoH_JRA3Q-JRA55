import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Set time range
time_start = '2001-01'
time_end = '2010-12'

# Configure plot parameters
plt.rcParams['font.family'] = 'Times New Roman'
colorbar_ticklabel_size = 50
text_size = 50
title_size = 50

# Define data and plot settings
titles = ["(a) JRA-3Q BGC_LAIoff - noBGC", "(b) JRA-55 BGC_LAIoff - noBGC", "(c) JRA-3Q BGC_LAIon - BGC_LAIoff", "(d) JRA-55 BGC_LAIon - BGC_LAIoff"]
vmin, vmax = -1, 1
ticks = np.linspace(vmin, vmax, 13)
# folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_BGC_diff_noLAI/output/comparisons/Diff_Comparison'
file_Path = ['C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_BGC_diff_noLAI/output/comparisons/Diff_Comparison/'
                'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_JRA3Q_0.25_BGC_vs_JRA3Q_0.25_noBGC_KGESS_diff.nc',
            'C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_BGC_diff_noLAI/output/comparisons/Diff_Comparison/'
                'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_JRA55_0.25_BGC_vs_JRA55_0.25_noBGC_KGESS_diff.nc',
            'C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_LAI_diff/output/comparisons/Diff_Comparison/'
                'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_JRA3Q_0.25_LAI_vs_JRA3Q_0.25_noLAI_KGESS_diff.nc',
            'C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_LAI_diff/output/comparisons/Diff_Comparison/'
                'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_JRA55_0.25_LAI_vs_JRA55_0.25_noLAI_KGESS_diff.nc',   
              ]


# Generate ticks and boundaries
# ticks = [np.linspace(vmin[i], vmax[i], 13) for i in range(len(vmin))]
# boundaries = ticks

# Create figure and subplots
fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(40, 18), subplot_kw={'projection': ccrs.PlateCarree()})

# Plot each variable
for i, ax in enumerate(axs.flat):
    file = xr.open_dataset(file_Path[i])
    lon = file['lon']
    lat = file['lat']
    data1 = file['KGESS_diff']
    data = data1
    # data = np.flipud(data1)
    im = ax.pcolormesh(lon, lat, data, cmap='RdBu_r',
                       vmin=vmin, vmax=vmax, shading='auto')

    # 加地理元素
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=1.5)
    # ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=1)
    # ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
    ax.set_extent([-125, -66, 24, 54], crs=ccrs.PlateCarree())

    # 添加标题
    # ax.set_title(titles[i], fontsize=title_size, loc='left')
    ax.text(0.01, 1.15, titles[i],
        fontsize=title_size,
        transform=ax.transAxes,
        ha='left', va='top')


    # 添加色条
    cbar = plt.colorbar(im, ax=ax, orientation='vertical',
                        pad=0.02, shrink=0.8, ticks=ticks[::3], extend='both')
    cbar.ax.tick_params(labelsize=colorbar_ticklabel_size)

    for spine in ax.spines.values():
        spine.set_linewidth(3)

# 布局调整和保存
plt.subplots_adjust(wspace=-0.1, hspace=0.2)
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig9.jpg',
            dpi=300, bbox_inches='tight')
plt.close()