"""People Counter."""
"""
 Copyright (c) 2018 Intel Corporation.
 Copyright (c) 2021 Aditya Srivastava.
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit person to whom the Software is furnished to do so, subject to
 the following conditions:
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    Response,
    send_from_directory,
)
import logging
import time
from logging import info
from main import main

app = Flask(__name__)
input = None
frames = []
frame_counts = []

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
            total_count=sum(frame_counts),
            cam_counts=frame_counts,
            num_cam=num_cams
        )

    if request.method == "GET":
        return render_template("dashboard.html")


def view_stream(id):

    global input, frames, frame_counts
    if input is None or frames == [] or frame_counts == []:
        time.sleep(1)

    for data in main(input):
        frames = [ frame[0] for frame in data ]
        frame_counts = [ frame[1] for frame in data ]
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frames[id-1].tobytes() + b'\r\n\r\n')


@app.route("/view/<idx>")
def get_single_frame(idx):
    idx = int(idx)
    return Response(view_stream(idx), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
