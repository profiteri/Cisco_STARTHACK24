import numpy as np
import globals

# Function to calculate the Euclidean distance between two points
def distance(pos1, pos2):
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

all_devices = dict()

def process_devices_events(raw_ds):
    
    events_at_timestamp = dict()
    total_events = 0
    for obj in raw_ds:
        if obj["eventType"] == "DEVICE_LOCATION_UPDATE":
            total_events += 1
            device_location_update = obj["deviceLocationUpdate"]

            mac = device_location_update["device"]["macAddress"]
            if mac not in all_devices:
                all_devices[mac] = (len(all_devices), device_location_update["deviceClassification"] == "EMPLOYEE")

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

def build_connection_matrix(events_at_timestamp):
    threshold = 2.0
    connection_matrix = np.zeros((len(all_devices), len(all_devices)), dtype=bool)
    for events in events_at_timestamp.values():
        for event1 in events:
            pos1 = (event1["deviceLocationUpdate"]["xPos"], event1["deviceLocationUpdate"]["yPos"])
            id1 = all_devices[event1["deviceLocationUpdate"]["device"]["macAddress"]][0]
            for event2 in events:
                pos2 = (event2["deviceLocationUpdate"]["xPos"], event2["deviceLocationUpdate"]["yPos"])
                id2 = all_devices[event2["deviceLocationUpdate"]["device"]["macAddress"]][0]
                dist = distance(pos1, pos2)
                if dist <= threshold and id1 != id2:
                    connection_matrix[id1][id2] = True
    return connection_matrix


def analyze_connection_matrix(connection_matrix):
    num_devices = len(all_devices)
    num_employees = sum(employee for (_, employee) in all_devices.values() if employee)
    num_approached_customers = 0
    for (id, employee) in all_devices.values():
        if employee:
            continue
        approached = sum(connection_matrix[id])
        num_approached_customers += approached > 0

    print(f"Total employees: {num_employees}")
    total_customers = num_devices - num_employees
    print(f"Total customers: {total_customers}")
    print(f"Approached customers: {num_approached_customers} => {num_approached_customers / (total_customers) * 100}%")
    
    
def prepare_devices_data(events_at_timestamp):

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