from utils import misc


threshold = 0.63
iou_threshold = 0.4
k = 25
min_frames = 5


def iou(box1, box2):
    xa = max( box1[1] , box2[1] )
    ya = max( box1[0] , box2[0] )
    xb = min( box1[3] , box2[3] )
    yb = min( box1[2] , box2[2] )
    
    interArea = max(0, xb - xa ) * max(0, yb - ya )

    box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1] )
    box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1] )

    if interArea == box1Area + box2Area:
        return 1

    return float(interArea) / float(box1Area + box2Area - interArea)


def track(boxes, scores, classes, img, odapi, ids):
    cur_ids = {}
    for i in range(len(boxes)):
        if classes[i] == 1 and scores[i] > threshold:
            box = boxes[i]
            max_id = -1
            max_iou = 0

            for id, val in ids.items():
                old_box = val[0][-1]
                _iou = iou(old_box, box)
                if _iou > iou_threshold:
                    if _iou > max_iou:
                        max_iou = _iou
                        max_id = id

            startx, starty = box[1], box[0]
            endx, endy = box[3], box[2]
            cropped_img = img[starty:endy, startx:endx]

            final_id = max_id
            if max_id == -1:
                final_id = odapi.find(cropped_img)
                if final_id == -1:
                    final_id = len(ids) + 1
                    ids[final_id] = [[], 1]

            ids[final_id][0].append(box)
            if len(ids[final_id][0]) == min_frames + 1:
                ids[final_id][0].pop(0)
            cur_ids[final_id] = box
            misc.save_img(cropped_img, final_id)

    return cur_ids, ids
