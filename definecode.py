#coding:utf8
'''
Created on 2014-9-1

@author: xiaobei
'''

#===============================================================================
# DEFINE CODE
#===============================================================================
#sys
CODE_OK = 10000
CODE_BADPARAMS = 10001

#account
CODE_ACCOUNT_ACCOUNTNOTMATCH = 11001
CODE_ACCOUNT_PASSWORDERROR = 11002
CODE_ACCOUNT_DBERROR = 11003
CODE_ACCOUNT_EXIST = 11004
CODE_ACCOUNT_NICKNAME_EXIST = 11005

#session
CODE_SESSION_EXPIRED = 12001
CODE_SESSION_INVAILD = 12002

#geo
CODE_GEO_BAIDURPC_FAILD = 13001

#file/album
CODE_FILEOP_DBERROR = 14001
CODE_ALBUM_NOTEXIST = 14002
CODE_CITY_NOTEXIST = 14003

CODE_FILE_NOTEXIST = 14004


#oss
CODE_OSS_BUCKET_NOTEXIST = 15001
CODE_OSS_RPC_ERROR = 15002

# follow
CODE_FOLLOWEE_NOTEXIST = 16001
CODE_FOLLOWER_NOTEXIST = 16002
