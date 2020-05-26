#!/usr/bin/env python3
"""
 Copyright (c) 2018 Intel Corporation.

 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to
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
import logging as log
from openvino.inference_engine import IENetwork, IECore


class Network:
    """
    Load and configure inference plugins for the specified target devices 
    and performs synchronous and asynchronous modes for the specified infer requests.
    """

    def __init__(self):
        #Initialize any class variables desired ###
        self.network = None
        self.plugin = None
        self.exec_network = None
        self.input_blob = None
        self.output_blob = None
        self.infer_request = None


    def load_model(self,model,device,cpu_extension):
        # Load the model ###
        xml = model
        bin_model = os.path.splitext(xml)[0] + ".bin"

        self.plugin = IECore()
        self.network = IENetwork(model=xml, weights=bin_model)

        # Check for supported layers
        layers_supported = self.plugin.query_network(self.network,device)
        layers = self.network.layers.keys()
        supported = True
        for l in layers:
            if l not in layers_supported:
                supported = False
                break

        if not supported:
            # Add any necessary extensions
            self.plugin.add_extension(cpu_extension, device)

        # Return the loaded inference plugin
        self.exec_network = self.plugin.load_network(self.network , device)
        self.input_blob = next(iter(self.network.inputs))
        self.output_blob = next(iter(self.network.outputs))
        return self.exec_network;

    def get_input_shape(self):
        # Return the shape of the input layer
        return self.network.inputs[self.input_blob].shape

    def exec_net(self,frame):
        # Start an asynchronous request
        # Return any necessary information
        self.exec_network.start_async(request_id=0,inputs={self.input_blob: frame})
        return self.exec_network

    def wait(self):
        # Wait for the request to be complete
        # Return any necessary information
        # Note: You may need to update the function parameters
        status = self.exec_network.requests[0].wait(-1)
        return status

    def get_output(self):
        #Extract and return the output results
        return self.exec_network.requests[0].outputs[self.output_blob]