# ParamSearch
## 前言
該程式為[曾宣瑋（2023）]([https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=2xaDqz/record?r1=1&h1=1](https://drive.google.com/file/d/1HzWZJDG_NqnpuAnuN1MCSQqdgab8XXlj/view?usp=share_link))實證所使用之程式源碼，其主要透過四種參數選擇法（權重選擇法、標準差選擇法、島嶼面積選擇法、島嶼體積選擇法）來找尋屬於參數高原之參數，而各個參數選擇法中皆有以下幾個參數，分別是窗格比例、延伸圈數或標竿PR。本文主要是希望透過該程式找尋出每一參數選擇法對應不同商品以及交易策略時，其最適之窗格比例、延伸圈數或標竿PR為何。接下來我會講解基本的操作方法，至於程式背後的邏輯則需自行探討。
## 操作說明
### BackTestData
'BackTestData'資料夾內為存放參數窮舉後的日結績效數據，檔案命名規則為「'策略名稱'_'商品名稱'_'參數幾維參數'」，如「BB_FITXN_2」即是使用策略BB，回測商品為台指期（FITXN），
共有兩維度的參數。而參數窮舉後的日結數據格式說明如下圖：
![image](https://github.com/TsengAllen/image/blob/main/截圖%202023-07-16%20下午3.37.46.png)
### BnHPnL
'BnHPnL'資料夾內為存放四種商品（FITXN、FITE、FITF、FIXI）的買進持有日結績效數據，此為用來與使用參數選擇法後的績效進行比較。
____
### main主程式
主程式中有四個「mainAve、mainStd、mainRga、mainRgv」其分別為回測「權重選擇法、標準差選擇法、島嶼面積選擇法、島嶼體積選擇法」這四種參數選擇法之主程式。以下舉mainAve的操作方式為例：
#### step1.
執行時須先在輸入欄位上填入所要回測的策略名稱。  
```sh
輸入策略名稱：
```
#### step2.
回測時會以迴圈的方式，逐一跑完所有「窗格比例、延伸圈數或標竿PR」的回測數據。  
<img src="https://github.com/TsengAllen/image/blob/main/截圖%202023-07-16%20下午3.54.21.png" width=20% height=20%>
#### step3.
最後回測後的數據會呈現在'result'資料夾（會自動生成）內。
___
### mainOrganiz
mainOrganiz則是將前面所回測後的數據進行整理，並且生成視覺化圖型（熱區圖）存放在'result2'資料夾中，其最後呈現之效果將會如論文所示。報表的閱讀方式可以參考論文P.50頁。
___
作者：曾宣瑋  
Email：allenta109@gmail.com  
如有任何疑問，歡迎諮詢。  
