#!/usr/bin/env python
# -*- coding: utf-8 -*-
from entities.SiteCategory import SiteCategory
from entities.SpecialTimeInterval import SpecialTimeInterval
from utils.Singleton import Singleton
from plugins.JsonReader import JsonReader
from plugins.Logger import Logger
from plugins.RemoteService import RemoteService
from entities.User import User
from entities.Stadium import Stadium
from entities.Timing import Timing
from entities.TimeInterval import TimeInterval
from entities.ReservationCandidate import ReservationCandidate
import os


class Config(Singleton):
    DEFAULT_CONFIG_FILE_NAME = 'default.json'
    TIMINGS_FILE_NAME = 'timings.json'

    def __init__(self):
        self.default_cache = None
        self.timings_cache = None
        self.standard_sections_cache = None

    @staticmethod
    def _read_configs(path):
        reader = JsonReader()
        return reader.read(path)

    @staticmethod
    def _get_curr_abs_path(file_name):
        return os.path.dirname(os.path.abspath(__file__)) + os.sep + file_name

    def _get_default_config(self):
        if self.default_cache is None:
            self.default_cache = self._read_configs(
                self._get_curr_abs_path(Config.DEFAULT_CONFIG_FILE_NAME))
        return self.default_cache

    def _get_log_file_name(self, setting_name):
        return self._get_curr_abs_path('runtime_%s.log' % setting_name)

    def get_logger(self, setting_name):
        """
        :rtype: Logger
        """
        return Logger(self.is_debug(), self._get_log_file_name(setting_name), setting_name)

    def is_debug(self):
        return self._get_default_config()['debug']

    def get_timings(self):
        """
        :rtype: Timing
        """
        if self.timings_cache is not None:
            return self.timings_cache

        timings = self._read_configs(self._get_curr_abs_path(self.TIMINGS_FILE_NAME))
        specials = []
        for item in timings['specials']:
            specials.append(SpecialTimeInterval(item['interval'], item['start'], item['end']))
        self.timings_cache = Timing(timings['default']['interval'], specials)
        return self.timings_cache

    def get_standard_time_section(self, section_name):
        """
        :rtype: TimeInterval
        """
        if self.standard_sections_cache is None:
            config = self._read_configs(self._get_curr_abs_path(self.DEFAULT_CONFIG_FILE_NAME))
            self.standard_sections_cache = config['unit']['section']
        section = self.standard_sections_cache.get(section_name)
        if section is None:
            se = section_name.split('-')
            return TimeInterval(se[0], se[1])
        else:
            return TimeInterval(section['start'], section['end'])


class LocalConfig(Config):
    ACCOUNTS_FILE_NAME = 'accounts.json'
    RESERVATION_DIR = 'reservations'
    BASIS_FILE_NAME = 'basis.json'

    def __init__(self):
        super(LocalConfig, self).__init__()
        self.stadiums_cache = None
        self.settings_cache = None
        self.accounts_cache = None

    def get_accounts(self):
        """
        :rtype: dict
        """
        if self.accounts_cache is not None:
            return self.accounts_cache

        users = self._read_configs(self._get_curr_abs_path(self.ACCOUNTS_FILE_NAME))
        self.accounts_cache = {}
        if users is not None:
            for name in users:
                item = users[name]
                user = User(name, item['id'], item['username'], item['password'], item['phone'], item['user_type'])
                self.accounts_cache[name] = user
        return self.accounts_cache

    def get_default_account(self, account_name):
        """
        :rtype: User
        """
        return self.get_accounts().get(account_name)

    def get_stadiums(self):
        """
        :rtype: list
        """
        if self.stadiums_cache is not None:
            return self.stadiums_cache

        stadiums = self._read_configs(self._get_curr_abs_path(self.BASIS_FILE_NAME))
        self.stadiums_cache = []
        for item in stadiums:
            sites = item['sites']
            badminton = SiteCategory(sites['badminton']['id'], sites['badminton']['exceptions'])
            pingpong = SiteCategory(sites['pingpong']['id'], sites['pingpong']['exceptions'])
            basketball = SiteCategory(sites['basketball']['id'], sites['basketball']['exceptions'])
            stadium = Stadium(item['name'], item['gymnasium_id'], badminton, pingpong, basketball)
            self.stadiums_cache.append(stadium)
        return self.stadiums_cache

    def get_reservation_settings(self):
        """
        :rtype: list
        """
        if self.settings_cache is not None:
            return self.settings_cache

        self.settings_cache = []
        for root, _, files in os.walk(self._get_curr_abs_path(self.RESERVATION_DIR)):
            for name in files:
                setting = self._read_configs(os.path.join(root, name))
                setting_name = name.split('.')[0]
                item = {
                    'setting_name': setting_name,
                    'tasks': [],
                    'account': self.get_default_account(setting['account']),
                    'receivers': setting['receivers']
                }
                for l in setting['reservations']:
                    task = []
                    for obj in l:
                        candidate = ReservationCandidate(
                            obj['available'],
                            obj['sport_type'],
                            obj['week'],
                            TimeInterval(obj['wish']['start'], obj['wish']['end']),
                            obj['length'],
                            self.get_standard_time_section(obj['section']),
                            obj['fixed']
                        )
                        task.append(candidate)
                    item['tasks'].append(task)
                self.settings_cache.append(item)

        return self.settings_cache

    def get_mail_account(self):
        return self._get_default_config()['mail_account']

    # noinspection PyTypeChecker
    def get_mail_receivers(self, setting_name):
        ret = []
        ret.extend(self._get_default_config()['receivers'])
        for item in self.get_reservation_settings():
            if item['setting_name'] == setting_name:
                ret.extend(item['receivers'])
                break
        return ret


class RemoteConfig(Config):
    SECRET_FILE_NAME = 'secrets.json'
    SPORT_TYPE = {
        0: 'badminton',
        1: 'pingpong',
        2: 'basketball'
    }

    def __init__(self):
        super(RemoteConfig, self).__init__()
        secrets = self.__get_secrets()
        self.service = RemoteService(
            secret_id=secrets.get('secret_id', ''),
            secret_key=secrets.get('secret_key', ''),
            aes_iv=secrets.get('aes_iv', ''))

    def __get_secrets(self):
        return self._read_configs(self._get_curr_abs_path(self.SECRET_FILE_NAME))

    def get_secret_id(self):
        return self.__get_secrets().get('secret_id')

    def get_secret_key(self):
        return self.__get_secrets().get('secret_key')

    def get_aes_iv(self):
        return self.__get_secrets().get('aes_iv')

    def get_reservation_settings(self):
        data = self.service.get_reservation_list()
        if data is False:
            return False

        settings = []
        for item in data:
            signature = item.get('sig')

            account = item.get('account')
            username = account.get('username')
            student_id = account.get('student_id')
            password = account.get('password')
            phone = account.get('phone')
            user_type = account.get('user_type')
            user = User(name=username, student_id=student_id, username=username, password=password, phone=phone,
                        user_type=user_type)

            setting = {
                'setting_name': user.name,
                'tasks': [],
                'account': user,
                'signature': signature,
                'open_ids': [],
                'group_ids': []
            }

            groups = item.get('groups')
            for group in groups:
                open_id = group.get('open_id')
                group_id = group.get('group_id')
                candidates = group.get('candidates')
                task = []
                for c in candidates:
                    instance = ReservationCandidate(
                        available=c.get('available'),
                        sport_type=c.get('sport_type'),
                        week=c.get('week'),
                        wish=TimeInterval(c.get('wish_start'), c.get('wish_end')),
                        length=c.get('length'),
                        section=TimeInterval(c.get('section_start'), c.get('section_end')),
                        fixed=c.get('fixed'))
                    task.append(instance)
                setting['tasks'].append(task)
                setting['open_ids'].append(open_id)
                setting['group_ids'].append(group_id)
            settings.append(setting)

        return settings

    def get_stadiums(self):
        data = self.service.get_stadiums()
        if data is False:
            return False

        stadium_map = {}
        for item in data:
            stadium_code = item.get('stadium_code')
            name = item.get('name')
            site_code = item.get('site_code')
            exceptions = item.get('exceptions')
            exceptions = [] if not exceptions else [int(atom) for atom in exceptions.split(';') if atom]
            sport_type = self.SPORT_TYPE[item.get('sport_type')]
            site = SiteCategory(site_code, exceptions)
            stadium = stadium_map.get(stadium_code)
            if not stadium:
                stadium = Stadium(name, stadium_code)

            if sport_type == Stadium.BADMINTON:
                stadium.badminton = site
            elif sport_type == Stadium.PINGPONG:
                stadium.pingpong = site
            elif sport_type == Stadium.BADMINTON:
                stadium.basketball = site

            stadium_map[stadium_code] = stadium

        return [stadium_map.get(key) for key in sorted(stadium_map)]
