import cv2 as cv
import numpy as np
from utils.misc import COLOR_PALETTE


def draw_detections(frame, detections):
    """Draws detections and labels"""
    for i, obj in enumerate(detections):
        left, top, right, bottom = obj.rect
        label = obj.label
        id = int(label.split(' ')[-1])
        box_color = COLOR_PALETTE[id % len(COLOR_PALETTE)]

        cv.rectangle(frame, (left, top), (right, bottom),
                     box_color, thickness=3)
        label_size, base_line = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 1, 2)
        top = max(top, label_size[1])
        cv.rectangle(frame, (left, top - label_size[1]), (left + label_size[0], top + base_line),
                     (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)


def visualize_multicam_detections(frames, all_objects, fps=''):
    assert len(frames) == len(all_objects)
    vis = None
    for frame, objects in zip(frames, all_objects):
        draw_detections(frame, objects)
        vis = np.vstack([vis, frame]) if vis is not None else frame
    n_cams = len(frames)
    vis = cv.resize(vis, (vis.shape[1] // n_cams, vis.shape[0] // n_cams))

    label_size, base_line = cv.getTextSize(str(fps),
                                           cv.FONT_HERSHEY_SIMPLEX, 1, 2)
    cv.putText(vis, str(fps), (base_line*2, base_line*3),
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    return vis
