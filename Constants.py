check_database_interval = 5 # How often to check the database in seconds
older_than = 4  # Record older than <minutes>

min_weather_code = 100
max_weather_code = 499
min_temperature = -50
max_temperature = 50
min_humidity = 0
max_humidity = 100
min_air_quality = 4  # values under this might be produced even with damaged sensor
max_air_quality = 100

# Data path for data in FireBase database - where the regions with their records are stored
data_path = 'data'
# Weather path for weather in Firebase database - where the regions with their calculated weather are stored
weather_path = 'weather'

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
