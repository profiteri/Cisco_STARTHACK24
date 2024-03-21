import matplotlib.pyplot as plt

# Create the initial figure and axis
fig, ax = plt.subplots()

# Load bg image
bg_image = plt.imread('../data/test_background.png')

# Plot the background image
ax.imshow(bg_image,
        aspect='auto',
        extent=[globals.MIN_X, globals.MAX_X, globals.MIN_Y, globals.MAX_Y])
ax.axis('off')

# Set the limits for the x and y axes to prevent the graph from changing height
ax.set_xlim(globals.MIN_X, globals.MAX_X)
ax.set_ylim(globals.MIN_Y, globals.MAX_Y)