# coding:utf8
"""

Author: ilcwd
"""

import flask
import logging

import ujson as _json


application = flask.Flask(__name__)
logger = logging.getLogger(__name__)


def jsonify(content):
    return application.response_class(_json.dumps(content), mimetype='application/json')