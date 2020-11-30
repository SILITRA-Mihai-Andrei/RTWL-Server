import pyrebase
from datetime import datetime

import Constants
import Texts
import Utils
from threading import Timer


def stream_handler(message):
    """
    Listener to database - called when database data changed (add, modify, remove)

    :parameter message: dictionary with 'event', 'data' and 'path' keys
    :return: Nothing

    Example:

    # print(message["event"]) -> put\n
    # print(message["path"]) -> /-data\n
    # print(message["data"]) -> {'temperature': '25', "humidity": "50"}
    """
    event = message["event"]
    data = message["data"]
    path = message["path"]
    split_path = path.split('/')
    # Check if a region was deleted from 'data' node in database (event = put and data is None)
    if event == 'put' and data is None and Constants.data_path in path and len(split_path) == 3:
        # If region was deleted - delete the region from 'weather' node too - the region has no longer weather data
        db.child(path.replace(Constants.data_path, Constants.weather_path)).remove()
        # Print a message on terminal
        print(Texts.region_deleted_delete_weather_data % split_path[2])
    # No new data
    if data is None:
        return


def checkDataBaseInterval():
    """
    Called every <Utils.check_database_interval> second to check the database content

    time.run() will recall this function after <Constants.check_database_interval> seconds. This will throw
    <RecursionError> exception, which is handled by <Utils.handleRecursionError()> function

    :return: Nothing
    """
    print(Texts.checking_database % datetime.now().strftime("%H:%M:%S"))
    # Get database data
    data = db.child(Constants.data_path).get().val()
    try:
        # Create a list from database data
        result = list(data.items())
    except AttributeError:
        Utils.handleRecursionError(timer, my_stream)
        return
    # Get database dictionary as two list of regions and records
    regions, records = Utils.getDataBaseLists(result, db)
    # No valid regions or records received from database
    if regions is None or records is None:
        # Call the function again after <check_database_interval> minutes
        timer.run()
        return
    # If received valid data from database - check all data
    try:
        # Check database data
        Utils.checkDataBaseData(db, records, regions, data)
    # If something goes wrong
    except (TypeError, KeyError):
        pass  # Do nothing
    print(Texts.string_done)
    # Call the function again after <Utils.check_database_interval> seconds
    timer.run()
    return


print("=== START ===")
firebase = pyrebase.initialize_app(Constants.config)  # initialize firebase with that config
db = firebase.database()  # Get firebase instance object
my_stream = db.stream(stream_handler)  # Create a stream for listening to events (update, remove, set)

db.child(Constants.data_path).set(Constants.data_test)

# Create timer - call function (parameter 2) after a time (parameter 1)
timer = Timer(Constants.check_database_interval, checkDataBaseInterval, args=None, kwargs=None)
# Start the timer
timer.start()

# Waiting for any key to stop the program and close stream
string = input("Press any key to end!\n")
if len(string) > 0 or string == '':
    my_stream.close()
    timer.cancel()
    print("=== END ===")
