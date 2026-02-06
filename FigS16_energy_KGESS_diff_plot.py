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
titles = ["(a) Albedo", "(b) Net Longwave Radiation", "(c) Net Shortwave Radiation", ]
var = ['Albedo', 'Surface_Net_LW_Radiation', 'Surface_Net_SW_Radiation', ]
ref_data = ['CLARA_3', 'CLARA_3', 'CLARA_3', ]
sim_data = ['JRA3Q_0.25', 'JRA55_0.25']
vmax = [1, 1, 1,]
vmin = [-1, -1, -1,]
folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/diffres/0.25/all_diff/'

# Generate ticks and boundaries
ticks = [np.linspace(vmin[i], vmax[i], 13) for i in range(len(vmin))]
boundaries = ticks

# Create figure and subplots
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(40, 27), subplot_kw={'projection': ccrs.PlateCarree()})

# Plot each variable
for i, ax in enumerate(axs.flat):
    data1 = xr.open_dataset(
        f'{folder_path}/{var[i]}_ref_{ref_data[i]}_{sim_data[0]}_vs_{sim_data[1]}_KGESS_diff.nc')['KGESS_diff']
    data = np.flipud(data1)
    
    im = ax.imshow(data, cmap='RdBu_r', vmin=vmin[i], vmax=vmax[i], 
                    extent=[-180, 180, -60, 90]
                    )
    cbar = plt.colorbar(im, ticks=ticks[i][::3], boundaries=boundaries[i], 
                        orientation='vertical', pad=0.01, 
                    #    shrink=0.8,
                        extend='both', ax=ax)
    cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)
    ax.coastlines(linewidth=2)
    ax.set_facecolor('white')
    
    ax.set_title(f"{titles[i]}", fontsize=title_size, transform=ax.transAxes, loc="left")
    for spine in ax.spines.values():
        spine.set_linewidth(3)

# Adjust layout and save
plt.subplots_adjust(wspace=-0.2, hspace=0.2)
plt.savefig(
    'C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/FigS15_energy_KGESS_diff.jpg', 
    format='jpg', dpi=300, bbox_inches='tight')
plt.close()
