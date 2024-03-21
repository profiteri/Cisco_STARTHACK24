def init():
    global TIMESTAMP_GRANULARITY
    global LOCATION_PRECISION
    global HEATMAP_SELECTED
    global ILLUMINOCITY_SELECTED
    global HUMIDITY_SELECTED
    global USERS_TRACKING_SELECTED
    global MIN_X
    global MAX_X
    global MIN_Y
    global MAX_Y
    global HUMIDITY_INITIALIZED

    TIMESTAMP_GRANULARITY = 5
    LOCATION_PRECISION = 50

    HUMIDITY_INITIALIZED = False

    MIN_X = MAX_X = MIN_Y = MAX_Y = 0