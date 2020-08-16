import pyrebase
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
    if event == 'put' and data is None and Utils.data_path in path:
        db.child(path.replace(Utils.data_path, Utils.weather_path)).remove()
    if data is None:
        return
    try:
        result = data[Utils.data_path].items()
        print(Utils.getDataBaseLists(result, db))
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
    data = db.child(Utils.data_path).get().val()
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
                    db.child(Utils.data_path).child(region).child(record).remove()
                    db.child(Utils.weather_path).child(region).remove()
                    del data[region][record]
                    if not bool(data[region]):
                        del data[region]
        regions, records = Utils.getDataBaseLists(list(data.items()), db)
        regions_weather, regions_danger = Utils.calculateWeatherForEachRegion(regions, records)
        if regions_weather is not None and regions_danger is not None \
                and len(regions) == len(regions_weather) and len(regions) == len(regions_danger):
            for i in range(len(regions)):
                try:
                    db.child(Utils.weather_path).child(regions[i]).child(Utils.getTime()).set(
                        {'weather': regions_weather[i], 'danger': str(regions_danger[i])})
                    current_record = next(iter(db.child(Utils.weather_path).child(regions[i]).get().val()))
                    if current_record is not None and current_record != Utils.getTime():
                        db.child(Utils.weather_path).child(regions[i]).child(current_record).remove()
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

timer = Timer(Utils.check_database_interval, checkDataBaseInterval, args=None, kwargs=None)
timer.start()

# waiting for any key to stop the program and close stream
string = input("Press any key to end!\n")
if len(string) > 0 or string == '':
    my_stream.close()
    timer.cancel()
    print("Finish!")
