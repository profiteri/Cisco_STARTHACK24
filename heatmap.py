import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
import os
import json
from matplotlib.widgets import Slider

TIMESTAMP_GRANULARITY = 5
LOCATION_PRECISION = 50

HEATMAP_SELECTED = True 
ILLUMINOCITY_SELECTED = False
HUMIDITY_SELECTED = False
USERS_TRACKING_SELECTED = False

MIN_X = MAX_X = MIN_Y = MAX_Y = 0

def load_dataset():

    filename = os.path.join("logs_short.json")
    with open(filename, 'r') as file:
        json_list = json.load(file)
        return json_list

def filter_events(raw_ds, event_type):

    global TIMESTAMP_GRANULARITY

    global MIN_X
    global MAX_X
    global MIN_Y
    global MAX_Y

    events_at_timestamp = dict()
    total_events = 0
    for obj in raw_ds:
        if obj["eventType"] == event_type:
            total_events += 1
            device_location_update = obj["deviceLocationUpdate"]
            pos_x = device_location_update["xPos"]
            pos_y = device_location_update["yPos"]
            
            if MIN_X == None or MIN_X > pos_x:
                MIN_X = pos_x
            if MAX_X == None or MAX_X < pos_x:
                MAX_X = pos_x
            if MIN_Y == None or MIN_Y > pos_y:
                MIN_Y = pos_y
            if MAX_Y == None or MAX_Y < pos_y:
                MAX_Y = pos_y

            if TIMESTAMP_GRANULARITY > 0:
                ts = int(str(obj["recordTimestamp"])[:-TIMESTAMP_GRANULARITY])
            else:
                ts = obj["recordTimestamp"]
            if ts not in events_at_timestamp:
                events_at_timestamp[ts] = []
            events_at_timestamp[ts].append(obj)

    print(f"{len(events_at_timestamp)}/{total_events}")
    print(f"x: {MIN_X} - {MAX_X}")
    print(f"y: {MIN_Y} - {MAX_Y}")

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

def draw_kdeplot(all_data):
    return sns.kdeplot(data=all_data[current_index], x="x", y="y", bw_adjust=0.2, cmap="Reds", fill=True, alpha=0.4, ax=ax)

def initialize_heatmap(all_data, ax, bg_image):

    current_index = 0

    # Plot the background image
    ax.imshow(bg_image,
            aspect='auto',
            extent=[MIN_X, MAX_X, MIN_Y, MAX_Y])

    # Plot the initial KDE plot
    draw_kdeplot(all_data)
    ax.axis('off')

# Prepare generic data
raw_ds              = load_dataset()
events_at_timestamp = filter_events(raw_ds, "DEVICE_LOCATION_UPDATE")

# Prepare heatmap data
global all_heatmap_data
all_heatmap_data    = prepare_heatmap_data(events_at_timestamp)

# Prepare illumisocity data
# ...

# Create the initial figure and axis
fig, ax = plt.subplots()
current_index = 0

# Set the limits for the x and y axes to prevent the graph from changing height
ax.set_xlim(MIN_X, MAX_X)
ax.set_ylim(MIN_Y, MAX_Y)

# Load bq image
bg_image = plt.imread('test_background.png')

initialize_heatmap(all_heatmap_data, ax, bg_image)
#initialize_illumisocity
#initialize_humidity

# Add a slider for timeline navigation
ax_slider = plt.axes([0.2, 0.05, 0.65, 0.03])  # [left, bottom, width, height]
slider = Slider(ax_slider, 'Timeline', 0, len(all_heatmap_data) - 1, valinit=0, valstep=1)

# Update function for slider
def update(val):

    if HEATMAP_SELECTED == True:
        global current_index
        current_index = int(slider.val)

        # Remove only the KDE plot, not the background image
        for artist in ax.collections:
            artist.remove()        
            
        # Plot the KDE plot without clearing the background image
        draw_kdeplot(all_heatmap_data)
        
        # Ensure the x and y limits remain the same after updating the plot
        ax.set_xlim(MIN_X, MAX_X)
        ax.set_ylim(MIN_Y, MAX_Y)
        plt.draw()

slider.on_changed(update)

plt.show()