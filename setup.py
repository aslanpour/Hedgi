import getpass
#first run main.py on PEERs

#epoch driver
test_name = ['test']

test_duration= 10 * 60 #####
#[0] position (e.g.,COORDINATOR, PEER, or -) [1] node (host) name [2] node ip
#for scheduling, max 5 nodes are considered.
nodes=[["COORDINATOR","master","10.0.0.90"],
       ["www", "w1","10.0.0.91"],
       ["www", "w2","10.0.0.92"],
       ["www", "w3","10.0.0.93"],
       ["www", "w4","10.0.0.94"],
       ["www", "w5","10.0.0.95"],
       ["www", "w6","10.0.0.96"],
       ["PEER", "w7","10.0.0.97"],]

accelerators = {'w1': [], 'w2': [], 'w3': [], 'w4': [], 'w5': ['gpu', 'tpu'], 'w6': [], 'w7': []}

#load balancing
gateway_function = {
    'api_version': 'openfaas.com/v1',
    'kind': 'Function', 
    'object_name': 'gw-func',
    'namespace': 'openfaas-fn',
    'image': 'aslanpour/ssd:cpu-tpu-amd64',
    'labels': {'com.openfaas.scale.min': '1',
                'com.openfaas.scale.max': '1'},
    'annotations': {'linkerd.io/inject': 'enabled'},
    'constraints': ['kubernetes.io/hostname=master']}
#'image': 'ghcr.io/openfaas/nodeinfo:latest'

#backends ???only for ssd apps
backends = [{'service': node[1] + '-' + 'ssd', 'weight': 1000} for node in nodes if node[0] == 'PEER']
# backends = [{'service':'w4-ssd','weight': 1000}, {'service':'w5-ssd','weight': 1000}]
#note: service_mesh paramter must be True. backends must contain nodes that are part of the test. Backends service name must be equal to functions name.
load_balancing = [
    {'type': 'trafficsplit',
    'interval': 60,
    'algorithm': 'even',
    'accelerators': accelerators, 
    'backends': backends,
    'api_version': 'split.smi-spec.io/v1alpha2',
    'kind': 'TrafficSplit', 
    'object_name': 'my-traffic-split',
    'namespace': 'openfaas-fn',
    'service': gateway_function['object_name'],
    'operation': 'safe-patch',
    'gateway_function': gateway_function}
]

#NOTE if True, queues must be already created! and follows the name pattern as queue-worker-functionName
multiple_queue=False
#if true, Linkerd is required for OpenFaaS
service_mesh=True

gateway_IP = "10.0.0.90"
openfaas_gateway_port = "31112"
redis_server_ip= "10.43.189.161" #assume default port is selected as 3679
#??routes can replace gateway_IP, openfaas_gateway_port, redis_server_ip
routes = [{'gateway_IP': '10.0.0.90', 
        'openfaas_gateway_port': '31112', 
        'function_route': load_balancing[0]['service'] if load_balancing[0]['type'] == 'trafficsplit' else 'func_name',
        'redis_server_ip': '10.43.189.161'},
        # {'gateway_IP': '10.0.0.90', 
        # 'openfaas_gateway_port': '31112', 
        # 'function_route': load_balancing[1]['service'] if load_balancing[1]['type'] == 'trafficsplit' else 'func_name',
        # 'redis_server_ip': '10.43.189.161'},
        # {'gateway_IP': '10.0.0.90', 
        # 'openfaas_gateway_port': '31112', 
        # 'function_route': load_balancing[2]['service'] if load_balancing[2]['type'] == 'trafficsplit' else 'func_name',
        # 'redis_server_ip': '10.43.189.161'},
        # {'gateway_IP': '10.0.0.90', 
        # 'openfaas_gateway_port': '31112', 
        # 'function_route': load_balancing[3]['service'] if load_balancing[3]['type'] == 'trafficsplit' else 'func_name',
        # 'redis_server_ip': '10.43.189.161'},
        ]


#local #default-kubernetes #random #bin-packing #greedy #shortfaas
scheduler_name = ["local"]
#zonal categorization by Soc %
#[0] zone [1] priority [2] max Soc threshold [3] min Soc threshold
zones = [["rich", 1, 100, 60],
        ["vulnerable", 3, 60, 30],
        ["poor", 2, 30, 10],
        ["dead", 4, 10, -1]] #-1 means 0
#if 1250=100%, then 937.5=75%, 312.5=25% and 125=10%

#plugins and weights for shortfaas scoring
plugins = [{'energy':100, 'locally':100, 'sticky':30},
           {'energy':100, 'locally':100, 'sticky':30},
           {'energy':100, 'locally':100, 'sticky':30},
           {'energy':100, 'locally':100, 'sticky':30},]


#==0 only if scheduler_name=="greedy" and warm_scheduler=True
#and should be limited just in case function is not locally placed. (not implemented yet this part), so it is applied all the time if used
#this time takes for newly up node to be ready to send_sensors
boot_up_delay = 0   ####
#scheduler_greedy_config
sticky = True # it requires offloading=True to be effective
stickiness = [0.2, 0.2, 0.2, 0.2, 0.2] #20% # it requires offloading=True to be effective #####
warm_scheduler = False # it requires offloading=True to be effective -- if true, workload will be generated and sent once the node is down.


#cpu frequency: governors: ondemand, powersave, performance, conservative
#set_frequencies for setting static frequencies is used only if governors is 'userspace'.
#key "governors" tells which governor must be used.
#sample min frequency: 600000
cpu_freq_config={"effect": ["LOAD_GENERATOR", "STANDALONE"],"governors": "ondemand",
    "set_min_frequencies": 0, "set_max_frequencies": 0, "set_frequencies": 600000}

cpu_governor = ['ondemand', 'ondemand', 'ondemand']
#??????????????????image name has gpu
apps = {"ssd": True, "yolo3": False, "irrigation":False, "crop-monitor": False, "short": False}
apps_image = {"ssd": "aslanpour/ssd:cpu-tpu", "yolo3": "aslanpour/yolo3-quick", "irrigation":"aslanpour/irrigation", "crop-monitor": "aslanpour/crop-monitor", "short": "aslanpour/short"}

#[WORKLOAD]
#"static" or "poisson" (concurrently) or "exponential" (interval) or "exponential-poisson"
Workload_type ="static"
worker = "thread"  # or "gevent": low CPU usage (~5% improvement) but slower admission (0.098s vs 0.1s) and super difference between the max values.
seed = 5
session_enabled = True #if false, workload generator issues a new HTTP connection per request. On a Pi 3, sessions improve admission time by 25%, CPU usage 8% and memory 2% than new HTTP connection per request on Pi 3.

#Stages - Note: if max concurrently is more than 10 times the original concurrently, adjust the max_pool for requests.session.
shape_OFF = [{"stageStartTimePercent":None, "stageEndTimePercent": None, "stageConcurrentlyStart": None, "stageConcurrentlyEnd": None,"stageSlope": None, "stageStepLength": None},]
shape_RampUp5 = [{"stageStartTimePercent":None, "stageEndTimePercent": None, "stageConcurrentlyStart": None, "stageConcurrentlyEnd": 3,"stageSlope": None, "stageStepLength": None},]
shape_HalfRampUp5Down = [{"stageStartTimePercent":None, "stageEndTimePercent": 50, "stageConcurrentlyStart": None, "stageConcurrentlyEnd": 3,"stageSlope": None, "stageStepLength": None},
                        {"stageStartTimePercent":50.01, "stageEndTimePercent": None, "stageConcurrentlyStart": 5, "stageConcurrentlyEnd": None,"stageSlope": None, "stageStepLength": None},]

shapes = {"w1":shape_OFF, "w2":shape_OFF, "w3":shape_OFF, "w4":shape_OFF, "w5": shape_OFF, "w6": shape_OFF, "w7": shape_OFF}

#[0]: ssd, [1]: yolo3, [2]: irrigation, [3]: crop-monitor, [4]: short
#[x][0] iteration [x][1]interval/exponential lambda (lambda~=avg)
#[x][2]concurrently/poisson lambda (lambda~=avg) [x][3] random seed (def=5)]
# [x][4] shape, [x][5] worker "thread" or "gevent"
#in the main.py is w_config = my_app[3] --> w_config[0-3]
#if static, only set int values ????? otherwise, workload() gives error.
workload_cfg ={
"w1":[[1000, 5, 1,seed, shapes["w1"],worker], [10000, 6, 1.9,seed, shapes["w1"],worker], [10000, 10, 1,seed, shapes["w1"],worker], [10000, 1, 1,seed, shapes["w1"],worker], [10000, 1, 1,seed, shapes["w1"],worker]],
"w2":[[1000, 5, 1,seed, shapes["w2"],worker], [10000, 20, 1.9,seed, shapes["w2"],worker], [10000, 15, 1.0,seed, shapes["w2"],worker], [10000, 1, 1,seed, shapes["w2"],worker], [10000, 1, 1,seed, shapes["w2"],worker]],
"w3":[[1000, 60, 0.6,seed, shapes["w3"],worker], [10000, 10, 1.9,seed, shapes["w3"],worker], [10000, 8, 1.0,seed, shapes["w3"],worker], [10000, 10, 1,seed, shapes["w3"],worker], [10000, 10, 1,seed, shapes["w3"],worker]],
"w4":[[1000, 1, 1,seed, shapes["w4"],worker], [10000, 10, 1.9,seed, shapes["w4"],worker], [10000, 8, 1.0,seed, shapes["w4"],worker], [10000, 10, 1,seed, shapes["w4"],worker], [10000, 10, 1,seed, shapes["w4"],worker]],
"w5":[[1000, 1, 1,seed, shapes["w5"],worker], [10000, 6, 1.9,seed, shapes["w5"],worker], [10000, 5, 1.0,seed, shapes["w5"],worker], [10000, 10, 1,seed, shapes["w5"],worker], [10000, 10, 1,seed, shapes["w5"],worker]],
"w6":[[1000, 1, 1,seed, shapes["w6"],worker], [10000, 6, 1.9,seed, shapes["w6"],worker], [10000, 5, 1.0,seed, shapes["w6"],worker], [10000, 10, 1,seed, shapes["w6"],worker], [10000, 10, 1,seed, shapes["w6"],worker]],
"w7":[[1000, 1, 1,seed, shapes["w7"],worker], [10000, 6, 1.9,seed, shapes["w7"],worker], [10000, 5, 1.0,seed, shapes["w7"],worker], [10000, 10, 1,seed, shapes["w7"],worker],[10000, 10, 1,seed, shapes["w7"],worker]],}

#copy chart-latest and chart-profile folders to home directory of master
profile_chart = ["chart-profile", "~/charts/chart-profile"]
function_chart = ["chart-latest", "~/charts/chart-latest"]
excel_file_path = "/home/" + getpass.getuser() + "/logs/metrics.xlsx" # this file should already be there with a sheet named nodes

clean_up = True #####
profile_creation_roll_out = 15  #### 30
function_creation_roll_out = 60  # 120


#CPU intensity of applications request per nodes per app
counter=[{"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"10", "short":"5"},
         {"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"50", "short":"30"},
         {"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"50", "short":"30"},
         {"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"50", "short":"30"},
         {"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"50", "short":"30"},
         {"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"50", "short":"30"},
         {"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"50", "short":"30"}]

monitor_interval=10 #second
scheduling_interval= [180, 300, 300, 300]  ### second -- default 5 *  60 equivalent to 30 min
failure_handler_interval=10
battery_sim_update_interval=30
min_request_generation_interval = 1
sensor_admission_timeout = 3
max_request_timeout = 30 #max timeout set for apps, used for timers, failure_handler, etc.

intra_test_cooldown = 1 * 60 # 10 between each epoch to wait for workers
debug=True #master always True
max_cpu_capacity = 3600  #### #actual capacity is 4000m millicpu (or millicores), but 10% is deducted for safety net. Jetson nano and Pi 3 and 4 have 4 cores.

initial_battery_charge = 2000
min_battery_charge = 125 #mwh equals battery charge 10%
max_battery_charge = [1250,1250,1250,1250] #mwh full battery, 9376 - 20% and scale in 1/6: 1250mwh
#home dir will be attached before this path by pi-agent
#pics folder must be already filled with pics
pics_folder = "/pics/"
file_storage_folder = "/storage/"
#home dir comes before
log_path = "/logs/"

#renewable_input type" real OR poisson
renewable_type = "real"
#renewable input by poisson: set lambda for each nodes
renewable_poisson = [0,0,0,0,0]
#renewable inputs by real dataset: Melbourne CBD in 2018
renewable_real={
    "master":[],
    "w1":[0,0,0,0,0,67,252,486,694,877,1000,1068,1080,997,784,753,559,330,132,0,0,0,0,0],
    "w2":[0,0,0,0,0,68,239,448,701,882,999,1063,1051,557,689,249,72,338,134,0,0,0,0,0],
    "w3":[0,0,0,0,0,38,161,236,458,596,572,480,476,624,894,528,276,85,114,0,0,0,0,0],
    "w4":[0,0,0,0,0,19,76,101,525,164,679,588,282,484,362,349,269,65,41,0,0,0,0,0],
    "w5":[0,0,0,0,0,15,60,153,346,655,686,265,180,156,189,76,93,60,37,0,0,0,0,0],
    "w6":[0,0,0,0,0,15,60,153,346,655,686,265,180,156,189,76,93,60,37,0,0,0,0,0],
    "w7":[0,0,0,0,0,15,60,153,346,655,686,265,180,156,189,76,93,60,37,0,0,0,0,0],
} #####

#default=4 not sure if effective by updating on the fly
waitress_threads = 10
#NOTE:function name and queue name pattern is "node_name-function_name" like "w1-irrigation"
#Node_role: #MASTER #LOAD_GENERATOR #STANDALONE #MONITOR

#scheduling is based on requests, not limits


#two replica: request --- burstable : irrigation 400-600, crop 300-450 and short 100-150
app_cpu_quote = {"ssd":["1000m", "3600m"],
                "yolo3":["3000m", "3000m"],
                "irrigation": ["600m", "600m"],
                "crop-monitor": ["450m", "450m"],
                "short": ["100m", "100m"]}
app_memory_quote = {"ssd":["500M", "3000M"],
                    "yolo3":["500M", "500M"],
                    "irrigation": ["40M", "40M"],
                    "crop-monitor": ["30M", "30M"],
                    "short": ["200M", "200M"]}

#function_timeouts = {'yolo3':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'},
#                     'irrigation':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'},
#                     'crop-monitor':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'},
#                     'short':{'read':'15s', 'write':'15s', 'exec':'15s', 'handlerWait':'15s'}}
#function_timeout['yolo3']['read'], function_timeout['yolo3']['write'],
#function_timeout['yolo3']['exec'],function_timeout['yolo3']['handlerWait']

#USB METERs: Pair before tests
usb_meter={"master":"",
           "w1":"00:15:A5:00:03:E7",
           "w2":"00:15:A3:00:56:0F",
           "w3":"00:15:A3:00:52:2B",
           "w4":"00:15:A3:00:19:A7",
           "w5":"00:15:A3:00:5A:6F",
           "w6":"",
           "w7":"00:16:A5:00:0E:94"}
#Mohammad Goudarzi one ""
#broken USB meter: "00:15:A5:00:02:ED", "00:15:A3:00:68:C4"
#either battery_operated or battery_sim should be enabled
battery_operated = {"master": False, "w1": False, "w2": False, "w3": False,"w4": False,"w5": False,"w6": False,"w7": False} #means pijuice operated
battery_sim = {"master": False, "w1": True, "w2": True, "w3": True,"w4": True,"w5": True, "w6": True, "w7": True,}

#autoscaling
scale_to_zero = False #(not implemented yet)

#auto-scaling:  "openfaas"  or "hpa"
auto_scaling = "openfaas"
#factor: default is 20, if 0, if hpa, auto-scaling by hpa, otherwise openfaas scaling is disabled
auto_scaling_factor = 100
#if HPA is used, function objects get 1 for both min and max, instead HPA object applies these values.
min_replicas = {"ssd": 1, "yolo3": 1, "crop-monitor":2, "irrigation":2, "short":1}
max_replicas = {"ssd": 1, "yolo3": 1, "crop-monitor":2, "irrigation":2, "short":10} ####
#if HPA is used, set avg CPU utilization condition
avg_cpu_utilization = 60
#if HPA is used, set scale down stabilaztion window
scale_down_stabilizationWindowSeconds = 60
            
            

#Plan by node names
plan={
"master":{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"MASTER",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["master"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8]func_info -->[min,max,memory requests, memory limits, cpu request, cpu limit, env.counter, env.redisServerIp, env,redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile, version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w1"][0], 'master-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w1"][0], 'master-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w1"][1], 'master-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w1"][2], 'master-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w1"][3], 'master-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
    "peers":[],
    "usb_meter_involved":False,
    "battery_operated":battery_operated["master"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
    "battery_cfg":[battery_sim["master"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[0]], renewable_real["master"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":True,
    "cpu_freq_config": cpu_freq_config,},
#w1
"w1":
{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"LOAD_GENERATOR",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["w1"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8][min,max,mem requests,mem limits, cpu req, cpu limits,counter, redisServerIp, redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w1"][0], 'w1-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w1"][0], 'w1-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w1"][1], 'w1-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w1"][2], 'w1-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w1"][3], 'w1-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
    "peers":[],
    "usb_meter_involved":True,
    "battery_operated":battery_operated["w1"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge, 9 turned on at
    "battery_cfg":[battery_sim["w1"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[0]], renewable_real["w1"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":False,
    "cpu_freq_config": cpu_freq_config,},

#w2
"w2":{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"LOAD_GENERATOR",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["w2"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
        #??????unknown refer to profiles in openfaas and is only for filtering maximum of 5 nodes. 
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w2"][0], 'w2-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0,  apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w2"][0], 'w2-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0,  apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w2"][1], 'w2-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w2"][2], 'w2-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w2"][3], 'w2-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
    "peers":[],
    "usb_meter_involved":True,
    "battery_operated":battery_operated["w2"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
    "battery_cfg":[battery_sim["w2"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[1]], renewable_real["w2"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":False,
    "cpu_freq_config": cpu_freq_config,},

#w3
"w3":{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"LOAD_GENERATOR",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["w3"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w3"][0], 'w3-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w3"][0], 'w3-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w3"][1], 'w3-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w3"][2], 'w3-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w3"][3], 'w3-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
    "peers":[],
    "usb_meter_involved":True,
    "battery_operated":battery_operated["w3"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
    "battery_cfg":[battery_sim["w3"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[2]], renewable_real["w3"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":False,
    "cpu_freq_config": cpu_freq_config,},

#w4
"w4":{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"LOAD_GENERATOR",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["w4"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w4"][0], 'w4-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w4"][0], 'w4-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w4"][1], 'w4-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w4"][2], 'w4-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w4"][3], 'w4-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]]],
    "peers":[],
    "usb_meter_involved":True,
    "battery_operated":battery_operated["w4"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge, 9 turned on at
    "battery_cfg":[battery_sim["w4"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[3]], renewable_real["w4"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":False,
    "cpu_freq_config": cpu_freq_config,},

#w5
"w5":{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"LOAD_GENERATOR",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["w5"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w5"][0], 'w5-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w5"][0], 'w5-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w5"][1], 'w5-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w5"][2], 'w5-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w5"][3], 'w5-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],],
    "peers":[],
    "usb_meter_involved":True,
    "battery_operated":battery_operated["w5"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
    "battery_cfg":[battery_sim["w5"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[4]], renewable_real["w5"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":False,
    "cpu_freq_config": cpu_freq_config,},

#w6
"w6":{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"LOAD_GENERATOR",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["w6"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w6"][0], 'w6-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w6"][0], 'w6-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w6"][1], 'w6-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w6"][2], 'w6-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w6"][3], 'w6-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],],
    "peers":[],
    "usb_meter_involved":True,
    "battery_operated":battery_operated["w6"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
    "battery_cfg":[battery_sim["w6"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[4]], renewable_real["w6"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":False,
    "cpu_freq_config": cpu_freq_config,},
#w7
"w7":{
    "test_name": "",
    #MONITOR #LOAD_GENERATOR #STANDALONE #SCHEDULER
    "node_role":"LOAD_GENERATOR",
    "gateway_IP":gateway_IP,
    "openfaas_gateway_port": openfaas_gateway_port,
    "routes": routes,
    "debug":True,
    "bluetooth_addr":usb_meter["w7"],
    #[0]app name
    #[1] run/not
    #[2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
    #[3] workload_cfg
    #[4] func_name [5] func_data [6] sent [7] recv
    #[8][min,max,requests,limits,env.counter, env.redisServerIp, env,redisServerPort,
    #read,write,exec,handlerWaitDuration,linkerd,queue,profile,version
    #[9]nodeAffinity_required_filter1,nodeAffinity_required_filter2,nodeAffinity_required_filter3,
        # nodeAffinity_preferred_sort1,podAntiAffinity_preferred_functionName,
        # podAntiAffinity_required_functionName
    "apps":[
        ['ssd', apps["ssd"], Workload_type, workload_cfg["w7"][0], 'w7-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], Workload_type, workload_cfg["w7"][0], 'w7-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], Workload_type, workload_cfg["w7"][1], 'w7-irrigation', 'value', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], Workload_type, workload_cfg["w7"][2], 'w7-crop-monitor', 'value', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], Workload_type, workload_cfg["w7"][3], 'w7-short', 'value', 0, 0,
           [min_replicas["short"], max_replicas["short"], app_memory_quote["short"][0],app_memory_quote["short"][1],app_cpu_quote["short"][0], app_cpu_quote["short"][1], counter[0]["short"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-short" if multiple_queue else ""), "",0, apps_image["short"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],],
    "peers":[],
    "usb_meter_involved":True,
    "battery_operated":battery_operated["w7"],
    #1:max,2:initial #3current SoC,
    #4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge , 9 turned on at
    "battery_cfg":[battery_sim["w7"], 0,initial_battery_charge, initial_battery_charge,
        renewable_type,[seed,renewable_poisson[4]], renewable_real["w7"],
        battery_sim_update_interval, min_battery_charge, 0],
    "time_based_termination":[True, test_duration],
    "monitor_interval":monitor_interval,
    "failure_handler_interval":failure_handler_interval,
    "max_request_timeout":max_request_timeout,
    "min_request_generation_interval": min_request_generation_interval,
    "session_enabled": session_enabled,
    "sensor_admission_timeout": sensor_admission_timeout,
    "max_cpu_capacity": max_cpu_capacity,
    "log_path": log_path,
    "pics_folder":pics_folder,
    "file_storage_folder":file_storage_folder,
    "waitress_threads": waitress_threads,
    "boot_up_delay": boot_up_delay,
    #only master is True
    "raspbian_upgrade_error":False,
    "cpu_freq_config": cpu_freq_config,}
}


#openfaas setup chart 8.0.4
#Gateway: version 0.21.1
#replicas: 5, direct_functions=false, read_timeout:35s, write_timeout: 35s, upstream_timeout: 30s, operator:true, read_timeout: 30s, write_timeout: 30s

#gueue: version per app
#replicas: 2, ack_wait: 30s, max_inflight: 100, max_retry_attempt: 1, max_retry_wait: 10s, retry_http_code: 429,,
