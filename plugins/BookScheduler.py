#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BookHelper import BookHelper
from config.Config import Config
from utils.Common import Common
from utils.Constants import Constants
import threading
import requests


class BookScheduler:
    DEFAULT_PRIORITY = 1

    def __init__(self):
        self.config = Config()
        self.helper = None
        self.tasks = None
        self.timings = None
        self.logger = None
        self.timer = None

    def init(self):
        self.helper = BookHelper(self.config.get_default_account())
        self.tasks = self.config.get_reservation_tasks()
        self.timings = self.config.get_timings()
        self.logger = self.config.get_logger()

    def run(self):
        self.logger.log('thu-stadium-reservation ticking!')

        has_task = False
        tomorrow = Common.get_tomorrow()
        day_after_tomorrow = Common.get_day_after_tomorrow()
        more = Common.get_datetime_with_interval(3)
        all_dates = [Common.format_date(tomorrow, Common.DATETIME_PATTERN_YYYYMMDD),
                     Common.format_date(day_after_tomorrow, Common.DATETIME_PATTERN_YYYYMMDD),
                     Common.format_date(more, Common.DATETIME_PATTERN_YYYYMMDD)]
        try:
            date_strings = self.helper.should_book(all_dates)
        except requests.exceptions.RequestException, _:
            has_task = True
            self.logger.error('cannot fetch records from 50.tsinghua with a network error, please check your network.')
            date_strings = []
        
        if date_strings:
            # find dates occupied
            occupied = []
            for date_str in all_dates:
                if date_str not in date_strings:
                    occupied.append(date_str)

            # filter completed tasks
            curr_tasks = []
            for task in self.tasks:
                found = False
                for candidate in task:
                    for date_str in occupied:
                        if candidate.is_available() and candidate.validate_date(date_str):
                            found = True
                            break
                if not found:
                    curr_tasks.append(task)

            # attempt to book sites
            for date_str in date_strings:
                for task in curr_tasks:
                    for candidate in task:
                        if candidate.is_available() and candidate.validate_date(date_str):
                            has_task = True
                            try:
                                ret = self.helper.book(date_str, candidate)
                                if ret:
                                    account = self.config.get_mail_account()
                                    receivers = self.config.get_mail_receivers()
                                    self.helper.notify_all(ret, account, receivers)
                                    self.__ticking(True)
                                    return
                            except requests.exceptions.RequestException, _:
                                self.logger.error('cannot book sites or send emails with a network error, '
                                                  'please check your network.')

        self.__ticking(False, has_task)

    def __ticking(self, book_result, has_task_today=True):
        self.helper.clear_status()
        now = Common.get_today()
        curr_time = BookScheduler.__get_time_in_second(now.hour, now.minute, now.second)

        next_ticking = BookScheduler.__get_time_in_second(Constants.TIME_UNIT_HOUR, 0) - curr_time

        if has_task_today:
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

            next_ticking = min(min_value, interval, next_ticking)

        self.logger.log('next ticking after %d seconds...' % next_ticking)
        self.timer = threading.Timer(next_ticking, self.run)
        self.timer.start()
        self.logger.log('ticking down...')

    def start(self):
        self.run()

    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

    @staticmethod
    def __get_time_in_second(hour, minute, second=0):
        return (hour * Constants.TIME_UNIT_MINUTE + minute) * Constants.TIME_UNIT_SECOND + second
