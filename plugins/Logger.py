from utils.Singleton import Singleton
import logging


class Logger(Singleton):
    def __init__(self, debug):
        self.logger = logging.getLogger('thu-stadium-logger')
        if debug:
            level = logging.DEBUG
        else:
            level = logging.ERROR
        self.logger.setLevel(level)

        fh = logging.FileHandler('runtime.log')
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log(self, title, contents=list()):
        self.logger.debug(title)
        for content in contents:
            self.logger.debug(content)
