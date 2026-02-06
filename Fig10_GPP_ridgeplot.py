import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from scipy.stats import gaussian_kde

# sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0), "axes.labelsize": 10, "axes.labelcolor": "black"})
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 25  # Default font size for consistency
plt.rcParams['axes.labelsize'] = 25  # Font size for axis labels
plt.rcParams['axes.titlesize'] = 30  # Font size for titles
plt.rcParams['xtick.labelsize'] = 25  # Font size for x-axis ticks
plt.rcParams['ytick.labelsize'] = 25  # Font size for y-axis ticks (if used)

# Update Seaborn theme to ensure compatibility
sns.set_theme(style="white", rc={
    "axes.facecolor": (0, 0, 0, 0),
    "axes.labelsize": 25,
    "axes.labelcolor": "black",
    "axes.labelweight": "normal",  # Ensure normal weight for Times New Roman
    "font.family": "Times New Roman",
    "xtick.labelsize": 25
})
fontsize=25


def remove_outliers(data_array):
    q1, q3 = np.percentile(data_array, [5, 95])
    return data_array[(data_array >= q1) & (data_array <= q3)]

# 输入数据路径和标签
file_paths = [
    ('C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_BGC_diff_noLAI/output/metrics/'
     'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_sim_JRA3Q_0.25_noBGC_KGESS.nc', 'JRA3Q_noBGC'),
    ('C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_BGC_diff_noLAI/output/metrics/'
     'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_sim_JRA55_0.25_noBGC_KGESS.nc', 'JRA55_noBGC'),
    ('C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_BGC_diff_noLAI/output/metrics/'
     'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_sim_JRA3Q_0.25_BGC_KGESS.nc', 'JRA3Q_BGC_LAIoff'),
    ('C:/Users/fzjxw/Desktop/Datacomparison/BGC/US_0.25_BGC_diff_noLAI/output/metrics/'
     'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_sim_JRA55_0.25_BGC_KGESS.nc', 'JRA55_BGC_LAIoff'),
    ('C:/Users/fzjxw/Desktop/Datacomparison/US_0.25_LAI_diff/output/metrics/'
     'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_sim_JRA3Q_0.25_LAI_KGESS.nc', 'JRA3Q_BGC_LAIon'),
    ('C:/Users/fzjxw/Desktop/Datacomparison/US_0.25_LAI_diff/output/metrics/'
     'Gross_Primary_Productivity_ref_FLUXCOM-X-BASE_monthly_sim_JRA55_0.25_LAI_KGESS.nc', 'JRA55_BGC_LAIon'),
]

# 整合所有数据为 DataFrame
all_data = []
for path, label in file_paths:
    nc = Dataset(path, 'r')
    if 'KGESS' not in nc.variables:
        raise KeyError(f"'KGESS' not found in {path}")
    data = nc.variables['KGESS'][:].flatten()
    data = data[~np.isnan(data)]
    data = remove_outliers(data)
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
g.map(sns.kdeplot, "KGESS", bw_adjust=1.0, clip_on=False, fill=True, alpha=0.6, linewidth=1.5)

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
        x=df['KGESS'].min()-0.1,
        y=0.5,
        s=label,
        fontsize=fontsize,
        ha='right',
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
    # ax.axvline(x=median_val, ymin=0, ymax=0.5, color='black', linestyle='--', linewidth=1.5, clip_on=False)
    # 添加中位数标签
    ax.text(
        x=median_val+0.05,
        y=0.1,
        s=f'{median_val:.2f}',
        fontsize=fontsize,
        ha='left',
        va='bottom',
        color='black',
        transform=ax.transData
    )

g.despine(bottom=True, left=True)

# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/study/BaiduSyncdisk/JRA3Q&JRA55/plot_code/Figure10_seaborn.jpg', dpi=300, bbox_inches='tight')
plt.show()