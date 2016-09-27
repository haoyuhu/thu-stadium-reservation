class SiteCategory:
    def __init__(self, sport_id, exceptions):
        self.sport_id = sport_id
        self.exceptions = exceptions

    def in_exceptions(self, name):
        name = str(name)
        for e in self.exceptions:
            if str(e) in name:
                return True
        return False

    def get_id(self):
        return self.sport_id

    @staticmethod
    def from_json(obj):
        return SiteCategory(obj['id'], obj['exceptions'])
