#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 15:07:45 2023

@author: tsengallen
"""
import os
import pandas as pd
from ParamSearchClass import isdirAlive,Xmask,XXmask,aosTransform
stFile = input('請輸入策略名稱：')

#Profit 整理
stFileList = os.listdir('./Result')
stFileList.sort()
ProfitFileName = ['ChoseByPnL.csv', 'ChoseByMDD.csv', 'ChoseByMAR.csv']
TTestFileName = ['PnLTTest.csv', 'MDDTTest.csv', 'MARTTest.csv']
aosFile = ['Ave','Std','Rga','Rgv']
x = 0
num = []
IMFileList = os.listdir('./Result/'+stFile)
IMFileList.sort()
for IMFile in IMFileList[1:]:
    for aos in aosFile:
        
        path1 = './Result/'+stFile+'/'+IMFile+'/Profit'+aos+'/'
        path1test = './Result/'+stFile+'/'+IMFile+'/TTest'+aos+'/'
        path2 = './Result2/'+stFile+'/'+IMFile+'/'+aos+'/'
        isdirAlive(path2)
        x = 0
        for i,t in zip(ProfitFileName,TTestFileName):
            if x == 0:
                IND = i[7:-4]
                if IND == 'PnL':
                    IND = 'NetProfit'
                df = pd.read_csv(path1+i,encoding='cp950')
                df = df.loc[(df['Unnamed: 1']!='ISProfit')&(df['Unnamed: 1']!='WFE')]
                dfTTest = pd.read_csv(path1test+t,encoding='cp950')
                
                colname = IMFile+'_'+IND+'_'
                if aos == 'Rga' or aos == 'Rgv':
                    df.columns = ['窗格比例','績效指標','0-1',colname+'99',colname+'95',colname+'90']
                    dfTTest.columns = ['窗格比例','績效指標',colname+'99',colname+'95',colname+'90']
                else:
                    df.columns = ['窗格比例','績效指標','0-1',colname+'1',colname+'2',colname+'3']
                    dfTTest.columns = ['窗格比例','績效指標',colname+'1',colname+'2',colname+'3']


            else:
                IND = i[7:-4]
                if IND == 'PnL':
                    IND = 'NetProfit'
                dftemp = pd.read_csv(path1+i,encoding='cp950')
                dftemp = dftemp.loc[(dftemp['Unnamed: 1']!='ISProfit')&(dftemp['Unnamed: 1']!='WFE')]
                dfTTesttemp = pd.read_csv(path1test+t,encoding='cp950')
                colname = IMFile+'_'+IND+'_'
                if aos == 'Rga' or aos == 'Rgv':
                    dftemp.columns = ['窗格比例','績效指標','0-'+str(x+1),colname+'99',colname+'95',colname+'90']
                    dfTTesttemp.columns = ['窗格比例','績效指標',colname+'99',colname+'95',colname+'90']
                else:
                    dftemp.columns = ['窗格比例','績效指標','0-'+str(x+1),colname+'1',colname+'2',colname+'3']
                    dfTTesttemp.columns = ['窗格比例','績效指標',colname+'1',colname+'2',colname+'3']
        #                 dftemp.columns = ['window','績效指標',colname+'0',colname+'1',colname+'2',colname+'3']
                df = pd.concat([df,dftemp.iloc[:,2:]],axis = 1)
                dfTTest = pd.concat([dfTTest,dfTTesttemp.iloc[:,2:]],axis = 1)
            x+=1
            
        df.loc[df['績效指標']!='MAR',df.columns[2:]]=\
        df.loc[df['績效指標']!='MAR',df.columns[2:]].apply(lambda x:round(x/10000,2))
        count = 0
        
        #加入灰底之比例
        for row in [3,4,5,7,8,9,11,12,13]:
            a = count 
            if row < 6:
                top = 2
            elif row < 10:
                top = 6
            elif row < 14:
                top = 10
            for index in range(df.shape[0]):
                if df.iloc[index,1] != 'MDD':
                    if df.iloc[index,row] > df.iloc[index,top]:
                        count += 1
                else:
                    if df.iloc[index,row] < df.iloc[index,top]:
                        count += 1
            a = count - a
            df.loc['newrow',df.columns[row]] = str(int(round(a/15,2)*100))+'％'
        
        maskX = Xmask(dfTTest)
        maskX[['0-1','0-2','0-3']] = False
        maskX = maskX.iloc[:,[0,1,11,2,3,4,12,5,6,7,13,8,9,10]]
        maskXX = XXmask(dfTTest)
        maskXX[['0-1','0-2','0-3']] = False
        maskXX = maskXX.iloc[:,[0,1,11,2,3,4,12,5,6,7,13,8,9,10]]
        maskX = maskX.mask(maskXX,False)
        maskX.loc['newrow',:] = False 
        maskXX.loc['newrow',:] = False
        maskX = maskX.astype('bool')
        maskXX = maskXX.astype('bool')
        
        newindex = [i for i in range(15)]
        newindex += ['newrow']
        df.index = newindex

        df = df.mask(maskX,df.astype(str)+'*')
        df = df.mask(maskXX,df.astype(str)+'**')
        
        
        
        countList = []
        sigPosList = []
        sigNegList = []
        for row in [3,4,5,7,8,9,11,12,13]:     
            if row == 3:
                top = 2
                count = 0
                significantPos = 0
                significantNeg = 0
            elif row == 7:
                top = 6
                count = 0
                significantPos = 0
                significantNeg = 0
            elif row == 11:
                top = 10
                count = 0
                significantPos = 0
                significantNeg = 0
            for index in range(df.shape[0]-1):

                if df.iloc[index,1] != 'MDD':
                    if type(df.iloc[index,row])==str:
                        if float(df.iloc[index,row].replace('*','')) > df.iloc[index,top]:
                            significantPos += 1
                            count += 1
                        elif float(df.iloc[index,row].replace('*','')) < df.iloc[index,top]:
                            significantNeg += 1
                    elif df.iloc[index,row] > df.iloc[index,top]:
                        count += 1
                else:
                    if type(df.iloc[index,row])==str:
                        if float(df.iloc[index,row].replace('*','')) < df.iloc[index,top]:
                            significantPos += 1
                            count += 1
                        elif float(df.iloc[index,row].replace('*','')) > df.iloc[index,top]:
                            significantNeg += 1
                    elif df.iloc[index,row] < df.iloc[index,top]:
                        count += 1
            if row % 4 ==1:
                countList += [count]
                sigPosList += [significantPos]
                sigNegList += [significantNeg]

        profitTxt = '為{}之樣本外績效值，根據結果顯示，若以NetProfit進行篩選，共有{}個績效指標優於最佳點選擇法績效，佔總數的{}；在統計上顯著優於的有{}個，顯著劣於的有{}個。若以MDD進行篩選，共有{}個績效指標優於最佳點選擇法績效，佔總數的{}；在統計上顯著優於的有{}個，顯著劣於的有{}個。若以MAR進行篩選，共有{}個績效指標優於最佳點選擇法績效，佔總數的{}；在統計上顯著優於的有{}個，顯著劣於的有{}個。\
                    \n\n綜合上述結果，在135個績效指標中（NetProfit、MDD、MAR），共有{}個績效指標為{}優於最佳點選擇法，佔總數的{}；'\
        .format(aosTransform(aos),countList[0],str(int(round(countList[0]/45,2)*100))+'％',sigPosList[0],sigNegList[0]
               ,countList[1],str(int(round(countList[1]/45,2)*100))+'％',sigPosList[1],sigNegList[1]
               ,countList[2],str(int(round(countList[2]/45,2)*100))+'％',sigPosList[2],sigNegList[2]
               ,sum(countList),aosTransform(aos),str(int(round(sum(countList)/135,2)*100))+'％')
        f = open(path2+'profitTxt.txt', 'w')
        f.write(profitTxt)
        f.close()


        df.to_csv(path2+'profit.csv',encoding = 'cp950',index=False)
        
#ISProfit 整理
x = 0
num = []
IMFileList = os.listdir('./Result/'+stFile)
IMFileList.sort()
for IMFile in IMFileList[1:]:
    for aos in aosFile:
        
        path1 = './Result/'+stFile+'/'+IMFile+'/Profit'+aos+'/'
        path2 = './Result2/'+stFile+'/'+IMFile+'/'+aos+'/'
        isdirAlive(path2)
        x = 0

        for i in ProfitFileName:
            if x == 0:
                IND = i[7:-4]
                if IND == 'PnL':
                    IND = 'NetProfit'
                df = pd.read_csv(path1+i,encoding='cp950')
                df = df.loc[(df['Unnamed: 1']=='ISProfit')|(df['Unnamed: 1']=='WFE')]
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
                dftemp = dftemp.loc[(dftemp['Unnamed: 1']=='ISProfit')|(dftemp['Unnamed: 1']=='WFE')]
                colname = IMFile+'_'+IND+'_'
                if aos == 'Rga' or aos == 'Rgv':
                    dftemp.columns = ['窗格比例','績效指標',colname+'100',colname+'99',colname+'95',colname+'90']
                else:
                    dftemp.columns = ['窗格比例','績效指標',colname+'0',colname+'1',colname+'2',colname+'3']
        #                 dftemp.columns = ['window','績效指標',colname+'0',colname+'1',colname+'2',colname+'3']
                df = pd.concat([df,dftemp.iloc[:,2:]],axis = 1)
        
        countList = []
        for row in [3,4,5,7,8,9,11,12,13]:
             
            if row == 3:
                top = 2
                count = 0
            elif row == 7:
                top = 6
                count = 0
            elif row == 11:
                top = 10
                count = 0
            for index in range(df.shape[0]):
                if df.iloc[index,1] == 'WFE':
                    if df.iloc[index,row] > df.iloc[index,top]:
                        count += 1
            if row % 4 ==1:
                countList += [count]
            
        ISProfitTxt = '為{}之樣本內外績效比較，根據結果顯示，若以NetProfit進行篩選，共有{}個WFE優於最佳點選擇法，佔總數的{}。若以MDD進行篩選，共有{}個WFE優於最佳點選擇法，佔總數的{}。若以MAR進行篩選，共有{}個WFE優於最佳點選擇法，佔總數的{}。\
        \n\n在45個WFE中，共有{}個WFE為{}優於最佳點選擇法，佔總數的{}。'\
        .format(aosTransform(aos),countList[0],str(int(round(countList[0]/15,2)*100))+'％'
               ,countList[1],str(int(round(countList[1]/15,2)*100))+'％'
               ,countList[2],str(int(round(countList[2]/15,2)*100))+'％'
               ,sum(countList),aosTransform(aos),str(int(round(sum(countList)/45,2)*100))+'％')
        
        f = open(path2+'ISProfitTxt.txt', 'w')
        f.write(ISProfitTxt)
        f.close()
        
        df.loc[df['績效指標']=='ISProfit',df.columns[2:]]=\
        df.loc[df['績效指標']=='ISProfit',df.columns[2:]].apply(lambda x:round(x/10000,2))
        df.to_csv(path2+'ISprofit.csv',encoding = 'cp950',index=False)