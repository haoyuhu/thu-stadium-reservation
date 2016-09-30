#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils.Constants import Constants
from entities.Stadium import Stadium
from entities.User import User


class BookQuery:
    def __init__(self, stadium, date, fields, user, payment=Constants.THU_STADIUM_BOOK_PAYMENT['on_site']):
        """
        :param Stadium stadium:
        :param str date:
        :param list fields:
        :param User user:
        :param int payment:
        """
        self.stadium = stadium
        self.date = date
        self.fields = fields
        self.user = user
        self.payment = payment

    def get_reservation_params(self):
        if self.fields is None or len(self.fields) == 0:
            return None

        sport_type = self.fields[0].sport_type
        ft_sep = '#'
        l = []
        for field in self.fields:
            mix = field.field_id + ft_sep + self.date
            l.append(mix)

        return {
            'bookData.book_person_phone': self.user.phone,
            'bookData.book_mode': 'from-phone',
            'item_idForCache': self.stadium.get_site_info(sport_type).get_id(),
            'time_dateForCache': self.date,
            'userTypeNumForCache': Constants.THU_USER_TYPES[self.user.user_type],
            'putongRes': 'putongRes',
            'selectedPayWay': self.payment,
            'allFieldTime': l
        }
