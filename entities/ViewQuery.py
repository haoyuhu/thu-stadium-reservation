from entities.Stadium import Stadium
from entities.User import User
from utils.Constants import Constants


class ViewQuery:
    def __init__(self, stadium, sport_type, date, user):
        """
        :param Stadium stadium:
        :param str sport_type:
        :param str date:
        :param User user:
        """
        self.stadium = stadium
        self.sport_type = sport_type
        self.date = date
        self.user = user

    def get_view_site_params(self):
        return {
            'ms': Constants.THU_STADIUM_BOOK_ACTIONS['query'],
            'gymnasium_id': self.stadium.get_id(),
            'item_id': self.stadium.get_site_info(self.sport_type),
            'time_date': self.date,
            'userType': Constants.THU_USER_TYPES[self.user.user_type]
        }

    @staticmethod
    def get_view_reservation_params(stadium):
        """
        :param Stadium stadium:
        :return: dict
        """
        return {
            'ms': Constants.THU_STADIUM_BOOK_ACTIONS['view'],
            'gymnasium_id': stadium.get_id(),
            'viewType': 'm'
        }
