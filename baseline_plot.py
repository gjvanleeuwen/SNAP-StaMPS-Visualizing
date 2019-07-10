import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

year = '2018'
title = 'Baseline_chart'

asc_folder = 'E:\\Thesis\\1_insar_data\\ascending\\90_222\\' + year + '\\'
desc_folder_1 = 'E:\\Thesis\\1_insar_data\\descending\\25_365_366\\' + year + '\\'
desc_folder_2 = 'E:\\Thesis\\1_insar_data\\descending\\127_366_367_368\\' + year + '\\'
path_list = [asc_folder, desc_folder_1, desc_folder_2]

for path in path_list:
    base_path = path
    text_path = base_path + 'baselines.txt'


    data = np.loadtxt(text_path, usecols=(1,2))
    date_tag =np.loadtxt(text_path, dtype= str, usecols =(0,1))
    date_tag = date_tag[:,0]
    temp_baseline = data[:,1]
    perp_baseline = data[:,0]


    # plt.scatter(temp_baseline,perp_baseline)


    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.scatter(temp_baseline,perp_baseline, label='True Position')

    # Iterate over each point, and plot the line.
    for x, y in zip(temp_baseline,perp_baseline):
        ax.plot([x, 0.00], [y, 0.00], 'b', linewidth=0.5, markersize=12)

    for label, x, y in zip(date_tag,temp_baseline,perp_baseline ):
        plt.annotate(
            label[2:-1],
            xy=(x, y), xytext=(-5,30),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict( fc='blue', alpha=0.1),
            arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

    # fig.suptitle(title, fontsize=15)
    plt.xlabel('Temporal baseline(days)', fontsize=10)
    plt.ylabel('Perpendicular baseline(m)', fontsize=10)
    fig.savefig(base_path+title+'.jpg')

    #  boxstyle='round,pad=0.5',
    plt.show()