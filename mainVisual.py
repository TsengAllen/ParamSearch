#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:15:28 2023

@author: tsengallen
"""

from VisualFun import *

stFile = input('請輸入策略名稱：')
aosFile = ['Ave','Std','Rga','Rgv']
ProfitFileName = ['ChoseByPnL.csv', 'ChoseByMDD.csv', 'ChoseByMAR.csv']

for aos in aosFile:
    x = 0
#     for stFile in stFileList[1:]:
    IMFileList = os.listdir('./Result/'+stFile)
    IMFileList.sort()
    for IMFile in IMFileList[1:]:
        path1 = './Result/'+stFile+'/'+IMFile+'/Profit'+aos+'/'
        for i in ProfitFileName:
            if x == 0:
                IND = i[7:-4]
                if IND == 'PnL':
                    IND = 'NetProfit'
                df = pd.read_csv(path1+i,encoding='cp950')
                df = df.loc[(df['Unnamed: 1']!='ISProfit')&(df['Unnamed: 1']!='WFE')]
                colname = IMFile+'_'+IND+'_'
                if aos == 'Rga' or aos == 'Rgv':
                    df.columns = ['窗格比例','績效指標',colname+'100',colname+'99',colname+'95',colname+'90']
                else:
                    df.columns = ['窗格比例','績效指標',colname+'0',colname+'1',colname+'2',colname+'3']
                x=1
            else:
                IND = i[7:-4]
                if IND == 'PnL':
                    IND = 'NetProfit'
                dftemp = pd.read_csv(path1+i,encoding='cp950')
                dftemp = dftemp.loc[(dftemp['Unnamed: 1']!='ISProfit')&(dftemp['Unnamed: 1']!='WFE')]
                colname = IMFile+'_'+IND+'_'
                if aos == 'Rga' or aos == 'Rgv':
                    dftemp.columns = ['窗格比例','績效指標',colname+'100',colname+'99',colname+'95',colname+'90']
                else:
                    dftemp.columns = ['窗格比例','績效指標',colname+'0',colname+'1',colname+'2',colname+'3']
#                 dftemp.columns = ['window','績效指標',colname+'0',colname+'1',colname+'2',colname+'3']
                df = pd.concat([df,dftemp.iloc[:,2:]],axis = 1)
    for i in range(df.shape[1]):
        if i>=2:
            df.iloc[:,i] = df.iloc[:,i].apply(lambda x:(float(stripX(x))))
    
    for IM in ['FITXN','FITE','FITF','FIXI']:
        for i in ['NetProfit','MDD','MAR','all']:
            plotHeat_window(aos,df,'MAR',stFile,IM,i,'all')
            

for aos in aosFile:
    x = 0
    IMFileList = os.listdir('./Result/'+stFile)
    IMFileList.sort()
    for IMFile in IMFileList[1:]:
        path1 = './Result/'+stFile+'/'+IMFile+'/Profit'+aos+'/'
        for i in ProfitFileName:
            if x == 0:
                IND = i[7:-4]
                if IND == 'PnL':
                    IND = 'NetProfit'
                df = pd.read_csv(path1+i,encoding='cp950')
                df = df.loc[(df['Unnamed: 1']!='ISProfit')&(df['Unnamed: 1']!='WFE')]
                df = df.set_index(['Unnamed: 0','Unnamed: 1']).unstack().T.reset_index(level=1).reset_index(level=0)
                df.index.name = None;df.columns.name = None
                colname = IMFile+'_'+IND+'_'
                if aos == 'Rgv' or aos == 'Rga':
                    df.columns = ['標竿PR','績效指標',colname+'11',colname+'21',colname+'31',colname+'41',colname+'51']
                else:
                    df.columns = ['延伸圈數','績效指標',colname+'11',colname+'21',colname+'31',colname+'41',colname+'51']
                x=1
            else:
                IND = i[7:-4]
                if IND == 'PnL':
                    IND = 'NetProfit'
                dftemp = pd.read_csv(path1+i,encoding='cp950')
                dftemp = dftemp.loc[(dftemp['Unnamed: 1']!='ISProfit')&(dftemp['Unnamed: 1']!='WFE')]
                dftemp = dftemp.set_index(['Unnamed: 0','Unnamed: 1']).unstack().T.reset_index(level=1).reset_index(level=0)
                dftemp.index.name = None;dftemp.columns.name = None
                colname = IMFile+'_'+IND+'_'
                if aos == 'Rgv' or aos == 'Rga':
                    dftemp.columns = ['標竿PR','績效指標',colname+'11',colname+'21',colname+'31',colname+'41',colname+'51']
                else:
                    dftemp.columns = ['延伸圈數','績效指標',colname+'11',colname+'21',colname+'31',colname+'41',colname+'51']
#                 dftemp.columns = ['圈數','績效指標',colname+'11',colname+'21',colname+'31',colname+'41',colname+'51']
                df = pd.concat([df,dftemp.iloc[:,2:]],axis = 1)
    for i in range(df.shape[1]):
        if i>=2:
            df.iloc[:,i] = df.iloc[:,i].apply(lambda x:(float(stripX(x))))
            
    for IM in ['FITXN','FITE','FITF','FIXI']:
        plotHeat_rd(aos,df,'MAR',stFile,IM,'all','all')