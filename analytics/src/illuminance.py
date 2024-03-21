import globals
def filter_illuminance_events(raw_ds):

    events_at_timestamp = dict()
    total_events = 0
    for obj in raw_ds:
        
        if obj["eventType"] != "IOT_TELEMETRY":
            continue

        if "iotTelemetry" not in obj:
            continue

        if "illuminance" not in obj["iotTelemetry"]:
            continue

        if "detectedPosition" not in obj["iotTelemetry"]:
            continue

        total_events += 1

        location_update = obj["iotTelemetry"]["detectedPosition"]
        pos_x = location_update["xPos"]
        pos_y = location_update["yPos"]

        new_obj = dict()
        new_obj["xPos"] = pos_x
        new_obj["yPos"] = pos_y
        new_obj["illuminance"] = obj["iotTelemetry"]["illuminance"]

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
        events_at_timestamp[ts].append(new_obj)

    print(f"illuminance: {len(events_at_timestamp)}/{total_events}")
    print(f"x: {globals.MIN_X} - {globals.MAX_X}")
    print(f"y: {globals.MIN_Y} - {globals.MAX_Y}")

    return events_at_timestamp    


def prepare_illuminance_data(events_at_timestamp):
    all_data = []
    events_at_timestamp = dict(sorted(events_at_timestamp.items()))
    for events in events_at_timestamp.values():
        df = {"x": list(), "y": list(), "illuminance": list()}
        for event in events:
            x = int(event["xPos"])
            y = int(event["yPos"])
            val = int(event["illuminance"]['value'])
            df["x"].append(x)
            df["y"].append(y)
            df["illuminance"].append(val)

        all_data.append(df)

    return all_data