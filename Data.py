class Data(object):
    """
    A Data object has the specific data for a region weather.

    - code -- the weather code, which can be from 100 (sun) to 499 (Massive snow fall)
    - temperature -- can be from -50 to 50 Celsius grades
    - humidity -- can be from 0 to 100%
    - air -- the air quality in region -- can be from <Constants.min_air_quality> to 100%
    """
    air = 0
    code = 0
    humidity = 0
    temperature = 0

    def __init__(self, _dict):
        """
        Used for creating a Data object from a dictionary.

        :param _dict: The dictionary containing the components (code, temperature, humidity and air)
        """
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
        """
        Return the Data object as string, with all components.

        :return: String -> The string containing all Data object components values separated by a space.
        """
        return str(self.air) + ' ' + str(self.code) + ' ' + str(self.humidity) + ' ' + str(self.temperature)
