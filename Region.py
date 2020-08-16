import Utils
from Record import Record


class Region(object):
    name = Utils.default_name
    records = [Record]

    def __init__(self, name, _dict):
        self.name = name
        self.__dict__.update(_dict)
