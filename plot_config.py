#coding:utf-8
'''

设置画图的一系列问题

'''

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors
from cycler import cycler
import pylab
import numpy as np


#### 显示中文的设置
# reload(sys)
# sys.setdefaultencoding('utf-8')
# mpl.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
# mpl.rcParams['axes.unicode_minus'] = False


ALL_MARKERS = ['-o','-v','-^','-s','-p','-P','-*','-h','-H','-<','-+','-x','-X','->','-D','-d','-|','-1','-2','-3','-4','-8']

## 最大的chunksize
mpl.rcParams['agg.path.chunksize'] = 10000

# 颜色循环，取代默认的颜色
color_sequence = ['#1f77b4',  '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#c5b0d5',
                '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5', '#aec7e8', '#ffbb78','#98df8a', '#ff9896']

mpl.rcParams['axes.prop_cycle'] = cycler('color', color_sequence)

## 用特定的color theme进行画图
# color = plt.cm.viridis(np.linspace(0.1,0.9,6)) # This returns RGBA; convert:
# hexcolor = map(lambda rgb:'#%02x%02x%02x' % (rgb[0]*255,rgb[1]*255,rgb[2]*255),
#                tuple(color[:,0:-1]))

# mpl.rcParams['axes.prop_cycle'] = cycler('color', hexcolor)

## 画图各种参数的大小
params = {'legend.fontsize': 10,
        'axes.labelsize': 12,
        'axes.titlesize':17,
        'xtick.labelsize':12,
        'ytick.labelsize':12}

pylab.rcParams.update(params)

'''
==================
## 画柱状图时进行自动标签
==================
'''
def autolabel(rects,ax,total_count=None,step=1,):
    """
    Attach a text label above each bar displaying its height
    """
    for index in np.arange(len(rects),step=step):
        rect = rects[index]
        height = rect.get_height()
        # print height
        if not total_count is None:
            ax.text(rect.get_x() + rect.get_width()/2., 1.005*height,
                '{:}\n({:.6f})'.format(int(height),height/float(total_count)),
                ha='center', va='bottom')
        else:
            ax.text(rect.get_x() + rect.get_width()/2., 1.005*height,
                '{:}'.format(int(height)),
                ha='center', va='bottom')





def plot_line_from_data(fig_data,ax=None):

    xs = fig_data['x']
    ys = fig_data['y']
    title = fig_data.get('title',None)
    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    marker = fig_data['marker']
    xscale = fig_data.get('xscale','linear')
    yscale = fig_data.get('yscale','linear')

    xtick = fig_data.get('xtick',False)


    if ax is None:

        plt.plot(xs,ys,marker)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xscale(xscale)
        plt.yscale(yscale)
        if title is not None:
            plt.title(title)

        if xtick:
            plt.xticks(xs,xs)

        plt.tight_layout()

    else:

        ax.plot(xs,ys,marker)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if title is not None:
            ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        if xtick:
            ax.set_xticks(xs)
            ax.set_xticklabels(xs)

def plot_scatter_from_data(fig_data,ax=None):

    xs = fig_data['x']
    ys = fig_data['y']
    title = fig_data.get('title',None)
    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    marker = fig_data['marker']
    xscale = fig_data.get('xscale','linear')
    yscale = fig_data.get('yscale','linear')

    xtick = fig_data.get('xtick',False)


    if ax is None:

        plt.scatter(xs,ys,marker=marker)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xscale(xscale)
        plt.yscale(yscale)
        if title is not None:
            plt.title(title)

        if xtick:
            plt.xticks(xs,xs)

        plt.tight_layout()

    else:

        ax.scatter(xs,ys,marker=marker)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if title is not None:
            ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        if xtick:
            ax.set_xticks(xs)
            ax.set_xticklabels(xs)



def plot_bar_from_data(fig_data,ax=None):

    xs = fig_data['x']
    ys = fig_data['y']
    title = fig_data.get('title',None)
    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    xscale = fig_data.get('xscale',None)
    yscale = fig_data.get('yscale',None)


    if ax is None:
        # print xs,ys

        # max_y = np.max(ys)

        plt.bar(np.arange(len(xs)),ys,align='center',width=0.6)
        plt.xticks(np.arange(len(xs)),xs)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)


        if xscale is not None:
            plt.xscale(xscale)

        if yscale is not None:
            plt.yscale(yscale)
        else:
            plt.yticks(range(0,np.max(ys)+1),[str(j) for j in range(0,np.max(ys)+1)])


        if title is not None:
            plt.title(title)
        plt.tight_layout()

    else:
        # print xs
        ax.bar(xs,ys,align='center',width=0.6)
        ax.set_xticks(xs)
        ax.set_xticklabels([str(x) for x in xs])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if title is not None:
            ax.set_title(title)
        if xscale is not None:

            ax.set_xscale(xscale)

        if yscale is not None:

            ax.set_yscale(yscale)



def plot_multi_lines_from_data(fig_data,ax=None):

    xs = fig_data['x']
    yses = fig_data['ys']
    title = fig_data.get('title',None)

    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    markers = fig_data['markers']
    labels = fig_data['labels']
    xscale = fig_data.get('xscale','linear')
    yscale = fig_data.get('yscale','linear')


    if ax is None:
        for i,ys in enumerate(yses):
            plt.plot(xs,ys,markers[i],label=labels[i])

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xscale(xscale)
        plt.yscale(yscale)
        if title is not None:
            plt.title(title)
        plt.legend()
        plt.tight_layout()

    else:
        for i,ys in enumerate(yses):
            ax.plot(xs,ys,markers[i],label=labels[i])

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if title is not None:
            ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        ax.legend()


def plot_multi_lines_from_two_data(fig_data,ax=None):

    xses = fig_data['xs']
    yses = fig_data['ys']
    title = fig_data.get('title',None)
    xlabel = fig_data['xlabel']
    ylabel = fig_data['ylabel']
    markers = fig_data['markers']
    labels = fig_data['labels']
    xscale = fig_data.get('xscale','linear')
    yscale = fig_data.get('yscale','linear')

    if ax is None:
        for i,ys in enumerate(yses):
            plt.plot(xses[i],ys,markers[i],label=labels[i])

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xscale(xscale)
        plt.yscale(yscale)
        if title is not None:

            plt.title(title)
        plt.legend()
        plt.tight_layout()

    else:
        for i,ys in enumerate(yses):
            ax.plot(xses[i],ys,markers[i],label=labels[i])

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if title is not None:
            ax.set_title(title)
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        ax.legend()


def hist_2_bar(data,bins=50):
    n,bins,patches = plt.hist(data,bins=bins)
    return [x for x in bins[:-1]],[x for x in n]

