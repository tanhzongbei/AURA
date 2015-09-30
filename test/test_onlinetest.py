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
#(30.6009280000,114.3065710000) wuhan
 
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


    def login(self):

        data = {'username' : '18601139462', 'password':'123456', 'type' : 'email'}
        data = ujson.dumps(data)

        res = self.api('login', data)
        assert res['result_code'] == 10000
        token = res['token']
        userid = res['userid']

        return token, userid


    def api(self, func, data):
        url = conf.AURA_URL + func        
        deviceId = 'fake_device_xiaobei'
        header = {'Content-Type': 'application/json', 'deviceId' : deviceId}
        code, res = curl.openurl(url, data, header, 30)
        return ujson.loads(res)


    def test(self):
        token, userid = self.login()

        # data = {'token' : token}
        # data = ujson.dumps(data)
        # res = self.api('queryMostPopPhoto', data)
        # assert res['result_code'] == 10000
        # print res
        #
        # data = {'token' : token, 'longitude' : 114.3065710000, 'latitude' : 30.6009280000}
        # data = ujson.dumps(data)
        # res = self.api('recommendPhotoesByCity', data)
        # assert res['result_code'] == 10000
        # print res


        data = {'access_token' : 'OezXcEiiBSKSxW0eoylIeE9zV0byFfmq9_sZ3zwIxwRk6wm54tPwLDlw2MYzKboK4QPzZodwoi9dGpDpVw-ag4YYnzWw3sVLpbUJcBb3wGz_bdeerc_XAunQoEJ6PvvJG-hrxsvT2qHB71OgjHszog', 'openid' : 'oDNO3t1jrZSBc1GcV9kzx4dbDCbw', 'type' : 'weixin'}
        data = ujson.dumps(data)
        res = self.api('openLogin', data)
        print res


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
