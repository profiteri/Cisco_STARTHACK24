def init():
    global TIMESTAMP_GRANULARITY
    global MIN_X
    global MAX_X
    global MIN_Y
    global MAX_Y
    global HUMIDITY_INITIALIZED

    global DEVICES_COORDINATES

    global START_TIME
    START_TIME = 8

    global END_TIME
    END_TIME = 20

    global MINUTES_PER_TIMESTAMP
    MINUTES_PER_TIMESTAMP = 0

    TIMESTAMP_GRANULARITY = 5

    HUMIDITY_INITIALIZED = False

    MIN_X = MAX_X = MIN_Y = MAX_Y = 0

    DEVICES_COORDINATES = [
        [200, 100], [300, 600], [300, 400], [550, 300], [820, 300], [1000, 600], [620, 620]
    ]