import globals

def filter_humidity_events(raw_ds):

    events_at_timestamp = dict()
    total_events = 0
    for obj in raw_ds:
        
        if obj["eventType"] != "IOT_TELEMETRY":
            continue

        if "iotTelemetry" not in obj:
            continue

        if "humidity" not in obj["iotTelemetry"]:
            continue

        if "humidityInPercentage" not in obj["iotTelemetry"]["humidity"]:
            continue

        if obj["iotTelemetry"]["humidity"]["humidityInPercentage"] == -1:
            continue

        if "detectedPosition" not in obj["iotTelemetry"]:
            continue

        total_events += 1

        location_update = obj["iotTelemetry"]["detectedPosition"]
        pos_x = location_update["xPos"]
        pos_y = location_update["yPos"]

        if globals.MIN_X == None or globals.MIN_X > pos_x:
            globals.MIN_X = pos_x
        if globals.MAX_X == None or globals.MAX_X < pos_x:
            globals.MAX_X = pos_x
        if globals.MIN_Y == None or globals.MIN_Y > pos_y:
            globals.MIN_Y = pos_y
        if globals.MAX_Y == None or globals.MAX_Y < pos_y:
            globals.MAX_Y = pos_y

        if globals.TIMESTAMP_GRANULARITY > 0:
            ts = int(str(obj["recordTimestamp"])[:-globals.TIMESTAMP_GRANULARITY])
        else:
            ts = obj["recordTimestamp"]
        if ts not in events_at_timestamp:
            events_at_timestamp[ts] = []

        ind = len(events_at_timestamp[ts])
        if ind < len(globals.DEVICES_COORDINATES):
            coord = globals.DEVICES_COORDINATES[ind]
        else:
            ts = globals.best_key(events_at_timestamp)
            if ts == None:
                continue
            if not (ts in events_at_timestamp):
                events_at_timestamp[ts] = []
                coord = globals.DEVICES_COORDINATES[0]
            else:
                coord = globals.DEVICES_COORDINATES[len(events_at_timestamp[ts])]       

        new_obj = dict()
        new_obj["xPos"] = coord[0]
        new_obj["yPos"] = coord[1]
        new_obj["humidity"] = obj["iotTelemetry"]["humidity"]["humidityInPercentage"]

        events_at_timestamp[ts].append(new_obj)

    print(f"humidity: {len(events_at_timestamp)}/{total_events}")
    print(f"x: {globals.MIN_X} - {globals.MAX_X}")
    print(f"y: {globals.MIN_Y} - {globals.MAX_Y}")

    return events_at_timestamp    

def prepare_humidity_data(events_at_timestamp):
    
    all_data = []
    events_at_timestamp = dict(sorted(events_at_timestamp.items()))

    for events in events_at_timestamp.values():
        df = {"x": list(), "y": list(), "Humidity": list()}
        for event in events:
            x = int(event["xPos"])
            y = int(event["yPos"])
            val = int(event["humidity"])
            df["x"].append(x)
            df["y"].append(y)
            df["Humidity"].append(val)

        all_data.append(df)

    return all_data