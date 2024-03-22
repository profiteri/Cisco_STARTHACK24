import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import time
from threading import Lock

MAX_X = 100
MIN_X = 0
MAX_Y = 100
MIN_Y = 0

coord_red   = [-1, -1]
coord_blue  = [-1, -1]

cashier_one = [85, 60]
cashier_two = [85, 40]

lock = Lock()

def get_closer_to_first():
    lock.acquire()
    dx_red = cashier_one[0] - coord_red[0]
    dy_red = cashier_one[1] - coord_red[1]
    d_red = dx_red * dx_red + dy_red * dy_red
    dx_blue = cashier_one[0] - coord_blue[0]
    dy_blue = cashier_one[1] - coord_blue[1]    
    d_blue = dx_blue * dx_blue + dy_blue * dy_blue
    lock.release()
    if d_red <= d_blue:
        return "red"
    else:
        return "blue"

def get_closer_to_second():
    lock.acquire()
    dx_red = cashier_two[0] - coord_red[0]
    dy_red = cashier_two[1] - coord_red[1]
    d_red = dx_red * dx_red + dy_red * dy_red
    dx_blue = cashier_two[0] - coord_blue[0]
    dy_blue = cashier_two[1] - coord_blue[1]    
    d_blue = dx_blue * dx_blue + dy_blue * dy_blue    
    lock.release()
    if d_red <= d_blue:
        return "red"
    else:
        return "blue"    

def walk():

    global coord_red
    global coord_blue
    global lock

    # Create the initial figure and axis
    fig, ax = plt.subplots()

    # Load bg image
    bg_image = plt.imread('transactions/data/store4.png')

    # Plot the background image
    ax.imshow(bg_image,
            aspect='auto',
            extent=[MIN_X, MAX_X, MIN_Y, MAX_Y])
    #ax.axis('off')

    # Set the limits for the x and y axes to prevent the graph from changing height
    ax.set_xlim(MIN_X, MAX_X)
    ax.set_ylim(MIN_Y, MAX_Y)

    traqectory_up   = [ [83, 36], [82, 38], [81, 40], [80, 42], [80, 44], [80, 45], [80, 46], [80, 47], [80, 48], [80, 49], [80, 50],
                        [80, 51], [80, 52], [80, 53], [80, 54], [79, 55], [80, 56], [81, 57], [82, 58], [83, 59], [83, 60] ]

    traqectory_down = [ [83, 60], [82, 59], [81, 58], [78, 57], [75, 56], [72, 55], [69, 52], [68, 49], [66, 45], [66, 42], [66, 39],
                        [66, 36], [66, 33], [66, 30], [68, 27], [72, 27], [76, 27], [80, 30], [81, 33], [82, 35], [83, 36] ]

    sns.scatterplot(x=[83], y=[40], color="blue", ax=ax)

    plt.ion()
    plt.show()

    while True:

        for i in range(len(traqectory_up)):
            for artist in ax.collections:
                artist.remove()
            sns.scatterplot(x=[traqectory_up[i][0]], y=[traqectory_up[i][1]], color="blue", ax=ax)
            sns.scatterplot(x=[traqectory_down[i][0]], y=[traqectory_down[i][1]], color="red", ax=ax)
            plt.draw()
            plt.pause(0.001)
            lock.acquire()
            coord_red = traqectory_down[i]
            coord_blue = traqectory_up[i]
            lock.release()
            time.sleep(0.2)

        for i in range(len(traqectory_up)):
            for artist in ax.collections:
                artist.remove()
            sns.scatterplot(x=[traqectory_down[i][0]], y=[traqectory_down[i][1]], color="blue", ax=ax)
            sns.scatterplot(x=[traqectory_up[i][0]], y=[traqectory_up[i][1]], color="red", ax=ax)
            plt.draw()
            plt.pause(0.001)
            lock.acquire()
            coord_blue = traqectory_down[i]
            coord_red = traqectory_up[i]
            lock.release()            
            time.sleep(0.2)

if __name__ == "__main__":
    walk()