#!/usr/bin/env python
# -*- coding: utf-8 -*-

from entities.User import User
from entities.Stadium import Stadium
from entities.ViewQuery import ViewQuery
from entities.BookRecord import BookRecord
from entities.SiteList import SiteList
from entities.TimeInterval import TimeInterval
from entities.BookQuery import BookQuery
from entities.ReservationCandidate import ReservationCandidate
from plugins.MailSender import MailSender
from config.Config import Config
from utils.Constants import Constants
from utils.UrlBuilder import UrlBuilder
from utils.Common import Common
import requests
import calendar
from datetime import datetime


class BookHelper:
    def __init__(self, user):
        """
        :param User user:
        """
        config = Config()
        self.user = user
        self.stadiums = config.get_stadiums()
        self.logger = config.get_logger()
        self.session = None
        self.records = None
        self.status = None

    def login(self):
        self.logger.log('attempt to log in tsinghua info platform...')
        url = UrlBuilder().schema(UrlBuilder.SCHEMA_HTTP).host(Constants.THU_INFO_HOST).build()
        self.session = requests.session()
        r = self.session.get(url)
        cookies = r.cookies

        url = UrlBuilder().schema(UrlBuilder.SCHEMA_HTTP).host(Constants.THU_INFO_HOST) \
            .segments(Constants.THU_INFO_LOGIN_SEGMENTS).build()
        login_params = self.user.get_login_params()
        r = self.session.post(url, data=login_params)
        success = 'result=1' in r.url

        if success:
            self.logger.log('log in successfully, now redirect to 50.tsinghua...')
            url = UrlBuilder().schema(UrlBuilder.SCHEMA_HTTP).host(Constants.THU_INFO_HOST) \
                .segments(Constants.THU_INFO_MAIN_PAGE_SEGMENTS).build()
            self.session.get(url, cookies=cookies)

            url = UrlBuilder().schema(UrlBuilder.SCHEMA_HTTP).host(Constants.THU_INFO_HOST) \
                .segments(Constants.THU_INFO_REDIRECT_TO_STADIUM_SEGMENTS).build()
            r = self.session.get(url, params=Constants.THU_INFO_REDIRECT_TO_STADIUM_QUERY_PARAMS, cookies=cookies)
            self.session.get(r.url)
        else:
            self.logger.log('fail to log in default account...')
        return success

    def get_records(self):
        self.logger.log('now start to get reservation records...')
        url = UrlBuilder().schema(UrlBuilder.SCHEMA_HTTP).host(Constants.THU_STADIUM_HOST) \
            .segments(Constants.THU_STADIUM_MAIN_SEGMENTS).build()
        params = ViewQuery.get_view_reservation_params(self.stadiums[Stadium.AIR_STADIUM])
        r = self.session.get(url, params=params)
        if r.url.startswith(url):
            self.logger.log('fetch reservation records successfully!')
            self.records = BookRecord.from_html(r.text)
        else:
            self.logger.log('fail to fetch records, retry next time...')
            self.records = None

    def book(self, date_str, candidate):
        """
        :param str date_str:
        :param ReservationCandidate candidate:
        """
        all_status = self.get_status(date_str, candidate.get_sport_type())
        ret = False
        for site_list in all_status:
            wish = candidate.get_wish()
            final_sites = site_list.find_available_site(wish)
            if final_sites is None and not candidate.is_fixed():
                iterator = SectionIterator(candidate.get_section(), candidate.get_length())
                while final_sites is None and iterator.has_next():
                    final_sites = site_list.find_available_site(iterator.current_item())
            if final_sites is not None:
                self.logger.log('start to book site %s on %s with account %s...'
                                % (final_sites[0].name, date_str, self.user.name))
                query = BookQuery(final_sites[0].belong_to, date_str, final_sites, self.user)
                data = query.get_reservation_params()
                params = Constants.THU_STADIUM_BOOK_ACTION_QUERY_PARAMS
                url = UrlBuilder().schema(UrlBuilder.SCHEMA_HTTP).host(Constants.THU_STADIUM_HOST).segments(
                    Constants.THU_STADIUM_BOOK_ACTION_SEGMENTS).build()
                self.session.post(url, data=data, params=params)
                if not self.should_book([date_str]):
                    stadium_name = query.stadium.name
                    site_name = ''
                    cost = 0.0
                    book_start = None
                    book_end = None
                    book_date = query.date
                    for field in query.fields:
                        if not site_name.endswith(field.name):
                            site_name += ' ' + field.name
                        cost += field.cost
                        if book_start is None:
                            book_start = SectionIterator.decode(field.start)
                        else:
                            book_start = min(book_start, SectionIterator.decode(field.start))
                        if book_end is None:
                            book_end = SectionIterator.decode(field.end)
                        else:
                            book_end = max(book_end, SectionIterator.decode(field.end))
                    book_time = TimeInterval(SectionIterator.encode(book_start),
                                             SectionIterator.encode(book_end)).get_section_str()
                    ymd = query.date.split('-')
                    index = calendar.weekday(int(ymd[0]), int(ymd[1]), int(ymd[2]))
                    weekday = Constants.WEEK_NAMES_EN[index]
                    ret = {
                        'location': stadium_name + site_name,
                        'book_datetime': book_date + ' ' + weekday + ' ' + book_time,
                        'owner': query.user.name,
                        'cost': cost,
                        'curr_datetime': Common.format_datetime(datetime.now(), Common.DATETIME_PATTERN_YYYYMMDDHHMMSS)
                    }
                    self.logger.log('sites booked successfully!', [
                        'location: ' + ret['location'],
                        'book datetime: ' + ret['book_datetime'],
                        'owner: ' + ret['owner'],
                        'cost: ' + ret['cost'],
                    ])
        return ret

    def should_book(self, date_strings):
        if self.session is not None:
            self.get_records()
        if self.records is None:
            if self.login():
                self.get_records()

        if self.records is not None:
            ret = []
            for date_str in date_strings:
                if not self.is_booked(date_str):
                    ret.append(date_str)
            if len(ret) != 0:
                return ret
        return False

    def is_booked(self, date_str):
        for record in self.records:
            if record.date_str == date_str:
                return True
        return False

    def get_status(self, date_str, sport_type):
        self.logger.log('start to fetch site status...')
        if self.status is not None and date_str in self.status.keys():
            return self.status[date_str]

        if self.status is None:
            self.status = {}
        info = []
        for stadium in self.stadiums:
            url = UrlBuilder().schema(UrlBuilder.SCHEMA_HTTP).host(Constants.THU_STADIUM_HOST).segments(
                Constants.THU_STADIUM_STATUS_SEGMENTS).build()
            query = ViewQuery(stadium, sport_type, date_str, self.user)
            params = query.get_view_site_params()
            r = self.session.get(url, params=params)
            site_list = SiteList(stadium, sport_type)
            site_list.parse(r.text)
            info.append(site_list)
        self.status[date_str] = info
        return info

    def clear_status(self):
        self.status = None

    @staticmethod
    def notify_all(info, account, receivers):
        sender = MailSender(account['sender'], account['username'], account['password'], account['host'],
                            account['port'])
        content = account['content'] % (info['location'], info['book_datetime'], info['owner'], info['cost'],
                                        info['curr_datetime'])

        for receiver in receivers:
            title = account['title'] % (receiver['nickname'])
            sender.send(receiver, title, content, account['nickname'])


class SectionIterator:
    TIME_SEP = ':'

    def __init__(self, section, length, step=30):
        """
        :param TimeInterval section:
        :param int length:
        """
        self.length = length * Constants.TIME_UNIT_MINUTE
        self.lower_bound = SectionIterator.decode(section.start) + self.length
        self.curr = SectionIterator.decode(section.end)
        self.step = step

    def current_item(self):
        ret = TimeInterval(SectionIterator.encode(self.curr - self.length), SectionIterator.encode(self.curr))
        self.curr -= self.step
        return ret

    def has_next(self):
        return self.curr >= self.lower_bound

    @staticmethod
    def encode(raw_time):
        h = raw_time / Constants.TIME_UNIT_MINUTE
        m = raw_time % Constants.TIME_UNIT_MINUTE
        if m < 10:
            m_str = '0' + str(m)
        else:
            m_str = str(m)
        return str(h) + SectionIterator.TIME_SEP + m_str

    @staticmethod
    def decode(format_time):
        hm = format_time.split(SectionIterator.TIME_SEP)
        return int(hm[0]) * Constants.TIME_UNIT_MINUTE + int(hm[1])
