import calendar
import datetime
import sys
import time
import threading
import requests

from plugins.BookHelper import SectionIterator
from plugins.MailSender import MailSender
from plugins.BookScheduler import BookScheduler
from utils.Common import Common
from utils.Constants import Constants
from configs.Config import *


class MasterScheduler(object):
    TICKING_INTERVAL = 900.0

    def __init__(self, remote):
        super(MasterScheduler, self).__init__()
        self.remote = remote
        self.__local_config = LocalConfig()
        self.__remote_config = RemoteConfig()
        self.__schedulers = {}
        self.__signatures = {}
        self.__timer = None
        self.__logger = self.__local_config.get_logger('master_scheduler')

    def start(self):
        self.run()

    def run(self):
        mode_str = 'REMOTE' if self.remote else 'LOCAL'
        self.__logger.log('master scheduler ticking! current mode is %s!' % mode_str)

        config = self.__get_config()
        timings = config.get_timings()
        stadiums = []
        settings = []
        try:
            stadiums = config.get_stadiums()
            settings = config.get_reservation_settings()
        except requests.exceptions.RequestException, _:
            self.__logger.log('network error on fetching stadiums or settings from remote configuration server!')

        # remove schedulers which is not alive
        for key in self.__schedulers.keys():
            s = self.__schedulers.get(key)
            if s is None or not s.is_alive():
                self.__schedulers.pop(key)
                if self.remote:
                    self.__signatures.pop(key)

        # skip when network error
        if stadiums and settings:
            # delete settings whose sig was changed or settings that have been removed
            names = [s['setting_name'] for s in settings]
            signatures = [s.get('signature') for s in settings]
            for key in self.__schedulers.keys():
                if (key not in names) or (self.remote and self.__signatures.get(key) not in signatures):
                    self.__remove_scheduler_and_signature(key)
                    self.__logger.log('account named %s has been REMOVED because config changed!' % key)

            # add create schedulers for new or changed settings
            for setting in settings:
                setting_name = setting['setting_name']
                if setting_name in self.__schedulers.keys():
                    continue
                user = setting['account']
                tasks = setting['tasks']
                logger = config.get_logger(setting_name=setting_name)

                mail_sender = config.get_mail_account() if not self.remote else None
                mail_receivers = config.get_mail_receivers(setting_name=setting_name) if not self.remote else None
                group_ids = setting.get('group_ids')
                open_ids = setting.get('open_ids')
                signature = setting.get('signature')

                scheduler = BookScheduler(user=user, tasks=tasks, timings=timings, logger=logger, stadiums=stadiums,
                                          send_mail=self.notify_all, mail_sender=mail_sender,
                                          mail_receivers=mail_receivers,
                                          group_ids=group_ids, open_ids=open_ids)
                scheduler.start()
                self.__logger.log('account named %s has been CREATED!' % setting_name)

                self.__schedulers[setting_name] = scheduler
                if self.remote:
                    self.__signatures[setting_name] = signature

        # ticking if using remote config
        if self.remote:
            self.__ticking()

    def stop(self):
        for scheduler in self.__schedulers.values():
            scheduler.stop()
        self.__schedulers.clear()
        self.__signatures.clear()
        self.__timer.cancel()
        self.__timer = None

    def is_alive(self):
        if self.__timer is None:
            return False
        return self.__timer.is_alive()

    def __ticking(self):
        self.__logger.log('next ticking after %d seconds...' % self.TICKING_INTERVAL)
        self.__timer = threading.Timer(self.TICKING_INTERVAL, self.run)
        self.__timer.start()
        self.__logger.log('ticking down...')

    def notify_all(self, record_list, **kwargs):
        mail_sender = kwargs.get('mail_sender')
        mail_receivers = kwargs.get('mail_receivers')
        group_id = kwargs.get('group_id')
        open_id = kwargs.get('open_id')

        if self.remote:
            info_list = []
            for record in record_list:
                start_time = self.__convert_datetime_str_to_timestamp(record.get('query_date'),
                                                                      record.get('start_time_str'))
                end_time = self.__convert_datetime_str_to_timestamp(record.get('query_date'),
                                                                    record.get('end_time_str'))
                item = {
                    'stadium_name': record.get('stadium_name'),
                    'site_name': record.get('site_name'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'thu_account': record.get('thu_account'),
                    'cost': record.get('cost'),
                }
                info_list.append(item)

            self.__notify_all_by_remote_sender(record_list=info_list, group_id=group_id, open_id=open_id)
        else:
            stadium_name = None
            site_name = ''
            cost = 0.0
            book_start = sys.maxint
            book_end = 0
            book_date = None
            thu_account = None

            for record in record_list:
                stadium_name = record.get('stadium_name') if stadium_name is None else stadium_name
                site_name += (' ' if site_name else '') + record.get('site_name')
                cost += record.get('cost')
                book_start = min(book_start, SectionIterator.decode(record.get('start_time_str')))
                book_end = max(book_end, SectionIterator.decode(record.get('end_time_str')))
                book_date = record.get('query_date') if book_date is None else book_date
                thu_account = record.get('thu_account') if thu_account is None else thu_account

            book_time = TimeInterval(SectionIterator.encode(book_start),
                                     SectionIterator.encode(book_end)).get_section_str()
            ymd = book_date.split('-')
            index = calendar.weekday(int(ymd[0]), int(ymd[1]), int(ymd[2]))
            weekday = Constants.WEEK_NAMES_EN[index]
            info = {
                'location': stadium_name + ' ' + site_name,
                'book_datetime': book_date + ' ' + weekday + ' ' + book_time,
                'owner': thu_account,
                'cost': cost,
                'curr_datetime': Common.format_datetime(datetime.datetime.now(), Common.DATETIME_PATTERN_YYYYMMDDHHMMSS)
            }
            self.__notify_all_by_local_sender(info=info, mail_sender=mail_sender, mail_receivers=mail_receivers)

    def __remove_scheduler_and_signature(self, key):
        self.__schedulers.get(key).stop()
        self.__schedulers.pop(key)
        if self.remote:
            self.__signatures.pop(key)

    @staticmethod
    def __convert_datetime_str_to_timestamp(date_str, time_str):
        datetime_str = date_str + ' ' + time_str
        array = time.strptime(datetime_str, '%Y-%m-%d %H:%M')
        return int(time.mktime(array)) * Constants.TIME_UNIT_MILLIS

    def __notify_all_by_remote_sender(self, record_list, group_id, open_id):
        service = RemoteService(self.__remote_config.SECRET_ID, self.__remote_config.SECRET_KEY)
        service.send_mail(open_id=open_id, group_id=group_id, record_list=record_list)

    @staticmethod
    def __notify_all_by_local_sender(info, mail_sender, mail_receivers):
        sender = MailSender(mail_sender['sender'], mail_sender['username'], mail_sender['password'],
                            mail_sender['host'],
                            mail_sender['port'])
        content = mail_sender['content'] % (info['location'], info['book_datetime'], info['owner'], info['cost'],
                                            info['curr_datetime'])

        for receiver in mail_receivers:
            title = mail_sender['title'] % (receiver['nickname'])
            sender.send(receiver, title, content, mail_sender['nickname'])

    def __get_config(self):
        return self.__remote_config if self.remote else self.__local_config
