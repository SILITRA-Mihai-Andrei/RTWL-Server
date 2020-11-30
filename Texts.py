default_name = 'unknown'
weather_sunny = 'Sunny'
weather_sun = 'Sun'
weather_heat = 'Heat'
weather_soft_rain = 'Soft rain'
weather_moderate_rain = 'Moderate rain'
weather_torrential_rain = 'Torrential rain'
weather_soft_wind = 'Soft wind'
weather_moderate_wind = 'Moderate wind'
weather_torrential_wind = 'Torrential wind'
weather_soft_snow_fall = 'Soft snow fall'
weather_moderate_snow_fall = 'Moderate snow fall'
weather_massive_snow_fall = 'Massive snow fall'

# Messages for firebase events
checking_database = '\nChecking database content - %s\n' \
    '------------------------------------'
removing_record = 'Removing old record %s.'
invalid_database_data = 'Invalid Database data'
updating_weather_for_region = 'Updating weather for region %s.'
updating_region_danger = "Updating danger state to '%s'."
region_deleted = "Region %s was deleted."
region_deleted_delete_weather_data = "Region %s has no more records. Delete its weather data."
string_nothing_to_do = 'Nothing to do.'
string_done = 'Done.'

# Dangers dictionary
danger_dict = {
    101: 'In this region is too hot',
    201: 'In this region the rain may be dangerous',
    301: 'In this region the wind may be dangerous',
    401: 'In this region the roads can be blocked by snow'
}
