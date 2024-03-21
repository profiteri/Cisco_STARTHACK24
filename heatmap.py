import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
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
        if min_x is None or min_x > pos_x:
            min_x = pos_x

        if max_x is None or max_x < pos_x:
            max_x = pos_x

        if min_y is None or min_y > pos_y:
            min_y = pos_y

        if max_y is None or max_y < pos_y:
            max_y = pos_y

        ts = obj["recordTimestamp"] // (10 ** timestamp_granularity) if timestamp_granularity > 0 else obj["recordTimestamp"]
        events_at_timestamp.setdefault(ts, []).append(obj)

print(f"{len(events_at_timestamp)}/{total_events}")
print(f"x: {min_x} - {max_x}")
print(f"y: {min_y} - {max_y}")

from matplotlib.widgets import Slider

all_data = []

events_at_timestamp = dict(sorted(events_at_timestamp.items()))

for events in events_at_timestamp.values():
    df = {"x": [], "y": []}
    for event in events:
        x = event["deviceLocationUpdate"]["xPos"]
        y = event["deviceLocationUpdate"]["yPos"]
        df["x"].append(x)
        df["y"].append(y)
    all_data.append(df)

# Create the initial figure and axis
fig, ax = plt.subplots()
current_index = 0

bg_image = plt.imread('test_background.png')

# Plot the background image
ax.imshow(bg_image,
           aspect='auto',
           extent=[min_x, max_x, min_y, max_y])

# Plot the initial KDE plot
kde_plot = sns.kdeplot(data=all_data[current_index], x="x", y="y", cmap="Reds", fill=True, alpha=0.4, ax=ax)

ax.axis('off')

# Set the limits for the x and y axes to prevent the graph from changing height
ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)

# Add a slider for timeline navigation
ax_slider = plt.axes([0.2, 0.05, 0.65, 0.03])  # [left, bottom, width, height]
slider = Slider(ax_slider, 'Timeline', 0, len(all_data) - 1, valinit=0, valstep=1)

# Update function for slider
def update(val):
    global current_index
    current_index = int(slider.val)
    # Remove only the KDE plot, not the background image
    for artist in ax.collections:
        artist.remove()
    # Plot the KDE plot without clearing the background image
    sns.kdeplot(data=all_data[current_index], x="x", y="y", cmap="Reds", fill=True, alpha=0.4, ax=ax)
    # Ensure the x and y limits remain the same after updating the plot
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    plt.draw()

slider.on_changed(update)

plt.show()