#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:27:05 2023

@author: tsengallen
"""
from ParamSearchClass import *

STIMPnLFolder = os.listdir('./BackTestData')
STIMPnLFolder.sort()

#輸入你要的策略名稱
STName = input('輸入策略名稱：')

#讀取每一績效檔
for filename in selectFile(STName,STIMPnLFolder):
    nameSplit = filename.split('_')
    STName = nameSplit[0]
    IMName = nameSplit[1]
    ParamNum = int(nameSplit[2][0])
    filename = './BackTestData/' + filename
    #原始檔處理
    OringinData = pd.read_csv(filename)
    colName = OringinData.columns.to_list()
    OringinData.set_index(colName[-ParamNum:],inplace=True)
    colDate = [datetime.datetime.strptime(i,'%Y-%m-%d %H:%M:%S').date() for i in colName[:-ParamNum]]
    colYear = [i.year for i in colDate]
    colTuples = list(zip(colYear,colDate))
    multiCol = pd.MultiIndex.from_tuples(colTuples,names=['Year','Date'])
    OringinData.columns = multiCol
    #買進持有報酬
    BnHPath = './BnHPnL/BnH'+'_'+IMName+'.csv'
    BnH = pd.read_csv(BnHPath)
    BnH = BnH.set_index(BnH.columns[0])
    IndicTTest = {'PnLTTest':[],'MDDTTest':[],'MARTTest':[]}
    IndicProfit = {'ChoseByPnL':[],'ChoseByMDD':[],'ChoseByMAR':[]}
    for rd in range(1,4):
        TTestDic = {'PnLTTest':[],'MDDTTest':[],'MARTTest':[]}
        ProfitDic = {'ChoseByPnL':[],'ChoseByMDD':[],'ChoseByMAR':[]}
        for i in range(1,6):
            IS = i
            OOS = 1

            d = data(OringinData,BnH,IS,OOS,ParamNum)
            d.ApplyAve(rd)
            prodata = ProfitData(d,rd)
            prodata.ApplyAve()

            TTestDic['PnLTTest'] += [GETTtestDF(prodata.PnLAveYBY,prodata.PnLTopYBY,IS,OOS,rd)]
            TTestDic['MDDTTest'] += [GETTtestDF(prodata.MDDAveYBY,prodata.MDDTopYBY,IS,OOS,rd)]
            TTestDic['MARTTest'] += [GETTtestDF(prodata.MARAveYBY,prodata.MARTopYBY,IS,OOS,rd)]
            
            if rd == 1:
                prodata.PnLTop.columns = ['圈數：0'];prodata.MDDTop.columns = ['圈數：0'];prodata.MARTop.columns = ['圈數：0']
                ProfitDic['ChoseByPnL'] += [pd.concat([prodata.PnLTop,prodata.PnLAve],axis = 1)]
                ProfitDic['ChoseByMDD'] += [pd.concat([prodata.MDDTop,prodata.MDDAve],axis = 1)]
                ProfitDic['ChoseByMAR'] += [pd.concat([prodata.MARTop,prodata.MARAve],axis = 1)]
            else:
                ProfitDic['ChoseByPnL'] += [prodata.PnLAve]
                ProfitDic['ChoseByMDD'] += [prodata.MDDAve]
                ProfitDic['ChoseByMAR'] += [prodata.MARAve]
                
            print(IMName,IS,OOS,rd)
        #分別輸出三個不同指標篩選的TTest
        for key,values in TTestDic.items():
            df = pd.concat(values)
            IndicTTest[key] += [df]
        for key,values in ProfitDic.items():
            df = pd.concat(values)
            IndicProfit[key] += [df]
    #將不同權重組合起來
    for key,values in IndicTTest.items():
        df = pd.concat(values,axis = 1)
        name = './Result/' + STName + '/'+ STName +'_'+IMName+'/TTestAve/'
        isdirAlive(name)
        name += key + '.csv'
        df.to_csv(name,encoding = 'cp950')
    for key,values in IndicProfit.items():
        df = pd.concat(values,axis = 1)
        name = './Result/' + STName + '/'+ STName +'_'+IMName+'/ProfitAve/'
        isdirAlive(name)
        name += key + '.csv'
        df.to_csv(name,encoding = 'cp950')
