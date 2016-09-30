#!/usr/bin/env python
# -*- coding: utf-8 -*-

from UrlBuilder import UrlBuilder


class Constants:
    TIME_UNIT_MILLIS = 1000
    TIME_UNIT_SECOND = 60
    TIME_UNIT_MINUTE = 60
    TIME_UNIT_HOUR = 24
    WEEK_NAMES_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    THU_SCHEMA = UrlBuilder.SCHEMA_HTTP

    THU_USER_TYPES = {
        'student': 1,
        'teacher': 0
    }
    THU_INFO_HOST = 'info.tsinghua.edu.cn'
    THU_INFO_LOGIN_SEGMENTS = ['Login']
    THU_INFO_MAIN_PAGE_SEGMENTS = ['render.userLayoutRootNode.uP']
    THU_INFO_REDIRECT_TO_STADIUM_SEGMENTS = ['minichan', 'roamaction.jsp']
    THU_INFO_REDIRECT_TO_STADIUM_QUERY_PARAMS = {'id': 424}

    THU_STADIUM_BOOK_ACTIONS = {
        'book': 'saveGymBook',
        'query': 'viewBook',
        'view': 'viewGymBook'
    }
    THU_STADIUM_HOST = '50.tsinghua.edu.cn'
    THU_STADIUM_BOOK_ACTION_SEGMENTS = ['gymbook', 'gymbook', 'gymBookAction.do']
    THU_STADIUM_BOOK_ACTION_QUERY_PARAMS = {'ms': THU_STADIUM_BOOK_ACTIONS['book']}
    THU_STADIUM_MAIN_SEGMENTS = ['gymbook', 'gymBookAction.do']
    THU_STADIUM_STATUS_SEGMENTS = ['gymsite', 'cacheAction.do']

    THU_STADIUM_BOOK_PAYMENT = {
        'on_site': 0,
        'on_line': 1
    }

    def __init__(self):
        pass
