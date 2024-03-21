from walker import walk, get_closer_to_first, get_closer_to_second
from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    res = "closer to first: " + get_closer_to_first() + '\n'
    res += "closer to second: " + get_closer_to_second()
    print("closer to first: ", get_closer_to_first())
    print("closer to second: ", get_closer_to_second())
    return res

if __name__ == '__main__':
    t1 = Thread(target=lambda: app.run(host="0.0.0.0", port=5001, use_reloader=False))
    t1.start()
    walk()
    t1.join()