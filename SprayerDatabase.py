#!/usr/bin/python3

import sqlite3
import logging
import os
from typing import Collection
import numpy as np
from datetime import datetime
import time

logging.basicConfig(level=logging.DEBUG)

class SprayerDatabase():
    
    db_filename = None
    db_connection = None
    db_fields = []
    __default_db_filename = 'SprayerDB.db'
    __default_db_tablename = 'spray'

    def __init__(self, db_filename=None, tablename= None):

        logging.debug("__init__ : params {}".format(db_filename))
        self.cursor = None
        self.table_name = None
        self._db_fields = []

        if not tablename:
            self.tablename = self.__default_db_tablename
        else:
            self.tablename = tablename
        if not db_filename:          
            self.db_filename = self.__default_db_filename
        else:
            self.db_filename = db_filename

        if os.path.isfile(self.db_filename):
            logging.debug("__init__ : '[+] Database {} exists.".format(db_filename))
            pass         
        else:                         
            self.connect()

        logging.debug("__init__ : [+] DB connected".format(db_filename))

    # def __getattribute__(self, name: str):
    #    print("[+] NAME PARAM: {}".format(name.upper()))


    def connect(self,db_filename=''):
        #logging.debug("connect() : [*] Connecting to database {}...".format(db_filename))   
        if not db_filename:
            db_filename = self.db_filename
        if not self.db_connection:            
            self.db_connection = sqlite3.connect(self.db_filename)
        #logging.debug("connect() : [+] Connected to database {}...".format(db_filename))  

    def create_table(self, table_name, field_list):       
        self.table_name = table_name
        self.fields = field_list 
        logging.debug("create_table() : fields: {}...".format(self.fields)) 
        res = self.get_table(table_name)
        if res:
            logging.debug("create_table() : [-] Table {} already exists. passing...".format(table_name))
            return
        query = "CREATE TABLE {} ({})".format(table_name, self.fields)
        logging.debug("create_table() : Creating Table '{}' with Fields {}".format(table_name, self.fields))     
        self.execute(query)

    def get_table(self, table_name):
        logging.debug("get_table() : [*] Getting table {}...".format(table_name))  
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)
        o = self.execute(query)
        if o:
            logging.debug("get_table() : [+] Got table {}".format(o[0]))
            return o
        logging.warn("get_table() : [-] No table {}".format(table_name))            
        return False            

    def get_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        o = self.execute(query)
        logging.debug("get_tables() : [+] Fetched all tables")
        return o

    def remove_table(self, table_name):
        if self.get_table(table_name):
            logging.debug("remove_table() : [*] Removing table {}".format(table_name)) 
            self.execute("DROP TABLE {}".format(table_name))
        else:
            logging.debug("remove_table() : [-] Table {} not found".format(table_name)) 

    def execute(self, query):
        self.connect()        
        logging.debug("execute() : [+] Query: {}".format(query))
        o = []        
        with self.db_connection as conn:
            cursor = conn.cursor()
            r = cursor.execute(query)

            print(r.rowcount)
            conn.commit()            
            #time.sleep(3)
            for res in r:
                logging.debug("execute() : Query response {}".format(res)) 
                o.append(res[0])  

        for res in r:
            logging.debug("execute() : Query response {}".format(res)) 
            o.append(res[0])  
            
        return o

    def executemany(self, query, tuple_values):
        self.connect()
        fquery = query.replace('?','{}')
        
        logging.debug("executemany() : [+] Query: {}".format(fquery.format(*tuple_values)))

    def close(self):
        if self.db_connection:
            self.db_connection.close()

    def log_entry(self,**kwargs):        
        for k, v in kwargs:
            print("key {} // val {}".format(k,v))
    
    def get_table_columns(self,table_name):
        if self.get_table(table_name):
            with self.db_connection as conn:
                cursor = conn.cursor()
                r = self.execute('SELECT * from {} LIMIT 1'.format(table_name))
                print(r)
        else:
            return False            
        if r:        
            names = [description[0] for description in r.description]
            logging.debug("get_table_columns() : Query response {}".format(names)) 
            return names
        logging.warn("get_table_columns() : No column names retrieved")             
        return False            
        
    def import_list(self, filename, table_name='', keyname=''):
        if not self.get_table(table_name):
            logging.warn("[-] Table '{}' doesn't exist".format(table_name))
            return

        with open(filename, 'r') as f:
            names = f.read().splitlines()
            f.close()
         
        if not names:
            logging.warn("import_list() : No users imported")
            return
        logging.debug("import_list() : Read {} users from file".format(len(names)))                
        if not self.get_table(table_name):
            self.create_table(table_name)
        
        for i in names:
            print(i)
            print(table_name)
            u = self.get_user(i, table_name)
            print("RES OF U: {}".format(u))
            if u:
                logging.warn("[-] Skipping insert for user {} (already exists)".format(i))
            else:
                logging.info("[-] UserID {} doesn't exist. Creating...".format(i))
                self.insert_user(**{ keyname : i, "table_name" : table_name, "timestamp": self.nowtime()})
            return
        
    def insert_user(self, table_name=None, **kwargs):
        if not table_name:
            tablename = self.table_name
        else:
            self.table_name = table_name                                
        query = "INSERT INTO {table_name} ({columns}) VALUES ({values})"
        columns = self.join_elements(tuple(kwargs.keys()))
        values = self.join_elements(tuple(kwargs.values()))
        assert len(tuple(kwargs.keys())) == len(tuple(kwargs.values())), "Column and Value Lengths don't match"
        fquery = query.format(table_name=table_name, 
                              columns=columns, 
                              values=values )
        logging.debug("insert_user() : [*] Insert Statement: {}...".format(fquery)) 
        self.execute(fquery)

    def get_user(self, userid, table_name=''):
        self.connect()
        logging.info("get_user() : [*] Getting record for user {} from {}...".format(userid, table_name))
        if not table_name:
            table_name = self.table_name
        if self.get_table(table_name):      
            query = "SELECT * FROM {table_name} WHERE userid = \'{userid}\'".format(table_name=table_name,
                                                                                userid=userid)
            user = self.execute(query)
            return user
        else:
            logging.warn("[-] Table '{}' doesn't exist".format(table_name))

    def update_user(self, **kwargs):
        return

    def delete_user(self, userid_list):
        return 
                
    def join_elements(self, elements):
        return ", ".join(["\"{}\"".format(i) for i in elements])

    @property
    def fields(self):
        if self._db_fields:
            o = ', '.join(
                ["{} {}".format(*(list(i.items())[0])) for i in self._db_fields]
                )
            return o
        return None

    @fields.setter
    def fields(self, field_list):
        self._db_fields = field_list

    @staticmethod
    def nowtime():
        return datetime.utcnow().strftime("%Y%m%d_%H%M")
