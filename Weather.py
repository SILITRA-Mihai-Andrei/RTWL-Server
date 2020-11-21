import Constants


class Weather:
    weather = ''
    danger = ''
    temperature = Constants.max_temperature+1
    humidity = Constants.max_humidity+1
    air = Constants.max_air_quality+1

    def __init__(self, weather, danger, temperature, humidity, air):
        self.weather = weather
        self.danger = danger
        self.temperature = round(temperature, 1)
        self.humidity = round(humidity, 1)
        self.air = round(air, 0)
