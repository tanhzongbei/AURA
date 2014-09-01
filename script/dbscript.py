#coding:utf8
'''
Created on 2014-9-1

@author: xiaobei
'''

import MySQLdb
import getopt
import sys


CONFIG = {
    'user': 'python',
    'password': 'gj4fKLCcnRJQz5U1',
    'host': '182.92.166.245',
    'port': 3306,
}


conn = MySQLdb.connect(host=CONFIG['host'],user = CONFIG['user'],passwd=CONFIG['password'],port=CONFIG['port'])
cursor=conn.cursor()

DB_NAME = 'account'
CREATE_ACCOUNT = '''
CREATE TABLE `account` (
  `userid` bigint(20) unsigned NOT NULL auto_increment,
  `passwd` varchar(128) default NULL,
  `email` varchar(64) default NULL,
  `mobile` bigint(20) default NULL,
  `extid` bigint(20) default NULL,
  PRIMARY KEY  (`userid`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `mobile` (`mobile`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
'''

def createAccount():
#    SQL = 'CREATE DATABASE %s' % DB_NAME
#    cursor.execute(SQL)
    SQL = 'USE %s' % DB_NAME
    cursor.execute(SQL)    
    cursor.execute(CREATE_ACCOUNT)


def main():
    createAccount()
    print 'done'

if __name__ == '__main__':
    main()
