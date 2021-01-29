def getBox(frame, output_result, prob_threshold, width, height):
    counter = 0
    start_point = None
    end_point = None
    color = (0, 255, 0)
    thickness = 1
    for box in output_result[0][0]:
        if box[2] > prob_threshold:
            start_point = (int(box[3] * width), int(box[4] * height))
            end_point = (int(box[5] * width), int(box[6] * height))
            frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
            counter += 1
    return frame, counter

# TODO: Write cropping code
