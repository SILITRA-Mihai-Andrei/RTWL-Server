import logging
from datetime import datetime

import Constants
import Machine_learning
import Texts
from Data import Data
from Record import Record


def getTime(form=Constants.record_name_format):
    """
    Get current date and time with the format= @form.

    :return: datetime.datetime object with the current date and time in specified format.
    """
    # Get the date and time from the system
    now = datetime.now()
    # Format and return
    return now.strftime(form)


def isNumber(number):
    """
    Check if is number.

    :param number: The number in string format.
    :return: Boolean -> Is @number a number? True : False
    """
    try:
        # Try to cast the string
        int(number)
        # The cast was successful
        return True
    # The cast was unsuccessful, the string is not a number
    except ValueError as err:
        # Write the exception in logging
        logging.exception(str(err))
        return False


def isRecordNameValid(record):
    """
    Check record name. The record name must be the same as getTime() function return.

    :param record: The record name.
    :return: Boolean -> Is the records name valid? True : False
    """
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


def olderThan(record):
    """
    Check if a record is older than <Constants.older_than> value.

    :param record: The record name, which is the date and time when was wrote.
    :return: Boolean -> Is the record older than Constants.older_than ? True : False
    """
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


def getDataBaseLists(data, db):
    """
    Take the dictionary from database and return it as two lists of @regions and @records.
    The @records will be a list of lists. Each region in @regions list will have a list of records in @records list.

    :param data: The firebase data dictionary. In this dictionary is received all database data.
    :param db: The Firebase.DataBase object. The firebase instance, used to manipulate data in database.
    :return: List(String), List(List(Record)) -> Each region in @regions list will have a list of records in @records
    list.
    """
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
                except TypeError as err:
                    # Write the exception in logging
                    logging.exception(str(err))
                    # Something was wrong with the current record - delete it from database
                    db.child(Constants.data_path).child(reg).child(rec_name).remove()
                    return None, None
            # Store the records list of the current region in the list
            records.append(rec_list)
        return regions, records
    except TypeError as err:
        # Write the exception in logging
        logging.exception(str(err))
        # There was some invalid data in database
        print(Texts.invalid_database_data)
        return None, None


def calculateWeatherForEachRegion(regions, records):
    """
    Get the average weather condition from all records of a region.
    A region is a string (its name) representing the coordinates of it.

    :Examples:
    - For 47.602151 26.230123, the region name will be '47 60 26 23'.
    - For 45.392151 20.210123, the region name will be '45 39 20 21'.

    :param regions: The list of regions.
    :param records:
    :return:
    """
    if not bool(regions) or not bool(records):
        return None, None
    try:
        weather_list = []
        danger_list = []
        for index in range(len(regions)):
            weather, mean_weather_code = Machine_learning.getWeatherForRegion(records[index])
            danger = Machine_learning.getDangerRegion(mean_weather_code)
            weather_list.append(weather)
            danger_list.append(danger)
        return weather_list, danger_list
    except (TypeError, KeyError) as err:
        # Write the exception in logging
        logging.exception(str(err))
        return None, None


def getWeatherIndex(code, return_if_none=Constants.return_value_index_of_weather_not_found):
    """
    Get the index of the weather using the weather code. Weather code can be from 100 to 499.

    :Examples:

    TABLE   \n
    Code - 00-33 _____________ 33-66 _____________ 66-99                \n
    1.. ____ Sunny _____________ Sun _______________ Heat               \n
    2.. ____ Soft Rain __________ Moderate rain _____ Torrential rain   \n
    3.. ____ Soft wind __________ Moderate wind ____ Torrential wind    \n
    4.. ____ Soft snow fall ______ Mod. snowfall _____ Massive snowfall \n

    :param code: The weather code. The one to get the index for.
    :param return_if_none: Is the return of the function if the weather code index is not found.
    :return: Integer -> The index of the weather code if was found.
    """
    # Start the index with 0
    index = 0
    for i in [100, 200, 300, 400]:
        for j in [0, 33, 66]:
            if inWeatherCodeRange(code, i+j, i+j+33):
                return index
            index += 1
    return return_if_none


def inWeatherCodeRange(code, _min, _max):
    """
    Check if the code is in range.

    :param code: The number to check if is in range.
    :param _min: The minimum value.
    :param _max: The maximum value.
    :return: Boolean -> _min <= code <= _max
    """
    # Example: code = 120
    # _min = 0  _max = 133
    # return 0 <= 120 <= 133 => true
    return _min <= code <= _max


def checkDataBaseData(db, records, regions, data):
    """
    Called every <Constants.check_database_interval> to check the database data.

    - Remove invalid data.
    - Write the calculated data.
    - Update new data.

    :param db: The FireBase.DataBase object used to manipulate data in database.
    :param records: The records list, which is a list of lists of records for each region.
    :param regions: The regions list, which is a list of strings that are the names of regions.
    :param data: The data dictionary received from database.
    :return: Nothing.
    """
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
                    # Delete the region from 'weather', 'dangers' and 'predictions' nodes
                    db.child(Constants.weather_path).child(region).remove()
                    db.child(Constants.danger_path).child(region).remove()
                    db.child(Constants.predictions_path).child(region).remove()
                    print(Texts.region_deleted_delete_its_data % region)
        # Check if the region is None
        if not bool(data[region]):
            # Remove the region from dictionary
            del data[region]
            # Put in regions list a None object instead of region
            regions[i] = None
    # After all data in data dictionary is checked
    # Write the data in database
    writeRegionWeather(data, db)
    return records


def writeRegionWeather(data, db):
    """
    Write the calculated weather conditions in database:

    - 'weather' node -- the calculated weather for each region
    - 'dangers' node -- for regions where there are dangers
    - 'predicts' node -- machine learning predictions for each region

    :param data: Dictionary containing the data received from database with old records removed.
    :param db: The FireBase.DataBase object for manipulating the database.
    :return: Nothing.
    """
    # Get two lists of regions and records from data dictionary
    regions, records = getDataBaseLists(list(data.items()), db)
    # Calculate an average weather for each region using its records list
    weather_list, danger_list = calculateWeatherForEachRegion(regions, records)
    # If the weather is valid and all regions have a valid weather
    if weather_list is not None and len(regions) == len(weather_list):
        # Loop through all regions
        for i in range(len(regions)):
            try:
                # The current region has no valid weather, continue with the next region
                if weather_list[i] is None:
                    continue
                # Write in database - node weather - the region weather
                db.child(Constants.weather_path).child(regions[i]).set(
                    {'weather': weather_list[i].weather,
                     'temperature': weather_list[i].temperature,
                     'humidity': weather_list[i].humidity,
                     'air': weather_list[i].air})
                # Print a message in terminal
                print(Texts.updating_weather_for_region % regions[i], end=' ')
                # If there is a danger state in the current region
                if danger_list[i] is not None:
                    # Write the danger state to database
                    db.child(Constants.danger_path).child(regions[i]).set(danger_list[i])
                    # Print a message for danger state updating
                    print(Texts.updating_region_danger % danger_list[i])
                # There is no danger state for the current region
                else:
                    # Print a new line in terminal if there is no danger state to print - the last print has no new line
                    print()
            except (AttributeError, Exception) as err:
                # Write the exception in logging
                logging.exception(str(err))


def writeRecordsInDataframe(records):
    """
    Write the new records in the main dataframe (from Machine_learning file). The records with the same values that
    exists in dataframe will be ignored (no duplications).

    :param records: list(list()) -- The list of list of Record objects used to write in dataframe
    :return: Nothing.
    """
    # The list is not defined -- something was wrong
    if records is None:
        return
    # Loop through the main list, containing the list of Record objects
    for region_recs in records:
        # Loop through all Record objects of each list
        for record in region_recs:
            # Check if the record is already wrote in dataframe (ignoring the record name - the record date and time)
            if not Machine_learning.existInDataframe(Machine_learning.dataFrame, record) and record is not None:
                # Write in the dataframe the new record values
                Machine_learning.dataFrame.loc[len(Machine_learning.dataFrame)] = \
                    [record.name, record.data.code, record.data.temperature, record.data.humidity, record.data.air]


def getSecondsFromStringDateTime(date_time):
    """
    Get the seconds of the @date_time string.

    :param date_time: String representing the date and time.
    :return: The integer value of @date_time
    """
    split_date_time = date_time.split(Constants.record_name_sep)
    if len(split_date_time) == 5:
        for value in split_date_time:
            if not isNumber(value):
                return Constants.return_value_invalid_datetime_value
        result = int(split_date_time[0]) * 31622400  # Year in seconds
        result += int(split_date_time[1]) * 2592000  # Month in seconds
        result += int(split_date_time[2]) * 86400  # Day in seconds
        result += int(split_date_time[3]) * 3600  # Hour in seconds
        result += int(split_date_time[4]) * 60  # Minute in seconds
        return result
    else:
        return Constants.return_value_invalid_datetime_value


def getWeatherString(index):
    """
    Returns the weather string (name) from the <Texts.py> file using the index of the weather. The weather titles are
    wrote in a dictionary, where the keys are the index.

    Example:

    - index = -1 -> Texts.weather_titles[-1] -> Invalid weather
    - index = 0 -> Texts.weather_titles[0] -> Sunny
    - index = 11 -> Texts.weather_titles[11] -> Massive snow fall

    :param index: The index of the weather.
    :return: String -> The weather title.
    """
    return Texts.weather_titles[index]


def convertToList(data):
    """
    Convert a dictionary to a list.
    :param data: is the dictionary.
    """
    try:
        # Try to create a list from dictionary
        result = list(data.items())
        # Successfully created
        # Return the list
        return result
    except Exception as err:
        # Couldn't convert the dictionary to a list
        print(err)
        return None
