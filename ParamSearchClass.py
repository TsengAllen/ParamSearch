#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:19:11 2023

@author: tsengallen
"""

import pandas as pd
import numpy as np
import datetime
import scipy.stats
import os

#TTest
def GETTtestDF(df1,df2,IS,OOS,rd):
    IOSname = 'IS：'+str(IS)+'，OOS：'+str(OOS)
    multiIndex = pd.MultiIndex(levels=[[IOSname], ['淨利','MDD','MAR']], codes=[[0,0,0], [0,1,2]])
    colname = '圈數：'+str(rd)
    TTestDF = pd.DataFrame(index = multiIndex,columns = [colname])
    x = 0
    for i in [2,4,6]:
        t,p = scipy.stats.ttest_rel(df1.iloc[:,i],df2.iloc[:,i])
        TTestDF.iloc[x,0] = significance(x,t,p)
        x += 1
    return TTestDF
def significance(x,t,p):
    if p < 0.05:
        tt = str(round(t,3))+'**'
        return tt
    elif p < 0.1:
        tt = str(round(t,3))+'*'
        return tt
    else:
        return round(t,3)

#BnHProfit
def getBnHProfit(IS,BnH):
    start = str(int(BnH.iloc[0].name[:4]) + IS) + '-01-01'
    y = int(BnH.iloc[-1].name[:4]) - int(BnH.iloc[0].name[:4]) + 1 - IS
    dfBnH = BnH.loc[start:]
    PnL = dfBnH.sum()
    MDD = getMDD(dfBnH)
    MAR = (PnL/y)/MDD
    return PnL.values[0]/10000,MDD.values[0]/10000,MAR.values[0]

def getMDD(df):
    CumDf = df.cumsum()
    MaxCap = CumDf.cummax()
    DD = MaxCap - CumDf
    MDD = DD.cummax()
    return MDD.iloc[-1]


def isdirAlive(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def verifyDF(name):
    df = pd.read_csv(name,encoding = 'cp950')
    df = df.set_index(df.columns.to_list()[0:2])
    for i in range(df.shape[1]):
        df.iloc[:,i] = df.iloc[:,i].apply(lambda x: str(x)[-1])
    df = df.groupby(level = 0).apply(lambda x : np.sum(x))
    for i in range(df.shape[1]):
        df.iloc[:,i] = df.iloc[:,i].apply(lambda x: countStar(x))
    return df

def countStar(x):
    result = 0
    for i in x:
        if i == '*':
            result += 1
    if result >= 2:
        return True
    else:
        return False
#檔案搜尋
def selectFile(key,list1): 
    list2 = []
    for i in list1:
        if i[:len(key)] == key:
            list2 += [i]
    return list2

#後期整理所需
def Xmask(df):
    df = df.copy()
    for i in range(df.shape[1]):
        df.iloc[:,i] = df.iloc[:,i].apply(lambda x: str(x)[-1])
    return df=='*'
def XXmask(df):
    df = df.copy()
    for i in range(df.shape[1]):
        df.iloc[:,i] = df.iloc[:,i].apply(lambda x: str(x)[-2:])
    return df=='**'
def aosTransform(aos):
    if aos == 'Ave':
        return '權重選擇法'
    elif aos == 'Std':
        return '標準差選擇法'
    elif aos == 'Rga':
        return '島嶼面積選擇法'
    elif aos == 'Rgv':
        return '島嶼體積選擇法'
    

class data():
    def __init__(self,OringinData,BnH,IS,OOS,ParamNum):
        self.OringinData = OringinData
        self.YearsData = self.OringinData.groupby(level = 0, axis = 1).sum()
        self.BnH = BnH
        self.IS = IS
        self.OOS = OOS
        self.ParamNum = ParamNum

    #IS & OOS Data
    def getIntervalColName(self,colList,windowsize):
        newcolList = []
        if windowsize == 1:
            for col in colList:
                name = str(col)
                newcolList += [name]
        else:
            windowsize -= 1
            for col in colList:
                name = str(col-windowsize)+'-'+str(col)
                newcolList += [name]
        return newcolList

    def GETISData(self):
        df = self.YearsData.copy()
        colList = df.columns.to_list()
        newcolList = self.getIntervalColName(colList,self.IS)
        df = df.rolling(self.IS,axis = 1).sum()
        df.columns = newcolList
        df = df.iloc[:,(self.IS-1):-self.OOS]
        return df
    
    def GETOOSData(self):
        df = self.YearsData.copy()
        colList = df.columns.to_list()
        newcolList = self.getIntervalColName(colList,self.OOS)
        df = df.rolling(self.OOS,axis = 1).sum()
        df.columns = newcolList
        if self.OOS == 1:
            df = df.iloc[:,self.IS:]
        else:
            df = df.iloc[:,(self.IS+1):]
        return df

    #ISMDD
    def getMDDDF(self,df):
        CumDf = df.cumsum(axis = 1)
        MaxCap = CumDf.cummax(axis = 1)
        DD = MaxCap - CumDf
        MDD = DD.cummax(axis = 1)
        return MDD.iloc[:,-1]

    def GETMDDData(self):
        ColList = [i.split('-') for i in self.ISData.columns.to_list()]
        for i,col in enumerate(ColList):
            if len(col) == 1:
                start = int(col[0])
                end = int(col[0])
                colname = str(start)
            else:
                start = int(col[0])
                end = int(col[1])
                colname = str(start)+'-'+str(end)
            if i == 0:
                df = pd.DataFrame(self.getMDDDF(self.OringinData.loc[:,start:end]))
                df.columns = [colname]
            else:
                df[colname] = self.getMDDDF(self.OringinData.loc[:,start:end])
        return df
    
    #ISRGarea
    def GETRGAData(self,df,quant,HL):
        df = df.copy()
        for i in range(df.shape[1]):
            RG = regionGrow(df.iloc[:,i],quant,HL,self.ParamNum).ApplyRegionGrow()
            RG.mask(RG == 0,np.nan,inplace=True)
            df.iloc[:,i].where(RG == RG.value_counts().index[0],np.nan,inplace=True)
        return df
    
    #ISRGvolume
    def getRGVID(self,RG,df,HL):
        IDnMean = []
        if HL == 'H':
            #idx是RG的編號
            for idx in RG.value_counts().index.to_list():
                if RG.value_counts()[idx]:
                    IDnMean += [(idx,df.loc[RG == idx].sum())]
        elif HL == 'L':
            #idx是RG的編號
            for idx in RG.value_counts().index.to_list():
                if RG.value_counts()[idx]:
                    IDnMean += [(idx,np.divide(idx,df.loc[RG == idx].sum(), out=np.zeros_like(idx), where=df.loc[RG == idx].sum()!=0))]
                    
        v,i = max((val,idx) for idx,val in IDnMean)
        return i
        
    def GETRGVData(self,df,quant,HL):
        df = df.copy()
        for i in range(df.shape[1]):
            RG = regionGrow(df.iloc[:,i],quant,HL,self.ParamNum).ApplyRegionGrow()
            RG.mask(RG == 0,np.nan,inplace=True)
            RGVID = self.getRGVID(RG,df.iloc[:,i],HL)
            df.iloc[:,i].where(RG == RGVID,np.nan,inplace=True)
        return df

    def ApplyAve(self,rd):
        self.OOSData = self.GETOOSData()
        
        self.ISData = self.GETISData()
        self.ISMDDData = self.GETMDDData()
        self.ISMARData = np.divide(self.ISData,self.ISMDDData, out=np.zeros_like(self.ISData), where=self.ISMDDData!=0)

        ASD = AveStdData(self.ISData,self.ParamNum)
        self.PnLaveData = ASD.GETAverageData(self.ISData,rd)
        self.MDDaveData = ASD.GETAverageData(self.ISMDDData,rd)
        self.MARaveData = ASD.GETAverageData(self.ISMARData,rd)
        
    def ApplyStd(self,rd):
        self.OOSData = self.GETOOSData()
        
        self.ISData = self.GETISData()
        self.ISMDDData = self.GETMDDData()
        self.ISMARData = np.divide(self.ISData,self.ISMDDData, out=np.zeros_like(self.ISData), where=self.ISMDDData!=0)

        ASD = AveStdData(self.ISData,self.ParamNum)
        self.PnLstdData = ASD.GETStdData(self.ISData,rd)
        self.MDDstdData = ASD.GETStdData(self.ISMDDData,rd)
        self.MARstdData = ASD.GETStdData(self.ISMARData,rd)
        
    def ApplyRGA(self,quant):
        self.OOSData = self.GETOOSData()
        
        self.ISData = self.GETISData()
        self.ISMDDData = self.GETMDDData()
        self.ISMARData = np.divide(self.ISData,self.ISMDDData, out=np.zeros_like(self.ISData), where=self.ISMDDData!=0)

        self.PnLrgaData = self.GETRGAData(self.ISData,quant,'H')
        self.MDDrgaData = self.GETRGAData(self.ISMDDData[self.ISMDDData>0],quant,'L')
        self.MARrgaData = self.GETRGAData(self.ISMARData,quant,'H')
    def ApplyRGV(self,quant):
        self.OOSData = self.GETOOSData()
        
        self.ISData = self.GETISData()
        self.ISMDDData = self.GETMDDData()
        self.ISMARData = np.divide(self.ISData,self.ISMDDData, out=np.zeros_like(self.ISData), where=self.ISMDDData!=0)

        self.PnLrgvData = self.GETRGVData(self.ISData,quant,'H')
        self.MDDrgvData = self.GETRGVData(self.ISMDDData[self.ISMDDData>0],quant,'L')
        self.MARrgvData = self.GETRGVData(self.ISMARData,quant,'H')

class ProfitData():
    def __init__(self,data,cname):
        self.data = data
        self.cname = cname
    def getMDD(self,df):
        CumDf = df.cumsum()
        MaxCap = CumDf.cummax()
        DD = MaxCap - CumDf
        MDD = DD.cummax()
        return MDD.iloc[-1]

    def getSE(self,st):
        if len(st) == 4:
            return int(st),int(st)
        else:
            arr = [int(i) for i in st.split('-')]
            return arr[0], arr[1]

    def getFinalDF(self,ISMaxParam):
        array = [['param','淨利','淨利','MDD','MDD','MAR','MAR'],['MA1,MA2','IS','OOS','IS','OOS','IS','OOS']]
        colTuples = list(zip(*array))
        multiCol = pd.MultiIndex.from_tuples(colTuples)
        rowTuples = list(zip(self.data.ISData.columns.to_list(),self.data.OOSData.columns.to_list()))
        multiRow = pd.MultiIndex.from_tuples(rowTuples,name = ['IS','OOS'])
        FinalDF = pd.DataFrame(index = multiRow,columns = multiCol)
        FinalDF['param'] = ISMaxParam.to_list()

        ProfitSeries = pd.Series(dtype = 'float64')
        IOSname = 'IS：'+str(self.data.IS)+'，OOS：'+str(self.data.OOS)
        Procolname = '圈數：'+str(self.cname)
        ProfitIndex = pd.MultiIndex(levels=[[IOSname], ['淨利','MDD','MAR','ISProfit','WFE']], codes=[[0,0,0,0,0], [0,1,2,3,4]])
        ProfitDF = pd.DataFrame(index = ProfitIndex,columns = [Procolname])

        for index,row in FinalDF.iterrows():
            ISIndex = index[0]
            OOSIndex = index[1]
            ISStart, ISEnd = self.getSE(ISIndex)
            OOSStart, OOSEnd = self.getSE(OOSIndex)
            param = row[('param','MA1,MA2')]
            FinalDF.loc[index,('淨利','IS')] = self.data.ISData.loc[param,ISIndex]
            FinalDF.loc[index,('淨利','OOS')] = self.data.OOSData.loc[param,OOSIndex]
            FinalDF.loc[index,('MDD','IS')] = self.getMDD(self.data.OringinData.loc[param,ISStart:ISEnd])
            FinalDF.loc[index,('MDD','OOS')] = self.getMDD(self.data.OringinData.loc[param,OOSStart:OOSEnd])

            ProfitSeries = ProfitSeries.append(self.data.OringinData.loc[param,OOSStart:OOSEnd])

        ProfitDF.iloc[0] = ProfitSeries.sum()
        ProfitDF.iloc[1] = self.getMDD(ProfitSeries)
        ProfitDF.iloc[2] = (ProfitDF.iloc[0]/FinalDF.shape[0])/ProfitDF.iloc[1]
        ProfitDF.iloc[2,0] = round(ProfitDF.iloc[2,0],3)
        ProfitDF.iloc[3,0] = FinalDF[('淨利','IS')].sum()
        ProfitDF.iloc[4,0] = round(FinalDF[('淨利','OOS')].sum()/((FinalDF[('淨利','IS')].sum())/self.data.IS),3)

        FinalDF['MAR'] = np.divide(FinalDF['淨利'],FinalDF['MDD'], out=np.zeros_like(FinalDF['淨利']), where=FinalDF['MDD']!=0)
        FinalDF['WFE'] = FinalDF[('淨利','OOS')]/FinalDF[('淨利','IS')]
        return FinalDF,ProfitDF
    
    #選定該績效指摽是要最大還是最小
    def selectF(self,data,s):
        if s == 1:
            param = data.idxmax()
        else:
            param = data.idxmin()
        return self.getFinalDF(param)
    
    def ApplyAve(self):
        self.PnLTopYBY,self.PnLTop = self.selectF(self.data.ISData,1)
        self.PnLAveYBY,self.PnLAve = self.selectF(self.data.PnLaveData,1)
        self.MDDTopYBY,self.MDDTop = self.selectF(self.data.ISMDDData[(self.data.ISData>0)|(self.data.ISMDDData>0)],2)
        self.MDDAveYBY,self.MDDAve = self.selectF(self.data.MDDaveData[(self.data.ISData>0)|(self.data.ISMDDData>0)],2)
        self.MARTopYBY,self.MARTop = self.selectF(self.data.ISMARData,1)
        self.MARAveYBY,self.MARAve = self.selectF(self.data.MARaveData,1)
        
    def ApplyStd(self):
        self.PnLTopYBY,self.PnLTop = self.selectF(self.data.ISData,1)
        self.PnLStdYBY,self.PnLStd = self.selectF(self.data.PnLstdData[(self.data.ISData>self.data.ISData.mean())|(self.data.ISData>0)],2)
        self.MDDTopYBY,self.MDDTop = self.selectF(self.data.ISMDDData[(self.data.ISData>0)|(self.data.ISMDDData>0)],2)
        self.MDDStdYBY,self.MDDStd = self.selectF(self.data.MDDstdData[(self.data.ISData>self.data.ISData.mean())|(self.data.ISData>0)],2)
        self.MARTopYBY,self.MARTop = self.selectF(self.data.ISMARData,1)
        self.MARStdYBY,self.MARStd = self.selectF(self.data.MARstdData[(self.data.ISData>self.data.ISData.mean())|(self.data.ISData>0)],2)
        
    def ApplyRga(self):
        self.PnLTopYBY,self.PnLTop = self.selectF(self.data.ISData,1)
        self.PnLRgaYBY,self.PnLRga = self.selectF(self.data.PnLrgaData,1)
        self.MDDTopYBY,self.MDDTop = self.selectF(self.data.ISMDDData[(self.data.ISData>0)|(self.data.ISMDDData>0)],2)
        self.MDDRgaYBY,self.MDDRga = self.selectF(self.data.MDDrgaData,2)
        self.MARTopYBY,self.MARTop = self.selectF(self.data.ISMARData,1)
        self.MARRgaYBY,self.MARRga = self.selectF(self.data.MARrgaData,1)
        
    def ApplyRgv(self):
        self.PnLTopYBY,self.PnLTop = self.selectF(self.data.ISData,1)
        self.PnLRgvYBY,self.PnLRgv = self.selectF(self.data.PnLrgvData,1)
        self.MDDTopYBY,self.MDDTop = self.selectF(self.data.ISMDDData[(self.data.ISData>0)|(self.data.ISMDDData>0)],2)
        self.MDDRgvYBY,self.MDDRgv = self.selectF(self.data.MDDrgvData,2)
        self.MARTopYBY,self.MARTop = self.selectF(self.data.ISMARData,1)
        self.MARRgvYBY,self.MARRgv = self.selectF(self.data.MARrgvData,1)
        
class AveStdData():
    def __init__(self,data,ParamNum):
        self.ParamNum = ParamNum
        if ParamNum == 1:
            self.param1 = data.index.to_list()
        else: 
            self.param1,self.param2 = zip(*data.index.to_list())
            self.param1 = self.unique(self.param1)
            self.param2 = self.unique(self.param2)
#         self.length = data.shape[1]
        self.length = 1
        
    def getMulti(self,init,index):
        multi = []
        for i in index:
            multi += [self.InDistence(init,i)]
        multi = np.array(multi)
        return np.repeat(multi,self.length).reshape(len(index),self.length)
    
    def InDistence(self,a,b):
        if type(a) == int:
            return abs(1/(a-b))
        else:
            dis = ((a[0]-b[0])**2 + (a[1]-b[1])**2)**(1/2)
            return 1/dis
        
    def getNeighborIndex(self,param,rd):
        if self.ParamNum == 1:
            p1 = param
            p1Index = self.param1.index(p1)
            NeighborList = []
            for i in range(-rd,rd+1):
                if p1Index + i < 0 or p1Index + i >= len(self.param1):
                    return False
                x = self.param1[p1Index + i]
                NeighborList += [x]
            NeighborList.remove(param)
        else:
            p1 = param[0]
            p2 = param[1]
            p1Index = self.param1.index(p1)
            p2Index = self.param2.index(p2)
            NeighborList = []
            for i in range(-rd,rd+1):
                for j in range(-rd,rd+1):
                    if p1Index + i < 0 or p2Index + j < 0 or p1Index + i >= len(self.param1) or p2Index + j >= len(self.param2):
                        return False
                    x = self.param1[p1Index + i]
                    y = self.param2[p2Index + j]
                    NeighborList += [(x,y)]
            NeighborList.remove(param)
        return NeighborList
         
    def unique(self,list0):
        list1 = []
        for i in list0:
            if i not in list1:
                list1 += [i]
        return list1
    
    def GETAverageData(self,data,rd):        
        averageData = data.copy()
        for index, row in data.iterrows():
            RIndex = self.getNeighborIndex(index,rd)            
            if RIndex != False:
                multi = self.getMulti(index,RIndex)
                averageData.loc[(index)] = (data.loc[(index)] + (data.loc[RIndex]*multi).sum())/(len(multi)+1)
            else:
                averageData.loc[(index)] = None
        return averageData  
        

    #取得與周圍標準差
    def GETStdData(self,data,rd):
        stdData = data[data>0]
        for index, row in data.iterrows():
            RIndex = self.getNeighborIndex(index,rd)
            if RIndex != False:
                stdData.loc[(index)] = pd.concat((data.loc[(index)],data.loc[RIndex]),axis=0).std(axis=0)
            else:
                stdData.loc[(index)] = None
        return stdData
    
class Stack():
    
    def __init__(self):
        self.item = []
    def push(self, value):
        self.item.append(value)

    def pop(self):
        return self.item.pop()

    def size(self):
        return len(self.item)

    def isEmpty(self):
        return self.size() == 0

    def clear(self):
        self.item = []
        
class regionGrow():
    
    def __init__(self,PnL,quant,HL,ParamNum):
        self.HL = HL
        self.quant = quant
        self.PnL = PnL.copy()
        self.passedBy = PnL.copy()
        self.passedBy.iloc[:] = 0
        self.currentRegion = 0
        self.iterations=0
        self.stack = Stack()
        self.ParamNum = ParamNum
        if ParamNum == 1:
            self.param1 = PnL.index.to_list()
        else: 
            self.param1,self.param2 = zip(*PnL.index.to_list())
            self.param1 = self.unique(self.param1)
            self.param2 = self.unique(self.param2)
            
    def unique(self,list0):
        list1 = []
        for i in list0:
            if i not in list1:
                list1 += [i]
        return list1
        
    def getNeighbour(self,param):
        if self.ParamNum == 1:
            p1 = param
            p1Index = self.param1.index(p1)
            NeighborList = []
            for i in [-1,1]:
                if p1Index + i < 0 or p1Index + i >= len(self.param1):
                    continue
                x = self.param1[p1Index + i]
                NeighborList += [x]
        else:
            p1 = param[0]
            p2 = param[1]
            p1Index = self.param1.index(p1)
            p2Index = self.param2.index(p2)
            NeighborList = []
            for i,j in [(-1,0),(0,1),(1,0),(0,-1)]:
                if p1Index + i < 0 or p2Index + j < 0 or p1Index + i >= len(self.param1) or p2Index + j >= len(self.param2):
                    continue
                x = self.param1[p1Index + i]
                y = self.param2[p2Index + j]
                NeighborList += [(x,y)]
        return NeighborList
    
    def ApplyRegionGrow(self):
        PnLIndex = self.PnL.index.to_list() 
        if self.HL == 'L':
            self.PnL = -self.PnL
        Level = self.PnL.quantile(self.quant)
        for index in PnLIndex:
            if self.passedBy.loc[index] == 0 and self.PnL.loc[index] >= Level:
                self.currentRegion += 1
                self.passedBy.loc[index] = self.currentRegion
                self.stack.push(index)
                var = Level
                while not self.stack.isEmpty():
                    index = self.stack.pop()
                    self.BFS(var,index)
        return self.passedBy

    def BFS(self, var,index):
        regionNum = self.passedBy.loc[index]
        neighbours = self.getNeighbour(index)

        for idx in neighbours:
            if self.passedBy.loc[idx] == 0 and self.PnL.loc[idx] >= var:
                self.passedBy.loc[idx] = regionNum
                self.stack.push(idx)
