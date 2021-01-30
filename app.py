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
app.config['SECRET_KEY'] = 'secret!' #TODO: Move to env file.
socketio = SocketIO(app, cors_allowed_origins="*") #, async_mode=None, logger=True, engineio_logger=True)


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
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frames[id-1].tobytes() + b'\r\n\r\n')


@app.route("/view/<idx>")
def get_single_frame(idx):
    idx = int(idx)
    return Response(view_stream(idx), mimetype='multipart/x-mixed-replace; boundary=frame')

# socket routes below
thread_tc = Thread()
thread_tc_stop_event = Event()

def update_tc():
    global total_count
    while not thread_tc_stop_event.isSet():
        socketio.emit('update tc', total_count, namespace='/test')


thread_fc = Thread()
thread_fc_stop_event = Event()

def update_frame_counts():
    global frame_counts
    while not thread_fc_stop_event.isSet():
        emit('update fcounts', frame_counts, namespace='/test')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread_fc, thread_tc

    if not thread_tc.isAlive():
        print("Starting TC Thread")
        thread_tc = socketio.start_background_task(update_tc())
    
    if not thread_fc.isAlive():
        print("Starting FC Thread")
        thread_fc = socketio.start_background_task(update_frame_counts())


if __name__ == "__main__":
    socketio.run(app, debug=True)
