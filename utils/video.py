import logging as log
import cv2 as cv


class MulticamCapture:
    def __init__(self, sources):
        assert sources
        self.captures = []

        try:
            sources = [int(src) for src in sources]
            mode = 'cam'
        except ValueError:
            mode = 'video'

        if mode == 'cam':
            for id in sources:
                log.info('Connection  cam {}'.format(id))
                cap = cv.VideoCapture(id)
                cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
                cap.set(cv.CAP_PROP_FPS, 30)
                cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*'MJPG'))
                assert cap.isOpened()
                self.captures.append(cap)
        else:
            for video_path in sources:
                log.info('Opening file {}'.format(video_path))
                cap = cv.VideoCapture(video_path)
                assert cap.isOpened()
                self.captures.append(cap)

    def get_frames(self):
        frames = []
        for capture in self.captures:
            has_frame, frame = capture.read()
            frame = cv.resize(frame, (640, 480))
            if has_frame:
                frames.append(frame)

        return len(frames) == len(self.captures), frames

    def get_num_sources(self):
        return len(self.captures)
