#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils.UrlBuilder import UrlBuilder
from entities.SiteCategory import SiteCategory
from entities.Stadium import Stadium
from entities.SiteList import SiteList
from entities.TimeInterval import TimeInterval
from entities.BookRecord import BookRecord
from plugins.BookHelper import SectionIterator
from plugins.BookHelper import BookHelper
from plugins.MailSender import MailSender
from config.Config import Config
from utils.Common import Common
import datetime
import os


def before(name):
    print '----------'
    print 'current test: ' + name
    print 'test started!'


def after(result):
    print 'test result: ' + str(result)
    print '----------'


def test_url_builder():
    before('test url builder')

    builder = UrlBuilder()
    url1 = builder.schema(UrlBuilder.SCHEMA_HTTPS).host('www.huhaoyu.com').segment('path1') \
        .segments(['path2', 'path3']).build()

    builder = UrlBuilder()
    url2 = builder.host('www.huhaoyu.com').build()
    success = url1 == 'https://www.huhaoyu.com/path1/path2/path3' and url2 == 'http://www.huhaoyu.com/'

    after(success)


def test_site_category():
    before('test site category')

    category = SiteCategory('123456', [1, 2, 3, 4])
    success = True and category.in_exceptions('yu1')
    success = success and not category.in_exceptions('yu5')

    after(success)


def test_mail_sender():
    before('test mail sender')

    config = Config()
    account = config.get_mail_account()
    receivers = config.get_mail_receivers()
    sender = MailSender(account['sender'], account['username'], account['password'], account['host'], account['port'])
    receiver = receivers[0]
    title = account['title'] % (receiver['nickname'])
    content = account['content'] % ('air stadium', '2016-9-20 Sunday 20:00-22:00', 'huhaoyu', 40.0,
                                    Common.format_datetime(datetime.datetime.now()))
    print
    print 'from:', account['sender']
    print 'to:', receiver['address']
    print
    print title
    print content
    print
    success = sender.send(receivers[0], title, content, account['nickname'])

    after(success)


def test_config():
    before('test config')

    config = Config()
    success = config.get_standard_time_section('morning') is not None
    success = success and config.get_mail_account() is not None
    success = success and config.get_mail_receivers() is not None
    success = success and config.get_accounts() is not None
    success = success and config.get_default_account() is not None
    success = success and config.get_timings() is not None
    success = success and config.get_stadiums() is not None
    success = success and config.get_reservation_tasks() is not None

    after(success)


def test_site_list():
    before('test site list')

    config = Config()
    success = True

    stadiums = config.get_stadiums()
    main_stadium = stadiums[Stadium.MAIN_STADIUM]
    with open(get_test_folder() + os.sep + 'main_stadium_site_status.html', 'r') as f:
        html = f.read()
        site_list = SiteList(main_stadium, Stadium.BADMINTON)
        site_list.parse(html)
        success = success and site_list.find_available_site(TimeInterval('11:30', '13:00')) is not None
        success = success and site_list.find_available_site(TimeInterval('11:00', '13:00')) is None

    west_stadium = stadiums[Stadium.WEST_STADIUM]
    with open(get_test_folder() + os.sep + 'west_stadium_site_status.html', 'r') as f:
        html = f.read()
        site_list = SiteList(west_stadium, Stadium.BADMINTON)
        site_list.parse(html)
        success = success and site_list.find_available_site(TimeInterval('12:00', '14:00')) is None

    air_stadium = stadiums[Stadium.AIR_STADIUM]
    with open(get_test_folder() + os.sep + 'air_stadium_site_status.html', 'r') as f:
        html = f.read()
        site_list = SiteList(air_stadium, Stadium.BADMINTON)
        site_list.parse(html)
        success = success and site_list.find_available_site(TimeInterval('11:30', '13:00')) is not None

    after(success)


def test_book_record():
    before('test book record')

    with open(get_test_folder() + os.sep + 'reservation_results.html', 'r') as f:
        html = f.read()
        success = BookRecord.from_html(html) is not None

    after(success)


def test_section_iterator():
    before('test section iterator')

    iterator = SectionIterator(TimeInterval('14:00', '22:00'), 2)
    count = 0
    while iterator.has_next():
        count += 1
        section = iterator.current_item()
        print section.start, section.end

    after(count == 13)


def test_book_helper():
    before('test book helper')

    helper = BookHelper(Config().get_default_account())
    success = helper.login()

    after(success)


def get_test_folder():
    return os.getcwd() + os.sep + 'tests'


# -----------------------
# run tests
# -----------------------

test_url_builder()
test_site_category()
# test_mail_sender()
test_config()
test_site_list()
test_book_record()
test_section_iterator()
test_book_helper()
