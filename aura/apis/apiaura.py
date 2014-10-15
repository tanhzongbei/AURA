# coding:utf8
"""

Author: ilcwd
"""


from flask import request
from aura.base import application, jsonify, logger
from aura.models import (
                         accountDAO,
                         sessionDAO
                         )
import definecode as _code
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
        
        #todo session and accountinfo
        ret = {'result_code':code, 'token' : token}
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
    ret = {'result_code':code}
    return jsonify(ret)
    
