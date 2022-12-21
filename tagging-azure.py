 ##python3 -m pip install --upgrade azure-cognitiveservices-vision-computervision
 #python3 -m pip install --upgrade pillow
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes, Details
from msrest.authentication import CognitiveServicesCredentials

import os
import sys
import time

subscription_key = "api_key"
endpoint = "https://machine.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))





'''
Categorize an Image -  local
This example extracts categories from a local image with a confidence score
'''
print("===== Categorize an Image - local =====")
# Open local image file
local_image = open('/home/ubuntu/pics-83num-resized-half-6mb-max130kb/pic_1.jpg', "rb")
# Select visual feature type(s)
local_image_features = ["categories"]
local_image_features = [VisualFeatureTypes.categories,VisualFeatureTypes.brands,VisualFeatureTypes.adult,VisualFeatureTypes.color,VisualFeatureTypes.description,VisualFeatureTypes.faces,VisualFeatureTypes.image_type,VisualFeatureTypes.objects,VisualFeatureTypes.tags]
# Call API
categorize_results_local = computervision_client.analyze_image_in_stream(local_image, local_image_features)

# Print category results with confidence score
print("Categories from local image: ")
if (len(categorize_results_local.categories) == 0):
    print("No categories detected.")
else:
    for category in categorize_results_local.categories:
        print("'{}' with confidence {:.2f}%".format(category.name, category.score * 100))
print()

# Return tags
# Print results with confidence score
print("Tags in the remote image: ")
if (len(categorize_results_local.tags) == 0):
    print("No tags detected.")
else:
    for tag in categorize_results_local.tags:
        print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))

print(dir(categorize_results_local))
print('xxxxx')
print(dir(categorize_results_local.tags))
print(categorize_results_local.tags[0])
print(len(categorize_results_local.tags))
print(categorize_results_local.tags[0].name)
print(type(categorize_results_local.tags[0].confidence))


