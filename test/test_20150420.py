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

        return username, token


    def api(self, func, data):
        url = conf.AURA_URL + func        
        deviceId = 'fake_device_xiaobei'
        header = {'Content-Type': 'application/json', 'deviceId' : deviceId}
        code, res = curl.openurl(url, data, header, 30)
        return ujson.loads(res)

    
    def createAlbum(self, token):
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
        data = {'token' : token, 'latitude':40.0425140000, 'longitude': 116.3293040000, 'sha1' : sha1, 'albumid' : albumid}
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
        ### 上传2个文件到相册，然后再删除
        username, token = self.regist()
        albumid = self.createAlbum(token)

        photoid1 = self.UploadPhoto(token, albumid)
        photoid2 = self.UploadPhoto(token, albumid)

        data = {'token' : token, 'latitude':40.0425140000, 'longitude': 116.3293040000}
        res = self.api('recommendAlbum', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token}
        res = self.api('queryAlbum', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert len(res['albums']) == 1

        ### 为photo1点赞
        username1, token1 = self.regist()
        data = {'token' : token1, 'photoid':photoid1}
        res = self.api('favourite', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token}
        res = self.api('queryAlbum', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert len(res['albums']) == 1
        assert int(res['albums'][0]['fcount']) == 1, res

        data = {'token' : token1, 'photoid':photoid1}
        res = self.api('delFavourite', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token}
        res = self.api('queryAlbum', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert len(res['albums']) == 1
        assert int(res['albums'][0]['fcount']) == 0, res

        data = {'token' : token, 'latitude':40.0425140000, 'longitude': 116.3293040000}
        res = self.api('recommendAlbum', ujson.dumps(data))
        assert res['result_code'] == 10000


        data = {'token' : token1, 'photoid':photoid1}
        res = self.api('favourite', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token1, 'photoid':photoid2}
        res = self.api('favourite', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token1, 'albumid' : albumid}
        res = self.api('queryPhotoInfo', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert res['photoes'][0]['haveFavourte']
        assert res['photoes'][1]['haveFavourte']

        data = {'token' : token, 'photoid' : photoid1}
        res = self.api('deletePhoto', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token1, 'albumid' : albumid}
        res = self.api('queryPhotoInfo', ujson.dumps(data))
        assert res['result_code'] == 10000
        assert len(res['photoes']) == 1

        data = {'token' : token, 'albumid' : albumid}
        res = self.api('deleteAlbum', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token}
        res = self.api('queryAlbum', ujson.dumps(data))
        assert res['result_code'] == 14002


    def test2(self):
        ### 上传2个文件到相册，然后再删除
        username, token = self.regist()
        albumid = self.createAlbum(token)

        photoid1 = self.UploadPhoto(token, albumid)
#        photoid2 = self.UploadPhoto(token, albumid)

        ### 为photo1点赞
        username1, token1 = self.regist()
        data = {'token' : token1, 'photoid':photoid1}
        res = self.api('favourite', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token1, 'albumid' : albumid}
        res = self.api('queryPhotoInfoByFcount', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token1, 'albumid' : albumid}
        res = self.api('queryPhotoInfoByCtime', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token1}
        res = self.api('queryMostPopPhoto', ujson.dumps(data))
        assert res['result_code'] == 10000

        data = {'token' : token, 'city' : '北京市'}
        res = self.api('recommendPhotoesByCity', ujson.dumps(data))
        assert res['result_code'] == 10000


        data = {'token' : '0000005524e9435aaf962efcb303e294', 'mtime' : '2014-01-01 00:00:00'}
        res = self.api('queryRecentlyInfo', ujson.dumps(data))
        print res

#------------------------------------------------------------------------------ 
if __name__ == '__main__':
    unittest.main(defaultTest='Test.test2')
