#coding:utf8
'''
Created on 2014-9-1

@author: xiaobei
'''

import config as _conf

from kputils import (
    mysql,
    cache,
)

#------------------------------------------------------------------------------ 

db_account = mysql.BaseDB(_conf.MYSQL_OPENAPI)
db_opensession = mysql.BaseDB(_conf.MYSQL_OPENSESSION)

mc_default = cache.MCCache(_conf.MC_DEFAULT)

cache_auth = cache.CacheContext(mc_default, prefix='AUTH@OPENAUTH@', expires=_conf.MC_EXPIRES)
