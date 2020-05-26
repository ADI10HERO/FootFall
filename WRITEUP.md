# Project Write-Up

 - First project of first NanoDegree :D
 - Open Visual Inference and Neural Network Optimization is a toolkit provided by Intel to carry out faster inference of deep learning models.
 - The main components of OpenVINO are Inference Engine and Model Optimizer.
 - Plans :
     - Download a model from Tensorflow Object Detection Model Zoo
     - Convert it to an Intermediate Representation (probably with custom layers)
     - Use to detect people

## Custom Layers

#### What is a Custom Layer ?
The model optimizer searches the list of known layers for each layer in the input model. The inference engine thenn loads the layers from the input model IR files into the specified device plugin, which will search a list of known layer implementations for the device. If your model architecure contains layer or layers that are not in the list of known layers for the device, the Inference Engine considers the layer to be unsupported and reports an error. This is what we call a custom layer.

#### How do I use custom layer if Inference Enginer reports an error ?
You will need to add extensions to both the Model Optimizer and the Inference Engine.

#### Handling custom layers is important ?
It is very important to handle custom layers as research teams usually work with something new, somehthing of their own so handling those layers and conversion is ciritcal for the application to work smoothly.

## Explaining Model Selection 
The zoo has many models for object detection. On basic research, I found that ssd_mobilenet_v2_coco, ssd_inception_v2_coco and faster_rcnn_inception_v2_coco should perform well so tried using those.
No custom layers were used, but check for custom supporting layers was added.
So further running my analysis on those models...

## Comparing Model Performance

Models were compared before and after converstion to intermediate representation.
### The size of the models:
1. ssd_inception_v2_coco :
    a. Before conversion : 540 Mbs
    b. After conversion  : 330 Mbs
2. faster_rcnn_inception_v2_coco:
    a. Before conversion : 560 Mbs
    b. After conversion  : 260 Mbs
3. ssd_mobilenet_v2_coco :
    a. Before conversion : 180 Mbs
    b. After conversion  : 100 Mbs

### The inference time of the models (approx.):
1. ssd_inception_v2_coco :
    a. Before conversion : 150 ms
    b. After conversion  : 155 ms
2. faster_rcnn_inception_v2_coco :
    a. Before conversion : 90 ms
    b. After conversion  : 20 ms
3. ssd_mobilenet_v2_coco :
    a. Before conversion : 50 ms
    b. After conversion  : 60 ms

For more details please head on to Model Research section.
### Cloud Vs Edge Deployment :

Not diving deep into this but edge models need only local network connection. 
Cost of the renting a cloud server is so high. 
Whereas edge models can run on minimal cpu with with minimal local network connection.
Needless to say, using cloud, your data goes aroung the world to reach the cloud and then enters the model.
While Edge computing your data doesn't even leave the local network, so the speed is drastically improved.

## Assess Model Use Cases

#### Social Distance checker
Potential use case of the people counter app is to check whether social distancing is maintained and there is only one person at the counter or rather in the frame. If more than one person is detected an alert can be raised.
This can help maintain socail distancing and prevent the spread of deadly COVID-19

#### A security system for banks / shops
We can use this application as a security system.
Identification of robbers breaking in the stores. This system can take pictures and send it to shop owner maybe even raise an automatic alarm.

#### Data Analysis at Shopping Malls
Keeping track of which shops are performing better than others.
How much time people spend in the shop.
This data can be benefical for both the shop owners as well as the mall management.
Ideal location of shops can be determined. Also if the owner changes decor of the shop results can be analysed and decision was good or bad can be found out.

## Assess Effects on End User Needs

Only thing end user needs to make sure is that camera quality is not too bad and lightining is not poor as these can hinder the person detection resulting in false negatives, i.e people may go uncounted and / or our social distance detector might not raise the alert it should have. 

Change in input from camera due to change in focal length and/or image size will affect the model because the model may fail to make sense of the input. A possible solution could be to use some augmnted images while training models. But this solution is quite sensitive as it could affect the accuracy if too many images are augumented and level of distortion also becomes a hyperparameter to worry about.

Well as we all know there's a decay in accuracy of almost all models over time as data starts to go farther from what the model was trained on. To solve this problem retraining the model with recent data can be a very good solution. 


## Model Research

In investigating potential people counter models, I tried each of the following models:

Steps I took for model conversions :

- Model 1: ssd_inception_v2_coco
  - http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz
  - I converted the model to an Intermediate Representation with the following arguments: 
    ```sh
    python /opt/intel/openvino/deployment_tools/model_optimizer/mo.py --input_model \
    ssd_inception_v2_coco_2018_01_28/frozen_inference_graph.pb \
    --tensorflow_object_detection_api_pipeline_config pipeline.config \
    --reverse_input_channels \
    --tensorflow_use_custom_operations_config \
    /opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf/ssd_v2_support.json
    ```
  - The model was insufficient for the app because :
      - Lacked the required Accuracy
      - People weren't getting detected in the frame
  - I tried to improve the model for the app by:
      - Chagning threshold values
      - Decreasing the duration / frame to count people
  
- Model 2: faster_rcnn_inception_v2_coco
  - http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
  - I converted the model to an Intermediate Representation with the following arguments:
    ```sh
   python /opt/intel/openvino/deployment_tools/model_optimizer/mo.py \
   --input_model frozen_inference_graph.pb \
   --tensorflow_object_detection_api_pipeline_config pipeline.config \
   --reverse_input_channels \
   --tensorflow_use_custom_operations_config \
   /opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf/faster_rcnn_support.json 
    ```
  - This model performed satisfactorily
  - Threshold value was experimented with and best value was found at 0.4* (* = range(0,5))
  - On project review the final statistics was a little too off from the ground truth and hence decided to not use it.

- Model 3: ssd_mobilenet_v2_coco
  - http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
  - I converted the model to an Intermediate Representation with the following arguments:
    ```sh
   python /opt/intel/openvino/deployment_tools/model_optimizer/mo.py \
   --input_model frozen_inference_graph.pb \
   --tensorflow_object_detection_api_pipeline_config pipeline.config \
   --reverse_input_channels \
   --tensorflow_use_custom_operations_config \
   /opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf/ssd_v2_support.json 
    ```
  - This model too did not perfrom well with the accuracy metric.
  - I tried to improve the model for the app by using some transfer learning techniques.
  - But that did not work too well for this use case.

# Model Used 

During the first review, the reviewer mentioned person-detection-retail-0013 shouldn't be igmored. So after trying those 3 models. I tried this one and ended up using it.

Steps to download the model :
- ``` cd /opt/intel/openvino/deployment_tools/open_model_zoo/tools/downloaderc ```
- ``` sudo ./downloader.py --name person-detection-retail-0013 --precisions FP16 -o /home/workspace ```

To run the model :
```sh
python main.py \
-i resources/Pedestrian_Detect_2_1_1.mp4 \
-m intel/person-detection-retail-0013/FP16/person-detection-retail-0013.xml \
-l /opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so \
-d CPU -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 \
-framerate 24 -i - http://0.0.0.0:3004/fac.ffm
```

```
python main.py -i resources/Pedestrian_Detect_2_1_1.mp4 -m intel/person-detection-retail-0013/FP16/person-detection-retail-0013.xml -l /opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so -d CPU -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://0.0.0.0:3004/fac.ffm
```