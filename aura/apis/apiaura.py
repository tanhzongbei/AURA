# coding:utf8
"""

Author: ilcwd
"""

import urlparse
import traceback

from flask import request
from aura.base import application, jsonify, logger
from aura.models import (
                         accountDAO,
                         )
import definecode as _code
import ujson


@application.route('/aura/emailRegist', methods=['POST'])
def emailRegist():
    args = list()
    for k in request.form:
        args.append(k)
    args = ujson.loads(args[0])
    email = args.get('email', None)
    password = args.get('password', None)
    if not email or not password:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})
    
    res = accountDAO.register(email, None, password)    
    return jsonify({'result_code' : res})


@application.route('/aura/mobileRegist', methods=['POST'])
def mobileRegist():
    args = list()
    for k in request.form:
        args.append(k)
    args = ujson.loads(args[0])
    mobile = args.get('mobile', None)
    password = args.get('password', None)
    if not mobile or not password:
        return jsonify({'result_code' : _code.CODE_BADPARAMS})
    res = accountDAO.register(None, mobile, password)        
    return jsonify({'result_code' : res})



@application.route('/aura/login', methods=['POST'])
def login():
    args = list()
    for k in request.form:
        args.append(k)
    args = ujson.loads(args[0])
    username = args.get('username', None)
    password = args.get('password', None)
    type = args.get('type', None)
    if type == 'email':
        code, res = accountDAO.checkAccountWithEmail(username, password)
    elif type == 'mobile':
        code, res = accountDAO.checkAccountWithMobile(username, password)
    else:
        code = _code.CODE_BADPARAMS
    
    #todo session and accountinfo
    ret = {'result_code':code}
    return jsonify(ret)
    
