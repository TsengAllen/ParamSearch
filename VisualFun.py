#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:09:06 2023

@author: tsengallen
"""
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
top = mpl.colormaps['Greens']
bottom = mpl.colormaps['Reds']
newcolors = np.vstack((top(np.linspace(1, 0, 128)),bottom(np.linspace(0, 1, 128))))
newcmp = ListedColormap(newcolors, name='OrangeBlue')

def stripX(x):
    x = str(x)
    if x[-1] == '*':
        return x[:-1]
    return x

def selectCol(arr,s):
    arr = [i.split('_') for i in arr]
    result = [arr[0][0],arr[1][0]]
    for a in arr[2:]:
        judge = []
        for i in range(len(s)):
            if s[i] == 'all':
                judge += [True]
            else:
                judge += [a[i]==s[i]]
        if all(judge):
            result+=['_'.join(a)]
    return result

def plotHeat_window(aos,df,ind,st,im,fil,rd):
    newdf = df.loc[df['績效指標']==ind,selectCol(df.columns.to_list(),
                    [st,im,fil,rd])]
    dd = newdf.sort_index(ascending=False).set_index(['窗格比例']).iloc[:,1:]
    if aos == 'Rgv' or aos == 'Rga':
        cname = '標竿PR'
        c = ['100','99','95','90']
    else:
        cname = '延伸圈數'
        c = ['0','1','2','3']
    dd.index = ['51','41','31','21','11']
    if im != 'all' and fil != 'all':
        dd.columns = c
        dd.columns.name = cname
        t = '策略：{}，商品：{}，以{}篩選'.format(st,im,fil)
    elif fil == 'all':
        dd.columns = ['_'.join(i.split('_')[2:]) for i in dd.columns.to_list()]
        dd.columns.name = '篩選指標_'+cname
        t = '策略：{}，商品：{}'.format(st,im)
    elif im == 'all':
        dd.columns = [i.split('_')[1]+'_'+i.split('_')[3] for i in dd.columns.to_list()]
        dd.columns.name = '商品_'+cname
        t = '策略：{}，以{}篩選'.format(st,fil)
    if im != 'all' and fil != 'all':
        ro = 0
        ansize = 15
        figx = 14;figy = 6
        xlabel = dd.columns.name;ylabel = '窗格比例'
    else:
        ro = 0
        ansize = 12
        figx = 8;figy = 10
        ylabel = dd.columns.name;xlabel = '窗格比例'
        dd = dd.T.loc[:,['11','21','31','41','51']]
    fig, ax = plt.subplots(figsize=(figx, figy))
    sns.heatmap(dd,cmap=newcmp, center=0,annot=True, linewidth=.5, annot_kws={'rotation': ro ,'size':ansize})
    ax.set_xlabel(xlabel,fontsize=18,weight='bold',color= '#717e94')
    ax.set_ylabel(ylabel,fontsize=18,weight='bold',color= '#717e94')
    ax.tick_params(axis='both', which='major', labelsize=12,colors= '#717e94')
#     plt.title(t, fontsize=20,x=0.55,y=1.07,weight='bold')
    print(t)
    plt.tight_layout()
    name = './Result2/{}/{}/{}/{}.png'.format(st,st+'_'+im,aos,fil)
#     name = '../'+fil+'.png'
    plt.savefig(name,dpi=400)
    
def plotHeat_rd(aos,df,ind,st,im,fil,rd):
    newdf = df.loc[df['績效指標']==ind,selectCol(df.columns.to_list(),
                    [st,im,fil,rd])]
    if aos == 'Rgv' or aos == 'Rga':
        dd = newdf.sort_index(ascending=False).set_index(['標竿PR']).iloc[:,1:]
        dd.index = ['90','95','99','100']
        label = '標竿PR'
        clist = ['100','99','95','90']
    else:
        dd = newdf.sort_index(ascending=False).set_index(['延伸圈數']).iloc[:,1:]
        dd.index = ['3','2','1','0']
        label = '延伸圈數'
        clist = ['0','1','2','3']
    if im != 'all' and fil != 'all':
        dd.columns = [i.split('_')[-1] for i in dd.columns.to_list()]
        dd.columns.name = '窗格比例'
        t = '策略：{}，商品：{}，以{}篩選'.format(st,im,fil)
    elif fil == 'all':
        dd.columns = ['_'.join(i.split('_')[2:]) for i in dd.columns.to_list()]
        dd.columns.name = '篩選指標_窗格比例'
        t = '策略：{}，商品：{}'.format(st,im)
    elif im == 'all':
        dd.columns = [i.split('_')[1]+'_'+i.split('_')[3] for i in dd.columns.to_list()]
        dd.columns.name = '商品_窗格比例'
        t = '策略：{}，以{}篩選'.format(st,fil)
    if im != 'all' and fil != 'all':
        ro = 0
        ansize = 15
        figx = 14;figy = 6
        xlabel = dd.columns.name;ylabel = label
    else:
        ro = 0
        ansize = 12
        figx = 8;figy = 10
        ylabel = dd.columns.name;xlabel = label
        dd = dd.T.loc[:,clist]
    fig, ax = plt.subplots(figsize=(figx, figy))
    sns.heatmap(dd,cmap=newcmp, center=0, annot=True, linewidth=.5, annot_kws={'rotation': ro ,'size':ansize})
    ax.set_xlabel(xlabel,fontsize=18,weight='bold',color= '#717e94')
    ax.set_ylabel(ylabel,fontsize=18,weight='bold',color= '#717e94')
    ax.tick_params(axis='both', which='major', labelsize=12,colors= '#717e94')
#     plt.title(t, fontsize=20,x=0.55,y=1.07,weight='bold')
    print(t)
    plt.tight_layout()
    name = './Result2/{}/{}/{}/{}.png'.format(st,st+'_'+im,aos,'rd')
#     name = '../temp.png'
    plt.savefig(name,dpi=400)