class Data(object):
    air = 0
    code = 0
    humidity = 0
    temperature = 0

    def __init__(self, _dict):
        self.__dict__.update(_dict)

    def __repr__(self):
        return (
            f'Data(\
                    air={self.air}, \
                    code={self.code}, \
                    humidity={self.humidity}, \
                    temperature={self.temperature}\
                )'
        )

    def toString(self):
        return str(self.air) + ' ' + str(self.code) + ' ' + str(self.humidity) + ' ' + str(self.temperature)
