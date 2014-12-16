# coding:utf8
'''
author : xiaobei
createtime : 2014-12-09 11:35:07
''' 

import definecode as _code
from aura.apis.apiaura import *
from aura.models import  accountDAO

@application.route('/aura/follow', methods=['POST'])
def follow():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    followeeid = args.get('followeeid', None)
    if not followeeid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code = accountDAO.follow(followeeid, userid)

    return  jsonify({'result_code' : code})


@application.route('/aura/delFollowee', methods=['POST'])
def delFollowee():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    followeeid = args.get('followeeid', None)
    if not followeeid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = accountDAO.delFollow(followeeid, userid)
    return jsonify({'result_code' : code})



@application.route('/aura/delFollower', methods=['POST'])
def delFollower():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    followerid = args.get('followerid', None)
    if not followerid:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})

    code, res = accountDAO.delFollow(userid, followerid)
    return jsonify({'result_code' : code})


@application.route('/aura/getAllFollowee', methods=['POST'])
def getAllFollowee():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    code, res = accountDAO.queryAllFollowee(userid)
    if code == _code.CODE_OK:
        return  jsonify({'result_code' : code, 'followee' : res})
    else:
        return jsonify({'result_code' : code})



@application.route('/aura/getAllFollower', methods=['POST'])
def getAllFollower():
    args = request.json
    token = args.get('token', None)
    code, userid = getSessionData(token)
    if code != _code.CODE_OK:
        return jsonify({'result_code' : _code.CODE_SESSION_INVAILD})

    code, res = accountDAO.queryAllFollower(userid)
    if code == _code.CODE_OK:
        return  jsonify({'result_code' : code, 'follower' : res})
    else:
        return jsonify({'result_code' : code})