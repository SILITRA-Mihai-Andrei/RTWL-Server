import logging

import pyrebase
from datetime import datetime
import time

import Constants
import Machine_learning
import Texts
import Utils

import sys
import threading


def add_input():
    """
    This is a thread that is waiting for user keyboard input.
    The input characters will be inserted into a queue.
    When the user press ENTER ('\n'), all characters inserted will be checked if forms a valid command.
    :return: Nothing.
    """
    command = ""
    print(Texts.ready_for_command)
    # The thread will run continuously until the server is shutting down
    while not stop:
        # Check if the any keyboard key was pressed
        # Put the key in the queue
        cmd = sys.stdin.read(1)
        if cmd == '\n':
            exec_command(command)
            command = ""
        else:
            command += cmd
        time.sleep(0.2)
    print(Texts.thread_closing % Texts.thread_commands)


def stream_handler(message):
    """
    Listener to database - called when database data changed (add, modify, remove)

    :param message: dictionary with 'event', 'data' and 'path' keys
    :return: Nothing

    Example:

    # print(message["event"]) -> put\n
    # print(message["path"]) -> /-data\n
    # print(message["data"]) -> {'temperature': '25', "humidity": "50"}
    """
    # Declare the <checking_data_execution> as external - it is declared in the main body
    global stream_execution
    # Set the variable True - the stream is busy
    stream_execution = True
    # Get the components from the messaged received
    event = message["event"]  # what event happened in database
    data = message["data"]  # what data was changed
    path = message["path"]  # where was the change
    split_path = path.split('/')  # split the path to get the event location

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
        print(Texts.region_deleted_delete_its_data % split_path[len(split_path) - 1])
    # The stream end its execution
    stream_execution = False


def checkDataBaseInterval():
    """
    Check the database content: add to database new calculated weather data, remove the old records.
    :return: Nothing
    """
    # Declare the <checking_data_execution> as external - it is declared in the main body
    global checking_data_execution

    # The thread will run continuously until the server is shutting down
    while not stop:
        # Set variable to True - the function started its execution
        # This is used when the server is closing, the variable will tell the function to wait until this function ends
        checking_data_execution = True

        print(Texts.checking_database % datetime.now().strftime("%H:%M:%S"))
        # Get database data as dictionary
        data = db.child(Constants.data_path).get().val()
        # There is no data in database or something was wrong in receiving data
        if data is None:
            print(Texts.no_database_data)
        else:
            # Convert the received database data to a list
            result = Utils.convertToList(data)
            # Check if the dictionary->list conversion was successful
            if result:
                # Check the data and write to database if needed
                checkAndWriteData(result, data)
        # End the procedure
        print(Texts.string_done)
        # Set variable to False - the function ended its execution
        checking_data_execution = False
        time.sleep(Constants.check_database_interval)
    print(Texts.thread_closing % Texts.thread_checking_database)


def checkAndWriteData(data_list, data):
    """
    Check the data from database:
    -- remove old records;
    -- calculate the weather condition for each region using their records;
    -- update new weather data for each region;
    -- delete regions that have no records.
    :param data_list: is the data as list.
    :param data: is the data that will checked.
    :return: Nothing.
    """
    # Get database dictionary as two list of regions and records
    regions, records = Utils.getDataBaseLists(data_list, db)
    # No valid regions or records received from database
    if regions is None or records is None:
        print(Texts.invalid_database_data)
        return
    # If received valid data from database - check all data
    try:
        # Check database data
        records = Utils.checkDataBaseData(db, records, regions, data)
        # Write the new records to Machine Learning dataframe
        Utils.writeRecordsInDataframe(records)
    # If something goes wrong
    except (TypeError, KeyError) as err:
        # Write the exception in logging
        logging.exception(str(err))


def closeServer():
    """
    When the user press any key or the specific commands, the server will start the stop process.
    - Closing the FireBase stream - the listener that triggers to any event in database.
    - Closing the checking database thread - this one call the <checkDataBaseInterval()> function every
        <Constants.check_database_interval> to check the database content.
    - Saving the machine learning dataframe to a <Constants.cvs_local> file - dataframe is what the server learned and
        it is used in machine learning functions (predictions, calculating the mean values, etc).
    """
    global stop
    # Update the variable that notify all functions and threads that the server is shutting down
    stop = True
    # The Firebase stream or the timer is in execution - wait until execution is done
    if stream_execution is True or checking_data_execution is True:
        # Create timer - call function (parameter 2) after a time (parameter 1)
        # This timer will be used to recall this function when all execution methods are done
        close_timer = threading.Timer(Constants.check_closing_server_interval, closeServer, args=None, kwargs=None)
        # The timer is not started - first call
        if not close_timer.is_alive():
            # Start the timer - call the function after specified time
            close_timer.start()
        else:
            # The timer is started - run again until the Firebase stream and timer execution is done
            close_timer.run()
    else:
        print(Texts.start_stop_server)
        print(Texts.stream_closing, end='')
        # Closing the FireBase stream - the listener that triggers to any event in database.
        my_stream.close()
        print(Texts.string_done)
        print(Texts.saving_machine_learning_dataframe % Constants.cvs_local, end='')
        # Get the updated dataframe from <Machine_learning.py>
        dataframe = Machine_learning.dataFrame
        # Saving the machine learning dataframe to a <Constants.cvs_local> file - dataframe is what the server
        # learned and it is used in machine learning functions (predictions, calculating the mean values, etc).
        dataframe.to_csv(Constants.cvs_local, index=False)
        print(Texts.string_done)
        print("=== END ===")
        return


def exec_command(_command):
    print(Texts.processing_command)
    if _command is None:
        print(Texts.ready_for_command)
        return
    if _command == 's' or _command == 'stop':
        # Close safety the server
        closeServer()
        return
    elif _command == 't' or _command == 'test':
        # Write test data in database
        print(Texts.writing_test_data_to_database, end='')
        db.child(Constants.data_path).set(Constants.get_data_test())
        print(Texts.string_done)
    else:
        print(Texts.invalid_command)
    print(Texts.ready_for_command)


print("=== START ===")
# This variable is True when the server is shutting down
stop = False
# Variable that indicates the stream is executing the function
stream_execution = False
# Variable that indicates the timer is executing the function
checking_data_execution = False

# Initialize the Firebase components
firebase = pyrebase.initialize_app(Constants.config)    # initialize firebase with that config
db = firebase.database()                                # get firebase instance object
my_stream = db.stream(stream_handler)                   # create a stream for listening to events (update, remove, set)

# Create the thread that will listen to keyboard keys and store them as a potential command
input_thread = threading.Thread(target=add_input)
# Make the thread daemon - clear all resources after thread finish execution
input_thread.daemon = True

# Create the thread that will check the database content
checking_thread = threading.Thread(target=checkDataBaseInterval)

# Start all threads
input_thread.start()
checking_thread.start()
