#coding:utf8
'''
Created on 2014-9-1

@author: xiaobei721
'''

from db import (
                db_account,
                cache_account
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
#------------------------------------------------------------------------------ 
def register(email, mobile, password):
    email = mysql.escape(email)
    mobile = mysql.escape(mobile)
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
    
    password = mysql.escape(encryptPassword(password))
    SQL = '''INSERT INTO `%s` (`email`, `mobile`, `passwd`, `ctime`) VALUES ('%s', '%s', '%s', now())
    ''' % (ACCOUNT_TABLE, email, mobile, password)
    res = db_account.execute(SQL)
    return _code.CODE_OK


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
    
    