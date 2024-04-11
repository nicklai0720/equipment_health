import joblib
import pandas as pd
import time
import datetime
from datascratch import data_export
import pymssql


def insert_data_to_sql(df):
    connection = pymssql.connect(
        host="",
        user="",
        password="",
        database=""
    )
    cursor = connection.cursor()

    table_name = 'kq_health'
    # insert data to SQL
    insert_query = f"INSERT INTO {table_name} (時間, X震動, Y震動, 電流, 溫度, 健康度, 設備狀態, 混合機名) " \
                   f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    for index, row in df.iterrows():
        health_rounded = round(row['Health'], 2)
        cursor.execute(insert_query, (
            row['DT'],
            row['X'],
            row['Y'],
            row['C'],
            row['T'],
            health_rounded,
            row['Status'],
            row['Machine']
        ))
    connection.commit()
    connection.close()


machine = ["KQ01", "KQ02", "KQ03", "KQ04", "KQ05", "KQ06", "KQ07", "KQ08"]
for i in machine:
    en = []
    temp1 = f"RPA_{i}_MIX_MOTOR_SHACK_PV"
    temp2 = f"RPA_{i}_MIX_SHACK_PV"
    temp3 = f"RPA_{i}_HOT_MIX_READ_CURRENT"
    temp4 = f"RPA_{i}_HOT_MIX_READ_TEMP"

    en.append(temp1)
    en.append(temp2)
    en.append(temp3)
    en.append(temp4)
    globals()[i+"_en"] = en

# KQ01~KQ08的ch
for i in machine:
    ch = []
    temp1 = f"{i}混合馬達震動值X"
    temp2 = f"{i}混合機震動值Y"
    temp3 = f"{i}熱拌機電流值"
    temp4 = f"{i}熱拌機混合溫度"

    ch.append(temp1)
    ch.append(temp2)
    ch.append(temp3)
    ch.append(temp4)
    globals()[i+"_ch"] = ch

# 將各機台tag英文名稱+路徑結合，後面PI系統抓資料用
pisource = 'pi:\\10.114.134.1\\'
for i in machine:
    globals()[i+"_pitag"] = [pisource + element for element in globals()[i+"_en"]]

# 建立中英對照dict，tag_name_trans = 中英對照dict
for i in machine:
    globals()[i+"_namedict"] = dict((en, ch) for en, ch in zip(globals()[i+"_en"], globals()[i+"_ch"]))

tag = [KQ01_pitag, KQ02_pitag, KQ03_pitag, KQ04_pitag, KQ05_pitag, KQ06_pitag, KQ07_pitag, KQ08_pitag]

catboost = joblib.load('catboost.pkl')
catboost_KQ07 = joblib.load('catboost_KQ#7.pkl')
catboost_KQ08 = joblib.load('catboost_KQ#8.pkl')

while True:
    start = datetime.datetime.now() - datetime.timedelta(minutes=0)
    end = datetime.datetime.now()
    time_format = '%Y-%m-%d %H:%M:%S'

    start_time = start.strftime(time_format)  # 注意这里使用了 strftime
    end_time = end.strftime(time_format)      # 注意这里使用了 strftime
    dt_time = datetime.datetime.strftime(end, time_format)

    pi_data1 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[0],
                           time_interval='1m').iloc[-1:, :]

    pi_data2 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[1],
                           time_interval='1m').iloc[-1:, :]

    pi_data3 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[2],
                           time_interval='1m').iloc[-1:, :]

    pi_data4 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[3],
                           time_interval='1m').iloc[-1:, :]

    pi_data5 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[4],
                           time_interval='1m').iloc[-1:, :]

    pi_data6 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[5],
                           time_interval='1m').iloc[-1:, :]

    pi_data7 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[6],
                           time_interval='1m').iloc[-1:, :]

    pi_data8 = data_export(start_time=start_time,
                           end_time=end_time,
                           tagpoint_list=tag[7],
                           time_interval='1m').iloc[-1:, :]

    all_pi = [pi_data1, pi_data2, pi_data3, pi_data4, pi_data5, pi_data6, pi_data7, pi_data8]

    # data = pd.read_excel('上線應用\pi_data\KQ_Data.xlsx')

    all_machine = ['KQ01', 'KQ02', 'KQ03', 'KQ04', 'KQ05', 'KQ06', 'KQ07', 'KQ08']

    temp_df = pd.DataFrame()

    for i in range(len(all_pi)):

        column_names = ['X', 'Y', 'C', 'T']
        current_pi = all_pi[i].copy()
        current_pi.columns = column_names

        if (current_pi['C'] < 10).all():
            current_pi['Health'] = 0
            current_pi['Status'] = 0

        elif i == 6:
            current_pi['Health'] = catboost_KQ07.predict(current_pi.values)
            current_pi['Status'] = 1

        elif i == 7:
            current_pi['Health'] = catboost_KQ08.predict(current_pi.values)
            current_pi['Status'] = 1

        else:
            current_pi['Health'] = catboost.predict(current_pi.values)
            current_pi['Status'] = 1
        
        current_pi['Machine'] = all_machine[i]
        current_pi['DT'] = dt_time
        current_pi = current_pi[['DT'] + [col for col in current_pi.columns if col != 'DT']]

        # print('第', i+1, '台KQ:', '健康度:', current_pi['Health'])

        temp_df = pd.concat([temp_df, current_pi], ignore_index=True)
    #     print('1:', temp_df)
    # print('2:', temp_df)

    insert_data_to_sql(temp_df)

    # excel_name = os.path.join('pi_data', 'KQ_Data.xlsx')
    # writer_data(temp_df, excel_name)
    
    # data = data.append(temp_df, ignore_index=True)
    # excel_filename = os.path.join('上線應用', 'pi_data', 'KQ_Data.xlsx') # 這邊要依據當前目錄做更改喔
    # # temp_df.to_excel(excel_filename, index=False)
    # data.to_excel(excel_filename, index=False)
    #     # all_result[i].to_excel(writer, sheet_name=f'KQ{str(i+1)}', index=False)
    print(f"{datetime.datetime.now()}的數據上傳成功!")

    time.sleep(600)
    # break

