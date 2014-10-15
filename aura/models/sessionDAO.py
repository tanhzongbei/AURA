#coding:utf8
'''
Created on 2014-10-14

@author: xiaobei
'''
from db import (
                db_account,
                mc_default
)

from kputils import (
                    mysql,
                    spy,
)
import definecode as _code
import uuid
import ujson as _json
import time
import hashlib
import datetime

EXPIRED_TIME = 15 * 24 * 3600
PREFIX = 'SESSION@'
SESSION_TABLE = 'session'
#------------------------------------------------------------------------------ 
def createSession(userid, deviceId, ip): 
    token = genToken(userid)
    ctime = int(time.time())
    etime = ctime +  EXPIRED_TIME
    code = insertSessionSQL(token, userid, ip, deviceId, ctime, etime)
    if code == _code.CODE_OK:
        setmc(token, userid, deviceId, ip, ctime, etime)
    
    return code, token


def deleteSession(token):
    code = deleteSessionSQL(token)
    if code == _code.CODE_OK:
        deletemc(token)
    return code


def querySession(token):
    res = querymc(token)
    if res:
        res = _json.loads(res)
        etime = res['etime']
        if int(etime) < int(time.time()):
            return _code.CODE_SESSION_EXPIRED, None
    else:
        code, res = querySessionSQL(token)
        if code != _code.CODE_OK:
            return code, None        
        etime = res['etime']
        if int(str2timestamp(etime)) < int(time.time()):
            return _code.CODE_SESSION_EXPIRED, None
        
    userid = res['userid']
    return _code.CODE_OK, userid
    

def setmc(token, userid, deviceId, ip, ctime, etime):
    key = PREFIX + token
    value = {'userid' : userid, 'deviceId' : deviceId, 'ip' : ip, 'ctime' : ctime, 'etime' : etime}
    value = _json.dumps(value)
    mc_default.set(key, value, EXPIRED_TIME)


def deletemc(token):
    #kes must be str()'s
    key = PREFIX + token
    mc_default.delete(key.encode('utf8'))


def querymc(token):
    key = PREFIX + token
    value = mc_default.get(key)
    return value
#------------------------------------------------------------------------------ 
def genToken(userid):
    uid = uuid.uuid4().hex
    sidHex = '%08x%s' % (int(userid), uid[8:])
    return sidHex


#------------------------------------------------------------------------------ 
def formatTokenToSql(token):
    return hashlib.sha1(token).digest()


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
def datetime2str(t):
    return t.strftime(TIME_FORMAT)


def timestamp2str(ts):
    return datetime2str(datetime.datetime.fromtimestamp(ts))


def str2timestamp(t):
    return time.mktime(time.strptime(t, TIME_FORMAT))


def insertSessionSQL(token, userid, ip, deviceId, ctime, etime):
    token = formatTokenToSql(token)
    SQL = '''INSERT INTO `%s` (`userid`, `sid`, `deviceid`, `ip`, `ctime`, `etime`) VALUES (%d, '%s', '%s', '%s', '%s', '%s')
    ''' % (SESSION_TABLE, int(userid), mysql.escape(token), mysql.escape(deviceId), mysql.escape(ip), timestamp2str(ctime), timestamp2str(etime))
    __, rows = db_account.insert(SQL)
    if rows == 1:
        return _code.CODE_OK
    else:
        return _code.CODE_ACCOUNT_DBERROR 


def deleteSessionSQL(token):
    token = formatTokenToSql(token)
    SQL = '''DELETE FROM `%s` WHERE `sid` = '%s' limit 1
    ''' % (SESSION_TABLE, mysql.escape(token))
    res = db_account.execute(SQL)
    if res == 1:
        return _code.CODE_OK
    else:
        return _code.CODE_ACCOUNT_DBERROR 

        
def querySessionSQL(token):
    token = formatTokenToSql(token)
    SQL = '''SELECT `userid`, `deviceid`, `ip`, `etime` FROM `%s` WHERE `sid` = '%s' LIMIT 1 
    ''' % (SESSION_TABLE, mysql.escape(token))
    res = db_account.query(SQL, mysql.QUERY_DICT)
    if res:
        return _code.CODE_OK, res[0]
    else:
        return _code.CODE_SESSION_EXPIRED, None
    

#------------------------------------------------------------------------------ 
if __name__ == '__main__':
    key = int(time.time())
    print mc_default.set(key, {'222':2222}, EXPIRED_TIME)
    print mc_default.get(key)
    print mc_default.delete(str(key))
    print mc_default.get(key)    
    