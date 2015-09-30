# coding:utf8
"""

Author: ilcwd
"""


MYSQL_ACCOUNT = dict(
    host="182.92.166.245",
    db="account",
    user="python",
    passwd="gj4fKLCcnRJQz5U1",
    port=3306,
    charset="utf8"
)

MYSQL_ALBUM = dict(
    host="182.92.166.245",
    db="album",
    user="python",
    passwd="gj4fKLCcnRJQz5U1",
    port=3306,
    charset="utf8"
)

MC_DEFAULT = ['182.92.166.245:11211']
MC_EXPIRES = 3600 * 12

REDIS_DEFAULT = {'host' : '182.92.166.245', 'port' : 6379}

OSS_HOST = 'oss.aliyuncs.com'
OSS_KEY = '8qyE85QH1EBRiV23'
OSS_SECRET = '8mkGjw4OkFbKAyWLLdntlSZZ4Q7nEU'
OSS_BUCKET_NAME = 'aura'


BAIDU_URL = 'http://api.map.baidu.com/geocoder/v2/?'
BAIDU_AK = 'rT6MtA2aCPAGxxCaSN347RwO'


OAUTH_WEIBO_USERINFO_URL = 'https://api.weibo.com/2/users/show.json'
WEIBO_NICKNAME_PREFIX = 'sinaweibo'

OAUTH_WEIXIN_USERINFO_URL = 'https://api.weixin.qq.com/sns/userinfo?'
WEIXIN_NICKNAME_PREFIX = 'weixin'
