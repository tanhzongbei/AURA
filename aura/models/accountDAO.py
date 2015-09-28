#coding:utf8
'''
Created on 2014-9-1

@author: xiaobei721
'''

from db import (
                db_account,
)

from kputils import (
                    mysql,
                    spy,
)
import definecode as _code

#------------------------------------------------------------------------------ 
#tools
from Crypto.Cipher import AES
import base64
import hashlib
import random
import binascii

def encryptPassword(password):
    INITIAL_VECTOR = '\xfc\x95\x46\x28\x3a\x93\x4c\x1c\xac\x93\x45\x6a\xa3\x88\x48\x4f'
    KEY = '\xb7\x79\xac\x80\x33\xd6\xf4\xbe\xa5\x85\x2e\x1b\x66\x66\xd6\x22'
    _cipher = AES.new(KEY, AES.MODE_CBC, INITIAL_VECTOR)
    padding = len(password) % 16
    if padding:
        password = password + '0' * (16 - padding)
    data = _cipher.encrypt(password)
    return data.encode('hex')


ACCOUNT_TABLE = 'account'    
SESSION_TABLE = 'session'
FOLLOW_TABLE = 'follow'
OAUTH_TABLE = 'oauth'
#------------------------------------------------------------------------------ 
def register(email, mobile, nickname, password):
    email = mysql.escape(email)
    mobile = mysql.escape(mobile)
    nickname = mysql.escape(nickname)
    if email:
        SQL = '''SELECT * FROM `%s` WHERE `email` = '%s' limit 1
        ''' % (ACCOUNT_TABLE, email)
        res = db_account.query(SQL, mysql.QUERY_DICT)
        if res:
            return _code.CODE_ACCOUNT_EXIST
    elif mobile:
        SQL = '''SELECT * FROM `%s` WHERE `mobile` = '%s' limit 1
        ''' % (ACCOUNT_TABLE, mobile)
        res = db_account.query(SQL, mysql.QUERY_DICT)
        if res:
            return _code.CODE_ACCOUNT_EXIST    

    if checkNickName(nickname):
        return _code.CODE_ACCOUNT_NICKNAME_EXIST        
    
    password = mysql.escape(encryptPassword(password))
    SQL = '''INSERT INTO `%s` (`email`, `mobile`, `passwd`, `nickname`, `ctime`) VALUES ('%s', '%s', '%s', '%s', now())
    ''' % (ACCOUNT_TABLE, email, mobile, password, nickname)
    res = db_account.execute(SQL)
    return _code.CODE_OK


def checkNickName(nickname):
    SQL = '''SELECT * FROM `%s` WHERE `nickname` = '%s'
    ''' % (ACCOUNT_TABLE, mysql.escape(nickname))
    res = db_account.query_one(SQL, mysql.QUERY_DICT)
    return True if res else False


def checkAccountWithEmail(email, password):
    email = mysql.escape(email)
    SQL = '''SELECT `userid`, `passwd` FROM `%s` WHERE `email` = '%s'
          ''' % (ACCOUNT_TABLE, email)
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        res = res[0]
        passwordInDB = res['passwd']
        password = mysql.escape(encryptPassword(password))
        if password == passwordInDB:
            return _code.CODE_OK, {'userid' : res['userid']}
        else:
            return _code.CODE_ACCOUNT_PASSWORDERROR, None
    else:
        return _code.CODE_ACCOUNT_ACCOUNTNOTMATCH, None
    


def checkAccountWithMobile(mobile, password):
    mobile = mysql.escape(mobile)
    SQL = '''SELECT `userid`, `passwd` FROM `%s` WHERE `mobile` = '%s'
          ''' % (ACCOUNT_TABLE, mobile)
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        res = res[0]        
        passwordInDB = res['passwd']
        password = mysql.escape(encryptPassword(password))
        if password == passwordInDB:
            return _code.CODE_OK, {'userid' : res['userid']}
        else:
            return _code.CODE_ACCOUNT_PASSWORDERROR, None
    else:
        return _code.CODE_ACCOUNT_ACCOUNTNOTMATCH, None


def follow(followee, follower):
    SQL = '''INSERT INTO `%s` (`followee`, `follower`) VALUES (%d, %d)
          '''% (FOLLOW_TABLE, int(followee), int(follower))
    db_account.execute(SQL)
    return  _code.CODE_OK


def delFollow(followee, follower):
    SQL = '''DELETE FROM `%s` WHERE `followee` =%d AND `follower` = %d
          ''' % (FOLLOW_TABLE, int(followee), int(follower))
    res = db_account.execute(SQL)
    if res == 1:
        return  _code.CODE_OK, res
    else:
        return  _code.CODE_FOLLOWER_NOTEXIST, None


def queryAllFollowee(userid):
    SQL = '''SELECT `userid`, `nickname`, `thumbnail`, `email`, `mobile`, `ctime`, `sign` FROM `account` LEFT JOIN `follow`
             ON `follow`.`followee` = `account`.`userid` WHERE `follower` = %d
          ''' % (int(userid))
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        return  _code.CODE_OK, res
    else:
        return  _code.CODE_FOLLOWEE_NOTEXIST, None


def queryAllFollower(userid):
    SQL = '''SELECT `userid`, `nickname`, `thumbnail`, `email`, `mobile`, `ctime`, `sign` FROM `account` LEFT JOIN `follow`
             ON `follow`.`follower` = `account`.`userid` WHERE `followee` = %d
          ''' % (int(userid))
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res
    else:
        return _code.CODE_FOLLOWER_NOTEXIST, None


def updateThumbnail(userid, thumbnail):
    SQL = '''UPDATE `%s` SET `thumbnail` = '%s' WHERE `userid` = %d
          ''' % (ACCOUNT_TABLE, mysql.escape(thumbnail), int(userid))
    rows = db_account.execute(SQL)
    if rows == 1:
        return _code.CODE_OK, None
    else:
        return _code.CODE_ACCOUNT_NOT_EXIST, None


def queryUserInfo(userid):
    SQL = '''SELECT `userid`, `nickname`, `thumbnail`, `sign` FROM `%s` WHERE `userid` = %d LIMIT 1
          ''' % (ACCOUNT_TABLE, int(userid))
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_ACCOUNT_NOT_EXIST, None


def updateSign(userid, sign):
    SQL = '''UPDATE `%s` SET `sign` = '%s' WHERE `userid` = %d LIMIT 1
          ''' % (ACCOUNT_TABLE, mysql.escape(sign), int(userid))
    rows = db_account.execute(SQL)
    if rows == 1:
        return  _code.CODE_OK, None
    else:
        return  _code.CODE_ACCOUNT_NOT_EXIST, None


def updateNickName(userid, nickname):
    SQL = '''UPDATE `%s` SET `nickname` = '%s' WHERE `userid` = %d LIMIT 1
          ''' % (ACCOUNT_TABLE, mysql.escape(nickname), int(userid))
    rows = db_account.execute(SQL)
    if rows == 1:
        return  _code.CODE_OK, None
    else:
        return  _code.CODE_ACCOUNT_NOT_EXIST, None


def searchNickname(nickname):
    SQL = '''SELECT `userid`, `thumbnail`, `nickname` FROM `%s` WHERE `nickname` = '%s' LIMIT 1
          ''' % (ACCOUNT_TABLE, mysql.escape(nickname))
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_ACCOUNT_NOT_EXIST, None


from kputils import misc
def format_oauth_nickname(nickname, source):
    return '%s(%s_%s)' % (nickname, misc.randomStr(), source)


def checkoauth(openid, source, nickname):
    SQL = '''SELECT `userid` FROM `oauth` WHERE `openid` = '%s' AND `source` = '%s' LIMIT 1
          ''' % (mysql.escape(openid), mysql.escape(source))
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        userid = res[0]['userid']
        SQL = '''SELECT `nickname` FROM `account` WHERE `userid` = %d LIMIT 1
              ''' % (int(userid))
        res = db_account.query(SQL, mysql.QUERY_DICT)
        nickname = res[0]['nickname']
        return _code.CODE_ACCOUNT_EXIST, userid, nickname
    else:
        #regist
        format_nickname =  format_oauth_nickname(nickname, source)
        SQL = '''INSERT INTO `%s` (`nickname`, `ctime`) VALUES ('%s', now())
              ''' % (ACCOUNT_TABLE, mysql.escape(format_nickname))
        userid = db_account.execute(SQL)
        if userid:
            SQL = '''INSERT INTO `oauth` (`openid`, `source`, `userid`) VALUES ('%s', '%s', %d)
                  ''' % (mysql.escape(openid), mysql.escape(source), int(userid))
            res = db_account.execute(SQL)
            if res:
                return _code.CODE_ACCOUNT_NOT_EXIST, userid, format_nickname

        return _code.CODE_ACCOUNT_DBERROR, None



