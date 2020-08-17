import pyrebase

import Constants
import Texts
import Utils
from threading import Timer


def stream_handler(message):
    # print(message["event"])  # put
    # print(message["path"])  # /-K7yGTTEp7O549EzTYtI
    # print(message["data"])  # {'title': 'Pyrebase', "body": "etc..."}
    event = message["event"]
    data = message["data"]
    path = message["path"]
    if event == 'put' and data is None and Constants.data_path in path:
        print(Texts.region_deleted_weather_delete % path.split('/')[1])
        db.child(path.replace(Constants.data_path, Constants.weather_path)).remove()
    if data is None:
        return
    try:
        # result = data[Utils.data_path].items()
        # print(Utils.getDataBaseLists(result, db))
        return
    except KeyError:
        pass
    except TypeError:
        pass
    try:
        # print(data)
        # print(path.split("/"))
        # splitted = path.split("/")
        # db.child(Utils.data_path).child(splitted[2]).child(splitted[3]).update({"code": 0})
        return
    except KeyError:
        return


def checkDataBaseInterval():
    data = db.child(Constants.data_path).get().val()
    try:
        result = list(data.items())
    except AttributeError:
        timer.run()
        return
    regions, records = Utils.getDataBaseLists(result, db)
    if regions is None or records is None:
        timer.run()
        return
    try:
        for i in range(len(records)):
            region = regions.__getitem__(i)
            for j in range(len(records.__getitem__(i))):
                record = records.__getitem__(i).__getitem__(j).name
                if Utils.olderThan(record):
                    print(Texts.removing_record % record)
                    db.child(Constants.data_path).child(region).child(record).remove()
                    db.child(Constants.weather_path).child(region).remove()
                    del data[region][record]
                    if not bool(data[region]):
                        del data[region]
        regions, records = Utils.getDataBaseLists(list(data.items()), db)
        weather = Utils.calculateWeatherForEachRegion(regions, records)
        if weather is not None and len(regions) == len(weather):
            for i in range(len(regions)):
                try:
                    print(Texts.updating_weather_for_region % regions[i])
                    db.child(Constants.weather_path).child(regions[i]).set(
                        {'weather': weather[i].weather,
                         'danger': weather[i].danger,
                         'temperature': weather[i].temperature,
                         'humidity': weather[i].humidity,
                         'air': weather[i].air})
                except AttributeError:
                    pass
    except TypeError:
        timer.run()
        return
    except KeyError:
        timer.run()
        return
    timer.run()


firebase = pyrebase.initialize_app(Utils.config)  # initialize firebase with that config
db = firebase.database()  # get firebase instance object
my_stream = db.stream(stream_handler)  # create a stream for listening to events (update, remove, set)

timer = Timer(Constants.check_database_interval, checkDataBaseInterval, args=None, kwargs=None)
timer.start()

# waiting for any key to stop the program and close stream
string = input("Press any key to end!\n")
if len(string) > 0 or string == '':
    my_stream.close()
    timer.cancel()
    print("Finish!")
