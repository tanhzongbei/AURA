#coding:utf8 
#__author__ = 'xiaobei'
#__time__= '9/25/15'

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import ujson
import config as _conf
from kputils.urltools import curl


def getWeiboNickname(access_token, openid):
    url = '&'.join(str(i) for i in [_conf.OAUTH_WEIBO_USERINFO_URL+ '?access_token=%s' % access_token, 'uid=%s' % str(openid)])
    code, res = curl.openurl(url)
    if code == 200 and res:
        res = ujson.loads(res)
        nickname = res['name']
        nickname = nickname + '(%s)' % _conf.WEIBO_NICKNAME_PREFIX
        return nickname
    else:
        return None



def getWeixinNickName(access_token, openid):
    url = '&'.join(str(i) for i in [_conf.OAUTH_WEIXIN_USERINFO_URL + 'access_token=%s' % access_token,
                                    'openid=%s' % str(openid),
                                    'lang=zn_CN'])
    code, res  = curl.openurl(url)
    return None




if __name__ == '__main__':
#    print getWeiboNickname('2.00jYRBJEqKtUKDd7dd7deb00S_z8MD', '3797824181')

    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % ('wx40e467363844c3c1', 'c42f189ee8b163718a609bde8be9f2de')
    code, res = curl.openurl(url)
    res = ujson.loads(res)
    access_token = res['access_token']
    print getWeixinNickName(access_token, 'oDNO3t1jrZSBc1GcV9kzx4dbDCbw')