# coding:utf8
"""

Author: ilcwd
"""

import urlparse
import traceback

from flask import request

from aura.base import application, jsonify, logger


@application.route('/aura/regist')
def regist():
    args = request.args
    return jsonify('Not implemented')