# coding:utf8
"""

Author: ilcwd
"""

import urlparse
import traceback

from flask import request

from userpartition.base import application, jsonify, logger


@application.route('/userpartition/querypartitionurl')
def querypartitionurl():
    return jsonify()