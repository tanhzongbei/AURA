#coding:utf8 
#__author__ = 'xiaobei'
#__time__= '9/7/15'

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

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
