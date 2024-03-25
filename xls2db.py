import pandas as pd
import pymysql
from datetime import datetime
def convert_date(date_str):
    # 假设date_str的格式为"02月28日"
    if date_str=='02月29日':
        return ("2024-2-29")
    date_obj = datetime.strptime(date_str, "%m月%d日")
    return date_obj.strftime("2024-%m-%d")

# 读取Excel文件
excel_file = 'O2FmEjpUU_三情感值.xlsx'
df = pd.read_excel(excel_file,sheet_name='sheet1')
# print(df)

# 连接MySQL数据库
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='zhang159',
    database='booksDB'
)
cursor = connection.cursor()
# exit(0)
# 将数据插入到MySQL数据库中
for index, row in df.iterrows():
    sql = "INSERT INTO system_comment (uid, nickname, content, date, polarity,probability) VALUES (%s, %s, %s, %s, %s, %s)"
    date=row['日期']
    # print(date)
    date=convert_date(date)
    # print(date)
    values = (row['uid'], row['昵称'], row['评论内容'], date, row['评论情感极性'], row['评论情感概率'])
    cursor.execute(sql, values)
    # print(values)

# 提交事务并关闭连接
connection.commit()
connection.close()

