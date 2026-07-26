from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime
import time

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get("https://realtime.gtfs.de/realtime-free.pb")
feed.ParseFromString(response.content)

len_trip_update = 0
len_trip_descriptor = 0
len_trip_id = 0
missing_entity_id = 0
both = 0
set_entity = set()
set_trip= set()
duplicated_entity_id = 0
duplicated_trip_id = 0
for entity in feed.entity:
    if entity.HasField("trip_update"):
        len_trip_update += 1

        if entity.trip_update.HasField("trip"):
            len_trip_descriptor += 1

        if entity.trip_update.HasField("trip") and entity.trip_update.trip.HasField("trip_id"):
            len_trip_id += 1
            id_trip = entity.trip_update.trip.trip_id
            if id_trip in set_trip:
                duplicated_trip_id +=1 
            else: set_trip.add(entity.trip_update.trip.trip_id)
        if not entity.HasField("id"):
            missing_entity_id += 1
        else :
            if entity.id in set_entity :
                duplicated_entity_id +=1
            else: set_entity.add(entity.id)
        if not entity.HasField("id") and not (entity.trip_update.HasField("trip") and entity.trip_update.trip.HasField("trip_id")):
            both += 1

missing_trip_descriptor = len_trip_update - len_trip_descriptor
missing_trip_id = len_trip_update - len_trip_id

print("total_trip_update: " + str(len_trip_update))
print("trip descriptor present: " + str(len_trip_descriptor))
print("trip ID present: " + str(len_trip_id))
print("missing trip descriptor: " + str(missing_trip_descriptor))
print("missing trip ID: " + str(missing_trip_id))
print("missing entity ID: " + str(missing_entity_id))
print("missing both entity ID and trip ID: " + str(both))
print("duplicated entity ids:" + str(duplicated_entity_id))
print("duplicated trip ids :" + str(duplicated_trip_id))
