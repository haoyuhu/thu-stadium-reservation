#!/usr/bin/env python
# -*- coding: utf-8 -*-

from entities.SpecialTimeInterval import SpecialTimeInterval


class Timing:
    def __init__(self, default_interval, specials):
        self.interval = default_interval
        self.specials = specials

    @staticmethod
    def from_json(obj):
        """
        :param dict obj:
        :rtype: Timing timing object
        """
        specials = []
        for item in obj['specials']:
            specials.append(SpecialTimeInterval.from_json(item))
        return Timing(obj['default']['interval'], specials)
