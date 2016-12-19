#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plugins.BookScheduler import BookScheduler
from configs.Config import Config

schedulers = []


def init_all_schedulers():
    config = Config()

    settings = config.get_reservation_settings()
    stadiums = config.get_stadiums()
    timings = config.get_timings()
    sender = config.get_mail_account()

    for setting in settings:
        # noinspection PyTypeChecker
        account_name = setting['account']
        # noinspection PyTypeChecker
        setting_name = setting['setting_name']
        user = config.get_default_account(account_name)

        scheduler = BookScheduler()
        # noinspection PyTypeChecker
        scheduler.init(user, setting['tasks'], timings, config.get_logger(setting_name), sender,
                       config.get_mail_receivers(setting_name), stadiums)
        schedulers.append(scheduler)


def start_all_schedulers():
    for scheduler in schedulers:
        scheduler.start()


def stop_all_schedulers():
    for scheduler in schedulers:
        scheduler.stop()


if __name__ == "__main__":
    init_all_schedulers()
    start_all_schedulers()
