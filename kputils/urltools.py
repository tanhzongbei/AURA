#coding:UTF-8

from threading import local
try:
    import cStringIO
    import pycurl
except ImportError:
    enable_pycurl = False
else:
    enable_pycurl = True

class PyCurl(local):
    
    def __init__(self, encoding='utf8'):
        self.encoding=encoding
    
    def openurl(self, url, postdata = None, header=None, timeout=8):
        buf = cStringIO.StringIO()
        c = pycurl.Curl()
        
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEFUNCTION, buf.write)
        c.setopt(pycurl.CONNECTTIMEOUT, timeout)
        c.setopt(pycurl.TIMEOUT, timeout)
    
        temp_header = {'Expect': ''}
        if header:
            temp_header.update(header)
            
        headerlist = []
        for k, v in temp_header.iteritems():
            item = '%s: %s' % (k, v)
            if isinstance(item, unicode):
                item = item.encode(self.encoding)
            headerlist.append(item)
            
        c.setopt(pycurl.HTTPHEADER, headerlist)
    
        if postdata:
            if isinstance(postdata, unicode):
                c.setopt(pycurl.POSTFIELDS, postdata.encode(self.encoding))
            else:
                c.setopt(pycurl.POSTFIELDS, postdata)
    
        try:
            c.perform()
            code = c.getinfo(pycurl.RESPONSE_CODE)
            ret =  buf.getvalue()
            return int(code), ret
        except pycurl.error, e:
            return 599, str(e)
        except Exception, e:
            return 598, str(e)
        finally:
            c.close()
            
import urllib2   
class UrlCurl(local):
    
    def __init__(self, encoding='utf8'):
        self.encoding=encoding
    
    def openurl(self, url, postdata = None, header=None, timeout=8):
        if header is None: header = {}
        
        req = urllib2.Request(url, postdata, header)
        
        try:
            resp = urllib2.urlopen(req, timeout=timeout)
            code = resp.getcode()
            result = resp.read()
        except urllib2.HTTPError as e:
            code = e.getcode()
            result = e.read()
        except Exception, e:
            code, result = 598, str(e)
        
        return code, result
        
# 兼容各种
if enable_pycurl:
    curl = PyCurl()
else:
    curl = UrlCurl()
    


if __name__ == '__main__':
    url = 'http://192.168.10.201/sxsvr/login'
    print curl.openurl(url, postdata='XSVR1111111',header={'v':4})
    
    