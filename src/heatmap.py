import globals

def filter_heatmap_events(raw_ds):

    events_at_timestamp = dict()
    total_events = 0
    for obj in raw_ds:
        if obj["eventType"] == "DEVICE_LOCATION_UPDATE":
            total_events += 1
            device_location_update = obj["deviceLocationUpdate"]
            pos_x = device_location_update["xPos"]
            pos_y = device_location_update["yPos"]
            
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
            events_at_timestamp[ts].append(obj)

    print(f"{len(events_at_timestamp)}/{total_events}")
    print(f"x: {globals.MIN_X} - {globals.MAX_X}")
    print(f"y: {globals.MIN_Y} - {globals.MAX_Y}")

    return events_at_timestamp

def prepare_heatmap_data(events_at_timestamp):

    all_data = []
    events_at_timestamp = dict(sorted(events_at_timestamp.items()))

    for events in events_at_timestamp.values():
        df = {"x": list(), "y": list()}
        for event in events:
            x = int(event["deviceLocationUpdate"]["xPos"])
            y = int(event["deviceLocationUpdate"]["yPos"])
            df["x"].append(x)
            df["y"].append(y)

        all_data.append(df)

    return all_data
