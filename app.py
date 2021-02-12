from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    Response,
    send_from_directory,
)
from flask_socketio import SocketIO, emit
import time
from main import main
from threading import Thread, Event
from utils.misc import encode


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None, logger=False, engineio_logger=False)


input = None
frames = []
frame_counts = []
total_count = 0
num_cams = 0


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return "Dude...Implement Basic Auth!"

    if request.method == "GET":
        return render_template("index.html")


@app.route("/info/1", methods=["GET", "POST"])
def get_num_cams():
    global input, num_cams
    if request.method == "POST":
        num_cams = int(request.form.get("num_cams"))
        ans = request.form.get("ques")

        if ans == "yes":
            input = [i for i in range(num_cams)]
            return render_template("dashboard.html", num_cams=num_cams)
        return render_template("get_cam_info.html", num_cams=num_cams)

    if request.method == "GET":
        return render_template("index.html")


@app.route("/info/2", methods=["POST"])
def get_input_urls():
    global input
    if request.method == "POST":
        data = dict(request.form)
        input = [data["cam_" + str(i+1)] for i in range(num_cams)]
        return render_template("dashboard.html", num_cams=num_cams)

    if request.method == "GET":
        return render_template("dashboard.html")


# socket routes below
thread = Thread()
thread_stop_event = Event()


def getupdatedinfo():

    global total_count, frame_counts, frames, input

    callback = main(input)
    print("Starting stream")
    while not thread_stop_event.isSet():
        t1 = time.time()
        print("Takes {} time to get 1 batch of frames".format(time.time()-t1))
        resp = next(callback)
        frames = [ encode(frame[0]) for frame in resp ]
        frame_counts = [ frame[1] for frame in resp ]
        total_count = sum(frame_counts)
        data = {
            'total_count': total_count,
            'frame_counts': frame_counts,
            'frames': frames
        }

        socketio.emit('newdata', data, namespace='/test')
        time.sleep(1)
        # socketio.sleep(2)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print("Client Connected")

    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(getupdatedinfo)


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == "__main__":
    socketio.run(app, debug=True)
