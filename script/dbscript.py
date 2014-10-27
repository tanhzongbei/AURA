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
  `nickname` varchar(32),
  `email` varchar(64) default NULL,
  `mobile` bigint(20) default NULL,
  `extid` bigint(20) default NULL,
  `ctime` datetime NOT NULL,
  PRIMARY KEY  (`userid`),
  KEY `email` (`email`),
  KEY `mobile` (`mobile`),
  UNIQUE KEY `nickname` (`nickname`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
'''


CREATE_SESSION = '''
CREATE TABLE IF NOT EXISTS `session` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `userid` int(10) NOT NULL,
  `sid` binary(20) NOT NULL,
  `deviceid` varchar(64) NOT NULL,
  `ip` varchar(15) NOT NULL,
  `ctime` timestamp default current_timestamp,
  `etime` timestamp NOT NULL,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uidx_sid` (`sid`),
  KEY `idx_ctime` (`ctime`),
  KEY `idx_etime` (`etime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT 'session';
'''

DB_ALBUM = 'album'

CREATE_PHOTO = '''
CREATE TABLE `photo` (
  `photoid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `albumid` int(10) unsigned NOT NULL,
  `ctime` datetime NOT NULL,
  `geohash` varbinary(10) DEFAULT NULL,
  `cityid` int(10) unsigned DEFAULT NULL,
  `userid` bigint(20) NOT NULL,
  `sha1` varchar(40) NOT NULL,
  `optime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `prop` bigint(20) NOT NULL COMMENT 'some properties of the photo',
  PRIMARY KEY (`photoid`),
  KEY `_photo_idx_albumid` (`albumid`),
  KEY `_photo_idx_geohash_ctime` (`geohash`,`optime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='photo album table';

'''

CREATE_ALBUM = '''
CREATE TABLE `album` (
      `albumid` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
      `name` varchar(64) NOT NULL,
      `mtime` datetime NOT NULL,
      `geohash` varbinary(10) DEFAULT NULL,
      `cityid` int(10) unsigned DEFAULT NULL,
      `userid` bigint(20) NOT NULL,
      `prop` bigint(20) NOT NULL COMMENT 'some properties of the photo',      
      PRIMARY KEY (`albumid`),
      KEY `_album_idx_cityid` (`cityid`),
      KEY `_album_idx_geohash_mtime` (`geohash`, `mtime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='album table';


'''

CREATE_CITY = '''
CREATE TABLE `city` (
    `autoid` int unsigned NOT NULL AUTO_INCREMENT,
    `city` varchar(20) NOT NULL,
    PRIMARY KEY (`autoid`),
    KEY `city` (`city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='city table';
'''

def createAccount():
#    SQL = 'CREATE DATABASE %s' % DB_NAME
#    cursor.execute(SQL)
    SQL = 'USE %s' % DB_ALBUM
    cursor.execute(SQL)    
    cursor.execute(CREATE_PHOTO)


def main():
    createAccount()
    print 'done'

if __name__ == '__main__':
    main()
