from flask import Flask
import random
import json
import requests
import time

app = Flask(__name__)

def random_payment():
    
    # Simulate random payment details
    payment_details = {
        "amount": round(random.uniform(10.0, 100.0), 2),
        "currency": random.choice(["USD", "EUR", "GBP"]),
        "recipient": "Merchant {}".format(random.randint(1, 100)),
        "status": "pending",
        "station": random.choice([1, 2])
    }
    # Convert the payment details into a JSON formatted string
    payment_json = json.dumps(payment_details)
    # Print the payment details to the console for logging
    print(payment_json)
    # Send a POST request to the server running on port 5001 to indicate payment was done
    response = requests.post('http://localhost:5001/', json=payment_details)
    print("Payment notification sent successfully.")
    # Return the updated payment details as a JSON response
    return json.dumps(payment_details)

if __name__ == '__main__':
    import sys, tty, termios  # Use tty and termios for Unix-based systems

    print("Press 'Space' to send a random payment or 'Esc' to exit.")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(sys.stdin.fileno())

        while True:
            import select
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                if key == ' ':  # If the Spacebar was pressed
                    payment_info = random_payment()
                    # Send the payment details to localhost:5001
                    requests.post('http://localhost:5001/', data=payment_info)
                elif key == '\x1b':  # If the Escape key was pressed
                    break
            time.sleep(0.1)  # Add a short delay to reduce CPU usage
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
