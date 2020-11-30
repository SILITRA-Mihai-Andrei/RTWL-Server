import Data
import Texts


class Record:
    """
    A record has:

    # a name -- This is a string representing the date and time when the record was in database. The format of the
    record name is <Texts.record_name_format>.

    # a Data object -- This object contain the record data, such as temperature, humidity, code and air.
    """
    name = Texts.default_name
    data = Data

    def __init__(self, time, data):
        self.name = time
        self.data = data
