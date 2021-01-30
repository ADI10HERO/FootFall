import numpy as np
import tensorflow as tf
import cv2
import time

from utils.misc import pre_reid_process


MODEL_PATH = "detector/frozen_inference_graph.pb"

class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        end_time = time.time()

        im_height, im_width,_ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0,i,0] * im_height),
                        int(boxes[0,i,1]*im_width),
                        int(boxes[0,i,2] * im_height),
                        int(boxes[0,i,3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()


odapi = DetectorAPI(path_to_ckpt=MODEL_PATH)

def detect(img, threshold=0.63):
    """
    Parameters
    -----------
    threshold: float
        Confidence threshold for detection

    img: cv2 image object
        Single image frame
    """

    img = cv2.resize(img, (640, 480))
    boxes, scores, classes, num = odapi.processFrame(img)
    # print("\n\n ====NUM===== ", num, len(boxes))

    count_ppl = 0
    detections = []
    for i in range(len(boxes)):

        if classes[i] != 1 or not (scores[i] > threshold):
            # class 1 represents humans
            continue

        count_ppl += 1
        box = boxes[i]
        detections.append(pre_reid_process(box, img))
        cv2.rectangle(img,(box[1],box[0]),(box[3],box[2]),(255,0,0),2)

    img = cv2.putText(img, 'Count :'+str(count_ppl), (30, 30), cv2.FONT_HERSHEY_SIMPLEX,  
            1, (0, 0, 255), 2, cv2.LINE_AA)

    return img, count_ppl, detections
