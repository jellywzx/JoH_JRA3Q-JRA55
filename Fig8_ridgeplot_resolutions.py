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
fontsize=30
titlesize=40
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

titles = ["(a) Net Radiation", "(b) Sensible Heat", "(c) Evapotranspiration", 
          "(d) Surface Soil Moisture", "(e) Total Runoff", "(f) Streamflow"]
var = ['Net_Radiation', 'Sensible_Heat', 'Evapotranspiration', 'Surface_Soil_Moisture', 'Total_Runoff', 'Streamflow']
ref_data = ['CLARA_3', 'GLEAM4.2a_monthly', 'GLEAM4.2a_monthly', 'GLEAM4.2a_monthly', 'GRUN_ENSEMBLE' ,'GRDC']
sim_data = [ 'JRA3Q_1.0', 'JRA55_1.0','JRA3Q_0.5', 'JRA55_0.5','JRA3Q_0.25', 'JRA55_0.25',  ]
vmax = [0.6, 0.6, 1, 1, 2, 1]
vmin = [-0.6, -0.6, -1, -1, -2, -1]
folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/allvars_ridgeplot/'



#——————————————————————————————————————————————————————————————————————————
#region (a) Rn 
# 输入数据路径和标签
file_paths = [ f'{folder_path}/{var[0]}_ref_{ref_data[0]}_sim_{sim_data[k]}_KGESS.nc' for k in range(6)]
print(file_paths[1])

# 整合所有数据为 DataFrame
all_data = []
for i in range(6):
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
g.set(xlim=(0,1))

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
        x=0,
        y=0.6,
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
        x=median_val+0.03,
        y=height*0.4,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='left',
        va='bottom',
        color='black',
        transform=ax.transData
    )

g.despine(bottom=True, left=True)
plt.text(0.05, 1, '(a) Net Radiation', fontsize=titlesize, ha='left', va='top',transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig8a_Rn.jpg', dpi=300, bbox_inches='tight')
# plt.show()
#endregion


#————————————————————————————————————————————————————————————————————————————————
#region (b) SH
#Sensible Heat
j=1
file_paths = [ f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(6)]
print(file_paths[1])

# 整合所有数据为 DataFrame
all_data = []
for i in range(6):
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

g.figure.set_size_inches(10, 6)
# 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0,clip=(-1, 1),fill=True, alpha=0.6, linewidth=1.5, )

# 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)

# 设置 x 轴范围
g.set(xlim=(-1,1))

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
        x=-0.25,
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
    ax.text(
        x=median_val+0.05,
        y=height*0.4,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='left',
        va='bottom',
        color='black',
        transform=ax.transData
    )

g.despine(bottom=True, left=True)
plt.text(0.05, 1,'(b) Sensible Heat',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig8b_SH.jpg', dpi=300, bbox_inches='tight')
# plt.show()
#endregion
'''


#——————————————————————————————————————————————————————————————————————————————————————————————————————
#region (c) ET
j=2
file_paths = [ f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(6)]
print(file_paths[1])

# 整合所有数据为 DataFrame
all_data = []
for i in range(6):
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
g.set(xlim=(-1,1))

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
        x=-0.5,
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
        x=median_val+0.05,
        y=height*0.4,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='left',
        va='bottom',
        color='black',
        transform=ax.transData
    )

g.despine(bottom=True, left=True)
plt.text(0.05, 1,'(c) Evapotranspiration',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig8c_ET.jpg', dpi=300, bbox_inches='tight')
# plt.show()
#endregion


#——————————————————————————————————————————————————————————————————————
#region (d) SSM
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

j = 3 
file_paths = [f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(6)]

# 整合所有数据为 DataFrame
all_data = []
for i in range(6):
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
        x=-0.75,
        y=0.8,
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
        x=median_val + 0.05,
        y=height*0.4,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='left',
        va='bottom',
        color='black',
        alpha=0.7,
        transform=ax.transData
    )

g.despine(bottom=True, left=True)

# 添加标题
plt.text(0.05, 1,'(d) Surface Soil Moisture',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig8d_SSM.jpg', dpi=300, bbox_inches='tight', transparent=True)
#endregion


#————————————————————————————————————————————————————————————
#region (e) Total runoff 
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

j = 4 
file_paths = [f'{folder_path}/{var[j]}_ref_{ref_data[j]}_sim_{sim_data[k]}_KGESS.nc' for k in range(6)]

# 整合所有数据为 DataFrame
all_data = []
for i in range(6):
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
        x=-0.8,
        y=0.7,
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
        x=median_val + 0.05,
        y=height*0.1,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='left',
        va='bottom',
        color='black',
        alpha=0.7,
        transform=ax.transData
    )

g.despine(bottom=True, left=True)

# 添加标题
plt.text(0.05, 1,'(e) Total runoff',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)
# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig8e_Tro.jpg', dpi=300, bbox_inches='tight', transparent=True)
# plt.show()
#endregion


#————————————————————————————————————————————————————————————————————————————————————————————————————————————
#region (f) Streamflow
# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})

def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

sim_data = ['JRA3Q_cama_1.0', 'JRA55_cama_1.0','JRA3Q_cama_0.5', 'JRA55_cama_0.5','JRA3Q_cama_0.25', 'JRA55_cama_0.25', ]
labels = ['JRA3Q_1.0', 'JRA55_1.0','JRA3Q_0.5', 'JRA55_0.5','JRA3Q_0.25', 'JRA55_0.25',]
vmax = [0.6, 0.6, 1, 1, 2, 1]
vmin = [-0.6, -0.6, -1, -1, -2, -1]
folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/allvars_ridgeplot/'
file_paths = [f'{folder_path}/Streamflow_stn_GRDC_{sim_data[k]}_evaluations.csv' for k in range(6)]

# 整合所有数据为 DataFrame
all_data = []
for i in range(6):
# 从 CSV 文件读取 KGESS 列
    df_csv = pd.read_csv(file_paths[i])
    data = df_csv['KGESS'].dropna().values  # 提取 KGESS 列并移除 NaN
    data = remove_outliers(data)
    data = np.where(data < -1, -1, data)
    data = data[(data >= -1) & (data <= 1)]
    print(f"Simulation {sim_data[i]}: {len(data)} data points after filtering")
    label = labels[i]
    for val in data:
        all_data.append({'KGESS': val, 'Simulation': label})
df = pd.DataFrame(all_data)
# print(df)
# 计算每个 Simulation 类别的中位数
medians = df.groupby('Simulation')['KGESS'].median().to_dict()
# print(medians)

# # 使用 seaborn 创建 ridgeline 图
pal = sns.cubehelix_palette(len(df['Simulation'].unique()), rot=-.25, light=.7)
g = sns.FacetGrid(df, row="Simulation", hue="Simulation", aspect=15, height=0.8, palette=pal)
# # 设置画幅尺寸
g.figure.set_size_inches(10, 6)
# # 绘制 KDE 曲线
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0, clip=(-1, 1), fill=True, alpha=0.6, linewidth=1.5)
# # 添加 y=0 的参考线
g.refline(y=0, linewidth=2, linestyle="-", color="black", clip_on=False)
# # 设置 x 轴范围
g.set(xlim=(-1, 1))
# # 美化图像
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
        x=-0.75,
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

    ax.text(
        x=median_val + 0.05,
        y=height * 0.4,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='left',
        va='bottom',
        color='black',
        alpha=0.7,
        transform=ax.transData
    )

g.despine(bottom=True, left=True)

# # 添加标题
plt.text(0.05, 1,'(f) Streamflow',fontsize=titlesize, ha='left', va='top', transform=plt.gcf().transFigure)

# # 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Fig8f_Streamflow.jpg', dpi=300, bbox_inches='tight', transparent=True)
# plt.show()
# #endregion
'''