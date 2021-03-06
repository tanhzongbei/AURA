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


def parseGeoHash(hash):
    return geohash.decode(hash)


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
    lat_org = 40.0425140000
    lng_org = 116.3293040000
    hash = getGeoHash(lat_org, lng_org)
    res = parseGeoHash(hash)
    lat, lng = res
    code, location = getLocation(lat_org, lng_org)
    code, location1 = getLocation(lat, lng)
    print location['formatted_address']
    print location1['formatted_address']