#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils.Constants import Constants


class TimeInterval:
    def __init__(self, start, end):
        """
        :param str start: start time
        :param str end: end time
        """
        self.start = start
        self.end = end

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_interval_in_minute(self):
        shm = self.start.split(':')
        ehm = self.end.split(':')
        s = int(shm[0]) * Constants.TIME_UNIT_MINUTE + int(shm[1])
        e = int(ehm[0]) * Constants.TIME_UNIT_MINUTE + int(ehm[1])
        return e - s

    def pair(self):
        return self.start, self.end

    def get_possible_pairs(self):
        shm = self.start.split(':')
        ehm = self.end.split(':')
        mid = [shm[0], shm[1]]
        ret = []
        while mid[0] != ehm[0] or mid[1] != ehm[1]:
            mid_time = mid[0] + ':' + mid[1]
            ret.append(((self.start, mid_time), (mid_time, self.end)))
            if mid[1] == '30':
                mid[1] = '00'
                mid[0] = str(int(mid[0]) + 1)
            else:
                mid[1] = '30'
        return ret[1:]

    def in_interval(self, time):
        """
        :param str time: time in string
        """
        hm = time.split(':')
        shm = self.start.split(':')
        ehm = self.end.split(':')
        if len(hm) != 2 or len(shm) != 2 or len(ehm) != 2:
            return False
        if int(shm[0]) < int(hm[0]) < int(ehm[0]):
            return True
        elif int(hm[0]) == int(shm[0]):
            return int(hm[1]) >= int(shm[1])
        elif int(hm[0]) == int(ehm[0]):
            return int(hm[1]) <= int(ehm[1])
        return False

    def get_section_str(self):
        return self.start + '-' + self.end
