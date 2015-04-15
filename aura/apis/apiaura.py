# coding:utf8
"""

Author: ilcwd
"""


from flask import request
from aura.base import application, jsonify, logger
from aura.models import (
                         accountDAO,
                         sessionDAO,
                         fileDAO
                         )
import definecode as _code
from aura.models.geo import geomisc
from aura.models.oss import ossmisc
import ujson

@application.route('/aura/emailRegist', methods=['POST'])
def emailRegist():
    args = request.json
    email = args.get('email', None)
    password = args.get('password', None)
    nickname = args.get('nickname', None)
    if not email or not password or not nickname:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})
    
    res = accountDAO.register(email, None, nickname, password)    
    return jsonify({'result_code' : res})


@application.route('/aura/mobileRegist', methods=['POST'])
def mobileRegist():
    args = request.json
    mobile = args.get('mobile', None)
    password = args.get('password', None)
    nickname = args.get('nickname', None)    
    if not mobile or not password or not nickname:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})
    res = accountDAO.register(None, mobile, nickname, password)        
    return jsonify({'result_code' : res})


@application.route('/aura/checkNickName', methods=['POST'])
def checkNickName():
    args = request.json
    nickname = args.get('nickname', None)    
    if not nickname:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})
    res = accountDAO.checkNickName(nickname)
    return jsonify({'result_code':_code.CODE_OK, 'exist' : res})


@application.route('/aura/login', methods=['POST'])
def login():
    header = request.headers.environ
    deviceId = header.get('HTTP_DEVICEID', None)
    ip = header.get('REMOTE_ADDR', None)
    args = request.json
    username = args.get('username', None)
    password = args.get('password', None)
    type = args.get('type', None)
    if not username or not password or not type:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})        
    if type == 'email':
        code, res = accountDAO.checkAccountWithEmail(username, password)
    elif type == 'mobile':
        code, res = accountDAO.checkAccountWithMobile(username, password)
    else:
        code = _code.CODE_BADPARAMS
    
    if code == _code.CODE_OK:
        userid = res['userid']
        #create session
        code, token = sessionDAO.createSession(userid, deviceId, ip)

        ret = {'result_code':code, 'token' : token, 'userid' : userid}
    else:
        ret = {'result_code':code}
    return jsonify(ret)
    

@application.route('/aura/refreshToken', methods=['POST'])
def refreshToken():
    header = request.headers.environ
    deviceId = header.get('HTTP_DEVICEID', None)
    ip = header.get('REMOTE_ADDR', None)
    args = request.json
    token = args.get('token', None)
    if not token :
        return jsonify({'result_code' : _code.CODE_BADPARAMS})
    
    code, userid = sessionDAO.querySession(token)
    if code != _code.CODE_OK:
        ret = {'result_code':code}
    
    code, newtoken = sessionDAO.createSession(userid, deviceId, ip)
    if code == _code.CODE_OK:
        sessionDAO.deleteSession(token)
    ret = {'result_code':code, 'token' : newtoken}
    return jsonify(ret)


@application.route('/aura/confirm', methods=['POST'])
def confirm():
    args = request.json
    token = args.get('token', None)
    if not token :
        return jsonify({'result_code' : _code.CODE_BADPARAMS})
    
    code, userid = sessionDAO.querySession(token)
    ret = {'result_code': code, 'userid' : userid}
    return jsonify(ret)


def getSessionData(token):
    code, userid = sessionDAO.querySession(token)
    if code == _code.CODE_OK:
        return code, userid
    else:
        return code, None


#------------------------------------------------------------------------------ 
@application.route('/aura/recommendAlbum', methods = ['POST'])
def recommendAlbum():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    latitude = args.get('latitude', None)
    longitude = args.get('longitude', None)
    
    geohash = geomisc.getGeoHash(latitude, longitude)
    
    code, res = fileDAO.queryPhotoInfoByLocate(geohash)
    if code == _code.CODE_OK:
        return jsonify({'result_code' : code, 'photoes' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/createAlbum', methods = ['POST'])
def createAlbum():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    latitude = args.get('latitude', None)
    longitude = args.get('longitude', None)
    name = args.get('name', None)
    type = args.get('type', None)
    onlyfindbyfriend = args.get('onlyfindbyfriend', None)
    
    if not latitude or not longitude or not name or not type:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})        
    
    code, result = geomisc.getLocation(latitude, longitude)
    if code == _code.CODE_OK:
        city = result['addressComponent']['city']
    else:
        return jsonify({'result_code' : code})
    
    code, res = fileDAO.queryCityId(city)
    if code == _code.CODE_CITY_NOTEXIST:
        code, cityid = fileDAO.insertCity(city)
    else:
        cityid = res['autoid']
        
    geohash = geomisc.getGeoHash(latitude, longitude)
        
    code, res = fileDAO.insertAlbum(name, geohash, cityid, userid, type, onlyfindbyfriend)
    if code == _code.CODE_OK:
        return jsonify({'result_code': code, 'albumid' : res})
    else:
        return jsonify({'result_code' : code})
     

@application.route('/aura/setOnlyFindbyFriend')
def setOnlyFindbyFriend():
    args = request.json

    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    albumid = args.get('albumid', None)
    onlyfindbyfriend = args.get('onlyfindbyfriend', None)
    if not albumid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = fileDAO.setOnlyFindbyFriend(albumid, onlyfindbyfriend)
    return jsonify({'result_code' : code})


@application.route('/aura/commit', methods = ['POST'])
def commit():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})
    
    # check if need upload
    sha1 = args.get('sha1', None)
    albumid = args.get('albumid', None)
    latitude = args.get('latitude', None)
    longitude = args.get('longitude', None)
    
    if not sha1 or not albumid or not latitude or not longitude :
        return jsonify({'result_code' : _code.CODE_BADPARAMS})        

    res = ossmisc.headObj(sha1)
    if res != _code.CODE_OK:
        return jsonify({'result_code': res})
    
    geohash = geomisc.getGeoHash(latitude, longitude)
    
    code, result = geomisc.getLocation(latitude, longitude)
    if code == _code.CODE_OK:
        city = result['addressComponent']['city']
    else:
        return jsonify({'result_code' : code})
    
    code, res = fileDAO.queryCityId(city)
    if code == _code.CODE_CITY_NOTEXIST:
        code, cityid = fileDAO.insertCity(city)
    else:
        cityid = res['autoid']
    
    code, res = fileDAO.insertPhoto(albumid, geohash, cityid, userid, sha1)
    if code == _code.CODE_OK:
        return jsonify({'result_code': code, 'photoid' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/queryAlbum', methods = ['POST'])
def queryAlbum():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    code, res = fileDAO.queryAlbumByUid(userid)
    if code == _code.CODE_OK:
        return jsonify({'result_code': code, 'albums' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/queryAlbumByUid', methods = ['POST'])
def queryAlbumByUid():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    uid = args.get('userid', None)

    code, res = fileDAO.queryAlbumByUid(uid)
    if code == _code.CODE_OK:
        return jsonify({'result_code': code, 'albums' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/queryAlbumByUidList', methods = ['POST'])
def queryAlbumByUidList():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    uid_list = args.get('uid_list', None)
    uid_list = ujson.loads(uid_list)

    res_list = list()
    for uid in uid_list:
        code, res = fileDAO.queryAlbumByUid(uid)
        if code == _code.CODE_OK:
            res_list.append({'uid': uid, 'albums' : [ i for i in res]})
        else:
            res_list.append({'uid': uid, 'albums' : code})

    return jsonify({'result_code' : _code.CODE_OK, 'result' : ujson.dumps(res_list)})


@application.route('/aura/queryPhotoInfo', methods = ['POST'])
def queryPhotoInfoByAlbum():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    albumid = args.get('albumid', None)

    if not albumid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = fileDAO.queryPhotoInfoByAlbumId(albumid)
    if code == _code.CODE_OK:
        return jsonify({'result_code': code, 'photoes' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/queryPhotoInfoByFcount', methods = ['POST'])
def queryPhotoInfoByFcount():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    albumid = args.get('albumid', None)
    cursor = args.get('cursor', 0)
    size = args.get('size', 100)

    if not albumid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = fileDAO.queryPhotoInfoByFcount(albumid, cursor, size)
    if code == _code.CODE_OK:
        return jsonify({'result_code': code, 'photoes' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/queryPhotoInfoByCtime', methods = ['POST'])
def queryPhotoInfoByCtime():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    albumid = args.get('albumid', None)
    cursor = args.get('cursor', 0)
    size = args.get('size', 100)

    if not albumid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = fileDAO.queryPhotoInfoByCtime(albumid, cursor, size)
    if code == _code.CODE_OK:
        return jsonify({'result_code': code, 'photoes' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/favourite', methods = ['POST'])
def favourite():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    photoid = args.get('photoid', None)

    code, __ = fileDAO.addFavourite(userid, photoid)
    return jsonify({'result_code' : code})


@application.route('/aura/delFavourite', methods = ['POST'])
def delFavourite():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    photoid = args.get('photoid', None)

    code, __ = fileDAO.delFavourite(userid, photoid)
    return jsonify({'result_code' : code})


@application.route('/aura/queryMostPopPhoto', methods = ['POST'])
def queryMostPopPhoto():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    cursor = args.get('cursor', 0)
    size = args.get('size', 10)

    code, res = fileDAO.queryMostPopPhothoes(cursor, size)

    return jsonify({'result_code' : code, 'photoes' : res})


@application.route('/aura/recommendAlbumByCity', methods = ['POST'])
def recommendPhotoesByCity():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    city = args.get('city', None)
    cursor = args.get('cursor', 0)
    size = args.get('size', 10)
    if not city:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = fileDAO.queryPhotoInfoByCity(city, cursor, size)
    if code == _code.CODE_OK:
        return jsonify({'result_code' : code, 'photoes' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/queryCityInfo', methods = ['POST'])
def queryCityInfo():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    cityid = args.get('cityid', None)
    if not cityid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = fileDAO.queryCityInfo(cityid)
    if res:
        return jsonify({'result_code':code, 'city' : res})
    else:
        return jsonify({'result_code' : code})


@application.route('/aura/queryRecentlyInfo', methods = ['POST'])
def queryRecentlyInfo():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    cursor_time = args.get('mtime', None)

    ret_list = list()
    code, res = accountDAO.queryAllFollowee(userid)
    if code == _code.CODE_OK:
        for item in res:
            code, res = fileDAO.queryRecentlyInfo(item['userid'], cursor_time)
            if code == _code.CODE_OK:
                ret_list.append(res)

    code, res = fileDAO.queryRecentlyInfo(userid, cursor_time)
    if code == _code.CODE_OK:
        ret_list.append(res[0])

    return jsonify({'result_code' : code, 'photoes' : ret_list})





#------------------------------------------------------------------------------ 
