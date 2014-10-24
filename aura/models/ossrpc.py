#coding:utf8
'''
Created on 2014-10-16

@author: xiaobei
'''
import time
from oss.oss_api import *
from oss.oss_xml_handler import *
import config as _cnf

#------------------------------------------------------------------------------ 
def getBucketInfo():
    res = oss.get_service()
    if (res.status / 100) == 2:
        body = res.read()
        h = GetServiceXml(body)
        print "bucket list size is: ", len(h.list())
        print "bucket list is: "
        for i in h.list():
            print i
    else:
        print res.status


oss = OssAPI(_cnf.OSS_HOST, _cnf.OSS_KEY, _cnf.OSS_SECRET)

#------------------------------------------------------------------------------ 
if __name__ == '__main__':
    getBucketInfo()