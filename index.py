import requests
import json
import socket
import os
import sys


def get_API_Key_and_auth():
    # Gets public key from spaces and places in correct format
    print("-- No API Key Found --")

    # Gets user to paste in generated token from app
    token = input('Enter provided API key here: ')

    # Writes activation key to file. This key can be used to open up Firehose connection
    f = open("API_KEY.txt", "a")
    f.write(token)
    f.close()
    return token


# work around to get IP address on hosts with non resolvable hostnames
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IP_ADRRESS = s.getsockname()[0]
s.close()
url = 'http://' + str(IP_ADRRESS) + '/update/'

# Tests to see if we already have an API Key
try:
    if os.stat("API_KEY.txt").st_size > 0:
        # If we do, lets use it
        f = open("API_KEY.txt")
        apiKey = f.read()
        f.close()
    else:
        # If not, lets get user to create one
        apiKey = get_API_Key_and_auth()
except:
    apiKey = get_API_Key_and_auth()

# overwrite previous log file
f = open("logs.json", 'w+')
f.truncate(0)
f.write("[")

# Opens a new HTTP session that we can use to terminate firehose onto
s = requests.Session()
s.headers = {'X-API-Key': apiKey}
r = s.get(
    'https://partners.dnaspaces.io/api/partners/v1/firehose/events', stream=True)  # Change this to .io if needed

# Jumps through every new event we have through firehose
print("Starting Stream")
for line in r.iter_lines():
    if line:

        # decodes payload into useable format
        decoded_line = line.decode('utf-8')
        event = json.loads(decoded_line)

        ### All this crap just to make sure that the log is always a valid list of json objects

        # Check if the file ends with ']'
        f.seek(0, 2)  # Move the file pointer to the end of the file
        end_of_file = f.tell()  # Get the current position of the file pointer
        if end_of_file > 0:
            f.seek(end_of_file - 1)  # Move the file pointer to the position of the last character
            last_char = f.read(1)  # Read the last character
            if last_char == ']':
                # Replace ']' with ','
                f.seek(end_of_file - 1)  # Move the file pointer back to the position of the last character
                f.write(',')  # Write ',' to replace ']'

        # writes every event to the logs.json in readible format
        f.write(str(json.dumps(json.loads(line), indent=4, sort_keys=True)) + "]")

        # gets the event type out the JSON event and prints to screen
        eventType = event['eventType']
        print(eventType)