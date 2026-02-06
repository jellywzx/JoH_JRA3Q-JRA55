import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from scipy.stats import gaussian_kde
# import matplotlib.pyplot as plt
# import seaborn as sns

# Set the font family to Times New Roman globally
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 35  # Default font size for consistency
plt.rcParams['axes.labelsize'] = 35  # Font size for axis labels
plt.rcParams['axes.titlesize'] = 40  # Font size for titles
plt.rcParams['xtick.labelsize'] = 35  # Font size for x-axis ticks
plt.rcParams['ytick.labelsize'] = 35  # Font size for y-axis ticks (if used)

# Update Seaborn theme to ensure compatibility
sns.set_theme(style="white", rc={
    "axes.facecolor": (0, 0, 0, 0),
    "axes.labelsize": 35,
    "axes.labelcolor": "black",
    "axes.labelweight": "normal",  # Ensure normal weight for Times New Roman
    "font.family": "Times New Roman",
    "xtick.labelsize": 35
})
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

# titles = ['(a) Downward Longwave Radiation','(b) Downward Shortwave Radiation','(c) Precipitation','(d) Specific Humidity','(e) Air Temperature', '(f) Wind Speed']
var = ['Surface_Downward_LW_Radiation','Surface_Downward_SW_Radiation','Precipitation','Surface_Specific_Humidity','Surface_Air_Temperature','Surface_Wind_Speed']
ref_data = ['CLARA_3', 'CLARA_3','MSWEP_0p25','MSWX_0p25','CRU-TS4.08','ERA5LAND_0p25']
sim_data = ['JRA3Q_0.25', 'JRA55_0.25',]
# vmax = [0.6, 0.6, 1, 1, 2, 1]
# vmin = [-0.6, -0.6, -1, -1, -2, -1]
folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/Evaluation_forcing/output/metrics/'
fontsize=35
titlesize=40


#——————————————————————————————————————————————————————————————————————————
#region (a) LW 
# 输入数据路径和标签
file_paths = [ f'{folder_path}/{var[0]}_ref_{ref_data[0]}_sim_{sim_data[k]}_KGESS.nc' for k in range(2)]
print(file_paths[1])

# 整合所有数据为 DataFrame
all_data = []
for i in range(2):
    nc = Dataset(file_paths[i], 'r')
    if 'KGESS' not in nc.variables:
        raise KeyError(f"'KGESS' not found in {file_paths[i]}")
    data = nc.variables['KGESS'][:].flatten()
    data = data[~np.isnan(data)]
    data = remove_outliers(data)
    data = np.where(data < -1, -1, data)
    label = sim_data[i]
    for val in data:
        all_data.append({'KGESS': val, 'Simulation': label})
    nc.close()

df = pd.DataFrame(all_data)

# 计算每个 Simulation 类别的中位数
medians = df.groupby('Simulation')['KGESS'].median().to_dict()
# 使用 seaborn 创建 ridgeline 图
pal = sns.cubehelix_palette(len(df['Simulation'].unique()), rot=-.25, light=.7)
g = sns.FacetGrid(df, row="Simulation", hue="Simulation", aspect=15, height=0.8, palette=pal)

g.figure.set_size_inches(10, 6)
# 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0, clip_on=False, fill=True, alpha=0.6, linewidth=1.5, )

# 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)

# 设置 x 轴范围
g.set(xlim=(0.4,1))

# 美化图像
g.figure.subplots_adjust(hspace=-0.1, left=0.05, right=0.95, top=0.95, bottom=0.05)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.set_xlabels('KGESS',fontsize=fontsize)
for ax in g.axes.flat:
    ax.tick_params(axis='x', labelsize=fontsize)  # 设置 x 轴刻度字体大小为 12
# 添加左侧 Simulation 标签和中位线+中位数标签
for ax, label in zip(g.axes.flat, df['Simulation'].unique()):
    # 添加左侧 Simulation 标签
    ax.text(
        x=0.4,
        y=1,
        s=label,
        fontsize=fontsize,
        ha='left',
        va='center',
        transform=ax.transData
    )
    # 获取当前 Simulation 的中位数
    median_val = medians[label]
    data = df[df['Simulation'] == label]['KGESS'].values
    kde = gaussian_kde(data, bw_method='scott')
    # # 生成高分辨率 x 值
    kde_x = np.linspace(-1,1, 1000)
    kde_y = kde(kde_x)
    height = np.interp(median_val, kde_x, kde_y)
    ax.vlines(median_val, 0, height, color='black', ls=':', lw=1.5)
    # 添加中位线
    # ax.axvline(x=median_val, ymin=0, ymax=median_val, color='black', linestyle='--', linewidth=1.5, clip_on=False)
    # 添加中位数标签
    ax.text(
        x=median_val,
        y=height,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='right',
        va='bottom',
        color='black',
        transform=ax.transData
    )

g.despine(bottom=True, left=True)
plt.text(0.05, 1, '(a) Downward Longwave Radiation', fontsize=titlesize, ha='left', va='top',transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig3a_LW.jpg', dpi=300, bbox_inches='tight')
# plt.show()
#endregion

'''
#————————————————————————————————————————————————————————————————————————————————
#region (b) SW
#Sensible Heat
j=1
file_paths = [ f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(2)]
print(file_paths[1])

# 整合所有数据为 DataFrame
all_data = []
for i in range(2):
    nc = Dataset(file_paths[i], 'r')
    if 'KGESS' not in nc.variables:
        raise KeyError(f"'KGESS' not found in {file_paths[i]}")
    data = nc.variables['KGESS'][:].flatten()
    data = data[~np.isnan(data)]
    data = remove_outliers(data)
    data = np.where(data < -1, -1, data)
    label = sim_data[i]
    for val in data:
        all_data.append({'KGESS': val, 'Simulation': label})
    nc.close()

df = pd.DataFrame(all_data)

# 计算每个 Simulation 类别的中位数
medians = df.groupby('Simulation')['KGESS'].median().to_dict()
# 使用 seaborn 创建 ridgeline 图
pal = sns.cubehelix_palette(len(df['Simulation'].unique()), rot=-.25, light=.7)
g = sns.FacetGrid(df, row="Simulation", hue="Simulation", aspect=15, height=0.8, palette=pal)

g.figure.set_size_inches(10, 6)
# 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0,clip=(-1, 1),fill=True, alpha=0.6, linewidth=1.5, )

# 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)

# 设置 x 轴范围
g.set(xlim=(0.5,1))

# 美化图像
g.figure.subplots_adjust(hspace=-0.1, left=0.05, right=0.95, top=0.95, bottom=0.05)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.set_xlabels('KGESS',fontsize=fontsize)
for ax in g.axes.flat:
    ax.tick_params(axis='x', labelsize=fontsize)  # 设置 x 轴刻度字体大小为 12
# 添加左侧 Simulation 标签和中位线+中位数标签
for ax, label in zip(g.axes.flat, df['Simulation'].unique()):
    # 添加左侧 Simulation 标签
    ax.text(
        x=0.5,
        y=1.2,
        s=label,
        fontsize=fontsize,
        ha='left',
        va='center',
        transform=ax.transData
    )
    # 获取当前 Simulation 的中位数
    median_val = medians[label]
    data = df[df['Simulation'] == label]['KGESS'].values
    kde = gaussian_kde(data, bw_method='scott')
    # # 生成高分辨率 x 值
    kde_x = np.linspace(-1,1, 1000)
    kde_y = kde(kde_x)
    height = np.interp(median_val, kde_x, kde_y)
    ax.vlines(median_val, 0, height, color='black', ls=':', lw=1.5)
    ax.text(
        x=median_val,
        y=height,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='right',
        va='bottom',
        color='black',
        transform=ax.transData
    )

g.despine(bottom=True, left=True)
plt.text(0.05, 1,'(b) Downward Shortwave Radiation',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig3b_SW.jpg', dpi=300, bbox_inches='tight')
# plt.show()
#endregion



#——————————————————————————————————————————————————————————————————————————————————————————————————————
#region (c) Precipitation
j=2
file_paths = [ f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(2)]
print(file_paths[1])

# 整合所有数据为 DataFrame
all_data = []
for i in range(2):
    nc = Dataset(file_paths[i], 'r')
    if 'KGESS' not in nc.variables:
        raise KeyError(f"'KGESS' not found in {file_paths[i]}")
    data = nc.variables['KGESS'][:].flatten()
    data = data[~np.isnan(data)]
    data = remove_outliers(data)
    data = np.where(data < -1, -1, data)
    label = sim_data[i]
    for val in data:
        all_data.append({'KGESS': val, 'Simulation': label})
    nc.close()

df = pd.DataFrame(all_data)

# 计算每个 Simulation 类别的中位数
medians = df.groupby('Simulation')['KGESS'].median().to_dict()
# 使用 seaborn 创建 ridgeline 图
pal = sns.cubehelix_palette(len(df['Simulation'].unique()), rot=-.25, light=.7)
g = sns.FacetGrid(df, row="Simulation", hue="Simulation", aspect=15, height=0.8, palette=pal)

g.figure.set_size_inches(10, 6)
# 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0, clip=(-1,1), fill=True, alpha=0.6, linewidth=1.5, )

# 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)

# 设置 x 轴范围
g.set(xlim=(-0.1,1))

# 美化图像
g.figure.subplots_adjust(hspace=-0.1, left=0.05, right=0.95, top=0.95, bottom=0.05)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.set_xlabels('KGESS',fontsize=fontsize)
for ax in g.axes.flat:
    ax.tick_params(axis='x', labelsize=fontsize)  # 设置 x 轴刻度字体大小为 12
# 添加左侧 Simulation 标签和中位线+中位数标签
for ax, label in zip(g.axes.flat, df['Simulation'].unique()):
    # 添加左侧 Simulation 标签
    ax.text(
        x=-0.05,
        y=0.5,
        s=label,
        fontsize=fontsize,
        ha='left',
        va='center',
        transform=ax.transData
    )
    # 获取当前 Simulation 的中位数
    median_val = medians[label]
    data = df[df['Simulation'] == label]['KGESS'].values
    kde = gaussian_kde(data, bw_method='scott')
    # # 生成高分辨率 x 值
    kde_x = np.linspace(-1,1, 1000)
    kde_y = kde(kde_x)
    height = np.interp(median_val, kde_x, kde_y)
    ax.vlines(median_val, 0, height, color='black', ls=':', lw=1.5)
    # 添加中位线
    # ax.axvline(x=median_val, ymin=0, ymax=median_val, color='white', linestyle='--', linewidth=1.5, clip_on=False)
    # 添加中位数标签
    ax.text(
        x=median_val,
        y=height,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='right',
        va='bottom',
        color='black',
        transform=ax.transData
    )

g.despine(bottom=True, left=True)
plt.text(0.05, 1,'(c) Precipitation',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig3c_P.jpg', dpi=300, bbox_inches='tight')
# plt.show()
#endregion

#——————————————————————————————————————————————————————————————————————
#region (d) surface specific humidity
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

j = 3 
file_paths = [f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(2)]

# 整合所有数据为 DataFrame
all_data = []
for i in range(2):
    nc = Dataset(file_paths[i], 'r')
    if 'KGESS' not in nc.variables:
        raise KeyError(f"'KGESS' not found in {file_paths[i]}")
    data = nc.variables['KGESS'][:].flatten()
    data = data[~np.isnan(data)]
    data = remove_outliers(data)
    data = np.where(data < -1, -1, data)
    data = data[(data >= -1) & (data <= 1)]
    label = sim_data[i]
    for val in data:
        all_data.append({'KGESS': val, 'Simulation': label})
    nc.close()

df = pd.DataFrame(all_data)

# 计算每个 Simulation 类别的中位数
medians = df.groupby('Simulation')['KGESS'].median().to_dict()

# 使用 seaborn 创建 ridgeline 图
pal = sns.cubehelix_palette(len(df['Simulation'].unique()), rot=-.25, light=.7)
g = sns.FacetGrid(df, row="Simulation", hue="Simulation", aspect=15, height=0.8, palette=pal)

# 设置画幅尺寸
g.figure.set_size_inches(10, 6)

# 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0, clip=(-1, 1), fill=True, alpha=0.6, linewidth=1.5)

# 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)

# 设置 x 轴范围
g.set(xlim=(0.5, 1))

# 美化图像
g.figure.subplots_adjust(hspace=-0.1, left=0.05, right=0.95, top=0.95, bottom=0.05)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.set_xlabels('KGESS', fontsize=fontsize)
for ax in g.axes.flat:
    ax.tick_params(axis='x', labelsize=fontsize)

# 添加左侧 Simulation 标签和中位线+中位数标签
for ax, label in zip(g.axes.flat, df['Simulation'].unique()):
    # 添加左侧 Simulation 标签
    ax.text(
        x=0.5,
        y=1.2,
        s=label,
        fontsize=fontsize,
        ha='left',
        va='center',
        transform=ax.transData
    )
    # 获取当前 Simulation 的中位数
    median_val = medians[label]
    data = df[df['Simulation'] == label]['KGESS'].values
    kde = gaussian_kde(data, bw_method='scott')
    # # 生成高分辨率 x 值
    kde_x = np.linspace(-1,1, 1000)
    kde_y = kde(kde_x)
    height = np.interp(median_val, kde_x, kde_y)
    ax.vlines(median_val, 0, height, color='black', ls=':', lw=1.5)
    # 添加中位数标签
    ax.text(
        x=median_val,
        y=height,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='right',
        va='bottom',
        color='black',
        alpha=0.7,
        transform=ax.transData
    )

g.despine(bottom=True, left=True)

# 添加标题
plt.text(0.05, 1,'(d) Specific Humidity',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig3d_Q.jpg', dpi=300, bbox_inches='tight', transparent=True)
#endregion


#————————————————————————————————————————————————————————————
#region (e) surface air temperature
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

j = 4 
file_paths = [f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(2)]

# 整合所有数据为 DataFrame
all_data = []
for i in range(2):
    nc = Dataset(file_paths[i], 'r')
    if 'KGESS' not in nc.variables:
        raise KeyError(f"'KGESS' not found in {file_paths[i]}")
    data = nc.variables['KGESS'][:].flatten()
    data = data[~np.isnan(data)]
    if len(data) == 0:
        raise ValueError(f"No valid data in {file_paths[i]} after removing NaN")
    data = remove_outliers(data)
    data = np.where(data < -1, -1, data)
    data = data[(data >= -1) & (data <= 1)]
    label = sim_data[i]
    for val in data:
        all_data.append({'KGESS': val, 'Simulation': label})
    nc.close()

df = pd.DataFrame(all_data)

# 计算每个 Simulation 类别的中位数
medians = df.groupby('Simulation')['KGESS'].median().to_dict()

# 使用 seaborn 创建 ridgeline 图
pal = sns.cubehelix_palette(len(df['Simulation'].unique()), rot=-.25, light=.7)
g = sns.FacetGrid(df, row="Simulation", hue="Simulation", aspect=15, height=0.8, palette=pal)

# 设置画幅尺寸
g.figure.set_size_inches(10, 6)

# 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0, clip=(-1, 1), fill=True, alpha=0.6, linewidth=1.5)

# 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)

# 设置 x 轴范围
g.set(xlim=(0.5, 1))

# 美化图像
g.figure.subplots_adjust(hspace=-0.1, left=0.05, right=0.95, top=0.95, bottom=0.05)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.set_xlabels('KGESS', fontsize=fontsize)
for ax in g.axes.flat:
    ax.tick_params(axis='x', labelsize=fontsize)

# 添加左侧 Simulation 标签和中位线+中位数标签
for ax, label in zip(g.axes.flat, df['Simulation'].unique()):
    # 添加左侧 Simulation 标签
    ax.text(
        x=0.5,
        y=1.4,
        s=label,
        fontsize=fontsize,
        ha='left',
        va='center',
        transform=ax.transData
    )
    # 获取当前 Simulation 的中位数
    median_val = medians[label]
    data = df[df['Simulation'] == label]['KGESS'].values
    kde = gaussian_kde(data, bw_method='scott')
    # # 生成高分辨率 x 值
    kde_x = np.linspace(-1,1, 1000)
    kde_y = kde(kde_x)
    height = np.interp(median_val, kde_x, kde_y)
    ax.vlines(median_val, 0, height, color='black', ls=':', lw=1.5)
    # 添加中位数标签
    ax.text(
        x=median_val,
        y=height,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='right',
        va='bottom',
        color='black',
        alpha=0.7,
        transform=ax.transData
    )

g.despine(bottom=True, left=True)

# 添加标题
plt.text(0.05, 1,'(e) Air Temperature',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig3e_T.jpg', dpi=300, bbox_inches='tight', transparent=True)
# plt.show()
#endregion

#————————————————————————————————————————————————————————————————————————————————————————————————————————————
#region (f) surface wind speed
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})
#region (e) surface air temperature
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

j = 5 
file_paths = [f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(2)]

# 整合所有数据为 DataFrame
all_data = []
for i in range(2):
    nc = Dataset(file_paths[i], 'r')
    if 'KGESS' not in nc.variables:
        raise KeyError(f"'KGESS' not found in {file_paths[i]}")
    data = nc.variables['KGESS'][:].flatten()
    data = data[~np.isnan(data)]
    if len(data) == 0:
        raise ValueError(f"No valid data in {file_paths[i]} after removing NaN")
    data = remove_outliers(data)
    data = np.where(data < -1, -1, data)
    data = data[(data >= -1) & (data <= 1)]
    label = sim_data[i]
    for val in data:
        all_data.append({'KGESS': val, 'Simulation': label})
    nc.close()

df = pd.DataFrame(all_data)

# 计算每个 Simulation 类别的中位数
medians = df.groupby('Simulation')['KGESS'].median().to_dict()

# 使用 seaborn 创建 ridgeline 图
pal = sns.cubehelix_palette(len(df['Simulation'].unique()), rot=-.25, light=.7)
g = sns.FacetGrid(df, row="Simulation", hue="Simulation", aspect=15, height=0.8, palette=pal)

# 设置画幅尺寸
g.figure.set_size_inches(10, 6)

# 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0, clip=(-1, 1), fill=True, alpha=0.6, linewidth=1.5)

# 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)

# 设置 x 轴范围
g.set(xlim=(-1, 1))

# 美化图像
g.figure.subplots_adjust(hspace=-0.1, left=0.05, right=0.95, top=0.95, bottom=0.05)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.set_xlabels('KGESS', fontsize=fontsize)
for ax in g.axes.flat:
    ax.tick_params(axis='x', labelsize=fontsize)

# 添加左侧 Simulation 标签和中位线+中位数标签
for ax, label in zip(g.axes.flat, df['Simulation'].unique()):
    # 添加左侧 Simulation 标签
    ax.text(
        x=-1.0,
        y=0.3,
        s=label,
        fontsize=fontsize,
        ha='left',
        va='center',
        transform=ax.transData
    )
    # 获取当前 Simulation 的中位数
    median_val = medians[label]
    data = df[df['Simulation'] == label]['KGESS'].values
    kde = gaussian_kde(data, bw_method='scott')
    # # 生成高分辨率 x 值
    kde_x = np.linspace(-1,1, 1000)
    kde_y = kde(kde_x)
    height = np.interp(median_val, kde_x, kde_y)
    ax.vlines(median_val, 0, height, color='black', ls=':', lw=1.5)
    # 添加中位数标签
    ax.text(
        x=median_val-0.07,
        y=height*0.8,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='right',
        va='bottom',
        color='black',
        alpha=0.7,
        transform=ax.transData
    )

g.despine(bottom=True, left=True)

# 添加标题
plt.text(0.05, 1,'(f) Wind Speed',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig3f_WS.jpg', dpi=300, bbox_inches='tight', transparent=True)
# plt.show()
#endregion
'''