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
        return nickname
    else:
        return None



def getWeixinNickName(access_token, openid):
    url = '&'.join(str(i) for i in [_conf.OAUTH_WEIXIN_USERINFO_URL + 'access_token=%s' % access_token,
                                    'openid=%s' % str(openid)])
    code, res  = curl.openurl(url)
    if code == 200 and res:
        res = ujson.loads(res)
        nickname = res['nickname']
        return nickname
    else:
        return None



if __name__ == '__main__':
#    print getWeiboNickname('2.00jYRBJEqKtUKDd7dd7deb00S_z8MD', '3797824181')

    access_token = 'OezXcEiiBSKSxW0eoylIeE9zV0byFfmq9_sZ3zwIxwRk6wm54tPwLDlw2MYzKboK44feYxda-XJvELys4e87Xl5gOyV6Nt_vCb0e3Nm8XfVBMU7P9zPanRIyp_Dxf7OI_DiZcNHw0dmg9efTYHdwBg'
    print getWeixinNickName(access_token, 'oDNO3t1jrZSBc1GcV9kzx4dbDCbw')