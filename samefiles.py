# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 16:43:53 2016

@author: apotokin
"""

import sqlite3
import os
import hashlib


DBNAME = 'db.sqlite3'
PATH = 'c:/users/apotokin/Desktop'

connection = sqlite3.connect(DBNAME)
cursor = connection.cursor()

db_ex = cursor.execute

def make_db():
    db_ex('''
    DROP TABLE IF EXISTS samefiles;
    ''')
    db_ex('''
    CREATE table IF NOT EXISTS samefiles (
      md5 char(32),
      dir text,
      name text,
      size int,
      ctime datetime
    );
    ''')
    db_ex('''
    CREATE INDEX IF NOT EXISTs idx_samefiles_md5_01 
    ON samefiles (md5);
    ''')
    db_ex('''
    CREATE INDEX IF NOT EXISTs idx_samefiles_dirname_01
    ON samefiles (dir, name);
    ''')
    connection.commit()
    
def fill_db():    
    numfiles = 0;
    for dirname, dirs, filenames in os.walk(PATH):
        for fn in filenames:
            try:
                stat = os.lstat(os.path.join(dirname, fn))
            except FileNotFoundError:
                continue
            
            hasher = hashlib.md5()
            with open(os.path.join(dirname, fn), 'rb') as file:
                while True:
                    block = file.read(4*1024*1024)
                    if not block: 
                        break
                    hasher.update(block)
            md5 = hasher.hexdigest()
            
            print(dirname, fn, stat.st_size // 1024 // 1024)
            db_ex('''INSERT INTO samefiles (md5, dir, name, size, ctime) values (?, ?, ?, ?, ?)''', 
                         (md5, dirname, fn, stat.st_size, stat.st_ctime))
            numfiles += 1;
            if numfiles % 10: 
                connection.commit()
        print(numfiles)
            
            
    
if __name__ == '__main__':
    make_db()
    fill_db()
    
    connection.close()