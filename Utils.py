from datetime import datetime

import Constants
import Machine_learning
import Texts
from Data import Data
from Record import Record


# Get current date and time with the format
def getTime():
    # Get the date and time from the system
    now = datetime.now()
    # Format and return
    return now.strftime("%y:%m:%d:%H:%M")


# Check if is number
def isNumber(number):
    try:
        # Try to cast the string
        int(number)
        # The cast was successful
        return True
    # The cast was unsuccessful, the string is not a number
    except ValueError:
        return False


# Check record name - it must be as in <getTime> function
def isRecordNameValid(record):
    # Split the string with the record separator ':'
    splitted = record.split(':')
    # There must be 5 values - year:month:day:hour:minute
    if len(splitted) != 5:
        # Not valid - more or less than 5 values
        return False
    # There are 5 values - check each one if is a number
    for x in splitted:
        # If one of the values is not a number - record is not valid
        if not isNumber(x):
            return False
    # The record is valid
    return True


# Check if a record is older than <older_than> value
def olderThan(record):
    # Check first if the record is valid
    if isRecordNameValid(record):
        # Get the record values and split them - year:month:day:hour:minute
        splitted_record = record.split(':')
        # Get the current date and time from the system and split them
        splitted_date = getTime().split(':')
        # Check if the year, month and day are the same
        if splitted_record[0] == splitted_date[0] \
                and splitted_record[1] == splitted_date[1] \
                and splitted_record[2] == splitted_date[2]:
            # Change the record hour in minutes and add the record minutes - how many minutes since the record stored
            record_minutes = int(splitted_record[3]) * 60 + int(splitted_record[4])
            # Change the current hour in minutes and add the current minutes - how many minutes passed today
            minutes = int(splitted_date[3]) * 60 + int(splitted_date[4])
            # Check if the difference is bigger than the constant - the record is too old and must be deleted
            if int(minutes) - int(record_minutes) > Constants.older_than:
                return True
            else:
                return False
        else:
            # The record is way too old - at least 1 day
            return True
    # The record is not valid and must be deleted
    return True


# Take the dictionary from database and store it as two lists of regions and records
def getDataBaseLists(data, db):
    # The list of regions - ex: "46 60 26 23" for region of coordinates 46.60 26.23
    regions = []
    # The list of lists of records - each region can have multiple records
    records = []
    try:
        # Loop through all data in database dictionary
        for reg, rec in data:
            # Store the region name in list
            regions.append(reg)
            # Create a new list for the current region to store its records
            rec_list = []
            # Loop through records dictionary to get records name and data
            for rec_name, rec_data in rec.items():
                try:
                    # Store all records for the current region as Record object
                    rec_list.append(Record(rec_name, Data(rec_data)))
                except TypeError:
                    # Something was wrong with the current record - delete it from database
                    db.child(Constants.data_path).child(reg).child(rec_name).remove()
                    return None, None
            # Store the records list of the current region in the list
            records.append(rec_list)
        return regions, records
    except TypeError:
        # There was some invalid data in database
        print(Texts.invalid_database_data)
        return None, None


# Get the average weather condition from all records of a region
def calculateWeatherForEachRegion(regions, records):
    if not bool(regions) or not bool(records):
        return None
    try:
        weather_list = []
        for index in range(len(regions)):
            weather = Machine_learning.getWeatherForRegion(records[index])
            if weather is not None:
                weather_list.append(weather)
        return weather_list
    except (TypeError, KeyError) as err:
        print(err)
        return None


# Get the index of the weather using the weather code
# weather code can be 100-499
# TABLE
#       00-33           33-66               66-99
# 1..   Sunny           Sun                 Heat
# 2..   Soft Rain       Moderate rain       Torrential rain
# 3..   Soft wind       Moderate wind       Torrential wind
# 4..   Soft snow fall  Moderate snow fall  Massive snow fall
def getWeatherIndex(code):
    index = -1
    for i in [100, 200, 300, 400]:
        for j in [0, 33, 66]:
            if inWeatherCodeRange(code, i+j, i+j+33):
                return index + 1
            index += 1


# Check if the code is in range
def inWeatherCodeRange(code, _min, _max):
    # Example: code = 120
    # _min = 0  _max = 133
    # return 0 <= 120 <= 133 => true
    return _min <= code <= _max


# Check database data
def checkDataBaseData(db, records, regions, data):
    # Loop through all list of list of records - every region has a list of records
    # The <records> list has list for each region (list of lists)
    for i in range(len(regions)):
        # Get the current region object from loop
        region = regions.__getitem__(i)
        # Store the current record list from loop
        records_list = records.__getitem__(i)
        # Loop through all lists from the records list
        for j in range(len(records_list)):
            # Get the current record name
            record = records_list.__getitem__(j).name
            # Check if is older than <Constants.older_than> value
            if olderThan(record):
                # The record is too old
                # Remove the record from data node in database
                db.child(Constants.data_path).child(region).child(record).remove()
                # Remove the record from dictionary
                del data[region][record]
                # Add a None object in the current position of the record
                records_list.insert(j, None)
                # Remove the record from records list - remaining a None object instead
                records_list.remove(records_list.__getitem__(j+1))
                # Print a message in terminal for removing the current record
                print(Texts.removing_record % record)
                # Check if this record is the last one in list
                if len(records_list) == j+1:
                    # The region will no longer have records - because the current one was removed
                    print(Texts.region_deleted % region)
                    # Delete the region from 'weather' node
                    db.child(Constants.weather_path).child(region).remove()
                    print(Texts.region_deleted_delete_weather_data % region)
        # Check if the region is None
        if not bool(data[region]):
            # Remove the region from dictionary
            del data[region]
            # Put in regions list a None object instead of region
            regions[i] = None
    # Create a new list to store the remaining regions
    new_regions = []
    for x in regions:
        # For each regions that is not None object
        if x is not None:
            # Put in the new list the region
            new_regions.append(x)
    # After all data in data dictionary is checked
    writeRegionWeather(data, db)


# Write the calculated weather conditions in 'weather' node
def writeRegionWeather(data, db):
    # Get two lists of regions and records from data dictionary
    regions, records = getDataBaseLists(list(data.items()), db)
    # Calculate an average weather for each region using its records list
    weather = calculateWeatherForEachRegion(regions, records)
    # If the weather is valid and all regions have a valid weather
    if weather is not None and len(regions) == len(weather):
        # Loop through all regions
        for i in range(len(regions)):
            try:
                # Write in database - node weather - the region weather
                db.child(Constants.weather_path).child(regions[i]).set(
                    {'weather': weather[i].weather,
                     'temperature': weather[i].temperature,
                     'humidity': weather[i].humidity,
                     'air': weather[i].air})
                # Print a message in terminal
                print(Texts.updating_weather_for_region % regions[i])
                db.child(Constants.danger_path).child(regions[i]).set(
                    {'danger_code': None})
            except AttributeError as err:
                print(err)


# Handle the RecursionError threw when callback stack is full
def handleRecursionError(timer, my_stream):
    try:
        # Call the function again after <check_database_interval> minutes
        timer.run()
    except RecursionError:
        # Exception: when the callback stack is full
        print("################### RecursionError #######################")
        # Remove database listener
        my_stream.close()
        # Stop call function timer
        timer.cancel()
        # Restart database listener
        my_stream.start()
        # Call the function again after <check_database_interval> minutes
        timer.run()


# Returns the weather string (name) from the <Texts.py> file using the index of the weather
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
