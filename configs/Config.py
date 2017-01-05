#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils.Singleton import Singleton
from plugins.JsonReader import JsonReader
from plugins.Logger import Logger
from entities.User import User
from entities.Stadium import Stadium
from entities.Timing import Timing
from entities.TimeInterval import TimeInterval
from entities.ReservationCandidate import ReservationCandidate
import os


class Config(Singleton):
    DEFAULT_CONFIG_FILE_NAME = 'default.json'
    ACCOUNTS_FILE_NAME = 'accounts.json'
    RESERVATION_DIR = 'reservations'
    BASIS_FILE_NAME = 'basis.json'
    TIMINGS_FILE_NAME = 'timings.json'

    def __init__(self):
        self.default_cache = None
        self.accounts_cache = None
        self.stadiums_cache = None
        self.timings_cache = None
        self.settings_cache = None
        self.standard_sections_cache = None

    def get_accounts(self):
        """
        :rtype: dict
        """
        if self.accounts_cache is not None:
            return self.accounts_cache

        users = Config.read_configs(Config.get_curr_abs_path(Config.ACCOUNTS_FILE_NAME))
        self.accounts_cache = {}
        if users is not None:
            for name in users:
                item = users[name]
                user = User(name, item['id'], item['username'], item['password'], item['phone'], item['user_type'])
                self.accounts_cache[name] = user
        return self.accounts_cache

    def get_default_config(self):
        if self.default_cache is None:
            self.default_cache = Config.read_configs(Config.get_curr_abs_path(Config.DEFAULT_CONFIG_FILE_NAME))
        return self.default_cache

    def get_log_file_name(self, setting_name):
        return self.get_curr_abs_path('runtime_%s.log' % setting_name)

    def get_default_account(self, account_name):
        """
        :rtype: User
        """
        return self.get_accounts()[account_name]

    def get_logger(self, setting_name):
        """
        :rtype: Logger
        """
        return Logger(self.get_default_config()['debug'], self.get_log_file_name(setting_name))

    def get_stadiums(self):
        """
        :rtype: list
        """
        if self.stadiums_cache is not None:
            return self.stadiums_cache

        stadiums = Config.read_configs(Config.get_curr_abs_path(Config.BASIS_FILE_NAME))
        self.stadiums_cache = []
        for item in stadiums:
            self.stadiums_cache.append(Stadium.from_json(item))
        return self.stadiums_cache

    def get_timings(self):
        """
        :rtype: Timing
        """
        if self.timings_cache is not None:
            return self.timings_cache

        timings = Config.read_configs(Config.get_curr_abs_path(Config.TIMINGS_FILE_NAME))
        self.timings_cache = Timing.from_json(timings)
        return self.timings_cache

    def get_reservation_settings(self):
        """
        :rtype: list
        """
        if self.settings_cache is not None:
            return self.settings_cache

        self.settings_cache = []
        for root, _, files in os.walk(Config.get_curr_abs_path(Config.RESERVATION_DIR)):
            for name in files:
                setting = Config.read_configs(os.path.join(root, name))
                setting_name = name.split('.')[0]
                item = {
                    'setting_name': setting_name,
                    'tasks': [],
                    'account': setting['account'],
                    'receivers': setting['receivers']
                }
                for l in setting['reservations']:
                    task = []
                    for obj in l:
                        candidate = ReservationCandidate.from_json(obj, self.get_standard_time_section(obj['section']))
                        task.append(candidate)
                    item['tasks'].append(task)
                self.settings_cache.append(item)

        return self.settings_cache

    def get_standard_time_section(self, section_name):
        """
        :rtype: TimeInterval
        """
        if self.standard_sections_cache is None:
            config = Config.read_configs(Config.get_curr_abs_path(Config.DEFAULT_CONFIG_FILE_NAME))
            self.standard_sections_cache = config['unit']['section']
        section = self.standard_sections_cache[section_name]
        if section is None:
            se = section_name.split('-')
            return TimeInterval(se[0], se[1])
        else:
            return TimeInterval(section['start'], section['end'])

    def get_mail_account(self):
        return self.get_default_config()['mail_account']

    # noinspection PyTypeChecker
    def get_mail_receivers(self, setting_name):
        ret = []
        ret.extend(self.get_default_config()['receivers'])
        for item in self.get_reservation_settings():
            if item['setting_name'] == setting_name:
                ret.extend(item['receivers'])
                break
        return ret

    @staticmethod
    def read_configs(path):
        reader = JsonReader()
        return reader.read(path)

    @staticmethod
    def get_curr_abs_path(file_name):
        return os.path.dirname(os.path.abspath(__file__)) + os.sep + file_name
