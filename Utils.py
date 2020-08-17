from datetime import datetime

import Constants
import Texts
from Weather import Weather
from Data import Data
from Record import Record


def getTime():
    now = datetime.now()
    return now.strftime("%y:%m:%d:%H:%M")


def isNumber(number):
    try:
        int(number)
        return True
    except ValueError:
        return False


def isRecordNameValid(record):
    splitted = record.split(':')
    if len(splitted) != 5:
        return False
    for x in splitted:
        if not isNumber(x):
            return False
    return True


def olderThan(record):
    if isRecordNameValid(record):
        splitted_record = record.split(':')
        splitted_date = getTime().split(':')
        if splitted_record[0] == splitted_date[0] \
                and splitted_record[1] == splitted_date[1] \
                and splitted_record[2] == splitted_date[2]:
            record_minutes = int(splitted_record[3]) * 60 + int(splitted_record[4])
            minutes = int(splitted_date[3]) * 60 + int(splitted_date[4])
            if int(minutes) - int(record_minutes) > Constants.older_than * 60:
                return True
            else:
                return False
        else:
            return True
    return True


class Utils(object):
    pass


def getDataBaseLists(data, db):
    regions = []
    records = []
    try:
        for reg, rec in data:
            regions.append(reg)
            rec_list = []
            for rec_name, rec_data in rec.items():
                try:
                    rec_list.append(Record(rec_name, Data(rec_data)))
                except TypeError:
                    db.child(Constants.data_path).child(reg).child(rec_name).remove()
                    return None, None
            records.append(rec_list)
        return regions, records
    except TypeError:
        print(Texts.invalid_database_data)
        return None, None


def calculateWeatherForEachRegion(regions, records):
    if not bool(regions) or not bool(records):
        return None
    try:
        weather = []
        for i in range(len(regions)):
            average_code = 0
            average_temperature = 0
            average_humidity = 0
            average_air = 0
            length = len(records.__getitem__(i))
            for j in range(length):
                data = records.__getitem__(i).__getitem__(j).data
                average_code += data.code
                average_temperature += data.temperature
                average_humidity += data.humidity
                average_air += data.air
            if length != 0:
                average_code = average_code / length
                average_temperature = average_temperature / length
                average_humidity = average_humidity / length
                average_air = average_air / length
                if inWeatherCodeRange(average_code, Constants.min_weather_code, Constants.max_weather_code):
                    weather.append(Weather(getWeatherString(getWeatherIndex(average_code)), None,
                                           average_temperature, average_humidity, average_air))
        return weather
    except TypeError:
        return None
    except KeyError:
        return None


def getWeatherIndex(code):
    for i in [1, 2, 3, 4]:
        if inWeatherCodeRange(code, i * 100, 33 + (i * 100)):
            return (i - 1) + ((i - 1) * 2)  # 0, 3, 6, 9
        elif inWeatherCodeRange(code, 34 + (i * 100), 66 + (i * 100)):
            return i + ((i - 1) * 2)  # 1, 4, 7, 10
        elif inWeatherCodeRange(code, 67 + (i * 100), 99 + (i * 100)):
            return i + 1 + ((i - 1) * 2)  # 2, 5, 7, 11
    return -1


def inWeatherCodeRange(code, _min, _max):
    return _min <= code <= _max


def getWeatherString(index):
    if index == 0:
        return Texts.weather_sunny
    elif index == 1:
        return Texts.weather_sun
    elif index == 2:
        return Texts.weather_heat
    elif index == 3:
        return Texts.weather_soft_rain
    elif index == 4:
        return Texts.weather_moderate_rain
    elif index == 5:
        return Texts.weather_torrential_rain
    elif index == 6:
        return Texts.weather_soft_wind
    elif index == 7:
        return Texts.weather_moderate_wind
    elif index == 8:
        return Texts.weather_torrential_wind
    elif index == 9:
        return Texts.weather_soft_snow_fall
    elif index == 10:
        return Texts.weather_moderate_snow_fall
    elif index == 11:
        return Texts.weather_massive_snow_fall


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
