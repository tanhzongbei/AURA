# coding:utf8
"""

Author: ilcwd
"""
import gevent
import gevent.monkey
gevent.monkey.patch_all()

def main():
    import urllib2

    urls = ['http://openapi.kuaipan.cn/open/time'] * 10

    def _work(url):
        return urllib2.urlopen(url).read()

    jobs = [gevent.spawn(_work, url) for url in urls]
    gevent.joinall(jobs, timeout=7)

    for ix, i in enumerate(jobs):
        print "Connect to", urls[ix], ix, ':',
        if i.value:
            print 'Done'
        else:
            print 'Fail'


if __name__ == '__main__':
    main()
