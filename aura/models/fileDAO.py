#coding:utf8
'''
Created on 2014-10-22

@author: xiaobei
'''
from geo.geomisc import *
from aura.models.db import db_album
from kputils import (
                    mysql,
                    spy,
                    misc,
)
import definecode as _code
import time

TABLE_PHOTO = 'photo'
TABLE_ALBUM = 'album'
TABLE_CITY = 'city'
TABLE_FAVOURITE = 'favourite'

DELAY_TIME = 2 * 3600
#------------------------------------------------------------------------------ 

def insertPhoto(albumid, geohash, cityid, userid, sha1, prop = 0):
    geohash = mysql.escape(geohash)
    sha1 = mysql.escape(sha1)
    SQL = '''INSERT INTO `%s` (`albumid`, `ctime`, `geohash`, `cityid`, `userid`, `sha1`, `prop`) VALUES 
            (%d, now(), '%s', %d, %d, '%s', %d)
    ''' % (TABLE_PHOTO, int(albumid), geohash, int(cityid), int(userid), sha1, int(prop))
    photoid, rows = db_album.insert(SQL)
    if rows == 1:
        return _code.CODE_OK, photoid
    else:
        return _code.CODE_FILEOP_DBERROR, None 
    
    
def queryPhotoInfoByLocate(geohash):
    geohash = mysql.escape(geohash)
    mtime = misc.timestamp2str(int(time.time()) - DELAY_TIME)
    SQL = '''SELECT `albumid`, `cityid`, `userid` ,`sha1` FROM `%s` WHERE `geohash` LIKE '%s' AND `optime` > '%s'
    ''' % (TABLE_PHOTO, geohash[:5] + '%', mtime)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None
    
    
def insertAlbum(name, geohash, cityid, userid, prop = 0):
    geohash = mysql.escape(geohash)
    name = mysql.escape(name)
    SQL = '''INSERT INTO `%s` (`name`, `geohash`, `mtime`, `cityid`, `userid`, `prop`) VALUES
            ('%s', '%s', now(), %d, %d, %d)
    ''' % (TABLE_ALBUM, name, geohash, int(cityid), int(userid), int(prop))
    albumid, rows = db_album.insert(SQL)
    if rows == 1:
        return _code.CODE_OK, albumid
    else:
        return _code.CODE_FILEOP_DBERROR, None
    

def queryAlbumBylocate(geohash):
    geohash = mysql.escape(geohash)
    mtime = misc.timestamp2str(int(time.time()) - DELAY_TIME)
    SQL = '''SELECT `albumid`, `name`, `cityid`, `userid` FROM `%s` WHERE `geohash` LIKE '%s' AND `mtime` > '%s'
    ''' % (TABLE_ALBUM, geohash[:5] + '%', mtime)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def insertCity(city):
    city = mysql.escape(city)
    SQL = '''INSERT INTO `%s` SET `city` = '%s'
    ''' % (TABLE_CITY, city)
    cityid, rows = db_album.insert(SQL)
    if rows == 1:
        return _code.CODE_OK, cityid
    else:
        return _code.CODE_FILEOP_DBERROR, None
    
    
def queryCityId(city):
    city = mysql.escape(city)
    SQL = '''SELECT `autoid` from `%s` WHERE `city` = '%s'
    ''' % (TABLE_CITY, city)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_CITY_NOTEXIST, None


def queryAlbumByUid(userid):
    SQL = '''SELECT `albumid`, `name`, `cityid` FROM `%s` WHERE `userid` = %d
          ''' % (TABLE_ALBUM, int(userid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryPhotoInfoByAlbumId(albumid):
    SQL = '''SELECT `photoid`, `ctime`, `cityid` FROM `%s` WHERE `albumid` = %d
          ''' % (TABLE_PHOTO, int(albumid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryPhotoInfoByFcount(albumid, cursor, size):
    SQL = '''SELECT `photoid`, `ctime`, `cityid`, `fcount` FROM `%s` WHERE `albumid` = %d and photoid > %d order by `fcount` LIMIT %d
          ''' % (TABLE_PHOTO, int(albumid), int(cursor), int(size))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryPhotoInfoByCtime(albumid, cursor, size):
    SQL = '''SELECT `photoid`, `ctime`, `cityid`, `fcount` FROM `%s` WHERE `albumid` = %d and photoid > %d order by `ctime` LIMIT %d
          ''' % (TABLE_PHOTO, int(albumid), int(cursor), int(size))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def addFavourite(userid, photoid):
    SQL = '''INSERT INTO `%s` (`photoid`, `userid`) VALUES ('%s', '%s')
          ''' % (TABLE_FAVOURITE, mysql.escape(photoid), mysql.escape(userid))
    autoid, rows = db_album.insert(SQL)
    if rows == 1:
        SQL = '''UPDATE `%s` SET `fcount` = `fcount` + 1 WHERE `photoid` = '%s'
              ''' % (TABLE_PHOTO, mysql.escape(photoid))
        rows = db_album.execute(SQL)
        if rows == 1:
            return _code.CODE_OK, None
        else:
            return  _code.CODE_FILEOP_DBERROR, None

    else:
        return _code.CODE_FILEOP_DBERROR, None


def delFavourite(userid, photoid):
    SQL = '''DELETE FROM `%s` WHERE `userid` = '%s' AND `photoid` = '%s' LIMIT 1
          ''' % (TABLE_FAVOURITE, mysql.escape(userid), mysql.escape(photoid))
    rows = db_album.execute(SQL)
    if rows == 1:
        SQL = '''UPDATE `%s` SET `fcount` = `fcount` - 1 WHERE `photoid` = '%s'
              ''' % (TABLE_PHOTO, mysql.escape(photoid))
        rows = db_album.execute(SQL)
        if rows == 1:
            return _code.CODE_OK, None
        else:
            return  _code.CODE_FILEOP_DBERROR, None
    else:
        return _code.CODE_FILEOP_DBERROR, None


def queryFavouriteByUid(userid):
    SQL = '''SELECT `photoid` FROM `%s` WHERE `userid` = '%s'
          ''' % (TABLE_FAVOURITE, mysql.escape(userid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_FAVOURITE_NOTEXIST, None


def queryFavouriteByPid(photoid):
    SQL = '''SELECT `userid` FROM `%s` WHERE `photoid` = '%s'
          ''' % (TABLE_FAVOURITE, mysql.escape(photoid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_FAVOURITE_NOTEXIST, None