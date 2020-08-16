import Data
import Texts


class Record:
    name = Texts.default_name
    data = Data

    def __init__(self, time, data):
        self.name = time
        self.data = data
