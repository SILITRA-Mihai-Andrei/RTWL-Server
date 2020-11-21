# weather code can be 100-499
# TABLE
#       00-33           33-66               66-99
# 1..   Sunny           Sun                 Heat
# 2..   Soft Rain       Moderate rain       Torrential rain
# 3..   Soft wind       Moderate wind       Torrential wind
# 4..   Soft snow fall  Moderate snow fall  Massive snow fall


import Constants
import Utils
from Weather import Weather
import warnings
# Machine learning functions and tables
import pandas
# Statistics
from scipy import stats
# For linear progression - prediction
from sklearn import linear_model

# Hide UserWarning: Boolean Series key will be reindexed to match DataFrame index.
warnings.filterwarnings("ignore", category=UserWarning)


# Return date and time with <form> format
def getDateTime(datetime, form='%y:%m:%d:%H:%M'):
    return pandas.to_datetime(datetime, format=form)


# Sort all dataframe (tables) per weather code
def sortByWeatherCode(data_frame):
    # Create a list of tables (dataframe) for each weather code range (see the table in this file header)
    weather_list = []
    # First iteration is for weather type (ex: sun, rain, wind or snowfall)
    for i in [100, 200, 300, 400]:
        # Second iteration is for weather intensity (ex: sunny (100-133), sun (134-166) or heat (167-199))
        for j in [0, 33, 66]:
            # Add in list a table with records for each weather intensity
            weather_list.append(
                # Select the records with weather code in range
                # At first iteration: all records with weather code in range 100:133
                # At last iteration: all records with weather code in range 466:499
                data_frame[data_frame.weather_code >= i + j]
                [data_frame.weather_code <= i + j + 33])
    return weather_list


# Predict values by using a dataframe and some columns of it
def predict(dataframe, for_prediction, values, to_predict):
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


# Calculate the region weather using its records and machine learning
def getWeatherForRegion(records):
    # Set empty dictionary with empty lists for each column
    weather_dataframe_dict = Constants.dataframe_titles_dictionary
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
    # Calculate the average values for each column of dataframe
    weather = dataframe.mean()
    # Check if the weather code is in range (100-499)
    if Utils.inWeatherCodeRange(
            # Select weather code from list - index 1 is for 'weather_code'
            weather[Constants.dataframe_titles[1]],
            Constants.min_weather_code,
            Constants.max_weather_code):
        # Return the weather as a Weather object
        return Weather(
            # Get weather index by using weather code - using the index get the weather title
            Utils.getWeatherString(Utils.getWeatherIndex(weather[Constants.dataframe_titles[1]])),
            # Set the danger for current region
            None,
            # Set temperature, humidity and air quality
            weather[Constants.dataframe_titles[2]],
            weather[Constants.dataframe_titles[3]],
            weather[Constants.dataframe_titles[4]])
    return None


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
weather_data_frame_list = sortByWeatherCode(dataFrame)

slope, intercept, r, p, std_err = stats.linregress(weather_data_frame_list[0].weather_code,
                                                   weather_data_frame_list[0].temperature)

# print(predict(weather_data_frame_list[0], ['temperature', 'humidity'], [20, 30], ['weather_code']))
# print(predict(weather_data_frame_list[0], ['weather_code'], [120], ['temperature']))
