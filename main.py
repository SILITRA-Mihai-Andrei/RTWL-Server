import pyrebase
from datetime import datetime

import Constants
import Texts
import Utils
from threading import Timer


# Listener to database - called when database data changed (add, modify, remove)
def stream_handler(message):
    # print(message["event"])  # put
    # print(message["path"])  # /-K7yGTTEp7O549EzTYtI
    # print(message["data"])  # {'title': 'Pyrebase', "body": "etc..."}
    event = message["event"]
    data = message["data"]
    path = message["path"]
    # Check if a region was deleted from 'data' node in database (event = put and data is None)
    if event == 'put' and data is None and Constants.data_path in path:
        # If region was deleted - delete the region from 'weather' node too - the region has no longer weather data
        db.child(path.replace(Constants.data_path, Constants.weather_path)).remove()
        # Print a message on terminal
        print(Texts.region_deleted_weather_delete % path.split('/')[1])
    # No new data
    if data is None:
        return
    try:
        # result = data[Utils.data_path].items()
        # print(Utils.getDataBaseLists(result, db))
        return
    except (KeyError, TypeError):
        pass
    try:
        # print(data)
        # print(path.split("/"))
        # splitted = path.split("/")
        # db.child(Utils.data_path).child(splitted[2]).child(splitted[3]).update({"code": 0})
        return
    except KeyError:
        return


# Called every <check_database_interval> minute to check the database content
def checkDataBaseInterval():
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
    # Call the function again after <check_database_interval> minutes
    timer.run()


print("=== START ===")
firebase = pyrebase.initialize_app(Constants.config)  # initialize firebase with that config
db = firebase.database()  # get firebase instance object
my_stream = db.stream(stream_handler)  # create a stream for listening to events (update, remove, set)

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
