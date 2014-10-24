#coding:utf8
'''
Created on 2014-9-1

@author: xiaobei
'''

import config as _conf
import redis
from kputils import (
    mysql,
    cache,
)

#------------------------------------------------------------------------------ 

db_account = mysql.BaseDB(_conf.MYSQL_ACCOUNT)
db_album = mysql.BaseDB(_conf.MYSQL_ALBUM)
redis_default = redis.Redis(_conf.REDIS_DEFAULT['host'], _conf.REDIS_DEFAULT['port']) 
mc_default = cache.MCCache(_conf.MC_DEFAULT)
