# coding:utf8
"""
Created on Feb 20, 2014

@author: ilcwd
"""
import time

from logging.handlers import TimedRotatingFileHandler


class AccurateTimedRotatingFileHandler(TimedRotatingFileHandler):
    def computeRollover(self, currentTime):
        if self.when in ('M', 'H', 'D'):
            result = currentTime + self.interval

            # make next rolling time a integral point.
            left = result % self.interval
            if left != 0:
                result -= left

            # time.timezone == -8 * 3600 in China,
            # if split log files by day,
            # ``result`` is at midnight in UTC time,
            # which mean 8:00 am in China,
            # so we set it 8 hours earlier to adapt time in China.
            if not self.utc and self.when == 'D':
                result += time.timezone

            return result
        else:
            return super(AccurateTimedRotatingFileHandler, self).computeRollover(currentTime)


def test():
    import datetime

    def ts2datetime(ts):
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    def datetime2ts(date):
        return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple())

    print time.timezone
    print ts2datetime(0)
    h = AccurateTimedRotatingFileHandler('a.log', when='D')
    print datetime2ts("1970-01-01 08:00:00")

    print datetime2ts("1970-01-01 08:00:00"), ts2datetime(h.computeRollover(datetime2ts("1970-01-01 08:00:00")))

    print ts2datetime(h.computeRollover(1392866107))
