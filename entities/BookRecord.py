#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


class BookRecord:
    def __init__(self, stadium_name, site_name, date_str, start, end, cost):
        self.stadium_name = stadium_name
        self.site_name = site_name
        self.date_str = date_str
        self.start = start
        self.end = end
        self.cost = cost

    @staticmethod
    def from_html(html):
        ret = []
        pattern = re.compile(r'<td class=\"center\" style=\"width:150px;table-layout: fixed;WORD-BREAK: break-all; '
                             r'WORD-WRAP: break-word\">(.+?)</td>')
        match = pattern.findall(html)
        if match:
            count = 0
            stadium_name = None
            site_name = None
            date_str = None
            start = None
            end = None
            for item in match:
                if count == 0:
                    stadium_name = item
                elif count == 1:
                    site_name = item
                elif count == 2:
                    dt = item.split('&nbsp;&nbsp;')
                    date_str = dt[0]
                    se = dt[1].split('-')
                    start = se[0]
                    end = se[1]
                elif count == 3:
                    cost = float(item)
                    ret.append(BookRecord(stadium_name, site_name, date_str, start, end, cost))
                count += 1
                if count > 3:
                    count = 0
        return ret

    def to_tuple(self):
        return self.stadium_name, self.site_name, self.date_str, self.start, self.end, self.cost
