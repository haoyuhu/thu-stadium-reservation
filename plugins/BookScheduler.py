#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BookHelper import BookHelper
from utils.Common import Common
from utils.Constants import Constants
import threading
import requests


class BookScheduler:
    DEFAULT_PRIORITY = 1

    def __init__(self, user, tasks, timings, logger, stadiums, send_mail, **kwargs):
        self.__helper = BookHelper(user, stadiums, logger)
        self.__tasks = tasks
        self.__timings = timings
        self.__logger = logger
        self.__stadiums = stadiums
        self.__send_mail = send_mail
        self.__timer = None

        self.__mail_sender = kwargs.get('mail_sender')
        self.__mail_receivers = kwargs.get('mail_receivers')
        self.__group_ids = kwargs.get('group_ids')
        self.__open_ids = kwargs.get('open_ids')

    def run(self):
        self.__logger.log('book scheduler ticking!')

        has_task = False
        tomorrow = Common.get_tomorrow()
        day_after_tomorrow = Common.get_day_after_tomorrow()
        more = Common.get_datetime_with_interval(3)
        all_dates = [Common.format_date(tomorrow, Common.DATETIME_PATTERN_YYYYMMDD),
                     Common.format_date(day_after_tomorrow, Common.DATETIME_PATTERN_YYYYMMDD),
                     Common.format_date(more, Common.DATETIME_PATTERN_YYYYMMDD)]
        try:
            date_strings = self.__helper.should_book(all_dates)
        except requests.exceptions.RequestException, _:
            has_task = True
            self.__logger.error(
                'cannot fetch records from 50.tsinghua with a network error, please check your network.')
            date_strings = []

        if date_strings:
            # find dates occupied
            occupied = []
            for date_str in all_dates:
                if date_str not in date_strings:
                    occupied.append(date_str)

            # filter completed tasks
            curr_tasks = []
            curr_open_ids = []
            curr_group_ids = []
            for i in xrange(len(self.__tasks)):
                task = self.__tasks[i]
                found = False
                for candidate in task:
                    for date_str in occupied:
                        if candidate.is_available() and candidate.validate_date(date_str):
                            found = True
                            break
                if not found:
                    curr_tasks.append(task)
                    curr_open_ids.append(self.__open_ids[i] if self.__open_ids is not None else None)
                    curr_group_ids.append(self.__group_ids[i] if self.__group_ids is not None else None)

            # attempt to book sites
            for date_str in date_strings:
                for i in xrange(len(curr_tasks)):
                    task = curr_tasks[i]
                    for candidate in task:
                        if candidate.is_available() and candidate.validate_date(date_str):
                            has_task = True
                            try:
                                ret = self.__helper.book(date_str, candidate)
                                if ret:
                                    self.__send_mail(ret,
                                                     mail_sender=self.__mail_sender,
                                                     mail_receivers=self.__mail_receivers,
                                                     group_id=curr_group_ids[i],
                                                     open_id=curr_open_ids[i])
                                    self.__ticking(True)
                                    return
                            except requests.exceptions.RequestException, _:
                                self.__logger.error('cannot book sites or send emails with a network error, '
                                                    'please check your network.')

        self.__ticking(False, has_task)

    def __ticking(self, book_result, has_task_today=True):
        self.__helper.clear_status()
        now = Common.get_today()
        curr_time = BookScheduler.__get_time_in_second(now.hour, now.minute, now.second)

        next_ticking = BookScheduler.__get_time_in_second(Constants.TIME_UNIT_HOUR, 0) - curr_time

        if has_task_today:
            interval = self.__timings.interval
            min_value = interval

            for item in self.__timings.specials:
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

        self.__logger.log('next ticking after %d seconds...' % next_ticking)
        self.__timer = threading.Timer(next_ticking, self.run)
        self.__timer.start()
        self.__logger.log('ticking down...')

    def start(self):
        self.run()

    def stop(self):
        if self.__timer is not None:
            self.__timer.cancel()
            self.__timer = None

    def is_alive(self):
        if self.__timer is None:
            return False
        return self.__timer.is_alive()

    @staticmethod
    def __get_time_in_second(hour, minute, second=0):
        return (hour * Constants.TIME_UNIT_MINUTE + minute) * Constants.TIME_UNIT_SECOND + second
