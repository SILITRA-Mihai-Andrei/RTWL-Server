import Constants


class Weather:
    """
    A Weather object is the form in which the final calculated weather condition for each region is wrote in database
    and is read by users to display it on map.
    """
    weather = ''
    temperature = Constants.max_temperature+1
    humidity = Constants.max_humidity+1
    air = Constants.max_air_quality+1

    def __init__(self, weather, temperature, humidity, air):
        """
        This is used to create an Weather object from a dictionary or by using the parameters.

        :param weather: The weather title (ex: 'Moderate rain')
        :param temperature: The average temperature in the region (ex: 25)
        :param humidity: The average humidity in the region (ex: 50)
        :param air: The average air quality in the region (ex: 6)
        """
        self.weather = weather
        self.temperature = round(temperature, 1)
        self.humidity = round(humidity, 1)
        self.air = round(air, 0)
