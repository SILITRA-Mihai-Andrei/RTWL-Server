from datetime import datetime

from dateutil.relativedelta import relativedelta

check_database_interval = 5  # How often to check the database in seconds
check_for_closing_server_interval = 1  # How often to check the database in seconds
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
#
danger_weather_code = {
    100: [[190, 199]],
    200: [[290, 299]],
    300: [[390, 399]],
    400: [[490, 499]]
}

# Firebase configuration
config = {
    "apiKey": "AIzaSyBaEXgipqQIaBj8GkqDoiYaLcWlaZlreFQ",
    "authDomain": "real-time-weather-location.firebaseapp.com",
    "databaseURL": "https://real-time-weather-location.firebaseio.com",
    "storageBucket": "real-time-weather-location.appspot.com",
    "type": "service_account",
    "project_id": "real-time-weather-location",
    "private_key_id": "92c859f2e8247124879145d7fa46108d84a0dc96",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCdznDpcJ4Q2Xez"
                   "\npyBbVqENLEqcb61qbdFxmzqUqDGwHEBtFPD3Qc/E/lCGKuRUOQorwtX1B62GQ927\nL"
                   "+fxLgtYRzzGFY2X85Qx7Fsmiq39Uwig37U83gyV2cZdwZZlkBo+yzjMkgRrGNe/\nReNRQ1AZ4UG5v"
                   "/DV3gelwgLJFBpHn6XgoyCUYS8u3gaptV7tzB2V6yYJk/dnpX8y\nBBjS1hVAEX"
                   "/5af4Hnbb4Ye5ANKDqogLHU3SFALztLceDB6kk3I/fZDwAF+wgfVe7\n3/Nv2aT84ghpBTXnn+NCqxwUcHL8c4K"
                   "+vzlrtHRZDTZWY/bG2rBpaPAVY42v4CyE\nbtgDB41dAgMBAAECggEAPM7PYIymQ/zgbMgyJjAP"
                   "+BkAmR5JdxDhG4NCxAS5vNBu\nHPpsTgK8kn6ivchqWm/uVOWLd5NhULL3DonLuPpSoc41g2jLumlASip3Bzd6CvsD"
                   "\ngKYjWtR/igC0OO1/TByGmHrLpLyBWllkzU4bZXVoOMi9gFuPbIHVdZB4bU5DQCSP"
                   "\nlRIWpJtCSjpo61tuRa6BGE4neYxQrPwM2NY8VdEhMCbM0AANdmQLtR1chhZEZ4n/\ntI+ktk8yavbSyiPdgq9ads2SO"
                   "+hZ4hZyQ9IN5Zkp/+uC2f62M8nrESn6jmD/Luzj\n7mdwhOyxRxWH2ImFVQEPdVrbpYYabzuVzXPnw1"
                   "+eWwKBgQDbOAieQY3Rofi81/j2\nqdFJ8CvjBA8f2ZM82vKLMQoHIxg+bCMUvpilyVWJgR2RpYBjNTHjy5lQvHfIvPE2"
                   "\ndMRqmE1ew3OVjjQk1je+eMzrWPTLMBvG1j6cIIs8PWvnx4KGAabWcYgChuynQivk\ns42Sw4qV9URNwkKB2fzzNC"
                   "+mawKBgQC4SJjuOiHk9VEoKoYzy1Gg/Robzwx7DMYl\nRyMZWPoQE7K"
                   "/QA2Yiv4fRI8SJiRZgHCn1QCz6oEmB24EuYVjWYoFO33y+KVQPxYm"
                   "\nOlry8zJrXCZs6vYNfLOO19QU0DcTvuNDT5gtU9MvN29xOrI3FL3nHFBGJCORj0n5\nN"
                   "/kyryu9VwKBgFXHOzgRlpistFPQfo6mLEquO7383J4t2Ls7QSTN74qTZO0oCyIW\n4kwc1"
                   "+eSKivPgslPC1KDXF6HIKffptMUJbdAGSY3fIbMugKf//f79NMyX7cSAAxx\n0NXutgzAS/TJ0Hz3MH1At2Olv/xCnEJFL"
                   "+R5t0SuUCfNF5EP5zaS+QI5AoGAUikz\n3cqXQABLra+/46m7fB48HLfkJZxdX1NnB68O1koiAHirVx5pDEHB0+KjhC/qijlC"
                   "\nNfTQncbkO0EHgnLyQUDz93b6JVvrISIVWIorKYiNLTRYfUzitUXurVTjqW8K3gDH"
                   "\npTXhSwTZL89uk3Yw8LBD7fHA1e3fmjhlZz6ILsMCgYEAt+fxqwf4Zf8YNi2+fM9o\nXFz"
                   "+gKJ8SIDcBF5lynsYAYSaqGnVJvteDXkxhrIXDaPaETTeIgMkFyzMymcEm4cI"
                   "\njFx67iIi4K5YQoY8ZS3NnlgXarPRJUtkV0F0GW4k9DLyIytovX7tBKrh+E7F3I0/\nOdgs2rv8C7w/dvCP0VlFcy4=\n"
                   "-----END PRIVATE KEY-----\n",
    "client_email": "real-time-weather-location@appspot.gserviceaccount.com",
    "client_id": "103280618895051741441",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/real-time-weather-location%40appspot"
                            ".gserviceaccount.com "
}

dataframe_test = {
    'date':
        ['20:11:16:16:31', '20:11:16:16:32', '20:11:18:16:33', '20:11:17:16:27', '20:11:16:16:28', '20:11:16:16:29',
         '20:11:16:16:34', '20:11:18:16:35', '20:11:17:16:24', '20:11:16:16:25', '20:11:16:16:26',
         '20:11:16:16:36', '20:11:18:16:37', '20:11:17:16:21', '20:11:16:16:22', '20:11:16:16:23',
         '20:11:16:16:38', '20:11:16:16:39', '20:11:16:16:19', '20:11:16:16:20',
         '20:11:16:16:40', '20:11:16:16:41', '20:11:16:16:17', '20:11:16:16:18',
         '20:11:16:16:42', '20:11:16:16:43', '20:11:16:16:15', '20:11:16:16:16',
         '20:11:16:16:44', '20:11:16:16:45', '20:11:16:16:13', '20:11:16:16:14'],
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
