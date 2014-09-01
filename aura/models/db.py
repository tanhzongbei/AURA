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

db_account = mysql.BaseDB(_conf.MYSQL_ACCOUNT)
mc_default = cache.MCCache(_conf.MC_DEFAULT)
cache_account = cache.CacheContext(mc_default, prefix='ACCOUNT@AURA@', expires=_conf.MC_EXPIRES)
