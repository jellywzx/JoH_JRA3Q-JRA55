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
titles = ["(a) Net Radiation", "(b) Sensible Heat", "(c) Evapotranspiration", 
          "(d) Surface Soil Moisture", "(e) Total Runoff", "(f) Streamflow"]
var = ['Net_Radiation', 'Sensible_Heat', 'Evapotranspiration', 'Surface_Soil_Moisture', 'Total_Runoff']
ref_data = ['CLARA_3', 'GLEAM4.2a_monthly', 'GLEAM4.2a_monthly', 'GLEAM4.2a_monthly', 'GRUN_ENSEMBLE']
sim_data = ['JRA3Q_US_0.1', 'JRA55_US_0.1']
vmax = [0.6, 0.6, 1, 1, 3, 6]
vmin = [-0.6, -0.6, -1, -1, -3, -6]
folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/US_0.1_allvar/output/comparisons/Diff_Plot/'

# Generate ticks and boundaries
ticks = [np.linspace(vmin[i], vmax[i], 13) for i in range(len(vmin))]
boundaries = ticks

# Create figure and subplots
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(40, 27), subplot_kw={'projection': ccrs.PlateCarree()})

# Plot each variable
for i, ax in enumerate(axs.flat):
    if i == 5:  # Streamflow scatter plot
        file1 = pd.read_csv(
            'C:/Users/fzjxw/Desktop/Datacomparison/US_0.1_allvar/output/metrics/Streamflow_stn_GRDC_JRA3Q_US_0.1_cama_evaluations.csv', header=0)
        file2 = pd.read_csv(
            'C:/Users/fzjxw/Desktop/Datacomparison/US_0.1_allvar/output/metrics/Streamflow_stn_GRDC_JRA55_US_0.1_cama_evaluations.csv', header=0)
        lon, lat = file1['lon'], file1['lat']
        data1, data2 = file1['KGESS'], file2['KGESS']
        kgess = data1-data2
        cs1 = ax.scatter(lon, lat, s=200, c=kgess, cmap='RdBu_r', marker='.', 
                        edgecolors='none', alpha=0.9, vmin=vmin[i], vmax=vmax[i], 
                        label='Significant', transform=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, facecolor='0.8', edgecolor='0.6', linewidth=0.1)
        ax.add_feature(cfeature.COASTLINE, linewidth=2)
        ax.add_feature(cfeature.LAKES, facecolor='white', edgecolor='0.6', linewidth=0.1)
        ax.set_extent([-125, -66, 22, 54], crs=ccrs.PlateCarree())
        
        cbar = plt.colorbar(cs1, ticks=ticks[i][::3], boundaries=boundaries[i], 
                        #    shrink=0.7,
                             pad=0.01, orientation='vertical', extend='both')
        cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)
    else:  # Other variables (imshow)
        data1 = xr.open_dataset(
            f'{folder_path}/{var[i]}_ref_{ref_data[i]}_{sim_data[0]}_vs_{sim_data[1]}_KGESS_diff.nc')['KGESS_diff']
        data = np.flipud(data1)
        
        im = ax.imshow(data, cmap='RdBu_r', vmin=vmin[i], vmax=vmax[i], 
                      extent=[-125, -66, 22, 54]
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
    'C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/FigS14_US_KGESS_diff.jpg', 
    format='jpg', dpi=300, bbox_inches='tight')
plt.close()
