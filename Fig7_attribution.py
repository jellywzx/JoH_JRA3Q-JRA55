import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
from matplotlib.colors import ListedColormap
from matplotlib import rcParams
import cmaps
from cmaps import WhiteBlueGreenYellowRed
import subprocess

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

titles = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "(h)", "(i)", "(j)", "(k)", "(l)", "(m)", "(n)", "(o)", "(p)","(q)","(r)","(s)","(u)"]

variables = ["f_rnet", "f_fsena", "f_fevpa", "f_wliq_soisno", "f_rnof"]
sum_data = {}
for j in range(5):
    datanc_le = xr.open_dataset(f'/media/zhwei/data01/weizx/PLSR_DAY/results/mean/{variables[j]}/uncertainty.nc')
    data = [datanc_le['variable'].values[i, :, :] for i in range(4)]

    for i in range(4):
        data[i] = np.flipud(data[i])
        data[i] = np.where(np.isclose(data[i], -1e+36), np.nan, data[i])
        
    data0, data1, data2, data3 = [np.asarray(d) for d in data]
    sum_data[variables[j]] = np.nansum([data0, data1, data2, data3], axis=0)


fig, axs = plt.subplots(nrows=5, ncols=4, figsize=(65, 45), subplot_kw={'projection': ccrs.PlateCarree()})

for i, ax in enumerate(axs.flat):
    
    if i in [0+0, 1+0, 2+0, 3+0]:
        j = [0+0, 1+0, 2+0, 3+0].index(i)
        datanc = xr.open_dataset('/media/zhwei/data01/weizx/PLSR_DAY/results/mean/f_rnet/uncertainty.nc')
        data = np.flipud(datanc['variable'][j, :, :])
        data = np.where(np.isclose(data, -1e+36), np.nan, data)
        data = data/sum_data["f_rnet"]
                
    if i in [0+4, 1+4, 2+4, 3+4]:
        j = [0+4, 1+4, 2+4, 3+4].index(i)
        datanc = xr.open_dataset('/media/zhwei/data01/weizx/PLSR_DAY/results/mean/f_fsena/uncertainty.nc')
        data = np.flipud(datanc['variable'][j, :, :])
        data = np.where(np.isclose(data, -1e+36), np.nan, data)
        data = data/sum_data["f_fsena"]
        
    if i in [0+8, 1+8, 2+8, 3+8]:
        j = [0+8, 1+8, 2+8, 3+8].index(i)
        datanc = xr.open_dataset('/media/zhwei/data01/weizx/PLSR_DAY/results/mean/f_fevpa/uncertainty.nc')
        data = np.flipud(datanc['variable'][j, :, :])
        data = np.where(np.isclose(data, -1e+36), np.nan, data)
        data = data/sum_data["f_fevpa"]
        
    if i in [0+12, 1+12, 2+12, 3+12]:
        j = [0+12, 1+12, 2+12, 3+12].index(i)
        datanc = xr.open_dataset('/media/zhwei/data01/weizx/PLSR_DAY/results/mean/f_wliq_soisno/uncertainty.nc')
        data = np.flipud(datanc['variable'][j, :, :])
        data = np.where(np.isclose(data, -1e+36), np.nan, data)
        data = data
        data = data/(sum_data["f_wliq_soisno"])
        
    if i in [0+16, 1+16, 2+16, 3+16]:
        j = [0+16, 1+16, 2+16, 3+16].index(i)
        datanc = xr.open_dataset('/media/zhwei/data01/weizx/PLSR_DAY/results/mean/f_rnof/uncertainty.nc')
        data = np.flipud(datanc['variable'][j, :, :])
        data = np.where(np.isclose(data, -1e+36), np.nan, data)
        data = data*365
        data = data/(sum_data["f_rnof"]*365)
        # data = data
        # data = data/(sum_data["f_rnof"])
    
    im = ax.imshow(data, cmap=WhiteBlueGreenYellowRed, vmin=0, vmax=1, extent=[-180, 180, -60, 90])
    
    ax.coastlines(linewidth=2)
    ax.set_facecolor('white')

    ax.text(0.08, 0.1, f"{titles[i]}", fontsize=80, transform=ax.transAxes, ha="center")

    for spine in ax.spines.values():
        spine.set_linewidth(3)

font_size = 90
plt.text(0.22, 0.80, "LW", fontsize=font_size, transform=fig.transFigure, ha="center")
plt.text(0.415, 0.80, "SW", fontsize=font_size, transform=fig.transFigure, ha="center")
plt.text(0.61, 0.80, "P", fontsize=font_size, transform=fig.transFigure, ha="center")
plt.text(0.805, 0.80, "VPD", fontsize=font_size, transform=fig.transFigure, ha="center")

plt.text(0.1, 0.72, "Rn", fontsize=font_size, transform=fig.transFigure, ha="center")
plt.text(0.1, 0.61, "SH", fontsize=font_size, transform=fig.transFigure, ha="center")
plt.text(0.1, 0.49, "ET", fontsize=font_size, transform=fig.transFigure, ha="center")
plt.text(0.1, 0.37, "SSM", fontsize=font_size, transform=fig.transFigure, ha="center")
plt.text(0.1, 0.25, "Tro", fontsize=font_size, transform=fig.transFigure, ha="center")


cbar_ax = fig.add_axes([0.263, 0.17, 0.5, 0.02])  
cbar = plt.colorbar(im, ticks=np.arange(0, 1.1, 0.1), boundaries=np.arange(0, 1.001, 0.01),  orientation='horizontal',  pad=0.01, shrink=0.35,  cax=cbar_ax)
cbar.set_ticklabels(['0', '10', '20', '30', '40', '50', '60', '70', '80', '90','100'])
cbar.ax.tick_params(labelsize=80, width=3, length=8)
plt.text(1.02, 0.01, "%", fontsize=80, transform=cbar_ax.transAxes, ha="left")


plt.subplots_adjust(wspace=0.02, hspace=-0.6)

plt.savefig('/media/zhwei/data01/weizx/PLSR_DAY/fig8.jpg', format='jpg', dpi=300, bbox_inches='tight')
