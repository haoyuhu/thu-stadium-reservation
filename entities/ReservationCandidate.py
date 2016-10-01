#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TimeInterval import TimeInterval
import calendar


class ReservationCandidate:
    def __init__(self, available, sport_type, week, wish, length, section, fixed):
        """
        :param str sport_type:
        :param int week:
        :param TimeInterval wish:
        :param int length:
        :param TimeInterval section:
        :param bool fixed:
        """
        self.available = available
        self.sport_type = sport_type
        self.week = week
        self.wish = wish
        self.length = length
        self.section = section
        self.fixed = fixed

    def is_available(self):
        return self.available

    def is_fixed(self):
        return self.fixed

    def validate_date(self, date_str):
        """
        :type date_str: str
        """
        ymd = date_str.split('-')
        return calendar.weekday(int(ymd[0]), int(ymd[1]), int(ymd[2])) == self.week

    def get_sport_type(self):
        return self.sport_type

    def get_wish(self):
        """
        :rtype: TimeInterval
        """
        return self.wish

    def get_length(self):
        return self.length

    def get_section(self):
        """
        :rtype: TimeInterval
        """
        return self.section

    @staticmethod
    def from_json(obj, section):
        """
        :rtype: ReservationCandidate
        """
        return ReservationCandidate(
            obj['available'],
            obj['sport_type'],
            obj['week'],
            TimeInterval(obj['wish']['start'], obj['wish']['end']),
            obj['length'],
            section,
            obj['fixed'])
