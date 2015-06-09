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

TYPE_TOURISM = 'tourism'
TYPE_SPORTS = 'sports'
TYPE_PARTY = 'party'
TYPE_SHOW = 'show'
TYPE_PRIVTE = 'private'


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


    def regist(self):
        username = 'test%s@ks.com' % genusername()
        nickname = 'test%s' % genusername()
        data = {'email':username, 'password':'123456', 'nickname' : nickname}
        data = ujson.dumps(data)

        res = self.api('emailRegist', data)
        assert res['result_code'] == 10000,res

        data = {'username' : username, 'password':'123456', 'type' : 'email'}
        data = ujson.dumps(data)

        res = self.api('login', data)
        assert res['result_code'] == 10000
        token = res['token']

        return username, token, nickname


    def api(self, func, data):
        url = conf.AURA_URL + func        
        deviceId = 'fake_device_xiaobei'
        header = {'Content-Type': 'application/json', 'deviceId' : deviceId}
        code, res = curl.openurl(url, data, header, 30)
        return ujson.loads(res)

    
    def createAlbum(self, token, name = None):
        if not name:
            name = 'test%d' % int(time.time())
        data = {'token' : token, 'latitude':40.0425140000,
                'longitude': 116.3293040000, 'name' : name,
                'type' : TYPE_PRIVTE, 'onlyfindbyfriend' : 0}
        data = ujson.dumps(data)
        
        res = self.api('createAlbum', data)
        assert res['result_code'] == 10000
        albumid = res['albumid']
        return albumid


    def UploadPhoto(self, token, albumid):
        name = 'test2%d' % int(time.time())

        filename = './2.png'
        content = open(filename, 'r').read()
        
        sha = hashlib.sha1()
        sha.update(content)
        sha1 = sha.hexdigest()
        
        # first commit
        randomtags = genusername()
        data = {'token' : token,
                'latitude':40.0425140000, 'longitude': 116.3293040000,
                'sha1' : sha1, 'albumid' : albumid,
                'tag' : ['测试中文标签', 'test english tag', '第三个测试标签', randomtags]}
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
            data = {'token' : token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'sha1' : sha1, 'albumid' : albumid}
            data = ujson.dumps(data)
            res = self.api('commit', data)
            assert res['result_code'] == 10000
            photoid  = res['photoid']

        return photoid


    def test1(self):
        username, token, nickname = self.regist()
        username2, token2, nickname2 = self.regist()

        data = {'token' : token, 'nickname' : nickname}
        data = ujson.dumps(data)
        res = self.api('searchNickname', data)
        assert res['result_code'] == 10000
        assert res['userinfo']['nickname'] == nickname


        samepre = genusername(10)
        name = samepre + genusername(10)
        albumid1 = self.createAlbum(token, name)
        name1 = samepre + genusername(11)
        albumid2 = self.createAlbum(token, name1)

        data = {'token' : token, 'albumname' : name[-7:]}
        res = self.api('searchAlbumByName', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert len(res['albums']) == 1


        data = {'token' : token, 'albumname' : samepre}
        res = self.api('searchAlbumByName', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert len(res['albums']) == 2

        self.UploadPhoto(token, albumid1)
        self.UploadPhoto(token, albumid1)

        data = {'token' : token, 'albumname' : samepre}
        res = self.api('searchAlbumByName', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert len(res['albums']) == 2
        print res


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
