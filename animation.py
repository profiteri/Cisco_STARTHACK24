
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.pyplot import imread

# Load the heatmap data
heatmaps = np.load('./multiple_heatmap_data.npy')
background_pic = imread('./test_background.jpg')

# Animation parameters
FRAMES_START = 0
FRAMES_STOP = len(heatmaps)
WRITE = 1
FPS = 40

# Set up the writer for saving the animation
Writer = animation.writers['ffmpeg']
writer = Writer(fps=FPS, bitrate=3600)

# Create the figure with two subplots
fig, ax_left = plt.subplots(figsize=(15, 10))

# Configure the left axis for the heatmap
ax_left.set_title("Pick-frequency heatmap")
ax_left.axis("off")

# Add the background picture to the left axis
im_ax = [ax_left.imshow(background_pic, extent=[0, 200, 0, 100], alpha=0.4, zorder=2)]

# Set the colormap for the heatmap
cmap = plt.cm.YlOrRd
# Add the first heatmap to the list of drawables
im_ax.append(ax_left.imshow(heatmaps[0], extent=[0, 200, 0, 100], alpha=0.99, cmap=cmap, zorder=1))

# Initialize the animation
def init():
    return im_ax

# Define the animation function
def animate(i):
    '''Heatmap'''
    # Remove the previous heatmap before adding a new one
    im_ax[-1].remove()
    im_ax.pop()

    # Add the new heatmap for the current frame
    im_ax.append(ax_left.imshow(heatmaps[i], extent=[0, 200, 0, 100],
                                alpha=0.99, cmap=cmap, zorder=1))

    # Print the current frame index and the length of im_ax for debugging
    prints = "i: " + str(i) + " len_mi_ax: " + str(len(im_ax))
    print(prints)

    return im_ax

# Create the animation object
ani = animation.FuncAnimation(fig, animate, frames=range(FRAMES_START, FRAMES_STOP),
                              blit=True, interval=1, init_func=init,
                              repeat=False)

# Show or save the animation based on the WRITE flag
if WRITE == 0:
    plt.show()
else:
    ani.save('./vids/vid_' + str(WRITE) + '.mp4', writer=writer)
