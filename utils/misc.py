"""
 Copyright (c) 2019 Intel Corporation
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import cv2
import os.path as osp
import sys
from importlib import import_module


def check_file_exist(filename, msg_tmpl='file "{}" does not exist'):
    if not osp.isfile(filename):
        raise FileNotFoundError(msg_tmpl.format(filename))


def read_py_config(filename):
    filename = osp.abspath(osp.expanduser(filename))
    check_file_exist(filename)
    assert filename.endswith('.py')
    module_name = osp.basename(filename)[:-3]
    if '.' in module_name:
        raise ValueError('Dots are not allowed in config file path.')
    config_dir = osp.dirname(filename)
    sys.path.insert(0, config_dir)
    mod = import_module(module_name)
    sys.path.pop(0)
    return {
        name: value
        for name, value in mod.__dict__.items()
        if not name.startswith('__')
    }


def none_to_zero(a):
    if a is not None:
        return a
    return 0


def get_box(frame, output_result, prob_threshold, width, height):
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


def preprocess_image(frame, widht, height):
    image = cv2.resize(frame, (widht, height))
    image = image.transpose((2, 0, 1))
    image = image.reshape(1, *image.shape)
    return image


def pre_reid_process(box, frame):
    # TODO: Write cropping --> 9x9 --> Grayscale --> return list of detections?
    # crop frame (img) according to box coords
    # Grayscale
    # Compress (resize) to 9x9
    # Return cropped frame 
    return frame


COLOR_PALETTE = [[0, 113, 188],
                 [216, 82, 24],
                 [236, 176, 31],
                 [125, 46, 141],
                 [118, 171, 47],
                 [76, 189, 237],
                 [161, 19, 46],
                 [76, 76, 76],
                 [153, 153, 153],
                 [255, 0, 0],
                 [255, 127, 0],
                 [190, 190, 0],
                 [0, 255, 0],
                 [0, 0, 255],
                 [170, 0, 255],
                 [84, 84, 0],
                 [84, 170, 0],
                 [84, 255, 0],
                 [170, 84, 0],
                 [170, 170, 0],
                 [170, 255, 0],
                 [255, 84, 0],
                 [255, 170, 0],
                 [255, 255, 0],
                 [0, 84, 127],
                 [0, 170, 127],
                 [0, 255, 127],
                 [84, 0, 127],
                 [84, 84, 127],
                 [84, 170, 127],
                 [84, 255, 127],
                 [170, 0, 127],
                 [170, 84, 127],
                 [170, 170, 127],
                 [170, 255, 127],
                 [255, 0, 127],
                 [255, 84, 127],
                 [255, 170, 127],
                 [255, 255, 127],
                 [0, 84, 255],
                 [0, 170, 255],
                 [0, 255, 255],
                 [84, 0, 255],
                 [84, 84, 255],
                 [84, 170, 255],
                 [84, 255, 255],
                 [170, 0, 255],
                 [170, 84, 255],
                 [170, 170, 255],
                 [170, 255, 255],
                 [255, 0, 255],
                 [255, 84, 255],
                 [255, 170, 255],
                 [42, 0, 0],
                 [84, 0, 0],
                 [127, 0, 0],
                 [170, 0, 0],
                 [212, 0, 0],
                 [255, 0, 0],
                 [0, 42, 0],
                 [0, 84, 0],
                 [0, 127, 0],
                 [0, 170, 0],
                 [0, 212, 0],
                 [0, 255, 0],
                 [0, 0, 42],
                 [0, 0, 84],
                 [0, 0, 127],
                 [0, 0, 170],
                 [0, 0, 212],
                 [0, 0, 255],
                 [0, 0, 0],
                 [36, 36, 36],
                 [72, 72, 72],
                 [109, 109, 109],
                 [145, 145, 145],
                 [182, 182, 182],
                 [218, 218, 218],
                 [255, 255, 255]]
