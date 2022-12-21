##python3 -m pip install --upgrade azure-cognitiveservices-vision-computervision
 #python3 -m pip install --upgrade pillow
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes, Details
from msrest.authentication import CognitiveServicesCredentials

import os
import sys
import time
import requests
import json

#setup
config={'tags_container': 'load', 'do_actual': False, 'do_predict': False, 
        'metrics': True, 'metrics_max_tags_num': 20, 'matching_enabled': True, 'actual_min_threshold': 50, 'predict_min_threshold': 40}
#files
pics_name_format = 'pic_' + '#num#' + '.jpg'
pics_num = 83
json_write_file = 'tags.json'

#actual 
subscription_key = "add_your_api_key"
endpoint = "https://add_image_name.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


#prediction
#note: set MODEL_MIN_CONFIDENCE_THRESHOLD env in the deployment to "0.01" to capture all positive and negative taggings of the model because default is set to "0.5"

path = '/home/ubuntu/pics-83num-resized-half-6mb-max130kb/'
urls={'cpu': 'http://10.43.44.182:8080/', 'tpu': 'http://10.43.24.20:8080/', 'gpu': 'http://10.43.200.7:8080/'}

#matches for normaliztion
matches = [['star','sky'], ['plant', 'potted plant', 'vase'], ['chair', 'couch', 'armrest'], ['furniture', 'dining table', 'table', 'appliance'], ['surfboard', 'surfing equipment',], ['chair', 'furniture'],
['cup', 'coffee', 'mug', 'coffee cup'],['food', 'bowl'], ['tv', 'office equipment', 'display device'], ['knife', 'tableware', 'spoon'], ['plane', 'airplane'], ['light', 'traffic light'], ['fedora', 'hat'],
['pot', 'flowerpot', 'vase'], ['pier', 'beach'], ['pattern', 'kite'], ['car', 'land vehicle'],['fire hydrant', 'tap'], ['mobile device', 'cell phone'], ['dog', 'animal', 'mouse', 'teddy bear'], ['dessert', 'donut'],
['backpack', 'clothing'],['motorcycle', 'vehicle'], ['yellow', 'banana']]

#container for all data
tags = {}


def initiate_tags():
    tags = {}

    for i in range(1,pics_num + 1):
        tag ={}
        tag['actual'] = []
        tag['cpu'] = {'predicted':[], 'tp': 0, 'tn': 0, 'fp':0, 'fn':0}
        tag['tpu'] = {'predicted':[], 'tp': 0, 'tn': 0, 'fp':0, 'fn':0}
        tag['gpu'] = {'predicted':[], 'tp': 0, 'tn': 0, 'fp':0, 'fn':0}
        
        pic_name = pics_name_format.replace('#num#', str(i))
        
        tags[pic_name] = tag

    return tags

#Initiate tags, or, load it from json file
if config['tags_container'] == 'initiate':
    tags = create_tags()

#load tags.json
else:
    # read JSON file
    with open(json_write_file, 'r') as openfile:
    
        # Reading from json file
        tags = json.load(openfile)

# #temporary fix      
# for i in range(1,pics_num + 1):
#     pic_name = pics_name_format.replace('#num#', str(i))
#     #fix detected_objects to predicted
#     tags[pic_name]['cpu']['predicted'] = tags[pic_name]['cpu']['detected_objects']
#     del(tags[pic_name]['cpu']['detected_objects'])
    
#     tags[pic_name]['tpu']['predicted'] = tags[pic_name]['tpu']['detected_objects']
#     del(tags[pic_name]['tpu']['detected_objects'])
#     tags[pic_name]['gpu']['predicted'] = tags[pic_name]['gpu']['detected_objects']
#     del(tags[pic_name]['gpu']['detected_objects'])
#     #fix object to tag
#     for item in tags[pic_name]['cpu']['predicted']:
#         item['tag'] = item['object']
#         conf=float(item['confidence'])
#         del(item['confidence'])
#         item['confidence'] = conf
#         del(item['object'])
#     for item in tags[pic_name]['tpu']['predicted']:
#         item['tag'] = item['object']
#         conf=float(item['confidence'])
#         del(item['confidence'])
#         item['confidence'] = conf
#         del(item['object'])
#     for item in tags[pic_name]['gpu']['predicted']:
#         item['tag'] = item['object']
#         conf=float(item['confidence'])
#         del(item['confidence'])
#         item['confidence'] = conf
#         del(item['object'])


#do actual ground truth if required
if config['do_actual'] == True:
    accumulative_response_time = 0
    for i in range(1,pics_num + 1):
        #azure free tier allows only 20 calls per minutes, so this sleep times mitigates charged calls
        time.sleep(4)
        
        #timing
        start = time.time()

        #get pic
        pic_name = pics_name_format.replace('#num#', str(i))
        
        local_image = open(path + pic_name, 'rb')

        # Select visual feature type(s)
        local_image_features = ["categories"]
        local_image_features = [VisualFeatureTypes.categories,VisualFeatureTypes.brands,VisualFeatureTypes.adult,VisualFeatureTypes.color,VisualFeatureTypes.description,VisualFeatureTypes.faces,VisualFeatureTypes.image_type,VisualFeatureTypes.objects,VisualFeatureTypes.tags]
        # Call API
        categorize_results_local = computervision_client.analyze_image_in_stream(local_image, local_image_features)   

        #elapsed
        accumulative_response_time += time.time() - start

        # Return tags
        # Print results with confidence score
        print("Tags in the remote image: ")
        if (len(categorize_results_local.tags) == 0):
            print("No tags detected.")
        else:
            for tag in categorize_results_local.tags:
                print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))

        #get tags
        for j in range(len(categorize_results_local.tags)):
            tag = {'tag': categorize_results_local.tags[j].name, 'confidence': categorize_results_local.tags[j].confidence * 100}
            tags[pic_name]['actual'].append(tag)
        
    print('######################### Avg Response Time of Cloud ( accumulative response time /pics_num')   
    print(str(accumulative_response_time/float(pics_num)))
        
        
        

#do prediction if required
if config['do_predict'] == True:
    #inference for tagging pics per url
    for i in range(1,pics_num + 1):
        #get pic
        pic_name = pics_name_format.replace('#num#', str(i))

        #cpu
        if 'cpu' in urls and urls['cpu']:

            files = {'image_file': open(path + pic_name, 'rb'),}

            response = requests.get(urls['cpu'], files=files)
            print('######### ' + pic_name + ': cpu\n' + str(response.text))
            detected_objects = json.loads(response.text)

            #push to tags
            tags[pic_name]['cpu']['detected_objects'] = detected_objects['detected_objects']

        #tpu
        if 'tpu' in urls and urls['tpu']:

            files = {'image_file': open(path + pic_name, 'rb'),}

            response = requests.get(urls['tpu'], files=files)
            print('######### ' + pic_name + ': tpu\n' + str(response.text))
            detected_objects = json.loads(response.text)

            #push to tags
            tags[pic_name]['tpu']['detected_objects'] = detected_objects['detected_objects']

        #gpu
        if 'gpu' in urls and urls['gpu']:

            files = {'image_file': open(path + pic_name, 'rb'),}

            response = requests.get(urls['gpu'], files=files)
            print('######### ' + pic_name + ': gpu\n' + str(response.text))
            detected_objects = json.loads(response.text)

            #push to tags
            tags[pic_name]['gpu']['detected_objects'] = detected_objects['detected_objects']
    

#measure metricsif required
if config['metrics'] == True:
    precision = {'cpu': 0.0, 'tpu': 0.0, 'gpu': 0.0}
    recall = {'cpu': 0.0, 'tpu': 0.0, 'gpu': 0.0}
    f_measure = {'cpu': 0.0, 'tpu': 0.0, 'gpu': 0.0}
    sum_tp = {'cpu': 0, 'tpu': 0, 'gpu': 0}
    sum_fp = {'cpu': 0, 'tpu': 0, 'gpu': 0}
    sum_fn = {'cpu': 0, 'tpu': 0, 'gpu': 0}

    #all pics
    for i in range(1,pics_num + 1):
        #get pic_name
        pic_name = pics_name_format.replace('#num#', str(i))

        #get pic item
        pic = tags[pic_name]

        #metrics_max_tags_num
        max_tags_num = config['metrics_max_tags_num']

        #list of dicts( tag and confidence values)
        actual = pic['actual']
        #list of tags values with confidence > actual_min_threshold
        actual_tags = [v for item in actual for k,v in item.items() if k == 'tag' and item['confidence'] > config['actual_min_threshold']]
        

        #list of dicts( tag and confidence values)
        predictions = {'cpu':[], 'tpu':[], 'gpu':[]}
        #list of tags values
        predictions_tags = {'cpu':[], 'tpu':[], 'gpu':[]}

        #list of dicts( tag and confidence values)
        predictions['cpu'] = pic['cpu']['predicted']
        #list of tags values
        # predictions_tags['cpu'] = [v for item in predictions['cpu'] for k,v in item.items() if k == 'tag' and predictions['cpu'].index(item) < max_tags_num]
        for item in predictions['cpu']:
            if item['confidence'] < config['predict_min_threshold']:
                continue
            #get tag
            predictions_tags['cpu'].append(item['tag'])
            #keep only unique values
            predictions_tags['cpu'] = list(set(predictions_tags['cpu']))
            #if max reached, stop
            if len(predictions_tags['cpu']) == max_tags_num:
                break

        
        #list of dicts( tag and confidence values)
        predictions['tpu'] = pic['tpu']['predicted']
        #list of tags values
        # predictions_tags['tpu'] = [v for item in predictions['tpu'] for k,v in item.items() if k == 'tag' and predictions['tpu'].index(item) < max_tags_num]
        for item in predictions['tpu']:
            if item['confidence'] < config['predict_min_threshold']:
                continue
            #get tag
            predictions_tags['tpu'].append(item['tag'])
            #keep only unique values
            predictions_tags['tpu'] = list(set(predictions_tags['tpu']))
            #if max reached, stop
            if len(predictions_tags['tpu']) == max_tags_num:
                break
        
        #list of dicts( tag and confidence values)
        predictions['gpu'] = pic['gpu']['predicted']
        #list of tags values
        # predictions_tags['gpu'] = [v for item in predictions['gpu'] for k,v in item.items() if k == 'tag' and predictions['gpu'].index(item) < max_tags_num]
        for item in predictions['gpu']:
            if item['confidence'] < config['predict_min_threshold']:
                continue
            #get tag
            predictions_tags['gpu'].append(item['tag'])
            #keep only unique values
            predictions_tags['gpu'] = list(set(predictions_tags['gpu']))
            #if max reached, stop
            if len(predictions_tags['gpu']) == max_tags_num:
                break

        # if i == 1:
        #     print(predictions['tpu'])
        #     print(pic_name)
        #     print('actual_tags= ' + str(actual_tags))
        #     print('pred_tags_cpu= ' + str( predictions_tags['cpu']))
        #     print('pred_tags_tpu= ' + str( predictions_tags['tpu']))
        #     print('pred_tags_gpu= ' + str( predictions_tags['gpu']))

        #precision = true positives / (true positives + false positives)

        #cpu
        #true positives and false positives
        tp = 0; fp = 0; fn = 0; tn = 0

        for tag in predictions_tags['cpu']:

            is_found =False

            #if the predicted tag is found in any part of an actual tags, it is okay
            if any(tag in actual_tag for actual_tag in actual_tags):
                tp +=1
                is_found = True
            #or if matching is enabled and  any of tags matching with the predicted tag is found in any part of the an actual tags, it is okay
            elif config['matching_enabled'] == True:
                matched_tags = [item for item in matches if tag in item]
                if not matched_tags: 
                    matched_tags =[]
                else:
                    matched_tags = matched_tags[0]
                    
                for matched_tag in matched_tags:
                    if any(matched_tag in actual_tag for actual_tag in actual_tags):
                        tp +=1
                        is_found=True
                        break
            #tag not found in actual
            if not is_found:
                fp +=1
        #fn
        fn = len(actual_tags) - tp

        #set tp
        tags[pic_name]['cpu']['tp'] = tp
        #set fp
        tags[pic_name]['cpu']['fp'] = fp
        #set fn
        tags[pic_name]['cpu']['fn'] = fn

        #add sum
        sum_tp['cpu'] += tp
        sum_fp['cpu'] += fp
        sum_fn['cpu'] += fn

        #tpu
        #true positives and false positives
        tp = 0; fp = 0
        for tag in predictions_tags['tpu']:

            is_found = False

            #if the predicted tag is found in any part of an actual tags, it is okay
            if any(tag in actual_tag for actual_tag in actual_tags):
                tp +=1
                is_found = True

            #or if matching is enabled and  any of tags matching with the predicted tag is found in any part of the an actual tags, it is okay
            elif config['matching_enabled'] == True:
                matched_tags = [item for item in matches if tag in item]
                if not matched_tags: 
                    matched_tags =[]
                else:
                    matched_tags = matched_tags[0]

                for matched_tag in matched_tags:
                    if any(matched_tag in actual_tag for actual_tag in actual_tags):
                        tp +=1
                        is_found = True
                        break
            #tag not found in actual
            if not is_found:
                fp +=1
        
        #fn
        fn = len(actual_tags) - tp

        #set tp
        tags[pic_name]['tpu']['tp'] = tp
        #set fp
        tags[pic_name]['tpu']['fp'] = fp
        #set fn
        tags[pic_name]['tpu']['fp'] = fn

        #add sum
        sum_tp['tpu'] += tp
        sum_fp['tpu'] += fp
        sum_fn['tpu'] += fn

        #gpu
        #true positives and false positives
        tp = 0; fp = 0
        for tag in predictions_tags['gpu']:
            
            is_found = False

            #if the predicted tag is found in any part of an actual tags, it is okay
            if any(tag in actual_tag for actual_tag in actual_tags):
                tp +=1
                is_found = True

            #or if matching is enabled and  any of tags matching with the predicted tag is found in any part of the an actual tags, it is okay
            elif config['matching_enabled'] == True:
                matched_tags = [item for item in matches if tag in item]
                if not matched_tags: 
                    matched_tags =[]
                else:
                    matched_tags = matched_tags[0]
                for matched_tag in matched_tags:
                    if any(matched_tag in actual_tag for actual_tag in actual_tags):
                        tp +=1
                        is_found= True
                        break
            if not is_found:
                fp +=1
        
        #fn
        fn = len(actual_tags) - tp

        #set tp
        tags[pic_name]['gpu']['tp'] = tp
        #set fp
        tags[pic_name]['gpu']['fp'] = fp
        #set fp
        tags[pic_name]['gpu']['fn'] = fn

        #add sum
        sum_tp['gpu'] += tp      
        sum_fp['gpu'] += fp
        sum_fn['gpu'] += fn
        
    print('max ' + str(max_tags_num))
    #avg metrics
    print('sum_tp_cpu=' + str(sum_tp['cpu']))
    print('sum_fp_cpu=' + str(sum_fp['cpu']))
    print('sum_fn_cpu=' + str(sum_fn['cpu']))
    print('sum_tp_tpu=' + str(sum_tp['tpu']))
    print('sum_fp_tpu=' + str(sum_fp['tpu']))
    print('sum_fn_tpu=' + str(sum_fn['tpu']))
    print('sum_tp_gpu=' + str(sum_tp['gpu']))
    print('sum_fp_gpu=' + str(sum_fp['gpu']))
    print('sum_fn_gpu=' + str(sum_fn['gpu']))

    #precision
    precision['cpu'] = sum_tp['cpu'] / (sum_tp['cpu'] + sum_fp['cpu'])
    precision['tpu'] = sum_tp['tpu'] / (sum_tp['tpu'] + sum_fp['tpu'])
    precision['gpu'] = sum_tp['gpu'] / (sum_tp['gpu'] + sum_fp['gpu'])

    print('precision=' + str(precision))

    #recall
    recall['cpu'] = sum_tp['cpu'] / (sum_tp['cpu'] + sum_fn['cpu'])
    recall['tpu'] = sum_tp['tpu'] / (sum_tp['tpu'] + sum_fn['tpu'])
    recall['gpu'] = sum_tp['gpu'] / (sum_tp['gpu'] + sum_fn['gpu'])

    print('recall= ' + str(recall))

    #f-measure, f1-score or f-score
    f_measure['cpu'] = (2 * precision['cpu'] * recall['cpu']) / (precision['cpu'] + recall['cpu'])
    f_measure['tpu'] = (2 * precision['tpu'] * recall['tpu']) / (precision['tpu'] + recall['tpu'])
    f_measure['gpu'] = (2 * precision['gpu'] * recall['gpu']) / (precision['gpu'] + recall['gpu'])

    print('F-measure= ' + str(f_measure))

#write to json file
with open(json_write_file, "w") as outfile:
    json.dump(tags, outfile)



