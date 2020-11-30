default_name = 'unknown'

weather_titles = {
    -1: 'Invalid weather',
    0: 'Sunny',
    1: 'Sun',
    2: 'Heat',
    3: 'Soft rain',
    4: 'Moderate rain',
    5: 'Torrential rain',
    6: 'Soft wind',
    7: 'Moderate wind',
    8: 'Torrential wind',
    9: 'Soft snow fall',
    10: 'Moderate snow fall',
    11: 'Massive snow fall'
}

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
