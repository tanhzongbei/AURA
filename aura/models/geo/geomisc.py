#coding:utf8
'''
Created on 2014-10-22

@author: xiaobei
'''
import geohash
import math
from kputils.urltools import curl
import config as _cnf
import ujson as _json
import definecode as _code
#------------------------------------------------------------------------------ 
def getGeoHash(lat, lng):
    return geohash.encode(lat, lng, 9)


def getLocation(lat, lng):
    url = _cnf.BAIDU_URL + 'ak=%s&' % _cnf.BAIDU_AK + 'location=%s,%s&output=json&pois=0' % (str(lat),str(lng))
    code, res = curl.openurl(url)
    if code == 200:
        res = _json.loads(res)
        result = {}
        if res['status'] == 0:
            result = res['result']
            return _code.CODE_OK, result
        else:
            return _code.CODE_GEO_BAIDURPC_FAILD, None 
    else:
        code, res = curl.openurl(url)
        if code == 200:
            res = _json.loads(res)
            result = {}
            if res['status'] == 0:
                result = res['result']
                return _code.CODE_OK, result
        return _code.CODE_GEO_BAIDURPC_FAILD, None 
            
        
    
#------------------------------------------------------------------------------ 
if __name__ == '__main__':
    print getGeoHash(40.0425140000,116.3293040000)
    print getGeoHash(40.0439270000,116.3457650000)