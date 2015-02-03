# coding:utf8
'''
author : xiaobei
createtime : 2015-02-03 16:38:00
''' 
#coding:utf8
'''
Created on 2014-10-22

@author: xiaobei
'''
import urllib2
from kputils.urltools import curl
import unittest
import testconfig as conf
import ujson
import time
import hashlib
import random

from aura.models.oss import ossmisc


#------------------------------------------------------------------------------
#(40.0425140000,116.3293040000) 的地址是：北京市海淀区小营西路33号金山软件大厦
#(40.0493550000,116.3251520000) 的地址时：北京市海淀区安宁庄西路9号 当代城市家园

def genusername(n = 6):
    SAMPLE = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(SAMPLE) for _i in xrange(n)])


class Test(unittest.TestCase):
    def setUp(self):
        self.username, self.nickname = self.register()
        self.token, self.userid = self.login(self.username)

    def tearDown(self):
        pass


    def register(self):
        username = 'test%s@ks.com' % genusername()
        nickname = 'test%s' % genusername()
        data = {'email':username, 'password':'123456', 'nickname' : nickname}
        data = ujson.dumps(data)

        res = self.api('emailRegist', data)
        assert res['result_code'] == 10000,res
        return username, nickname


    def login(self, username):
        data = {'username' : username, 'password':'123456', 'type' : 'email'}
        data = ujson.dumps(data)

        res = self.api('login', data)
        assert res['result_code'] == 10000
        return res['token'], res['userid']



    def api(self, func, data):
        url = conf.AURA_URL + func
        deviceId = 'fake_device_xiaobei'
        header = {'Content-Type': 'application/json', 'deviceId' : deviceId}
        code, res = curl.openurl(url, data, header, 30)
        return ujson.loads(res)


    def testUploadPhoto(self):
        name = 'test2%d' % int(time.time())
        data = {'token' : self.token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'name' : name}
        data = ujson.dumps(data)

        res = self.api('createAlbum', data)
        assert res['result_code'] == 10000
        albumid = res['albumid']

        filename = './2.png'
        content = open(filename, 'r').read()

        sha = hashlib.sha1()
        sha.update(content)
        sha1 = sha.hexdigest()

        # first commit
        data = {'token' : self.token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'sha1' : sha1, 'albumid' : albumid}
        data = ujson.dumps(data)
        res = self.api('commit', data)

        if res['result_code'] == 10000:
            assert res['photoid'] is not None
            photoid  = res['photoid']
        else:
            assert res['result_code'] == 14004, res
            #upload file
            res = ossmisc.uploadFile(sha1, content)
            assert res == 10000

            # true commit
            data = {'token' : self.token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'sha1' : sha1, 'albumid' : albumid}
            data = ujson.dumps(data)
            res = self.api('commit', data)
            assert res['result_code'] == 10000
            photoid  = res['photoid']

        #download file
        res = ossmisc.downloadFile(sha1)
        assert res.read() == content

        username2, __ = self.register()
        token2, uid2 = self.login(username2)

        data = {'token':token2, 'photoid' : photoid}
        res = self.api('favourite', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token':self.token}
        res = self.api('queryAlbum', ujson.dumps(data))
        assert res['result_code'] == 10000
        albumid = res['albums'][0]['albumid']

        data = {'token':self.token, 'albumid' : albumid}
        res = self.api('queryPhotoInfoByFcount', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert res['photoes'][0]['fcount'] == '1'

        res = self.api('queryPhotoInfoByCtime', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert res['photoes'][0]['fcount'] == '1'


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
