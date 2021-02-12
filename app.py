from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    Response,
    send_from_directory,
)
from flask_socketio import SocketIO, emit
import logging
import time
from logging import info
from main import main
from threading import Thread, Event


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None, logger=True, engineio_logger=True)


input = None
frames = []
frame_counts = []
total_count = 0
logging.basicConfig(level=logging.INFO)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return "Dude...Implement Basic Auth!"

    if request.method == "GET":
        return render_template("index.html")


@app.route("/basic", methods=["GET", "POST"])
def basic():
    if request.method == "POST":
        num_cams = request.form.get("num_cams")
        ans = request.form.get("ques")
        if ans == "yes":
            total_count, cam_counts, frames = main(
                {"num_cams": num_cams, "ondevice": True}
            )
            # TODO: Create mtc object here or call driver code.
            return render_template("view_stream.html")
        return render_template("get_cam_info.html", num_cams=int(num_cams))

    if request.method == "GET":
        return render_template("index.html")


@app.route("/video_stream", methods=["POST"])
def process():
    global input, frames, frame_counts
    if request.method == "POST":
        data = dict(request.form)
        data["ondevice"] = False

        num_cams = int(data["num_cam"])
        input = [data["cam_" + str(i+1)] for i in range(num_cams)]

        return render_template("dashboard.html",
            cam_counts=frame_counts,
            num_cam=num_cams
        )

    if request.method == "GET":
        return render_template("dashboard.html")


def view_stream(id):

    global input, frames, frame_counts, total_count
    if input is None or frames == [] or frame_counts == []:
        time.sleep(1)

    for data in main(input):
        frames = [ frame[0] for frame in data ]
        frame_counts = [ frame[1] for frame in data ]
        total_count = sum(frame_counts)
        print(total_count, frame_counts)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frames[id-1].tobytes() + b'\r\n\r\n')


@app.route("/view/<idx>")
def get_single_frame(idx):
    idx = int(idx)
    return Response(view_stream(idx), mimetype='multipart/x-mixed-replace; boundary=frame')

# socket routes below
thread = Thread()
thread_stop_event = Event()


def getupdatedinfo():

    global total_count, frame_counts

    print("Starting stream")
    while not thread_stop_event.isSet():
        data = {
            'total_count': total_count,
            'frame_counts': [2, 3]
        }
        socketio.emit('newdata', data, namespace='/test')
        socketio.sleep(2)


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
