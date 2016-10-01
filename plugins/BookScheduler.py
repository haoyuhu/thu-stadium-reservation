#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BookHelper import BookHelper
from config.Config import Config
from utils.Common import Common
from utils.Constants import Constants
import time


class BookScheduler:
    def __init__(self):
        self.config = Config()
        self.helper = None
        self.tasks = None
        self.timings = None
        self.timer = None
        self.logger = None

    def init(self):
        self.helper = BookHelper(self.config.get_default_account())
        self.tasks = self.config.get_reservation_tasks()
        self.timings = self.config.get_timings()
        self.logger = self.config.get_logger()

    def run(self):
        self.logger.log('thu-stadium-reservation ticking!')

        tomorrow = Common.get_tomorrow()
        day_after_tomorrow = Common.get_day_after_tomorrow()
        t_str = Common.format_date(tomorrow, Common.DATETIME_PATTERN_YYYYMMDD)
        dat_str = Common.format_date(day_after_tomorrow, Common.DATETIME_PATTERN_YYYYMMDD)
        date_strings = self.helper.should_book([t_str, dat_str])

        if date_strings:
            for date_str in date_strings:
                for task in self.tasks:
                    for candidate in task:
                        if candidate.validate_date(date_str):
                            ret = self.helper.book(date_str, candidate)
                            if ret:
                                account = self.config.get_mail_account()
                                receivers = self.config.get_mail_receivers()
                                self.helper.notify_all(ret, account, receivers)
                                self.__ticking(True)
                                return

        self.__ticking(False)

    def cancel(self):
        self.timer.cancel()

    def __ticking(self, book_result):
        self.helper.clear_status()
        now = Common.get_today()
        curr_time = BookScheduler.__get_time_in_second(now.hour, now.minute, now.second)
        interval = self.timings.interval
        min_value = interval

        for item in self.timings.specials:
            shm = item.start.split(':')
            ehm = item.end.split(':')
            s_time = BookScheduler.__get_time_in_second(int(shm[0]), int(shm[1]))
            e_time = BookScheduler.__get_time_in_second(int(ehm[0]), int(ehm[1]))
            if s_time <= curr_time <= e_time:
                if book_result:
                    interval = e_time - curr_time + 1
                else:
                    interval = item.interval
                break
            elif s_time > curr_time:
                min_value = min(min_value, s_time - curr_time)
        next_ticking = min(min_value, interval)
        self.logger.log('next ticking after %d seconds...' % next_ticking)
        time.sleep(next_ticking)
        self.run()

    @staticmethod
    def __get_time_in_second(hour, minute, second=0):
        return (hour * Constants.TIME_UNIT_MINUTE + minute) * Constants.TIME_UNIT_SECOND + second
