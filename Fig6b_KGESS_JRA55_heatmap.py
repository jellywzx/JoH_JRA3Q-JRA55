import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# 定义列名和行名
titles = ['ENF', 'EBF', 'DNF', 'DBF', 'MF', 'CSH', 'OSH', 'WSA', 'SAV', 'GRA', 'WET', 'CRO', 'URB', 'CVM', 'SNO', 'BSV', 'WAT', 'Overall']
variables = ['Net Radiation', 'Sensible Heat', 'Evapotranspiration', 'Surface \nSoil Moisture', 'Total Runoff']
labels = ['Rn','SH','ET','SSM','Tro']
cmaps = ['RdBu_r'] * len(variables)  # 每个变量使用相同的 colormap
font_size = 22
label_size = 20

# 读取数据
folder_path = 'C:/Users/fzjxw/Desktop/Datacomparison/Glb_0.25_0317/output/metrics/IGBP_groupby/'
folder = ['JRA3Q_0.25___CLARA_3', 'JRA55_0.25___CLARA_3',
          'JRA3Q_0.25___GLEAM4.2a_monthly', 'JRA55_0.25___GLEAM4.2a_monthly',
          'JRA3Q_0.25___GLEAM4.2a_monthly', 'JRA55_0.25___GLEAM4.2a_monthly',
          'JRA3Q_0.25___GLEAM4.2a_monthly', 'JRA55_0.25___GLEAM4.2a_monthly',
          'JRA3Q_0.25___GRUN_ENSEMBLE', 'JRA55_0.25___GRUN_ENSEMBLE']
file_lists = ['Net_Radiation_JRA3Q_0.25___CLARA_3_metrics.txt', 'Net_Radiation_JRA55_0.25___CLARA_3_metrics.txt',
              'Sensible_Heat_JRA3Q_0.25___GLEAM4.2a_monthly_metrics.txt', 'Sensible_Heat_JRA55_0.25___GLEAM4.2a_monthly_metrics.txt',
              'Evapotranspiration_JRA3Q_0.25___GLEAM4.2a_monthly_metrics.txt', 'Evapotranspiration_JRA55_0.25___GLEAM4.2a_monthly_metrics.txt',
              'Surface_Soil_Moisture_JRA3Q_0.25___GLEAM4.2a_monthly_metrics.txt', 'Surface_Soil_Moisture_JRA55_0.25___GLEAM4.2a_monthly_metrics.txt',
              'Total_Runoff_JRA3Q_0.25___GRUN_ENSEMBLE_metrics.txt', 'Total_Runoff_JRA55_0.25___GRUN_ENSEMBLE_metrics.txt']

# 创建一个空的 DataFrame 用于存储所有变量的 KGESS 差异
kgess_diff_df = pd.DataFrame(index=variables, columns=titles)

# 循环处理每对文件，计算 KGESS 差异
for k in range(0, len(file_lists), 2):
    file1, file2 = file_lists[k], file_lists[k + 1]
    folder1, folder2 = folder[k], folder[k + 1]
    var_name = variables[k // 2]  # 获取变量名

    # 读取 JRA55 数据
    csv_path = folder_path + folder2 + '/' + file2
    df = pd.read_csv(csv_path, sep='\s+', header=0)
    df = df[df['ID'] == 'KGESS'].iloc[:, 1:]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    if df.isna().any().any():
        print(f"Warning: NaN values in {file2}:\n", df.isna().sum())
    df2 = df
    kgess_diff_df.loc[var_name] = df2.values[0]

# 处理 NaN 和确保数据类型

kgess_diff_df = kgess_diff_df.fillna(0)  # 替换 NaN 为 0
kgess_diff_df = kgess_diff_df.astype(float)  # 强制转换为 float

# 设置绘图样式
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Times New Roman'

# 创建子图
fig, axes = plt.subplots(nrows=len(variables), ncols=1, figsize=(20, 5.5), sharex=True)

# 如果只有一个变量，axes 不是列表
if len(variables) == 1:
    axes = [axes]

# 为每一行绘制热图
for i, (var_name, ax) in enumerate(zip(variables, axes)):
    row_data = kgess_diff_df.loc[[var_name]]  # 保持 DataFrame 格式

    vmin = np.min(row_data)
    vmax = np.max(row_data)

    # 画热图但不加默认 colorbar
    heatmap = sns.heatmap(row_data, ax=ax, cmap='YlGnBu', annot=True, fmt=".3f", linewidths=1, annot_kws={'size': font_size-2.5},
                          cbar=False, vmin=0, vmax=1, yticklabels=False)

    # 设置 y 轴标签
    ax.set_yticks([0.5])
    ax.set_yticklabels([labels[i]], fontsize=28, rotation=0, va='center', ha='right')
    ax.tick_params(left=False)

    # 设置 x 轴标签（仅最后一个子图）
    if i == len(variables) - 1:
        ax.set_xticks([j + 0.5 for j in range(len(titles))])
        ax.set_xticklabels(titles, fontsize=28, rotation=90, ha='center')
        ax.tick_params(bottom=False,labelbottom=True)
    else:
        ax.set_xticks([])
        ax.tick_params(bottom=False,labelbottom=False)


cbar_ax = fig.add_axes([0.86, 0.15, 0.01, 0.7])  # [左, 底, 宽, 高]
cbar = fig.colorbar(heatmap.collections[0], cax=cbar_ax, orientation='vertical',
                    ticks=np.linspace(0,1,11)[::2], extend='both')
cbar.ax.tick_params(labelsize=font_size-2, direction='in', length=0)

# 设置标题和布局
fig.text(0.15, 0.98, '(b)', fontsize=35,va='top', ha='left')
plt.suptitle('KGESS of JRA-55', fontsize=35,)
fig.subplots_adjust(hspace=0, left=0.15, right=0.85)

# 保存图像
plt.savefig('C:/Users/fzjxw/Desktop/Datacomparison/Glb_0.25_0317/output/metrics/IGBP_groupby/KGESS_JRA-55.jpg',
            format='jpg', dpi=300, bbox_inches='tight')
# plt.show()

