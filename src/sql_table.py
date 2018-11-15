#!/usr/bin/env python
#
# read a root tree using Pyroot and find muon track
#
#
from __future__ import print_function

import os

import sys, uuid

import operator
import datetime

from operator import itemgetter

import mysql.connector
from mysql.connector import errorcode

sys.path.insert(0, '../src')
import h1b_counting as cen

DB_NAME = 'visa_app_tmp'

TABLES = {}
TABLES['visa_app'] = (
    "CREATE TABLE `visa_app` ("
    " `id` MEDIUMINT NOT NULL AUTO_INCREMENT,"
    " `soc_name` varchar(100) NOT NULL,"
    " `workstate` varchar(20) NOT NULL,"
    " `soc_code` varchar(20) NOT NULL,"
    " `status` varchar(20) NOT NULL,"
    " PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")



def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def making_table():

    cnx = mysql.connector.connect(user='root', password='mysql_pw',
                                  host='127.0.0.1', auth_plugin='mysql_native_password')
    cursor = cnx.cursor()

    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} create successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    cursor.execute("USE {}".format(DB_NAME))
    #cursor.execute("ALTER TABLE visa_app DROP PRIMARY KEY, ADD PRIMARY KEY (`id`)")
    cursor.execute("ALTER TABLE visa_app MODIFY id INT NOT NULL")
    cursor.execute("ALTER TABLE visa_app DROP PRIMARY KEY")


def insert_table():

    cnx = mysql.connector.connect(user='root', password='mysql_pw', database = DB_NAME,
                                  host='127.0.0.1', auth_plugin='mysql_native_password')

    cursor = cnx.cursor()

    strip = ["SOC_NAME", "WORKSITE_STATE", "SOC_CODE", "CASE_STATUS"]

    add_visa_app = """INSERT INTO {}.visa_app                                                                
                       (id, soc_name, workstate, soc_code, status)                                                 
                       VALUES (%s, %s, %s, %s, %s);""".format(DB_NAME)


    infile = "../input/h1b_input.csv"                                                                             
    #infile = "../input/H1B_FY_2016.csv"

    print("Input file = %s" % infile)

    app = cen.save_info(infile, strip)
    #print(app)                                                                                                    

    ind = 0
    for ai in app:
        data_visa_app = (ind, str(ai['SOC_NAME']), str(ai['WORKSITE_STATE']), str(ai['SOC_CODE']), str(ai['CASE_STATUS']))
        #print(data_visa_app)                                                                                      
        #print(add_visa_app % data_visa_app)                                                                       
        cursor.execute(add_visa_app, data_visa_app)
        cnx.commit()
        ind += 1

    cursor.close()
    cnx.close()



def querying(sort_target, title):

    cnx = mysql.connector.connect(user='root', password='mysql_pw', database = DB_NAME,
                                  host='127.0.0.1', auth_plugin='mysql_native_password')

    cursor = cnx.cursor(buffered=True)
    
    #cursor.execute("show tables")
    #cnx.commit()

    query_for_sort = """select %s, sum(case when status='CERTIFIED' then 1 else 0 end), count(*),
                        sum(case when status='CERTIFIED' then 1 else 0 end)/(select count(*) from visa_app where status='CERTIFIED') as fraction
                        from visa_app group by %s order by fraction DESC, %s ASC limit 10;"""

    query_for_target = (sort_target, sort_target, sort_target)

    cursor.execute(query_for_sort % query_for_target)
    cnx.commit()

    print(cursor.statement)
    a = cursor.fetchall()

    print(title)
    for ai in a:
        print("%s : %d : %s" % (ai[0], ai[1], str(ai[3])))

    cursor.close()
    cnx.close()


if __name__ == '__main__':

    table_creation = True
    insert_query = True

    if table_creation is True:
        making_table()
    if insert_query is True:
        insert_table()
    
    target_title = ["TOP_OCCUPATIONS;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE", "TOP_STATES;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE"]
    querying('soc_name', target_title[0])
    querying('workstate', target_title[1])

