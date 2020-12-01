import logging

import pyrebase
from datetime import datetime

import Constants
import Machine_learning
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
    # Declare the <timer_execution> as external - it is declared in the main body
    global stream_execution
    # Set the variable True - the stream is busy
    stream_execution = True

    event = message["event"]
    data = message["data"]
    path = message["path"]
    split_path = path.split('/')
    # Check if a region was deleted from 'data' node in database (event = put and data is None)
    if event == 'put' and data is None and Constants.data_path in path and len(split_path) == 3:
        # If region was deleted
        # Delete the region from 'weather' node
        db.child(path.replace(Constants.data_path, Constants.weather_path)).remove()
        # Delete the region from 'dangers' node
        db.child(path.replace(Constants.data_path, Constants.danger_path)).remove()
        # Delete the region from 'predictions' node
        db.child(path.replace(Constants.data_path, Constants.predictions_path)).remove()
        # Print a message on terminal
        print(Texts.region_deleted_delete_its_data % split_path[2])
    # The stream end its execution
    stream_execution = False


def endTimerFunction():
    print(Texts.string_done)
    # Declare the <timer_execution> as external - it is declared in the main body
    global timer_execution
    timer_execution = False
    # Restart timer to call the function again after specified time
    timer.run()


def checkDataBaseInterval():
    """
    Called every <Utils.check_database_interval> second to check the database content

    time.run() will recall this function after <Constants.check_database_interval> seconds. This will throw
    <RecursionError> exception, which is handled by <Utils.handleRecursionError()> function

    :return: Nothing
    """
    # Declare the <timer_execution> as external - it is declared in the main body
    global timer_execution
    # Set variable to True - timer called this function
    timer_execution = True

    print(Texts.checking_database % datetime.now().strftime("%H:%M:%S"))
    # Get database data as dictionary
    data = db.child(Constants.data_path).get().val()
    # There is no data in database or something was wrong in receiving data
    if data is None:
        print(Texts.no_database_data)
        endTimerFunction()
        return
    # Declare result list, where database dictionary is converted to a list
    result = []
    # If there is any exception
    exception = False
    try:
        # Create a list from database data dictionary
        result = list(data.items())
    except RecursionError as err:
        # Write the exception in logging
        logging.exception(str(err))
        # The callback stack is full - timer called this function too many times and now must return something
        Utils.handleRecursionError(timer, my_stream)
        exception = True
    except Exception as err:
        print(err)
        # Write the exception in logging
        logging.exception(str(err))
        # If any kind of exception appear
        exception = True
    # There was an exception or the result list is empty
    if exception is True or not result:
        # There is nothing else to do
        endTimerFunction()
        return
    # Get database dictionary as two list of regions and records
    regions, records = Utils.getDataBaseLists(result, db)
    # No valid regions or records received from database
    if regions is None or records is None:
        print(Texts.invalid_database_data)
        endTimerFunction()
        return
    # If received valid data from database - check all data
    try:
        # Check database data
        Utils.checkDataBaseData(db, records, regions, data)
    # If something goes wrong
    except (TypeError, KeyError) as err:
        # Write the exception in logging
        logging.exception(str(err))
    endTimerFunction()
    return


def closeServer():
    """
    When the user press any key or the specific commands, the server will start the stop process.
    - Closing the FireBase stream - the listener that triggers to any event in database.
    - Closing the timer thread - this one call the <checkDataBaseInterval()> function every
        <Constants.check_database_interval> to check the database content.
    - Saving the machine learning dataframe to a <Constants.cvs_local> file - dataframe is what the server learned and
        it is used in machine learning functions (predictions, calculating the mean values, etc).
    """
    # Create timer - call function (parameter 2) after a time (parameter 1)
    close_server_timer = Timer(Constants.check_for_closing_server_interval, closeServer, args=None, kwargs=None)
    # The Firebase stream or the timer is in execution - wait until execution is done
    if stream_execution is True or timer_execution is True:
        # The timer is not started - first call
        if not close_server_timer.is_alive():
            # Start the timer - call the function after specified time
            close_server_timer.start()
        else:
            # The timer is started - run again until the Firebase stream and timer execution is done
            close_server_timer.run()
    else:
        print(Texts.start_stop_server)
        print(Texts.stream_closing, end='')
        # Closing the FireBase stream - the listener that triggers to any event in database.
        my_stream.close()
        print(Texts.string_done)
        print(Texts.timer_closing, end='')
        # Closing the timer thread - this one call the <checkDataBaseInterval()> function every
        # <Constants.check_database_interval> to check the database content.
        timer.cancel()
        print(Texts.string_done)
        print(Texts.saving_machine_learning_dataframe % Constants.cvs_local, end='')
        # Saving the machine learning dataframe to a <Constants.cvs_local> file - dataframe is what the server
        # learned and it is used in machine learning functions (predictions, calculating the mean values, etc).
        Machine_learning.dataFrame.to_csv(Constants.cvs_local, index=False)
        print(Texts.string_done)
        print("=== END ===")
        return


def exec_command():
    string = None
    if string is None:
        # Waiting for any key to stop the program and close stream
        string = input("Ready to read command.\n")
    if string == 's' or string == 'stop':
        closeServer()
        return
    elif len(string) > 0:
        if string == 't' or string == 'test':
            # Write test data in database
            print(Texts.writing_test_data_to_database, end='')
            db.child(Constants.data_path).set(Constants.data_test)
            print(Texts.string_done)
    else:
        print(Texts.invalid_command)
    exec_command()


print("=== START ===")
# Variable that indicates the stream is executing the function
stream_execution = False
# Variable that indicates the timer is executing the function
timer_execution = False
firebase = pyrebase.initialize_app(Constants.config)  # initialize firebase with that config
db = firebase.database()  # Get firebase instance object
my_stream = db.stream(stream_handler)  # Create a stream for listening to events (update, remove, set)

# Create timer - call function (parameter 2) after a time (parameter 1)
timer = Timer(Constants.check_database_interval, checkDataBaseInterval, args=None, kwargs=None)
# Start the timer
timer.start()

exec_command()
