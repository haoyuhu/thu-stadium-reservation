#!/usr/bin/env python
# -*- coding: utf-8 -*-

from entities.Stadium import Stadium
from entities.TimeInterval import TimeInterval


class SiteStatus:
    def __init__(self, sport_type, name, field_id, start, end, belong_to, cost=None):
        """
        :param str sport_type:
        :param str name:
        :param str field_id:
        :param str start:
        :param str end:
        :param Stadium belong_to:
        :param float cost:
        """
        self.sport_type = sport_type
        self.name = name
        self.field_id = field_id
        self.start = start
        self.end = end
        self.belong_to = belong_to
        self.cost = cost

    def set_cost(self, cost):
        """
        :param float cost:
        """
        self.cost = cost

    def get_section_str(self):
        return TimeInterval(self.start, self.end).get_section_str()
