# coding : utf-8
import sys
import akshare as ak
import pandas as pd

args = "".join(sys.argv[1:])
args = args.replace('，', ',')
args = args.replace('；', ';')
args = args.replace(' ', '')

allList = args.split(';')

df_outputs = {}

df_indexes = {}
df_stocks = {}

fieldDict_index = {'开盘价': 'open', '收盘价': 'close', '最高价': 'high', '最低价': 'low', '成交量': 'volume'}
fieldDict_stock = {'开盘价': 'open', '收盘价': 'close', '最高价': 'high', '最低价': 'low', '成交量': 'volume', '换手率': 'turnover'}

codes = allList[0].split(',')
for code in codes:
    if code[:3] == 'zh_':
        index_code = code.split('_')[1]
        try:
            df_temp = ak.stock_zh_index_daily(symbol=index_code).reset_index()
            df_target = pd.DataFrame()
            df_target['date'] = df_temp['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            for text in allList[1:]:
                if text in fieldDict_index:
                    col_name = fieldDict_index[text]
                    df_target[text] = df_temp[col_name]
            df_indexes[index_code] = df_target
        except:
            continue
    else:
        stock_code = ('sh' if code[0] == '6' else 'sz') + code
        try:
            if '后复权' in allList[1:]:
                df_temp = ak.stock_zh_a_daily(symbol=stock_code, adjust='hfq').reset_index()
            else:
                df_temp = ak.stock_zh_a_daily(symbol=stock_code).reset_index()
            df_target = pd.DataFrame()
            df_target['date'] = df_temp['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            for text in allList[1:]:
                if text in fieldDict_stock:
                    col_name = fieldDict_stock[text]
                    df_target[text] = df_temp[col_name]
            df_stocks[stock_code] = df_target
        except:
            continue


for s in allList[1:]:
    df_temp = pd.DataFrame()
    if s in fieldDict_index:
        for key, df in df_indexes.items():
            if df_temp.empty:
                df_temp = df[['date']]
            df_temp = pd.merge(left=df_temp, right=df[['date', s]].rename(columns={s: key}), on='date')
    if s in fieldDict_stock:
        for key, df in df_stocks.items():
            if df_temp.empty:
                df_temp = df[['date']]
            df_temp = pd.merge(left=df_temp, right=df[['date', s]].rename(columns={s: key}), on='date')
    df_outputs[s] = df_temp


excel_writer = pd.ExcelWriter('Data.xlsx')
for key, value in df_outputs.items():
    value.to_excel(excel_writer, sheet_name=key, index=False)
excel_writer.save()
excel_writer.close()
