import logging


class Logger:
    def __init__(self, debug, file_name, logger_name):
        # getLogger(logger_name) the same logger_name will return the same logger, so the logging info will be
        # duplicated if using the same logger_name
        self.logger = logging.getLogger('thu-stadium-logger(%s)' % logger_name)
        if debug:
            level = logging.DEBUG
        else:
            level = logging.ERROR
        self.logger.setLevel(level)

        self.file_handler = logging.FileHandler(file_name)
        self.file_handler.setLevel(level)
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.stream_handler.setFormatter(formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)

    def log(self, title, contents=list()):
        if not self.logger:
            return

        self.logger.debug(title)
        for content in contents:
            self.logger.debug(content)

    def error(self, title, contents=list()):
        if not self.logger:
            return

        self.logger.error(title)
        for content in contents:
            self.logger.error(content)

    # remove all handlers when the logger closed
    def close_all(self):
        self.file_handler.close()
        self.stream_handler.close()
        self.logger.removeHandler(self.file_handler)
        self.logger.removeHandler(self.stream_handler)
        self.file_handler = None
        self.stream_handler = None
        self.logger = None
