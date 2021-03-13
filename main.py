import cv2 as cv
import os
import queue
import time

from threading import Thread

from detection import detect, DetectorAPI
from mannequin import remove_mannequin
from utils.misc import get_box, read_py_config, preprocess_image, clear_detections
from utils.video import MulticamCapture
from pprint import pprint

MODEL_PATH = "detector/frozen_inference_graph.pb"

ids = {}
count = 0

class FramesThreadBody:
    def __init__(self, capture, max_queue_length=2):
        self.process = True
        self.frames_queue = queue.Queue()
        self.capture = capture
        self.max_queue_length = max_queue_length

    def __call__(self):
        while self.process:
            if self.frames_queue.qsize() > self.max_queue_length:
                time.sleep(0.1)
            has_frames, frames = self.capture.get_frames()
            if not has_frames and self.frames_queue.empty():
                self.process = False
                break
            if has_frames:
                self.frames_queue.put(frames)


def get_video_writer(output):
    if output is None:
        return None
    video_output_size = (1920 // capture.get_num_sources(), 1080)
    fourcc = cv.VideoWriter_fourcc(*'MJPG')
    return cv.VideoWriter("resources"+ os.sep + output, fourcc, 24.0, video_output_size)


def main(input_urls, prob_threshold=0.6, output=None):

    global ids

    odapi = DetectorAPI(path_to_ckpt=MODEL_PATH)
    capture = MulticamCapture(input_urls)
    thread_body = FramesThreadBody(capture, max_queue_length=len(capture.captures) * 2)
    frames_thread = Thread(target=thread_body)
    frames_thread.start()

    itr = 0
    clear_detections()
    # output_video = get_video_writer(output)
    while cv.waitKey(1) != 27 and thread_body.process:
        # start = time.time()
        try:
            frames = thread_body.frames_queue.get_nowait()
        except queue.Empty:
            frames = None

        if frames is None:
            continue

        # to_yield = []
        # if itr % 5 == 0:
        for i,frame in enumerate(frames):
            frame = cv.resize(frame, (480, 360))

            frame, frame_count, cur_ids, ids = detect(frame, odapi, ids)
            ids = remove_mannequin(ids)

            for id, box in cur_ids.items():
                flag = ids[id][1]
                if flag == 1 or flag == -1:
                    cv.rectangle(frame,(box[1],box[0]),(box[3],box[2]),(255,0,0),2)
                    frame = cv.putText(frame, str(id), (box[1],box[0]), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
                else:
                    cv.rectangle(frame,(box[1],box[0]),(box[3],box[2]),(0,0,255),2)
                    frame_count -= 1
    
            count = frame_count
            ret, jpeg = cv.imencode('.jpg', frame)
            frames[i] = [jpeg, count]

            # to_yield = frames[:]

        # if output_video:
        #     # TODO: Concat frames and write output
        #     # vis = concat(frames)
        #     output_video.write(cv.resize(vis, video_output_size))

        yield frames

    thread_body.process = False
    frames_thread.join()


if __name__ == "__main__":
    raise NotImplementedError("Please use flask app.")
