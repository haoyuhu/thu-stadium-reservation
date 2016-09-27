from TimeInterval import TimeInterval


class SpecialTimeInterval(TimeInterval):
    def __init__(self, interval, start, end):
        TimeInterval.__init__(self, start, end)
        self.interval = interval

    def get_interval(self):
        return self.interval

    @staticmethod
    def from_json(obj):
        return SpecialTimeInterval(obj['interval'], obj['start'], obj['end'])