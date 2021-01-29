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
    request,
    send_from_directory,
    render_template,
)
import logging
from logging import info
# from main import main

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# TODO: Integrate this
# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(VideoCamera()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/video_stream", methods=["POST"])
def process():
    if request.method == "POST":
        data = dict(request.form)
        data["ondevice"] = False
        # TODO: Call main subroutine here :)
        #       Render detected video and other params
        # param: total count, count in each cam
        total_count, cam_counts, frames = main(data)
        return render_template(
            "dashboard.html",
            total_count=total_count,
            cam_counts=cam_counts,
            frames=frames,
            num_cam=len(cam_counts),
        )

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


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return "Dude...Implement Basic Auth!"

    if request.method == "GET":
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
