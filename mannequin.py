import numpy as np

from tracking import iou
from pprint import pprint

min_frames = 5
mannq_threshold = 0.85
mann_to_human = 0.70

def remove_mannequin(ids):
    """
    ids: dict
        ids of ppl with boxes of past frames
    """
    for id, val in ids.items():
        boxes, flag = val
        if len(boxes) == min_frames:
            _iou = iou(boxes[0], boxes[-1])
            if flag == -1:
                if  _iou > mannq_threshold:
                    ids[id][1] = 0
                else:
                    ids[id][1] = 1
            if flag == 0 and _iou < mann_to_human:
                ids[id][1] = 1
    return ids

if __name__ == "__main__":
    ids = { 
            1:[[[9, 10, 12, 12], [12, 11, 12, 14] ], 1],
            2:[[[10, 10, 10, 10], [10, 10, 10, 11]], 1]
          }
    ids = remove_mannequin(ids)
    pprint(ids)
