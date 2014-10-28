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

from aura.models.oss import ossmisc

#------------------------------------------------------------------------------ 

class Test(unittest.TestCase):
    def setUp(self):
        self.username = 'test%d@ks.com' % int(time.time())
        self.nickname = 'test%d' % int(time.time())
        data = {'email':self.username, 'password':'123456', 'nickname' : self.nickname}
        data = ujson.dumps(data)
        
        res = self.api('emailRegist', data)
        assert res['result_code'] == 10000
        
        data = {'username' : self.username, 'password':'123456', 'type' : 'email'}
        data = ujson.dumps(data)
        
        res = self.api('login', data)
        assert res['result_code'] == 10000
        self.token = res['token']
  
    def tearDown(self):
        pass
    
    def api(self, func, data):
        url = conf.AURA_URL + func        
        deviceId = 'fake_device_xiaobei'
        header = {'Content-Type': 'application/json', 'deviceId' : deviceId}
        code, res = curl.openurl(url, data, header, 30)
        print res
        return ujson.loads(res)

    
#    def testCreateAlbum(self):
#        name = 'test%d' % int(time.time())
#        data = {'token' : self.token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'name' : name}
#        data = ujson.dumps(data)
#        
#        res = self.api('createAlbum', data)
#        assert res['result_code'] == 10000
#        albumid = res['albumid']
#        
#        data = {'token' : self.token, 'latitude':40.0425140000, 'longitude': 116.3293040000}
#        data = ujson.dumps(data)
        
#        res = self.api('recommendAlbum', data)
#        assert res['result_code'] == 10000


    def testUploadPhoto(self):
        name = 'test2%d' % int(time.time())
        data = {'token' : self.token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'name' : name}
        data = ujson.dumps(data)
        
        res = self.api('createAlbum', data)
        assert res['result_code'] == 10000
        albumid = res['albumid']
        
        
        
        filename = './1.jpg'
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
            return 

        assert res['result_code'] == 14004, res 
        #upload file
        res = ossmisc.uploadFile(sha1, content)
        assert res == 10000
        
        # true commit 
        data = {'token' : self.token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'sha1' : sha1, 'albumid' : albumid}
        data = ujson.dumps(data)
        res = self.api('commit', data)
        assert res['result_code'] == 10000
        

#------------------------------------------------------------------------------ 
if __name__ == '__main__':
    unittest.main(Test.testUploadPhoto)