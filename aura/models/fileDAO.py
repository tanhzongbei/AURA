#coding:utf8
'''
Created on 2014-10-22

@author: xiaobei
'''
from geo.geomisc import *
from aura.models.db import db_album
from aura.models import accountDAO as _account
from kputils import (
                    mysql,
                    spy,
                    misc,
)
import definecode as _code
import time
from aura.models.geo import geomisc
from aura.models.oss import ossmisc

TABLE_PHOTO = 'photo'
TABLE_ALBUM = 'album'
TABLE_CITY = 'city'
TABLE_FAVOURITE = 'favourite'
TABLE_ALBUMEXT = 'albumext'
TABLE_COMMENT = 'comment'

DELAY_TIME = 2 * 3600
DELAY_TIME_3DAYS = 3 * 24 * 3600
#------------------------------------------------------------------------------ 

def insertPhoto(albumid, geohash, cityid, userid, sha1, tag = None, prop = 0):
    flag = havaAlreadyInAlbum(userid, albumid)
    geohash = mysql.escape(geohash)
    sha1 = mysql.escape(sha1)
    SQL = '''INSERT INTO `%s` (`albumid`, `ctime`, `geohash`, `cityid`, `userid`, `sha1`, `tag`, `prop`) VALUES
            (%d, now(), '%s', %d, %d, '%s', '%s', %d)
    ''' % (TABLE_PHOTO, int(albumid), geohash, int(cityid), int(userid), sha1, mysql.escape(tag), int(prop))
    photoid, rows = db_album.insert(SQL)
    if rows == 1:
        if not flag:
            updateAlbumJcount(albumid)
        return _code.CODE_OK, photoid
    else:
        return _code.CODE_FILEOP_DBERROR, None 


def queryAlbumCoverPhoto(userid, albumid):
    SQL = '''SELECT `photoid`, `sha1`, `fcount`, `cityid`, `ctime`, `tag` FROM `photo` WHERE `albumid` = %d ORDER BY `fcount` DESC LIMIT 1
          ''' % int(albumid)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        __, city = queryCityInfo(res[0]['cityid'])
        res[0]['city'] = city['city']
        res[0]['haveFavourte'] = haveFavourte(userid, res[0]['photoid'])
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_PHOTO_NOTEXIST, None


def queryPhotoInfoByLocate(geohash):
    geohash = mysql.escape(geohash)
    mtime = misc.timestamp2str(int(time.time()) - DELAY_TIME)
    SQL = '''SELECT `albumid`, `cityid`, `userid`, `type`, `onlyfindbyfriend`, `location`, `geohash`, `mtime`, `name` FROM `%s` WHERE `geohash` LIKE '%s' AND `mtime` > '%s'
    ''' % (TABLE_ALBUM, geohash[:5] + '%', mtime)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            ext_code, ext_res = queryAlbumExt(item['albumid'])
            if ext_code == _code.CODE_OK:
                item.update(ext_res)

            photo_code, photo_res = queryAlbumCoverPhoto(item['userid'], item['albumid'])
            if photo_code == _code.CODE_OK:
                item['coverinfo'] = photo_res
            else:
                item['coverinfo'] = 'None'

            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

            geohash = item['geohash']
            lat, lng = geomisc.parseGeoHash(geohash)
            item.update({'geo' : {'lat' : lat, 'lng' : lng}})

        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryPhotoInfoByCity(city, cursor = 0, size = 100):
    code, cityId = queryCityId(city)
    if not cityId:
        return _code.CODE_CITY_NOTEXIST, None
    else:
        cityId = cityId['autoid']
    mtime = misc.timestamp2str(int(time.time()) - DELAY_TIME_3DAYS)
    SQL = '''SELECT `photoid`, `albumid`, `userid` ,`sha1`, `cityid`, `ctime`, `fcount`, `tag` FROM `%s` WHERE `cityid` = %d AND `optime` > '%s' ORDER BY `fcount` DESC LIMIT %d,%d
          ''' % (TABLE_PHOTO, int(cityId), mtime, cursor, size)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            album_code, albuminfo = queryAlbumInfo(item['albumid'])
            if album_code == _code.CODE_OK:
                item['albuminfo'] = albuminfo
            else:
                item['albuminfo'] = 'None'
            __, city = queryCityInfo(item['cityid'])
            item['city'] = city['city']
            item['haveFavourte'] = haveFavourte(item['userid'], item['photoid'])

            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None

    
def insertAlbum(name, geohash, cityid, userid, type, onlyfindbyfriend, location, prop = 0):
    geohash = mysql.escape(geohash)
    name = mysql.escape(name)
    type = mysql.escape(type)
    location = mysql.escape(location)
    SQL = '''INSERT INTO `%s` (`name`, `geohash`, `mtime`, `cityid`, `userid`, `type`, `onlyfindbyfriend`, `location`, `prop`) VALUES
            ('%s', '%s', now(), %d, %d, '%s', %d, '%s', %d)
    ''' % (TABLE_ALBUM, name, geohash, int(cityid), int(userid), type, int(onlyfindbyfriend), location, int(prop))
    albumid, rows = db_album.insert(SQL)
    if rows == 1:
        return _code.CODE_OK, albumid
    else:
        return _code.CODE_FILEOP_DBERROR, None


def setOnlyFindbyFriend(albumid, onlyfindbyfriend):
    SQL = '''UPDATE `%s` SET `onlyfindbyfriend` = %d WHERE albumid = %d
          ''' % (TABLE_ALBUM, int(onlyfindbyfriend), int(albumid))
    res = db_album.execute(SQL)
    if res == 1:
        return _code.CODE_OK, None
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryAlbumBylocate(geohash):
    geohash = mysql.escape(geohash)
    mtime = misc.timestamp2str(int(time.time()) - DELAY_TIME)
    SQL = '''SELECT `albumid`, `name`, `cityid`, `userid`, `type`, `location`, `geohash` FROM `album` WHERE `geohash` LIKE '%s' AND `mtime` > '%s'
    ''' % (geohash[:5] + '%', mtime)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            ext_code, ext_res = queryAlbumExt(item['albumid'])
            if ext_code == _code.CODE_OK:
                item.update(ext_res)

            photo_code, photo_res = queryAlbumCoverPhoto(item['userid'], item['albumid'])
            if photo_code == _code.CODE_OK:
                item['coverinfo'] = photo_res
            else:
                item['coverinfo'] = 'None'

            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

            geohash = item['geohash']
            lat, lng = geomisc.parseGeoHash(geohash)
            item.update({'geo' : {'lat' : lat, 'lng' : lng}})

            __, city = queryCityInfo(item['cityid'])
            res[0]['city'] = city['city']
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


def queryCityInfo(cityid):
    SQL = '''SELECT `city` FROM `%s` WHERE `autoid` = %d
          ''' % (TABLE_CITY, int(cityid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_CITY_NOTEXIST, None


def queryAlbumIdByPhotoId(photoid):
    SQL = '''SELECT `albumid` FROM `%s` WHERE `photoid` = %d LIMIT 1
          ''' % (TABLE_PHOTO, int(photoid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]['albumid']
    else:
        return _code.CODE_PHOTO_NOTEXIST, None


def queryAlbumByUid(userid):
    SQL = '''SELECT `albumid`, `cityid`,  `type`, `onlyfindbyfriend`, `location`, `geohash`, `mtime`, `name` FROM `album` WHERE `userid` = %d
          ''' % int(userid)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            ext_code, ext_res = queryAlbumExt(item['albumid'])
            if ext_code == _code.CODE_OK:
                item.update(ext_res)

            photo_code, photo_res = queryAlbumCoverPhoto(userid, item['albumid'])
            if photo_code == _code.CODE_OK:
                item['coverinfo'] = photo_res
            else:
                item['coverinfo'] = 'None'

            account_code, account_info = _account.queryUserInfo(userid)
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

            geohash = item['geohash']
            lat, lng = geomisc.parseGeoHash(geohash)
            item.update({'geo' : {'lat' : lat, 'lng' : lng}})

            __, city = queryCityInfo(item['cityid'])
            item['city'] = city['city']
        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryPhotoInfoByAlbumId(userid, albumid):
    SQL = '''SELECT `photoid`, `ctime`, `cityid`, `sha1`, `tag` FROM `%s` WHERE `albumid` = %d
          ''' % (TABLE_PHOTO, int(albumid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            __, city = queryCityInfo(item['cityid'])
            item['city'] = city['city']
            item['haveFavourte'] = haveFavourte(userid, item['photoid'])

        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryPhotoInfoByFcount(userid, albumid, cursor, size):
    SQL = '''SELECT `photoid`, `ctime`, `cityid`, `fcount`, `sha1`, `userid`, `tag` FROM `photo` WHERE `albumid` = %d and photoid > %d order by `fcount` DESC LIMIT %d
          ''' % (int(albumid), int(cursor), int(size))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            __, city = queryCityInfo(item['cityid'])
            item['city'] = city['city']
            item['haveFavourte'] = haveFavourte(userid, item['photoid'])

            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryPhotoInfoByCtime(userid, albumid, cursor, size):
    SQL = '''SELECT `photoid`, `ctime`, `cityid`, `fcount`, `sha1`, `userid`, `tag` FROM `photo` WHERE `albumid` = %d and photoid > %d order by `ctime` DESC LIMIT %d
          ''' % (int(albumid), int(cursor), int(size))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            __, city = queryCityInfo(item['cityid'])
            item['city'] = city['city']
            item['haveFavourte'] = haveFavourte(userid, item['photoid'])

            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

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
            code, albumid = queryAlbumIdByPhotoId(photoid)
            if albumid:
                updateAlbumFcount(albumid)

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
            code, albumid = queryAlbumIdByPhotoId(photoid)
            if albumid:
                deleteAlbumFcount(albumid)
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
    res = db_album.query(SQL, mysql.QUERY_TUPLE)
    return  res


def haveFavourte(userid, photoid):
    uidlist = queryFavouriteByPid(photoid)
    for item in uidlist:
        if int(item[0]) == int(userid):
            return True
    else:
        return False


def queryAlbumInfo(albumid):
    SQL = '''SELECT `albumid`, `userid`, `name`, `mtime`, `type`, `onlyfindbyfriend`, `location`, `geohash` FROM `album` WHERE `albumid` = %d LIMIT 1
          ''' % int(albumid)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        albuminfo = res[0]
        ext_code, ext_res = queryAlbumExt(albumid)
        if ext_code == _code.CODE_OK:
            albuminfo.update(ext_res)

        tag_info = queryAlbumtag(albumid)
        if tag_info:
            albuminfo.update(tag_info)

        account_code, account_info = _account.queryUserInfo(albuminfo['userid'])
        if account_code == _code.CODE_OK:
            albuminfo['creatorinfo'] = account_info
        else:
            albuminfo['creatorinfo'] = 'None'

        geohash = albuminfo['geohash']
        lat, lng = geomisc.parseGeoHash(geohash)
        albuminfo.update({'geo' : {'lat' : lat, 'lng' : lng}})

        return _code.CODE_OK, albuminfo
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryMostPopPhothoes(userid, cursor = 0, size = 10):
    SQL = '''SELECT `photoid`, `ctime`, `cityid`, `fcount`, `sha1`, `albumid`, `userid`, `tag` FROM `photo`  ORDER BY `fcount` DESC LIMIT %d,%d
          ''' % (int(cursor), int(size))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            album_code, albuminfo = queryAlbumInfo(item['albumid'])
            if album_code == _code.CODE_OK:
                item['albuminfo'] = albuminfo
            else:
                item['albuminfo'] = 'None'
            __, city = queryCityInfo(item['cityid'])
            item['city'] = city['city']
            item['haveFavourte'] = haveFavourte(userid, item['photoid'])

            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

        return _code.CODE_OK, res
    else:
        return _code.CODE_ACCOUNT_DBERROR, None


def queryRecentlyInfo(userid, cursor):
    cursor = mysql.escape(cursor)
    SQL = '''SELECT `photoid`, `ctime`, `cityid`, `fcount`, `sha1`, `albumid`, `userid`, `tag` FROM `photo` WHERE `userid` = %d AND `ctime` > '%s' ORDER BY `ctime` DESC
          ''' % (int(userid), cursor)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            album_code, albuminfo = queryAlbumInfo(item['albumid'])
            if album_code == _code.CODE_OK:
                item['albuminfo'] = albuminfo
            else:
                item['albuminfo'] = 'None'
            __, city = queryCityInfo(item['cityid'])
            item['city'] = city['city']
            item['haveFavourte'] = haveFavourte(userid, item['photoid'])
            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

        return _code.CODE_OK, res
    else:
        return _code.CODE_ACCOUNT_DBERROR, None


def updateAlbumFcount(albumid):
    SQL = '''INSERT INTO `%s` (`albumid`, `fcount`, `jcount`) VALUES (%d, 1, 0) ON DUPLICATE KEY UPDATE fcount = fcount + VALUES(`fcount`)
          ''' % (TABLE_ALBUMEXT, int(albumid))
    id, rows = db_album.insert(SQL)
    if rows == 1:
        return _code.CODE_OK, id
    else:
        return _code.CODE_FILEOP_DBERROR, None


def deleteAlbumFcount(albumid):
    SQL = '''SELECT `fcount` FROM `%s` WHERE `albumid` = %d
          ''' % (TABLE_ALBUMEXT, int(albumid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        fcount = res[0]['fcount']
        SQL = '''UPDATE `%s` SET `fcount` = %d WHERE `albumid` = %d
              ''' % (TABLE_ALBUMEXT, int(fcount) - 1, int(albumid))
        rows = db_album.execute(SQL)
        return _code.CODE_OK, rows
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def updateAlbumJcount(albumid):
    SQL = '''INSERT INTO `%s` (`albumid`, `fcount`, `jcount`) VALUES (%d, 0, 1) ON DUPLICATE KEY UPDATE jcount = jcount + VALUES(`jcount`)
          ''' % (TABLE_ALBUMEXT, int(albumid))
    id, rows = db_album.insert(SQL)
    if rows == 1:
        return _code.CODE_OK, id
    else:
        return _code.CODE_FILEOP_DBERROR, None


def queryAlbumExt(albumid):
    SQL = '''SELECT `fcount`, `jcount` FROM `%s` WHERE `albumid` = %d LIMIT 1
          ''' % (TABLE_ALBUMEXT, int(albumid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def delAlbumExt(albumid):
    SQL = '''DELETE FROM `%s` WHERE `albumid` = %d LIMIT 1
          ''' % (TABLE_ALBUMEXT, int(albumid))
    res = db_album.execute(SQL)
    if res == 1:
        return _code.CODE_OK, None
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def deletePhoto(photoid, userid):
    SQL = '''SELECT `userid` FROM `%s` WHERE `photoid` = %d LIMIT 1
          ''' % (TABLE_PHOTO, int(photoid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        userid_db = res[0]['userid']
        if int(userid_db) != int(userid):
            return _code.CODE_FILEOP_NORIGHT, None

    SQL = '''DELETE FROM `%s` WHERE `photoid` = %d LIMIT 1
          '''% (TABLE_PHOTO, int(photoid))
    res = db_album.execute(SQL)
    if res == 1:
        SQL = '''DELETE FROM `%s` WHERE `photoid` = '%s'
              ''' % (TABLE_FAVOURITE, int(photoid))
        db_album.execute(SQL)
        return _code.CODE_OK, None
    else:
        return _code.CODE_PHOTO_NOTEXIST, None


def deletePhotoNoCheck(photoid):
    SQL = '''DELETE FROM `%s` WHERE `photoid` = %d LIMIT 1
          '''% (TABLE_PHOTO, int(photoid))
    res = db_album.execute(SQL)
    if res == 1:
        SQL = '''DELETE FROM `%s` WHERE `photoid` = '%s'
              ''' % (TABLE_FAVOURITE, int(photoid))
        db_album.execute(SQL)
        return _code.CODE_OK, None
    else:
        return _code.CODE_PHOTO_NOTEXIST, None


def deleteAlbum(albumid, userid):
    SQL = '''SELECT `userid` FROM `%s` WHERE `albumid` = %d LIMIT 1
          ''' % (TABLE_ALBUM, int(albumid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        userid_db = res[0]['userid']
        if int(userid_db) != int(userid):
            return _code.CODE_FILEOP_NORIGHT, None

    SQL = '''SELECT `photoid` FROM `%s` WHERE `albumid` = %d
          ''' % (TABLE_PHOTO, int(albumid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    for item in res:
        photoid = item['photoid']
        deletePhotoNoCheck(photoid)

    delAlbumExt(albumid)

    SQL = '''DELETE FROM `%s` WHERE `albumid` = %d LIMIT 1
          '''% (TABLE_ALBUM, int(albumid))
    rows = db_album.execute(SQL)
    if rows == 1:
        return _code.CODE_OK, None
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def havaAlreadyInAlbum(userid, albumid):
    SQL = '''SELECT `userid` FROM `%s` WHERE `albumid` = %d AND `userid` = %d LIMIT 1
          ''' % (TABLE_PHOTO, int(albumid), int(userid))
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        return True
    else:
        return False


def insertComment(photoid, userid, comment):
    SQL = '''INSERT `%s` (`photoid`, `userid`, `comment`, `ctime`) VALUES (%d, %d, '%s', now())
          ''' % (TABLE_COMMENT, int(photoid), int(userid), mysql.escape(comment))
    __, rows = db_album.insert(SQL)
    if rows == 1:
        return _code.CODE_OK, None
    else:
        return _code.CODE_FILEOP_DBERROR, None



def queryComment(photoid, size = 0):
    if size > 0:
        SQL = '''SELECT `comment`, `userid`, `ctime` FROM `%s` WHERE `photoid` = %d ORDER BY `ctime` desc LIMIT %d
              ''' % (TABLE_COMMENT, int(photoid), int(size))
    else:
        SQL = '''SELECT `comment`, `userid`, `ctime` FROM `%s` WHERE `photoid` = %d ORDER BY `ctime` desc
              ''' % (TABLE_COMMENT, int(photoid))

    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            userid = item['userid']
            account_code, account_info = _account.queryUserInfo(userid)
            if account_code == _code.CODE_OK:
                item['from_user'] = account_info
            else:
                item['from_user'] = 'None'

        return _code.CODE_OK, res
    else:
        return _code.CODE_COMMENT_NOTEXIST, None


def queryAlbumByName(albumname):
    SQL = '''SELECT `albumid`, `userid`, `name`, `mtime`, `type`, `onlyfindbyfriend`, `location`, `geohash` FROM `album` WHERE `name` LIKE '%%%s%%'
          ''' % mysql.escape(albumname)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        for item in res:
            ext_code, ext_res = queryAlbumExt(item['albumid'])
            if ext_code == _code.CODE_OK:
                item.update(ext_res)

            photo_code, photo_res = queryAlbumCoverPhoto(item['userid'], item['albumid'])
            if photo_code == _code.CODE_OK:
                item['coverinfo'] = photo_res
            else:
                item['coverinfo'] = 'None'

            tag_info = queryAlbumtag(item['albumid'])
            if tag_info:
                item.update(tag_info)

            account_code, account_info = _account.queryUserInfo(item['userid'])
            if account_code == _code.CODE_OK:
                item['creatorinfo'] = account_info
            else:
                item['creatorinfo'] = 'None'

            geohash = item['geohash']
            lat, lng = geomisc.parseGeoHash(geohash)
            item.update({'geo' : {'lat' : lat, 'lng' : lng}})

        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None


def queryAlbumtag(albumid):
    SQL = '''SELECT `tag` FROM `photo` WHERE `albumid` = %d LIMIT 20
          ''' % int(albumid)
    res = db_album.query(SQL, mysql.QUERY_DICT)
    if res:
        ret_list = list()
        for item in res:
            ret_list.append(item['tag'])
        tags = ','.join(str(i) for i in ret_list)
        return {'tags' : tags}
    else:
        return None


def queryPhotoInfo(photoid):
    SQL = '''SELECT `photoid`, `albumid`, `userid` ,`sha1`, `cityid`, `ctime`, `fcount`, `tag` FROM `%s` WHERE `photoid`= %d LIMIT 1
          ''' % (TABLE_PHOTO, int(photoid))
    res = db_album.query(SQL, mysql.QUERY_DICT)[0]
    if res:
        album_code, albuminfo = queryAlbumInfo(res['albumid'])
        if album_code == _code.CODE_OK:
            res['albuminfo'] = albuminfo
        else:
            res['albuminfo'] = 'None'

        url = ossmisc.getUrl(res['sha1'])
        res.update({'url':url})
        return _code.CODE_OK, res
    else:
        return _code.CODE_ALBUM_NOTEXIST, None
