def init():
    global TIMESTAMP_GRANULARITY
    global LOCATION_PRECISION
    global MIN_X
    global MAX_X
    global MIN_Y
    global MAX_Y
    global SLIDER_SIZE
    global DEVICES_COORDINATES

    TIMESTAMP_GRANULARITY = 5
    LOCATION_PRECISION = 50


    MIN_X = MAX_X = MIN_Y = MAX_Y = 0

    DEVICES_COORDINATES = [
        [200, 100], [300, 600], [300, 400], [550, 300], [820, 300], [1000, 600], [620, 620]
    ]

def best_key(dic):

    if len(dic) <= SLIDER_SIZE:
        return len(dic)

    min_len = 1000
    its_key = None
    for key, value in dic.items():
        if (len(value) < min_len) and (len(value) < len(DEVICES_COORDINATES)):
            min_len = len(value)
            its_key = key
    return its_key