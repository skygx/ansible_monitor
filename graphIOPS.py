#/usr/bin/env python
# -*- coding:utf-8 -*-
'''
    @File    :   graphIOPS.py    
    @Contact :   guoxin@126.com
    @License :   (C)Copyright 2018-2019, xguo

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/9/18  16:37   xguo      1.0         None

'''
import pymysql
from pyecharts.charts import Line,Funnel
from pyecharts import options as opts
import pandas as pd
import sqlite3

def main():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='ansible',
        charset='utf8'
    )
    # conn = pymysql.connect(host='localhost', user='root', passwd='root', db='ansible')
    conn = sqlite3.connect('./db_data/ansible.db')
    # sql = 'select * from ansible where name="k8s-node2" order by date'
    sql = 'select * from ansible order by date'
    df = pd.read_sql(sql, conn)

    line = Line()
    print(df['date'])
    host='k8s-master'
    d = df.loc[df['name'] == host]
    # line.add_xaxis([y for y in range(13)])
    line.add_xaxis(list(d['date']))
    line.add_yaxis('RIOPS',d['RIOPS'])
    line.add_yaxis('WIOPS',d['WIOPS'])
    line.set_global_opts(title_opts=opts.TitleOpts(title=host))

    line.render(r"./result/line.html")

if __name__ == "__main__":
    main()