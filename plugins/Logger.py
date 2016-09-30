from utils.Singleton import Singleton
from utils.Common import Common
import datetime


class Logger(Singleton):
    def __init__(self, debug):
        self.debug = debug

    def log(self, title, contents=list()):
        if not self.debug:
            return False
        print '[%s] %s' % (Common.format_datetime(datetime.datetime.now()), title)
        for content in contents:
            print content
        return True
