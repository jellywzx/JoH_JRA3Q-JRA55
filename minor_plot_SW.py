import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# Configure plot parameters
plt.rcParams['font.family'] = 'Times New Roman'
colorbar_ticklabel_size = 50
title_size = 50

# === Settings for Net Radiation only ===
title = "Downward SW Radiation \nRef: CERES_EBAF_Ed4.2"
var_name = "Surface_Downward_SW_Radiation"
ref_data = "CERES_EBAF_Ed4.2"
sim_data_1 = "JRA3Q_0.25"
sim_data_2 = "JRA55_0.25"

vmax = 0.6
vmin = -0.6
ticks = np.linspace(vmin, vmax, 13)
boundaries = ticks

folder_path = r"/share/home/dq134/wzx/Datacomparison/open_cases/Glb_LWSW_ref_260206/output/metrics"
infile = f"{folder_path}/{var_name}_ref_{ref_data}_{sim_data_1}_vs_{sim_data_2}_KGESS_diff_sellonlat.nc"
outfile = r"/share/home/dq134/wzx/Datacomparison/open_cases/Glb_LWSW_ref_260206/output/metrics/CERES_SW_KGESS_diff.jpg"

# === Read data ===
da = xr.open_dataset(infile)["KGESS"]

# 如果你的数据纬度是从北到南（降序），imshow会倒；这里保持你原来 flipud 的做法
data = np.flipud(da.values)

# === Plot ===
fig = plt.figure(figsize=(20, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

im = ax.imshow(
    data,
    cmap="RdBu_r",
    vmin=vmin,
    vmax=vmax,
    extent=[-180, 180, -60, 90],
    transform=ccrs.PlateCarree(),
)

cbar = plt.colorbar(
    im,
    ticks=ticks[::3],
    boundaries=boundaries,
    orientation="vertical",
    pad=0.02,
    shrink=0.8,
    extend="both",
    ax=ax,
)
cbar.ax.tick_params(labelsize=colorbar_ticklabel_size, width=2, length=7)

ax.coastlines(linewidth=2)
ax.set_facecolor("white")
ax.set_title(title, fontsize=title_size, loc="left")

for spine in ax.spines.values():
    spine.set_linewidth(3)

plt.savefig(outfile, format="jpg", dpi=300, bbox_inches="tight")
plt.close()

