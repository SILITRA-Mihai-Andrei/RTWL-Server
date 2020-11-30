# weather code can be 100-499
# TABLE
#       00-33           33-66               66-99
# 1..   Sunny           Sun                 Heat
# 2..   Soft Rain       Moderate rain       Torrential rain
# 3..   Soft wind       Moderate wind       Torrential wind
# 4..   Soft snow fall  Moderate snow fall  Massive snow fall

import copy

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


def getDateTime(datetime, form='%y:%m:%d:%H:%M'):
    """
    Return date and time with <form> format.

    :parameter datetime: A string with date and time, having the format=form
    :parameter form: The format in which the datetime string comes
    :return: pandas.to_datetime(datetime, format=form)
    """
    return pandas.to_datetime(datetime, format=form)


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
    # Get the columns data used for prediction
    columns_for_prediction = dataframe[for_prediction]
    # Select the columns to predict
    columns_to_predict = dataframe[to_predict]
    # Calculate regression - necessary to predict the values
    regression = linear_model.LinearRegression()
    # Set the columns for prediction
    regression.fit(columns_for_prediction, columns_to_predict)
    # Return the predicted values as a list
    return regression.predict([values])


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
    dataframe = checkMultipleWeather(dataframe)
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
            # Check in which limit the weather_code is
            if Utils.inWeatherCodeRange(weather_code, limit[0], limit[1]):
                # The weather_code is in a danger limit - return the danger string from <danger_dict>
                return Texts.danger_dict[i+index]
            # Go for the next danger limit
            index += 1
    # No dangers found
    return None


def getSliceOfDataFrame(dataframe, percent):
    """
    Get a portion of @dataframe from the end. The records in @dataframe is ordered and the last records represents
        the newest records. The first records representes the old records. That's why this function returns the records
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
    # Ex: If the length=10 and percent=0.5 than records_count = 5 - the function will return 5 records from the end
    records_count = int(length * percent)
    # If there are more than one valid record
    if records_count > 1:
        # Add one more record to return - 50% + 1
        records_count += 1
    # Return the number of record from the end of the table, which are the most recent records (less older)
    return dataframe.tail(records_count)


def checkMultipleWeather(dataframe):
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
                # Get <x% + 1> of the most recent records (less older)
                slice_dataframe = getSliceOfDataFrame(weather, Constants.records_count_percent)
                # Continue only if the returned dataframe has records
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
        return checkMultipleWeather(new_dataframe)
    else:
        # Something was wrong
        return None


def existInDataframe(dataframe, frame):
    """
    Check if the @frame exists in @dataframe with the same values, except @air_quality value.
    This function is used to check the @dataframe to avoid duplication of @frame.

    :param dataframe: The pandas.DataFrame object where are stored all records.
    :param frame: The pandas.DataFrame object that must be inserted in @dataframe.
    :return: Boolean -> @frame is in @dataframe ? True : False
    """
    # <frame> is a dictionary with <Constants.dataframe_titles> keys and one item for all of them -  a single record
    # If dataframe of frame is not defined, there is nothing to do here
    if dataframe is None or frame is None:
        return False
    # Store dataframe titles here - it is used to select data from dataframe
    dataframe_titles = Constants.dataframe_titles
    # Remove the 'date' column - which is not necessary here
    dataframe_titles.remove(Constants.dataframe_titles[1])
    # Dataframe table is where the dataframe table is stored without 'date' column
    dft = dataframe[dataframe_titles]
    # Store all records with column 'weather_code' equal to the one from the <frame>
    # In other words, get all records with the same <weather_code> as the <frame.weather_code>
    weather_code_tables = dft[dft[dataframe_titles[1]] == frame[dataframe_titles[1]][0]]
    # If there is at least one valid record (same <weather_code> as the <frame.weather_code>)
    if len(weather_code_tables) > 0:
        # Get all records with the same <temperature> as <frame.temperature>
        if len(weather_code_tables[dataframe_titles[2]][weather_code_tables[dataframe_titles[2]] ==
                                                        frame[dataframe_titles[2]][0]]) > 0:
            if len(weather_code_tables[dataframe_titles[3]][weather_code_tables[dataframe_titles[3]] ==
                                                            frame[dataframe_titles[3]][0]]) > 0:
                return True
    return False


# Set empty dictionary for machine learning
# The data inside this is used to as experience for machine learning
data_dict = {}

if Constants.cvs_url == '':
    # If the url is empty, read the test dictionary as .CVS file
    data_dict = Constants.dataframe_test
else:
    # If there is a .CVS file link, read from it
    data_dict = pandas.read_csv(Constants.cvs_url, names=Constants.dataframe_titles)
# Create dataframe (table) from .CVS file with columns name from parameter 2 (which is a list)
dataFrame = pandas.DataFrame(data_dict, columns=Constants.dataframe_titles)

# Split the dataframe (containing all records in database) in small tables by weather code
# Each small table contains weather codes for a single weather intensity (see table in this file header)
weather_data_frame_list, tables_count = sortByWeatherCode(dataFrame)

slope, intercept, r, p, std_err = stats.linregress(weather_data_frame_list[0].weather_code,
                                                   weather_data_frame_list[0].temperature)

# print(weather_data_frame_list)
# print(predict(weather_data_frame_list[0], ['temperature', 'humidity'], [20, 30], ['weather_code']))
# print(predict(weather_data_frame_list[0], ['weather_code'], [120], ['temperature']))
