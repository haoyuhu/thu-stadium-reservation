from Stadium import Stadium
from SiteStatus import SiteStatus
from TimeInterval import TimeInterval
import re


class SiteList:
    def __init__(self, belong_to, sport_type):
        """
        :param Stadium belong_to:
        :param str sport_type:
        """
        self.belong_to = belong_to
        self.sport_type = sport_type
        self.time_table = None

    def parse(self, html):
        self.time_table = {}
        costs = {}
        all_status = []
        pattern = re.compile(r'resourceArray\.push\(\{id:\'(\d+)\',time_session:\'(\d+:\d+)-(\d+:\d+)\','
                             r'field_name:\'(\S+?)\',overlaySize:\'\d+\'\}\)')
        match = pattern.findall(html)
        if match:
            for group in match:
                status = SiteStatus(self.sport_type, group[3], group[0], group[1], group[2], self.belong_to)
                all_status.append(status)
        pattern = re.compile(r'markResStatus\(\'\d+\',\'(\d+)\',\'\d\'\)')
        occupied = pattern.findall(html)
        pattern = re.compile(r'addCost\(\'(\d+)\',\'(\S+?)\'\)')
        match = pattern.findall(html)
        if match:
            for item in match:
                costs[item[0]] = float(item[1])

        sport = self.belong_to.get_site_info(self.sport_type)
        for s in all_status:
            if s.field_id not in occupied and not sport.in_exceptions(s.name):
                s.cost = costs[s.field_id]
                if (s.start, s.end) not in self.time_table.keys():
                    self.time_table[(s.start, s.end)] = [s]
                else:
                    self.time_table[(s.start, s.end)].append(s)

    def find_available_site(self, section):
        """
        :param TimeInterval section:
        """
        if section.pair() in self.time_table.keys():
            return [self.time_table[section.pair()][0]]
        possible_pairs = section.get_possible_pairs()
        for item in possible_pairs:
            front = item[0]
            rear = item[1]
            if front in self.time_table.keys() and rear in self.time_table.keys():
                fl = self.time_table[front]
                rl = self.time_table[rear]
                for f in fl:
                    for r in rl:
                        if f.name == r.name:
                            return [f, r]
                return [fl[0], rl[0]]
        return None
