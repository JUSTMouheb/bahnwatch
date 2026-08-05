from datetime import datetime, timezone

import requests
from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2


FEED_URL = "https://realtime.gtfs.de/realtime-free.pb"
REQUEST_TIMEOUT_SECONDS = 10


def download_feed():
    try:
        response = requests.get(
            FEED_URL,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("Request timed out")
        return None

    except requests.exceptions.ConnectionError:
        print("Connection error")
        return None

    except requests.exceptions.HTTPError as error:
        print("HTTP error:", error)
        return None

    if not response.content:
        print("Empty response")
        return None

    feed = gtfs_realtime_pb2.FeedMessage()

    try:
        feed.ParseFromString(response.content)
    except DecodeError as error:
        print("Protobuf decoding failed:", error)
        return None

    return feed


def get_entity_type(entity):
    if entity.HasField("trip_update"):
        return "trip_update"

    if entity.HasField("vehicle"):
        return "vehicle"

    if entity.HasField("alert"):
        return "alert"

    return "unknown"


def print_stop_time_event(name, event):
    print(f"{name} information:")

    if event.HasField("delay"):
        print("  Delay:", event.delay)
    else:
        print("  Delay: not provided")

    if event.HasField("time"):
        readable_time = datetime.fromtimestamp(
            event.time,
            tz=timezone.utc,
        )

        print("  Timestamp:", event.time)
        print("  UTC time:", readable_time)
    else:
        print("  Time: not provided")

    if event.HasField("uncertainty"):
        print("  Uncertainty:", event.uncertainty)
    else:
        print("  Uncertainty: not provided")


def inspect_first_entity(feed):
    print("Feed parsed successfully")
    print("GTFS-Realtime version:", feed.header.gtfs_realtime_version)

    if feed.header.HasField("timestamp"):
        feed_time = datetime.fromtimestamp(
            feed.header.timestamp,
            tz=timezone.utc,
        )

        print("Feed timestamp:", feed.header.timestamp)
        print("Feed time in UTC:", feed_time)
    else:
        print("Feed timestamp: not provided")

    print("Number of entities:", len(feed.entity))

    if not feed.entity:
        print("The feed contains no entities")
        return

    entity = feed.entity[0]
    serialized_entity = entity.SerializeToString()
    entity_type = get_entity_type(entity)
    print(type(serialized_entity))
    print("\nFirst entity")
    print("Entity ID:", entity.id)
    print("Entity type:", entity_type)

    if entity_type != "trip_update":
        print("The first entity is not a trip update")
        return

    trip_update = entity.trip_update
    trip = trip_update.trip

    print("Trip ID:", trip.trip_id)

    if trip.HasField("start_date"):
        print("Start date:", trip.start_date)
    else:
        print("Start date: not provided")

    if trip_update.HasField("timestamp"):
        print("Trip-update timestamp:", trip_update.timestamp)
    else:
        print("Trip-update timestamp: not provided")

    print(
        "Number of stop-time updates:",
        len(trip_update.stop_time_update),
    )

    if not trip_update.stop_time_update:
        print("This trip contains no stop-time updates")
        return

    first_stop_update = trip_update.stop_time_update[0]

    print("\nFirst stop-time update")

    if first_stop_update.HasField("stop_id"):
        print("Stop ID:", first_stop_update.stop_id)
    else:
        print("Stop ID: not provided")

    if first_stop_update.HasField("stop_sequence"):
        print("Stop sequence:", first_stop_update.stop_sequence)
    else:
        print("Stop sequence: not provided")

    if first_stop_update.HasField("arrival"):
        print_stop_time_event(
            "Arrival",
            first_stop_update.arrival,
        )
    else:
        print("Arrival information: not provided")

    if first_stop_update.HasField("departure"):
        print_stop_time_event(
            "Departure",
            first_stop_update.departure,
        )
    else:
        print("Departure information: not provided")


def main():
    feed = download_feed()

    if feed is None:
        return

    inspect_first_entity(feed)


if __name__ == "__main__":
    main()