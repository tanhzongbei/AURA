#coding:utf8
'''
Created on 2014-9-1

@author: xiaobei
'''

import urllib2
from kputils.urltools import curl
import unittest
import testconfig as conf
import ujson
import time

#------------------------------------------------------------------------------ 

class Test(unittest.TestCase):
    def setUp(self):
        pass
    
    
    def tearDown(self):
        pass
    
    def api(self, func, data):
        url = conf.AURA_URL + func        
        deviceId = 'fake_device_xiaobei'
        header = {'Content-Type': 'application/json', 'deviceId' : deviceId}
        code, res = curl.openurl(url, data, header, 10)
        return ujson.loads(res)

    
    def test(self):
        username = 'test%d@ks.com' % int(time.time())
        nickname = 'test%d' % int(time.time())
        data = {'email':username, 'password':'123456', 'nickname' : nickname}
        data = ujson.dumps(data)
        
        res = self.api('emailRegist', data)
        assert res['result_code'] == 10000
        
        res = self.api('emailRegist', data)
        assert res['result_code'] == 11004
        
        data = {'email' : 'test111%d@ks.com' % int(time.time()), 'password' : '123456', 'nickname' : nickname}
        data = ujson.dumps(data)
        res = self.api('emailRegist', data)
        assert res['result_code'] == 11005
        
        data = {'username' : username, 'password':'123456', 'type' : 'email'}
        data = ujson.dumps(data)
        
        res = self.api('login', data)
        assert res['result_code'] == 10000
        
        data = {'username' : username, 'password':'12111111', 'type' : 'email'}
        data = ujson.dumps(data)
        
        res = self.api('login', data)
        assert res['result_code'] == 11002
        
        
    def testSession(self):
        username = 'testsession%d@ks.com' % int(time.time())
        nickname = 'testsession%d' % int(time.time())
        data = {'email':username, 'password':'123456', 'nickname' : nickname}
        data = ujson.dumps(data)
        
        res = self.api('emailRegist', data)
        assert res['result_code'] == 10000, res
        
        data = {'username' : username, 'password':'123456', 'type' : 'email'}
        data = ujson.dumps(data)
        
        res = self.api('login', data)
        assert res['result_code'] == 10000
        token = res['token']
        
        data = {'token' : token}
        data = ujson.dumps(data)
        res = self.api('confirm', data)
        assert res['result_code'] == 10000
        
        data = {'token' : token}
        data = ujson.dumps(data)
        res = self.api('refreshToken', data)
        assert res['result_code'] == 10000
        newtoken = res['token']

        data = {'token' : token}
        data = ujson.dumps(data)
        res = self.api('confirm', data)
        assert res['result_code'] == 12001
        
        
        data = {'token' : newtoken}
        data = ujson.dumps(data)
        res = self.api('confirm', data)
        assert res['result_code'] == 10000
        
    def testCheckNickName(self):
        username = 'testsession%d1@ks.com' % int(time.time())
        nickname = 'testsession%d1' % int(time.time())
        data = {'email':username, 'password':'123456', 'nickname' : nickname}
        data = ujson.dumps(data)
        
        res = self.api('emailRegist', data)
        assert res['result_code'] == 10000, res
        
        data = {'nickname' : nickname}
        data = ujson.dumps(data)
        res = self.api('checkNickName', data)
        assert res['result_code'] == 10000 and res['exist'], res


    def testFollow(self):
        # 1关注2，2关注1，3关注1，然后互相查看关注的关系
        username1 = 'testsession%d11@ks.com' % int(time.time())
        username2 = 'testsession%d22@ks.com' % int(time.time())
        username3 = 'testsession%d33@ks.com' % int(time.time())
        self.register(username1)
        self.register(username2)
        self.register(username3)

        token1, userid1 = self.login(username1)
        token2, userid2 = self.login(username2)
        token3, userid3 = self.login(username3)

        res = self.api('follow', ujson.dumps({'followeeid' : userid2, 'token' : token1}))
        assert res['result_code'] == 10000, res

        res = self.api('follow', ujson.dumps({'followeeid' : userid1, 'token' : token2}))
        assert res['result_code'] == 10000, res

        res = self.api('follow', ujson.dumps({'followeeid' : userid1, 'token' : token3}))
        assert res['result_code'] == 10000, res

        # check user1
        res = self.api('getAllFollower', ujson.dumps({'token' : token1}))
        assert res['result_code'] == 10000, res
        for item in res['follower']:
            assert item['userid'] in (userid2, userid3)

        res = self.api('getAllFollowee', ujson.dumps({'token' : token1}))
        assert res['result_code'] == 10000, res
        for item in res['followee']:
            assert item['userid'] == userid2

        # check user2
        res = self.api('getAllFollower', ujson.dumps({'token' : token2}))
        assert res['result_code'] == 10000, res
        for item in res['follower']:
            assert item['userid'] == userid1

        res = self.api('getAllFollowee', ujson.dumps({'token' : token2}))
        assert res['result_code'] == 10000, res
        for item in res['followee']:
            assert item['userid'] == userid1

        # check user3
        res = self.api('getAllFollower', ujson.dumps({'token' : token3}))
        assert  res['result_code'] == 16002
        res = self.api('getAllFollowee', ujson.dumps({'token' : token3}))
        assert res['result_code'] == 10000, res
        for item in res['followee']:
            assert item['userid'] == userid1


    def register(self, username, password = '123456'):
        data = {'email':username, 'password': password, 'nickname' : username + 'nickname'}
        data = ujson.dumps(data)

        res = self.api('emailRegist', data)
        assert res['result_code'] == 10000, res


    def login(self, username, password = '123456', type = 'email'):
        data = {'username' : username, 'password':password, 'type' : type}
        data = ujson.dumps(data)

        res = self.api('login', data)
        assert res['result_code'] == 10000
        token = res['token']
        userid = res['userid']
        return  token, userid
    
if __name__ == '__main__':
    unittest.main()