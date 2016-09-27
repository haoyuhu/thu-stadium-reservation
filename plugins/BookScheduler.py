from BookHelper import BookHelper
from config.Config import Config
from utils.Common import Common
from utils.Constants import Constants
from threading import Timer


class BookScheduler:
    def __init__(self):
        self.config = Config()
        self.helper = None
        self.tasks = None
        self.timings = None
        self.timer = None

    def init(self):
        self.helper = BookHelper(self.config.get_default_account())
        self.tasks = self.config.get_reservation_tasks()
        self.timings = self.config.get_timings()

    def run(self):
        tomorrow = Common.get_tomorrow()
        day_after_tomorrow = Common.get_day_after_tomorrow()
        t_str = Common.format_date(tomorrow, Common.DATETIME_PATTERN_YYYYMMDD)
        dat_str = Common.format_date(day_after_tomorrow, Common.DATETIME_PATTERN_YYYYMMDD)
        date_strings = self.helper.should_book([t_str, dat_str])

        if date_strings:
            for date_str in date_strings:
                for task in self.tasks:
                    for candidate in task:
                        if candidate.validate_date(date_str) and self.helper.book(date_str, candidate):
                            self.__ticking(True)
                            return

        self.__ticking(False)

    def cancel(self):
        self.timer.cancel()

    def __ticking(self, book_result):
        self.helper.clear_status()
        now = Common.get_today()
        time = BookScheduler.__get_time_in_second(now.hour, now.minute, now.second)
        interval = self.timings['default']['interval']
        specials = self.timings['specials']
        min_value = interval

        for item in specials:
            shm = item['start'].split(':')
            ehm = item['end'].split(':')
            s_time = BookScheduler.__get_time_in_second(int(shm[0]), int(shm[1]))
            e_time = BookScheduler.__get_time_in_second(int(ehm[0]), int(ehm[1]))
            if s_time <= time <= e_time:
                if book_result:
                    interval = e_time - time + 1
                else:
                    interval = item['interval']
                break
            elif s_time > time:
                min_value = min(min_value, s_time - time)
        self.timer = Timer(min(min_value, interval), self.run())
        self.timer.start()

    @staticmethod
    def __get_time_in_second(hour, minute, second=0):
        return (hour * Constants.TIME_UNIT_MINUTE + minute) * Constants.TIME_UNIT_SECOND + second