import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
import os
import json

filename = os.path.join("logs.json")

with open(filename, 'r') as file:
    json_list = json.load(file)

timestamp_granularity = 5

min_x = None
max_x = None
min_y = None
max_y = None

events_at_timestamp = dict()
total_events = 0
for obj in json_list:
    if obj["eventType"] == "DEVICE_LOCATION_UPDATE":
        total_events += 1
        device_location_update = obj["deviceLocationUpdate"]
        pos_x = device_location_update["xPos"]
        pos_y = device_location_update["yPos"]
        if min_x == None or min_x > pos_x:
            min_x = pos_x

        if max_x == None or max_x < pos_x:
            max_x = pos_x

        if min_y == None or min_y > pos_y:
            min_y = pos_y

        if max_y == None or max_y < pos_y:
            max_y = pos_y

        if timestamp_granularity > 0:
            ts = int(str(obj["recordTimestamp"])[:-timestamp_granularity])
        else:
            ts = obj["recordTimestamp"]
        if ts not in events_at_timestamp:
            events_at_timestamp[ts] = []
        events_at_timestamp[ts].append(obj)

print(f"{len(events_at_timestamp)}/{total_events}")
print(f"x: {min_x} - {max_x}")
print(f"y: {min_y} - {max_y}")

from matplotlib.widgets import Slider

location_precision = 50

all_data = []

for events in list(events_at_timestamp.values())[:10]:
    # data = np.zeros((int(max_x) // location_precision + 1, int(max_y) // location_precision + 1))
    df = {"x": list(), "y": list()}
    for event in events:
        x = int(event["deviceLocationUpdate"]["xPos"]) // location_precision
        y = int(event["deviceLocationUpdate"]["yPos"]) // location_precision
        df["x"].append(x)
        df["y"].append(y)

    # data = np.where(data == 0, np.nan, data)

    all_data.append(df)

# Create the initial figure and axis
fig, ax = plt.subplots()
current_index = 0

bg_image = plt.imread('test_background.png')

# Plot the background image
ax.imshow(bg_image,
           aspect='auto',
           extent=[int(min_x) // location_precision,
                   int(max_x) // location_precision,
                   int(min_y) // location_precision,
                   int(max_y) // location_precision])

# Plot the initial KDE plot
kde_plot = sns.kdeplot(data=all_data[current_index], x="x", y="y", cmap="Reds", fill=True, alpha=0.4, ax=ax)

# Add a slider for timeline navigation
ax_slider = plt.axes([0.2, 0.05, 0.65, 0.03])  # [left, bottom, width, height]
slider = Slider(ax_slider, 'Timeline', 0, len(all_data) - 1, valinit=0, valstep=1)

# Update function for slider
def update(val):
    global current_index
    current_index = int(slider.val)
    ax.clear()
    ax.imshow(bg_image,
               aspect='auto',
               extent=[int(min_x) // location_precision,
                       int(max_x) // location_precision,
                       int(min_y) // location_precision,
                       int(max_y) // location_precision])
    sns.kdeplot(data=all_data[current_index], x="x", y="y", cmap="Reds", fill=True, alpha=0.4, ax=ax)
    plt.draw()

slider.on_changed(update)

plt.show()