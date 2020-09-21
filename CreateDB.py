#/usr/bin/env python
# -*- coding:utf-8 -*-
'''
    @File    :   CreateDB.py    
    @Contact :   guoxin@126.com
    @License :   (C)Copyright 2018-2019, xguo

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/9/18  11:21   xguo      1.0         None

'''
'''
create table if not exists ansible(id int not null auto_increment,
                                    name varchar(100) not null,
                                    date datetime ,
                                    wiops float,
                                    riops float,
                                    twiops float,
                                    triops float,
                                    primary key(id))engine=InnoDB DEFAULT CHARSET=utf8;
'''
import sqlite3

def main():
    cx = sqlite3.connect('./db_data/ansible.db')
    # con = sqlite3.connect(":memory:")
    print("Opened database successfully")
    cu = cx.cursor()
    cu.execute('''create table ansible
        (name   VARCHAR(100) NOT NULL ,
         date   DATETIME NOT NULL,
         WIOPS   FLOAT ,
         RIOPS   FLOAT 
         )''')
    print("Table create successfully")
    cx.commit()
    cx.close()

if __name__ == "__main__":
    main()