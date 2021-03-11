import numpy as np

from tracking import iou
from pprint import pprint

min_frames = 5
mannq_threshold = 0.95


def remove_mannequin(ids):
    """
    ids: dict
        ids of ppl with boxes of past frames
    """
    for id, val in ids.items():
        boxes, flag = val
        if flag == 1 and len(boxes) == min_frames:
            _iou = iou(boxes[0], boxes[-1])
            print(id, _iou)
            if _iou > mannq_threshold:
                ids[id][1] = 0
    return ids

if __name__ == "__main__":
    ids = { 
            1:[[[9, 10, 12, 12], [12, 11, 12, 14] ], 1],
            2:[[[10, 10, 10, 10], [10, 10, 10, 11]], 1]
          }
    ids = remove_mannequin(ids)
    pprint(ids)
