from SiteCategory import SiteCategory


class Stadium:
    AIR_STADIUM = 0
    MAIN_STADIUM = 1
    WEST_STADIUM = 2

    BADMINTON = 'badminton'
    PINGPONG = 'pingpong'
    BASKETBALL = 'basketball'

    def __init__(self, name, gymnasium_id, badminton, pingpong, basketball):
        """
        create stadium
        :param str name: string
        :param str gymnasium_id:
        :param SiteCategory badminton: badminton detail config
        :param SiteCategory pingpong: pingpong detail config
        :param SiteCategory basketball: basketball detail config
        """
        self.name = name
        self.gymnasium_id = gymnasium_id
        self.badminton = badminton
        self.pingpong = pingpong
        self.basketball = basketball

    def get_name(self):
        return self.name

    def get_id(self):
        return self.gymnasium_id

    def get_badminton_info(self):
        return self.badminton

    def get_pingpong_info(self):
        return self.pingpong

    def get_basketball_info(self):
        return self.basketball

    def get_site_info(self, sport_type):
        """
        :rtype: SiteCategory
        """
        if sport_type == Stadium.BADMINTON:
            return self.badminton
        elif sport_type == Stadium.PINGPONG:
            return self.PINGPONG
        elif sport_type == Stadium.BASKETBALL:
            return self.BASKETBALL
        return None

    @staticmethod
    def from_json(obj):
        badminton = SiteCategory.from_json(obj['sites']['badminton'])
        pingpong = SiteCategory.from_json(obj['sites']['pingpong'])
        basketball = SiteCategory.from_json(obj['sites']['basketball'])
        return Stadium(obj['name'], obj['gymnasium_id'], badminton, pingpong, basketball)
