import threading
from firebase import firebase

link = 'https://real-time-weather-location.firebaseio.com/'
data = 'data'
firebase = firebase.FirebaseApplication(link + data, None)
result = firebase.get(data, None)  # get all data from "data" branch
print(result)

data = dict(result)  # save result as dictionary (for manipulation)

# initialize variable with empty list
regions = []
records = []
collections = []
for reg, rec in data.items():  # for each region in data base
    regions.append(reg)  # add region name to list
    # create new list - each region has one or more records
    # each record has a data dictionary
    recList = []
    dataList = []
    for recName, recData in rec.items():
        recList.append(recName)
        dataList.append(recData)
    collections.append(dataList)
    records.append(recList)

print(">1>", regions)
print(">2>", records)
print(">3>", collections)
