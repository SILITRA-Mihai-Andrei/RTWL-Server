# weather code can be 100-499
# TABLE
#       00-33           33-66               66-99
# 1..   Sunny           Sun                 Heat
# 2..   Soft Rain       Moderate rain       Torrential rain
# 3..   Soft wind       Moderate wind       Torrential wind
# 4..   Soft snow fall  Moderate snow fall  Massive snow fall

import copy
from datetime import datetime

import numpy

import Constants
import Texts
import Utils
from Weather import Weather

import warnings
# Machine learning functions and tables
import pandas
# Statistics
from scipy import stats
# For linear progression - prediction
from sklearn import linear_model

# Hide UserWarning: Boolean Series key will be re-indexed to match DataFrame index.
warnings.filterwarnings("ignore", category=UserWarning)
pandas.set_option('display.max_rows', None)


def getDateTime(date_time, form='%y:%m:%d:%H:%M'):
    """
    Return date and time with <form> format.

    :parameter date_time: A string with date and time, having the format=form
    :parameter form: The format in which the datetime string comes
    :return: pandas.to_datetime(datetime, format=form)
    """
    return pandas.to_datetime(date_time, format=form)


def sortByWeatherCode(data_frame):
    """
    Sort all dataframe (which are tables) per weather type, using the weather_code.

    Example: All weather codes in range 100:133 (specific for sunny weather) will be stored in a list and so on.

    :parameter data_frame: pandas.DataFrame object. A sort of table with column=Constants.dataframe_titles
    :return: list(pandas.DataFrame), list(int)
    """
    # Create a list of tables (dataframe) for each weather code range (see the table in this file header)
    tables = []
    # Store the number of tables with records
    counter = 0
    # First iteration is for weather type (ex: sun, rain, wind or snowfall)
    for i in [100, 200, 300, 400]:
        # Second iteration is for weather intensity (ex: sunny (100-133), sun (134-166) or heat (167-199))
        for j in [0, 33, 66]:
            # Select the records with weather code in range
            # At first iteration: all records with weather code in range 100:133
            # At last iteration: all records with weather code in range 466:499
            table_list = data_frame[data_frame.weather_code >= i + j][data_frame.weather_code <= i + j + 33]
            # If there is data in the table, increment the counter
            if not table_list.empty:
                counter += 1
            # Add in list a table with records for each weather intensity
            tables.append(table_list)
    return tables, counter


def predict(dataframe, for_prediction, values, to_predict):
    """
    Predict values by using a dataframe and some columns of it.

    :param dataframe: The table source for records
    :param for_prediction: List of strings to select the columns from <dataframe> used for prediction.
        List with the names of columns from @dataframe that are used in prediction.
    :param values: List of values, according to @for_prediction list, that are used for prediction
    :param to_predict: List of strings to select the columns from @dataframe to be predicted.
        List with names of columns from @dataframe that are used to be predicted.
    :return: List(float) - predicted values, selected by @to_predict list, using the @for_prediction list.
    """

    # Create a new dataframe - used in the case <values> is a record name (string of date and time) and must be
    # converted to an integer (number of seconds)
    new_dataframe = dataframe
    if len(values) == 1:
        if type(values[0]) == str:
            # Create a copy of dataframe to modify the 'date' column (convert datetime string to integer)
            new_dataframe = copy.deepcopy(dataframe)
            # Convert datetime string to number of seconds (integer)
            values[0] = numpy.int64(Utils.getSecondsFromStringDateTime(values[0]))
            # Loop through all dataframe, row by row
            for index, row in new_dataframe.iterrows():
                # For each row, convert the string date and time to number of seconds
                new_dataframe.at[index, 'date'] = numpy.int64(Utils.getSecondsFromStringDateTime(row['date']))

    # Get the linear regression components
    # <relation> will be used to see the relationship between <for_prediction> and <to_predict> columns
    # The <relation> value gives the accurate percent of prediction
    slope, intercept, relation, p, std_err = stats.linregress(list(new_dataframe[for_prediction][for_prediction[0]]),
                                                              list(new_dataframe[to_predict][to_predict[0]]))
    # Check if the relationship between dataframe values and for_prediction values is <= 10% and >= -10%
    # The relationship can be from -1 (reverse related) to 1 (related), 0 means no relationship
    if Constants.min_relationship >= relation >= Constants.min_relationship * -1:
        return None, relation

    # Get the columns data used for prediction
    columns_for_prediction = new_dataframe[for_prediction]
    # Select the columns to predict
    columns_to_predict = new_dataframe[to_predict]
    # Calculate regression - necessary to predict the values
    regression = linear_model.LinearRegression()
    # Set the columns for prediction
    regression.fit(columns_for_prediction, columns_to_predict)
    # Return the predicted values as a list
    return regression.predict([values]), relation


def createPrediction(db, region, weather):
    """
    Create predictions of weather conditions for the region.

    Uses 3 dataframes. The first dataframe contains only the records with the same weather (ex: Sunny, Sun, Heat),
    the second dataframe contains the records with the same weather category (ex: Sun, Rain),
    the third dataframe contains all the records.

    Creates a list of lists that contains predicted weather code, the probability and the time for which is predicted.

    The prediction will use dataframes with old records and will create a relationship between date and time (if exists)

    :param db: is the database reference used to send the predictions.
    :param region: is the region for which are calculated predictions.
    :param weather: specifies the current weather condition in the region.
    :return: Nothing.
    """
    if region is None or weather is None:
        return
    # Get the index of the weather from the weather string received
    # Using the weather titles dictionary, where all the weather conditions are stored by its index
    # Convert the dictionary keys to a list and select the key by passing the index of the value
    index = list(Texts.weather_titles.keys())[list(Texts.weather_titles.values()).index(weather.weather)]
    # Check if the index is valid
    if index == -1 or index > 11:
        return
    # Calculate the first index of the weather
    # ex: for Sun weather, the first index is 0 (Sunny)
    # ex: for Torrential rain, the first index is 3 (Soft rain)
    _index = int(int(index / 3) * 3)
    # In this list will be appended the dataframes with the same weather category (Sun, Rain, Wind)
    frames = []
    # Loop through all 3 weather intensities (0-33, 34-66, 67-99)
    for i in range(_index, _index+3):
        # The list (passed as parameter below) is created in the main body of this file
        # It contains a list of dataframes, each one having only records with a weather intensity
        # ex: the first dataframe contains all records for Sunny weather
        # ex: the last dataframe contains all records for Massive snow fall
        frames.append(weather_data_frame_list[i])
    # Concatenate all the dataframes appended
    frame = pandas.concat(frames)
    # The list of dataframes, used for separate predictions to create medium values
    lists = [weather_data_frame_list[index], frame, dataFrame]
    # Store the result of predictions
    result = []
    # Loop through a list of values
    # The values represents how many minutes are added to the current date and time for prediction
    # ex: the first loop will predict the weather code after 10 minutes from now
    for i in [10, 30, 60]:
        # Store the predictions or the current loop (date time)
        p = []
        # Get the current date and time, plus the amount of minutes
        time = Constants.getDateTimeDelta(datetime.now(), '+', minutes=i)
        # Loop through all list of dataframes
        for dataframe in lists:
            # Store the prediction for the current loop
            predicted = predict(
                    dataframe,                          # the current dataframe in loop (3 are used for prediction)
                    [Constants.dataframe_titles[0]],    # use to select the 'date' column in dataframe used to predict
                    [time],                             # the value of the 'date' column that will be related
                    [Constants.dataframe_titles[1]])    # use to select the 'weather_code' column in dataframe
            # Append to list the prediction for the current dataframe
            p.append(predicted)
        # Append to list the predictions and the date-time for which prediction was made
        result.append([p, time])
    # Write the prediction to database
    writePrediction(db, region, result)


def writePrediction(db, region, predictions):
    """
    Write the predictions to database.

    The predictions will be cumulated and made an average value.

    :param db: is the database reference, used to write the data to database.
    :param region: is the region for which the predictions are calculated.
    :param predictions: the list of predictions for each date and time.
    :return: Nothing.
    """
    # Remove the old predictions
    db.child(Constants.predictions_path).child(region).remove()
    # Loop through all the predictions for each prediction date and time
    for i in predictions:
        r = 0           # the percent of probability for the current prediction
        code = 0        # the weather code of the current prediction
        counter = 0     # count how many predictions are valid - used for average calculation
        # Loop through all the predictions of the current prediction date and time
        for j in i[0]:
            # Check if the prediction is valid
            if j[0] is not None:
                code += j[0][0][0]  # add the current predicted weather code
                r += abs(j[1])      # add the current prediction probability
                counter += 1        # add one more successful prediction
        # Write to database the region with the current prediction date and time and with predicted values
        db.child(Constants.predictions_path).child(region).child(i[1]).set(
            {'code': int(code/counter),             # calculate the average weather code
             'probability': int(r/counter*100)})    # calculate the average prediction probability


def getWeatherForRegion(records):
    """
    Calculate the region weather using its records and machine learning.

    :param records: List of Record objects. A list of Record objects corresponds to a region. A region has many
        records used to calculate the weather inside it.
    :return: Weather, int -> A Weather object corresponding to the average weather calculated and an int value
        corresponding to the average weather_code
    """
    # Set empty dictionary with empty lists for each column
    weather_dataframe_dict = copy.deepcopy(Constants.dataframe_titles_dictionary)
    # Loop through all records
    for index in range(len(records)):
        # Get data from the record
        data = records[index].data
        # Add weather data to dictionary for current record
        weather_dataframe_dict[Constants.dataframe_titles[0]].append(records[index].name)
        weather_dataframe_dict[Constants.dataframe_titles[1]].append(data.code)
        weather_dataframe_dict[Constants.dataframe_titles[2]].append(data.temperature)
        weather_dataframe_dict[Constants.dataframe_titles[3]].append(data.humidity)
        weather_dataframe_dict[Constants.dataframe_titles[4]].append(data.air)
    # Create dataframe using the dictionary created above
    dataframe = pandas.DataFrame(weather_dataframe_dict, columns=Constants.dataframe_titles)
    # If there are multi weathers in one region - get the most common weather
    dataframe = getDominatingWeather(dataframe)
    # If there are no records - end the function
    if dataframe is None:
        return None, None
    # Calculate the average values for each column of dataframe
    mean_weather = dataframe[Constants.dataframe_titles[1:5]].mean()
    # The average weather_code
    mean_weather_code = mean_weather[Constants.dataframe_titles[1]]
    # Check if the weather code is in range (100-499)
    if Utils.inWeatherCodeRange(
            # Select weather code from list - index 1 is for 'weather_code'
            mean_weather_code,
            Constants.min_weather_code,
            Constants.max_weather_code):
        # Return the weather as a Weather object and the mean weather_code
        return Weather(
            # Get weather index by using weather code - using the index get the weather title
            Utils.getWeatherString(Utils.getWeatherIndex(mean_weather_code)),
            # Set the danger for current region
            # Set temperature, humidity and air quality
            mean_weather[Constants.dataframe_titles[2]],
            mean_weather[Constants.dataframe_titles[3]],
            mean_weather[Constants.dataframe_titles[4]]), \
               mean_weather_code
    return None, None


def getDangerRegion(weather_code):
    """
    Get the danger for a region, using its weather data.

    Example: If {weather_code = 199}, in the region is too hot.

    :param weather_code: Integer representing the average weather code used to determine if there is any danger.
    :return: String -> The string that mush be displayed on user interface for corresponding danger.
    """
    # Loop through all weather types
    for i in [100, 200, 300, 400]:
        # Store the weather_code limits dictionary - where all danger limits are stored for each weather type
        limits = Constants.danger_weather_code[i]
        # Initiate the counter for current danger limit
        index = 1
        # Loop through all limits of the current weather type - a weather type can have multiple danger types
        for limit in limits:
            # Check if the weather_code is not None
            if weather_code is None:
                return None
            # Check in which limit the weather_code is
            if Utils.inWeatherCodeRange(weather_code, limit[0], limit[1]):
                # The weather_code is in a danger limit - return the danger string from <danger_dict>
                return Texts.danger_dict[i + index]
            # Go for the next danger limit
            index += 1
    # No dangers found
    return None


def getSliceOfDataFrame(dataframe, percent):
    """
    Get a portion of @dataframe from the end. The records in @dataframe is ordered and the last records represents
        the newest records. The first records represents the old records. That's why this function returns the records
        from end.

    :Examples:

    - If the length=10 and percent=0.5 than records_count = 5 - the function will return 5 records from the end
    - If the length=15 and percent=0.75 than records_count = 11 - the function will return 11 records from the end
    - If the length=1 and percent=0.49 than records_count = 0, but the function will return 1 record from the end

    :param dataframe: The dataframe used to trim records.
    :param percent: (from 0 to 1.0) The percent of @dataframe records to return.
    """
    # Store the length of the dataframe (number of tables)
    length = len(dataframe)
    # Store the number of records to return
    # Calculate how many records to return from the end of table
    # Ex: If the length=10 and percent=0.49 than records_count = 4 - the function will return 4 records from the end
    # percent=0.49 will return (50%-1) records
    # percent=0.51 will return (50%+1) records
    # The int casting: a value under or equal to 0.50 will be converted to 0,
    #   and a value over 0.5 will be converted to 1
    records_count = round(length * percent)
    # Return the number of record from the end of the table, which are the most recent records (less older)
    return dataframe.tail(records_count)


def getDominatingWeather(dataframe):
    """
    Check if a region has records with different weather type (ex: sun and rain).
    This function has a recursion that helps in removing old data until a single weather type data remains.

    Examples:

    - If a region has 10 records with sun and 5 records with rain, this function will call itself until only the sun
    records will remain.

    - If a region has 10 records with sun and 10 records with rain, this function will call itself until no records will
    remain.

    :param dataframe: The pandas.DataFrame object used to sort records by weather code.
    :return: pandas.DataFrame object containing the records with only one weather (the dominating one).
    """
    # Get the list of tables depending on weather type (see the table in this file header) and how many non-empty tables
    weather_list, counter = sortByWeatherCode(dataframe)
    # There are no tables with records
    if counter == 0:
        return None
    # There is one table with records
    elif counter == 1:
        return dataframe
    # There are more than 1 tables with records - the region has multiple weathers type (impossible)
    elif counter > 1:
        # Create a new dictionary to store the new tables
        new_weather_list = []
        # Get through all tables
        for weather in weather_list:
            # Continue only if the table has records
            if not weather.empty:
                # Store in this variable a part of dataframe (from the end - the newest)
                slice_dataframe = None
                # If there are more than 1 record, get a slide of dataframe
                # If only one record, a slice of a record means no record
                if len(weather) != 1:
                    # Get <Constants.records_count_percent> of the most recent records (less older)
                    slice_dataframe = getSliceOfDataFrame(weather, Constants.records_count_percent)
                # Continue only if the returned dataframe has records
                if slice_dataframe is not None:
                    if not slice_dataframe.empty:
                        # Add the returned dataframe in the list
                        new_weather_list.append(slice_dataframe)
        # Create a new dataframe
        new_dataframe = pandas.DataFrame(columns=Constants.dataframe_titles)
        # Loop through all new weather list
        for weather in new_weather_list:
            # Here, new_weather_list has only the most newest records
            # Now all records, even the records with different weather type, are store in the same dataframe
            new_dataframe = new_dataframe.append(weather, ignore_index=False)
        # Call the function again and again, with all newest records, until dataframe remains with only one weather type
        return getDominatingWeather(new_dataframe)
    else:
        # Something was wrong
        return None


def existInDataframe(dataframe, record):
    """
    Check if the @frame exists in @dataframe with the same values, except @air_quality value.
    This function is used to check the @dataframe to avoid duplication of @frame.

    :param dataframe: The pandas.DataFrame object where are stored all records.
    :param record: The Record object that must be inserted in @dataframe.
    :return: Boolean -> @frame is in @dataframe ? True : False
    """
    # <frame> is a dictionary with <Constants.dataframe_titles> keys and one item for all of them -  a single record
    # If dataframe of frame is not defined, there is nothing to do here
    if dataframe is None or record is None:
        return False
    # Store dataframe titles here - it is used to select data from dataframe
    dataframe_titles = copy.deepcopy(Constants.dataframe_titles)
    # Remove the 'date' column - which is not necessary here
    dataframe_titles.remove(Constants.dataframe_titles[0])
    # Dataframe table is where the dataframe table is stored without 'date' column
    dft = dataframe[dataframe_titles]
    # Store all records with column 'weather_code' equal to the one from the <frame>
    # In other words, get all records with the same <weather_code> as the <frame.weather_code>
    table = dft[dft[dataframe_titles[0]] == record.data.code]
    # If there is at least one valid record (same <weather_code> as the <frame.weather_code>)
    if len(table) > 0:
        # Get all records with the same <temperature> as <frame.temperature>
        if len(table[dataframe_titles[1]][table[dataframe_titles[1]] == record.data.temperature]) > 0:
            if len(table[dataframe_titles[2]][table[dataframe_titles[2]] == record.data.humidity]) > 0:
                return True
    return False


# Set empty dictionary for machine learning
# The data inside this is used to as experience for machine learning
data_dict = {}

if Constants.cvs_url == '':
    if Constants.cvs_local == '':
        # If the external and local url are empty, read the test dictionary as .CVS file
        data_dict = Constants.dataframe_test
    else:
        data_dict = pandas.read_csv(Constants.cvs_local)
else:
    # If there is a .CVS file link, read from it
    data_dict = pandas.read_csv(Constants.cvs_url, names=Constants.dataframe_titles)
# Create dataframe (table) from .CVS file with columns name from parameter 2 (which is a list)
dataFrame = pandas.DataFrame(data_dict, columns=Constants.dataframe_titles)

# Split the dataframe (containing all records in database) in small tables by weather code
# Each small table contains weather codes for a single weather intensity (see table in this file header)
weather_data_frame_list, tables_count = sortByWeatherCode(dataFrame)
# This will start new predictions when the server is started
Utils.writeRegionWeather.last_prediction_time = None
