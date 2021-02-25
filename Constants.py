from datetime import datetime

from dateutil.relativedelta import relativedelta

import Config

# Firebase configuration
config = Config.firebase

check_database_interval = 5  # How often to check the database in seconds
check_closing_server_interval = 1  # How often to check the database in seconds
older_than = 60  # Record older than <minutes>

min_weather_code = 100
max_weather_code = 499
min_temperature = -50
max_temperature = 50
min_humidity = 0
max_humidity = 100
min_air_quality = 4  # values under this might be produced even with damaged sensor
max_air_quality = 100

record_name_format = '%y:%m:%d:%H:%M'
record_name_sep = ':'

return_value_index_of_weather_not_found = -1
return_value_invalid_datetime_value = -1

# Data path for data in FireBase database - where the regions with their records are stored
data_path = 'data'
# Weather path for weather in Firebase database - where the regions with their calculated weather are stored
weather_path = 'weather'
# Danger path for Firebase database - where the regions with their danger are stored
danger_path = 'dangers'
# Predictions path for Firebase database - where the regions with their weather predictions are stored
predictions_path = 'predictions'

# MACHINE LEARNING
# Percent of records to take from the end o a dataframe
# The int casting: a value under or equal to 0.50 will be converted to 0,
#   and a value over 0.5 will be converted to 1
# percent=0.49 will return (50%-1) records
# percent=0.51 will return (50%+1) records
records_count_percent = 0.51
# Minimum relationship percent to predict values
min_relationship = 0.1  # <= 10%
# Machine learning .CVS external file
cvs_url = ''
# Machine learning .CVS local file
cvs_local = 'ML_Server_RTWL.cvs'
# Titles for data frame
dataframe_titles = ['date', 'weather_code', 'temperature', 'humidity', 'air_quality']
# Data frame dictionary
dataframe_titles_dictionary = {dataframe_titles[0]: [],
                               dataframe_titles[1]: [],
                               dataframe_titles[2]: [],
                               dataframe_titles[3]: [],
                               dataframe_titles[4]: []}
# Danger weather_codes dictionary
# Each key is for a weather type (ex: 100 is for sun weather)
danger_weather_code = {
    100: [[167, 189], [190, 199]],
    200: [[267, 289], [290, 299]],
    300: [[367, 389], [390, 399]],
    400: [[467, 489], [490, 499]]
}

dataframe_test = {
    'date':
        ['20:11:16:16:31', '20:11:16:16:32', '20:11:18:16:33', '20:11:17:16:27', '20:11:16:16:28', '20:11:16:16:29',
         '20:11:16:16:34', '20:11:18:16:35', '20:11:17:16:24', '20:11:16:16:25', '20:11:16:16:26',
         '20:11:16:16:36', '20:11:18:16:37', '20:11:17:16:21', '20:11:16:16:22', '20:11:16:16:23',
         '20:11:16:16:38', '20:11:16:16:39', '20:11:16:16:19', '20:11:16:16:20',
         '20:11:16:16:40', '20:11:16:16:41', '20:11:16:16:17', '20:11:16:16:18',
         '20:11:16:16:42', '20:11:16:16:43', '20:11:16:16:15', '20:11:16:16:16',
         '20:11:16:16:44', '20:11:16:16:45', '20:11:16:16:13', '21:11:16:16:14'],
    'weather_code':
        [100, 100, 102, 104, 106, 108,
         110, 112, 114, 116, 118,
         121, 123, 127, 130, 133,
         166, 170, 180, 199,
         200, 233, 266, 299,
         300, 333, 366, 399,
         400, 433, 466, 499],
    'temperature':
        [15, 15, 15.5, 16, 16.7, 17.2,
         17.8, 18.3, 18.9, 19.4, 20,
         20.7, 21.3, 22.5, 23.8, 24.8,
         25.6, 27.3, 28.8, 33,
         18, 15, 12, 8,
         218, 15, 11, 9,
         5, 2, -2, -10],
    'humidity':
        [45, 44, 43.4, 41.7, 40.3, 39.5,
         36, 34.6, 33.1, 31.9, 30.5,
         29.4, 28.1, 26.8, 24, 20,
         40, 30, 22, 12,
         80, 85, 90, 98,
         50, 55, 66, 81,
         82, 84, 92, 99],
    'air_quality':
        [5, 5, 11, 8, 9, 7,
         12, 11, 10, 11, 12,
         13, 13, 12, 12, 12,
         8, 8, 9, 8,
         10, 11, 10, 10,
         7, 6, 8, 5,
         5, 5, 5, 5]
}


def getDateTimeDelta(date_time, op, form=record_name_format, days=0, hours=0, minutes=0, seconds=0):
    """
    Get the @date_time string with the @form format after the @op with the rest of parameters are applied.

    Examples:                                       \n
    date_time = 20/12/05 15:30                      \n
    op = '-'                                        \n
    form = '%y:%m:%d:%H:%M'                         \n
    days = 3                                        \n
    The function will return -> 20:12:02:15:30      \n

    :param date_time: datetime.datetime object -- the date and time you want to apply @op and the rest of parameters
    :param op: String -- the operator to apply between @date_time and the rest of parameters ('-', or '+')
    :param form: String -- the return format of date and time
    :param days: Int -- the days to add/subtract to/from @date_time
    :param hours: Int -- the hours to add/subtract to/from @date_time
    :param minutes: Int -- the minutes to add/subtract to/from @date_time
    :param seconds: Int -- the seconds to add/subtract to/from @date_time
    :return: String -- the date and time with @op applied, with @form format
    """
    ops = {'+': (lambda x, y: x + y), '-': (lambda x, y: x - y)}
    if op == '+' or op == '-':
        return (ops[op](date_time, relativedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))) \
            .strftime(form)
    return None


def get_data_test():
    dt = datetime.now()
    return {
        '47 63 26 24': {
            getDateTimeDelta(dt, '-', minutes=1): {'air': 8, 'code': 491, 'humidity': 28, 'temperature': 15}},
        '47 63 26 25': {
            getDateTimeDelta(dt, '-', minutes=2): {'air': 8, 'code': 450, 'humidity': 28, 'temperature': 15}},
        '47 63 26 26': {
            getDateTimeDelta(dt, '-', minutes=3): {'air': 8, 'code': 400, 'humidity': 28, 'temperature': 15}},
        '47 63 26 27': {
            getDateTimeDelta(dt, '-', minutes=4): {'air': 8, 'code': 380, 'humidity': 28, 'temperature': 15}},
        '47 64 26 20': {
            getDateTimeDelta(dt, '-', minutes=1): {'air': 8, 'code': 100, 'humidity': 40, 'temperature': 15},
            getDateTimeDelta(dt, '-', minutes=1): {'air': 8, 'code': 105, 'humidity': 37, 'temperature': 16},
            getDateTimeDelta(dt, '-', minutes=2): {'air': 9, 'code': 111, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=2): {'air': 9, 'code': 111, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=2): {'air': 9, 'code': 111, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=3): {'air': 9, 'code': 111, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=3): {'air': 9, 'code': 111, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=3): {'air': 9, 'code': 111, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=4): {'air': 9, 'code': 111, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=4): {'air': 9, 'code': 141, 'humidity': 35, 'temperature': 17},
            getDateTimeDelta(dt, '-', minutes=5): {'air': 9, 'code': 143, 'humidity': 33, 'temperature': 19}}
    }
