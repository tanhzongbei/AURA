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
        header = {'Content-Type': 'application/json'}
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
        
    
if __name__ == '__main__':
    unittest.main()