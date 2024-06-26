import numpy as np
import globals

def distance(pos1, pos2):
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

all_devices = dict()

def discretize_timestamp(orig_ts):
    if globals.TIMESTAMP_GRANULARITY > 0:
        return int(str(orig_ts)[:-globals.TIMESTAMP_GRANULARITY])
    else:
        return orig_ts


def process_devices_events(raw_ds):
    stats_at_timestamp = dict()
    events_at_timestamp = dict()
    total_events = 0
    for obj in raw_ds:
        if obj["eventType"] == "DEVICE_LOCATION_UPDATE":
            total_events += 1
            device_location_update = obj["deviceLocationUpdate"]

            mac = device_location_update["device"]["macAddress"]
            ts = discretize_timestamp(obj["recordTimestamp"])
            employee = device_location_update["deviceClassification"] == "EMPLOYEE"
            if mac not in all_devices:
                id = len(all_devices)
                device_data = {"id": id,
                               "employee": employee,
                               "first_ts": ts,
                               "last_ts": ts}
                all_devices[mac] = device_data
            else:
                id = all_devices[mac]["id"]
                all_devices[mac]["first_ts"] = min(all_devices[mac]["first_ts"], ts)
                all_devices[mac]["last_ts"] = max(all_devices[mac]["last_ts"], ts)
            
            if ts not in stats_at_timestamp:
                stats_at_timestamp[ts] = {"employee_ids": set(), "customer_ids": set()}
            stats_at_timestamp[ts]["employee_ids" if employee else "customer_ids"].add(id)

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

            if ts not in events_at_timestamp:
                events_at_timestamp[ts] = []
            events_at_timestamp[ts].append(obj)

    print(f"{len(events_at_timestamp)}/{total_events}")
    print(f"x: {globals.MIN_X} - {globals.MAX_X}")
    print(f"y: {globals.MIN_Y} - {globals.MAX_Y}")

    events_at_timestamp = dict(sorted(events_at_timestamp.items()))
    stats_at_timestamp = dict(sorted(stats_at_timestamp.items()))

    globals.MINUTES_PER_TIMESTAMP = (globals.END_TIME - globals.START_TIME) * 60 / max(1, len(events_at_timestamp) - 1) 

    return events_at_timestamp, stats_at_timestamp

peak_time = None
off_peak_time = None

customers_until_now = set()
employees_until_now = set()

def calculate_stats_at_timestamp(events_at_timestamp, stats_at_timestamp):
    threshold = 3.0
    connection_matrix = np.zeros((len(all_devices), len(all_devices)), dtype=bool)
    for i, (ts, events) in enumerate(events_at_timestamp.items()):
        for event1 in events:
            pos1 = (event1["deviceLocationUpdate"]["xPos"], event1["deviceLocationUpdate"]["yPos"])
            id1 = all_devices[event1["deviceLocationUpdate"]["device"]["macAddress"]]["id"]
            employee1 = all_devices[event1["deviceLocationUpdate"]["device"]["macAddress"]]["employee"]
            if employee1:
                employees_until_now.add(id1)
            else:
                customers_until_now.add(id1)
            for event2 in events:
                pos2 = (event2["deviceLocationUpdate"]["xPos"], event2["deviceLocationUpdate"]["yPos"])
                id2 = all_devices[event2["deviceLocationUpdate"]["device"]["macAddress"]]["id"]
                employee2 = all_devices[event2["deviceLocationUpdate"]["device"]["macAddress"]]["employee"]
                dist = distance(pos1, pos2)
                if dist <= threshold and employee1 != employee2:
                    connection_matrix[id1][id2] = True
        analyze_connection_matrix(connection_matrix, ts, stats_at_timestamp)
        stats_at_timestamp[ts]["num_employees"] = len(stats_at_timestamp[ts]["employee_ids"])
        num_customers = len(stats_at_timestamp[ts]["customer_ids"])
        stats_at_timestamp[ts]["num_customers"] = num_customers
        stats_at_timestamp[ts]["num_customers_until_now"] = len(customers_until_now)
        stats_at_timestamp[ts]["num_employees_until_now"] = len(employees_until_now)

        global peak_time
        if peak_time is None or peak_time[1] <= num_customers:
            peak_time = (i, num_customers)

        global off_peak_time
        if off_peak_time is None or off_peak_time[1] >= num_customers:
            off_peak_time = (i, num_customers)

        stats_at_timestamp[ts]["peak_time"] = peak_time
        stats_at_timestamp[ts]["off_peak_time"] = off_peak_time

all_durations = list()

def analyze_connection_matrix(connection_matrix, ts, stats_at_timestamp):
    num_approached_customers = 0
    num_active_employees = 0
    for device_data in all_devices.values():
        approached = sum(connection_matrix[device_data["id"]])
        if device_data["employee"]:
            num_active_employees += approached > 0
        else:
            num_approached_customers += approached > 0
            if ts >= device_data["first_ts"]:
                time_spent = min(ts, device_data["last_ts"]) - device_data["first_ts"]
                if time_spent > 0:
                    all_durations.append(time_spent)

    stats_at_timestamp[ts]["approached_customers"] = num_approached_customers
    stats_at_timestamp[ts]["active_employees"] = num_active_employees
    stats_at_timestamp[ts]["avg_time"] = sum(all_durations) / len(all_durations) if len(all_durations) else 0
    

def prepare_devices_data(events_at_timestamp):

    all_data = []

    for events in events_at_timestamp.values():
        df = {"x": list(), "y": list(), "employee": list()}
        for event in events:
            x = int(event["deviceLocationUpdate"]["xPos"])
            y = int(event["deviceLocationUpdate"]["yPos"])
            df["x"].append(x)
            df["y"].append(y)
            df["employee"].append("Employee" if event["deviceLocationUpdate"]["deviceClassification"] == "EMPLOYEE" else "Customer")

        all_data.append(df)

    return all_data