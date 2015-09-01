#coding:utf8
'''
Created on 2014-10-27

@author: xiaobei
'''
import time
try:
    from oss.oss_api import *
except:
    from oss_api import *
try:
    from oss.oss_xml_handler import *
except:
    from oss_xml_handler import *
import config as _cnf
import hashlib
import definecode as _code
#------------------------------------------------------------------------------

def headObj(sha1):
    res = oss.head_object(_cnf.OSS_BUCKET_NAME, sha1)
    if (res.status / 100) == 2:
        return _code.CODE_OK
    elif res.status == 404:
        return _code.CODE_FILE_NOTEXIST
    else:
        return _code.CODE_OSS_RPC_ERROR

def getBukect():
    res = oss.get_service()
    if (res.status / 100) == 2:
        body = res.read()
        h = GetServiceXml(body)
        return _code.CODE_OK, h.list()
    else:
        print _code.CODE_OSS_BUCKET_NOTEXIST, None


def uploadFile(sha1, input_content):
    content_type = "text/HTML"
    headers = {}
    res = oss.put_object_from_string(_cnf.OSS_BUCKET_NAME, sha1, input_content, content_type, headers)
    if (res.status / 100) == 2:
        print "put_object_from_string OK"
        return _code.CODE_OK
    else:
        print "put_object_from_string ERROR"
        return _code.CODE_OSS_RPC_ERROR



def downloadFile(sha1):
    res = oss.get_object(_cnf.OSS_BUCKET_NAME, sha1)

    if (res.status / 100) == 2:
        print "get_object OK"
    else:
        print "get_object ERROR"

    return res


def getUrl(sha1):
    res = oss.sign_url('GET', _cnf.OSS_BUCKET_NAME, sha1, 3600)
    if res:
        print "get_object OK"
    else:
        print "get_object ERROR"

    return res

    
oss = OssAPI(_cnf.OSS_HOST, _cnf.OSS_KEY, _cnf.OSS_SECRET)

#------------------------------------------------------------------------------ 
if __name__ == '__main__':
    #'test2014-oct-2716-08-27'
    getBukect()
    sample = 'hello wenda'
    sha = hashlib.sha1()
    sha.update(sample)
    sha1 = sha.hexdigest()
    # print uploadFile(sha1, sample)
    # print headObj(sha1)
    print downloadFile(sha1)
    print getUrl(sha1)
    

