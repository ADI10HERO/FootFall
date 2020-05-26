"""People Counter."""
"""
 Copyright (c) 2018 Intel Corporation.
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


import os
import sys
import time
import socket
import json
import cv2

import logging as log
import paho.mqtt.client as mqtt

from argparse import ArgumentParser
from inference import Network


# MQTT server environment variables
HOSTNAME = socket.gethostname()
IPADDRESS = socket.gethostbyname(HOSTNAME)
MQTT_HOST = IPADDRESS
MQTT_PORT = 3001
MQTT_KEEPALIVE_INTERVAL = 60

def build_argparser():
    """
    Parse command line arguments.

    :return: command line arguments
    """
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", required=True, type=str,
                        help="Path to an xml file with a trained model.")
    parser.add_argument("-i", "--input", required=True, type=str,
                        help="Path to image or video file")
    parser.add_argument("-l", "--cpu_extension", required=False, type=str,
                        default=None,
                        help="MKLDNN (CPU)-targeted custom layers."
                             "Absolute path to a shared library with the"
                             "kernels impl.")
    parser.add_argument("-d", "--device", type=str, default="CPU",
                        help="Specify the target device to infer on: "
                             "CPU, GPU, FPGA or MYRIAD is acceptable. Sample "
                             "will look for a suitable plugin for device "
                             "specified (CPU by default)")
    parser.add_argument("-pt", "--prob_threshold", type=float, default=0.5,
                        help="Probability threshold for detections filtering"
                        "(0.5 by default)")
    return parser


def connect_mqtt():
    # Connect to the MQTT client
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

    return client
 
def getBox(frame,output_result,prob_threshold, width, height):
    counter=0
    start_point = None
    end_point = None 
    color = (0, 255, 0)
    thickness = 1
    for box in output_result[0][0]:
        if box[2] > prob_threshold:
            start_point = (int(box[3] * width), int(box[4] * height))
            end_point = (int(box[5] * width), int(box[6] * height))
            # Using cv2.rectangle() method 
            # Draw a rectangle with Green line borders of thickness of 1 px
            frame = cv2.rectangle(frame, start_point, end_point, color,thickness)
            counter+=1
    return frame, counter
    
def infer_on_stream(args, client):
    """
    Initialize the inference network, stream video to network,
    and output stats and video.

    :param args: Command line arguments parsed by `build_argparser()`
    :param client: MQTT client
    :return: None
    """
    
    # Input arguments
    DEVICE = args.device
    CPUEXTENSION = args.cpu_extension
    inp = args.input
    # Initialise the class
    infer_network = Network()
    
    #Load the model through `infer_network`
    infer_network.load_model(args.model, DEVICE, CPUEXTENSION)
    network_shape = infer_network.get_input_shape()

    # Set Probability threshold for detections
    prob_threshold = args.prob_threshold
    
    # Handle the input stream
    single_image_mode = False
    if inp == 'CAM':
        inp = 0
    elif inp.endswith('.jpg') or inp.endswith('.bmp'):
        single_image_mode = True
    else:
        if not os.path.isfile(inp):
            raise Exception("File doesn't exist")

    cap = cv2.VideoCapture(inp)
    cap.open(inp)

    # Grab the shape of the input 
    width = int(cap.get(3))
    height = int(cap.get(4))
    
    # initlise some variable 
    report,counter,counter_prev,duration_prev = 0,0,0,0
    counter_total,dur,request_id = 0,0,0

    while cap.isOpened():
        flag, frame = cap.read()
        if not flag:
            break

        image = cv2.resize(frame, (network_shape[3], network_shape[2]))
        image = image.transpose((2,0,1))
        image = image.reshape(1, *image.shape)

        duration_report = None
        inf_start = time.time()
        infer_network.exec_net(image)

        if infer_network.wait() == 0:
            det_time = time.time() - inf_start
            # Results of the output layer of the network
            output_results = infer_network.get_output()
            #Extract any desired stats from the results 
            #Update the frame to include detected bounding boxes
            boxxed, pointer = getBox(frame, output_results, prob_threshold, width, height)
            # print("inf time", det_time)

            #Calculate and send relevant information on 
            # current_count, total_count and duration to the MQTT server
            # Topic "person": keys of "count" and "total"
            # Topic "person/duration": key of "duration"

            if pointer != counter:
                counter_prev = counter
                counter = pointer
                if dur >= 3:
                    duration_prev = dur
                    dur = 0
                else:
                    dur = duration_prev + dur
                    duration_prev = 0
            else:
                dur += 1
                if dur >= 3:
                    report = counter
                    if dur == 3 and counter > counter_prev:
                        counter_total += counter - counter_prev
                    elif dur == 3 and counter < counter_prev:
                        duration_report = int((duration_prev / 10.0) * 1000)

            client.publish('person',
                           payload=json.dumps({
                               'count': report, 
                               'total': counter_total
                               }),
                           qos=0, 
                           retain=False
                           )

            if duration_report is not None:
                client.publish('person/duration',
                               payload=json.dumps({
                                   'duration': duration_report
                                   }),
                               qos=0, 
                               retain=False
                               )

            # Send frame to the ffmpeg server
            sys.stdout.buffer.write(boxxed)
            sys.stdout.flush()
            
            if single_image_mode:
                cv2.imwrite('output.jpg', boxxed)

    cap.release()
    cv2.destroyAllWindows()

def main():
    """
    Load the network and parse the output.

    :return: None
    """
    # Grab command line args
    args = build_argparser().parse_args()
    # Connect to the MQTT server
    client = connect_mqtt()
    # Perform inference on the input stream
    infer_on_stream(args, client)


if __name__ == '__main__':
    main()
    
"""
TO run : 
python main.py -i resources/Pedestrian_Detect_2_1_1.mp4 -m intel/person-detection-retail-0013/FP16/person-detection-retail-0013.xml -l /opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so -d CPU -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://0.0.0.0:3004/fac.ffm

"""