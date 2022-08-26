from gevent import monkey;monkey.patch_all() #for gevent use: this allows async gevent (without it pool.join() is needed so gevents wrok that will block the workload generator) and must be placed before import Flask
from flask import Flask, request, send_file, make_response, json  # pip3 install flask
from waitress import serve  # pip3 install waitress
import requests  # pip3 install requests
import threading
import logging
import datetime
import time
import math
# Monitor
import psutil
from cpufreq import cpuFreq
import numpy as np
import statistics  # for using satistics.mean()  #numpy also has mean()
import re
import copy
import utils
if utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4'):
    import RPi.GPIO as GPIO
    from pijuice import PiJuice  # sudo apt-get install pijuice-gui
from bluetooth import *  # sudo apt-get install bluetooth bluez libbluetooth-dev && sudo python3 -m pip install pybluez
# sudo systemctl start bluetooth
# echo "power on" | bluetoothctl
import random
import socket
import os  # file path
import shutil  # empty a folder
import subprocess as sp  # to run cmd to disconnect Bluetooth
import getpass
# setup file exists?
dir_path = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(dir_path + "/setup.py"): import setup
if os.path.exists(dir_path + "/excel_writer.py"): import excel_writer  # pip3 install pythonpyxl
from os.path import expanduser  # get home directory by home = expanduser("~")
if os.path.exists(dir_path + "/pyhpa.py"): import pyhpa
if os.path.exists(dir_path + "/pyloadbalancing.py"): import pyloadbalancing
if os.path.exists(dir_path + "/pymanifest.py"): import pymanifest
if os.path.exists(dir_path + "/pykubectl.py"): import pykubectl

app = Flask(__name__)
app.config["DEBUG"] = True

from gevent.pool import Pool
from gevent import Timeout

session_enabled = False


# config
node_name = socket.gethostname()
node_role = ""  # MONITOR #LOAD_GENERATOR #STANDALONE #MASTER


def set_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    actual_ip = s.getsockname()[0]
    s.close()
    return actual_ip


node_IP = set_ip()
gateway_IP = "10.0.0.90"  # ??? set individually
peers = []
test_index = 0
test_updates = {}

epoch = 0
test_name = socket.gethostname() + "_test"
workers = []
functions = []
history = {'functions': {}, 'workers': {}}
metrics = {}

sessions = {}

debug = False
waitress_threads = 6  # default is 4
try:
    cpuFreq = cpuFreq()
except FileNotFoundError as e:
    #This error happens for intel devices since Intel is not publishing available frequencies, ref: https://askubuntu.com/questions/1064269/cpufrequtils-available-frequencies
    #Instead, all CPU informations are in files located in 'cd /sys/devices/system/cpu/cpu0/cpufreq'
    #Collect informations by 'paste <(ls *) <(cat *) | column -s $'\t' -t'
    #???If an Intel device is part of experiments + measurements, this is not considering them.
    cpuFreq = None
    print('cpuFreq object is not created. If this is a master node and Intel, dismiss it.\n' + str(e))

# get home directory
home = expanduser("~")
log_path = home + "/" + test_name
if not os.path.exists(log_path):
    os.makedirs(log_path)

bluetooth_addr = "00:15:A3:00:52:2B"
# master: #00:15:A3:00:52:2B #w1: 00:15:A3:00:68:C4 #w2: 00:15:A5:00:03:E7 #W3: 00:15:A5:00:02:ED #w4: 00:15:A3:00:19:A7 #w5: 00:15:A3:00:5A:6F
pics_folder = "/home/" + getpass.getuser()+ "/pics/"
pics_num = 170  # pics name "pic_#.jpg"
file_storage_folder = "/home/" + getpass.getuser() + "/storage/"
if not os.path.exists(file_storage_folder):
    os.makedirs(file_storage_folder)
# settings
# [0]app name
# [1] run/not
# [2] w type: "static" or "poisson" or "exponential" or "exponential-poisson"
# [3] workload: [[0]iteration
# [1]interval/exponential lambda(10=avg 8s)
# [2]concurrently/poisson lambda (15=avg 17reqs ) [3] random seed (def=5)]
# [4] func_name [5] func_data [6] created [7] recv
# [8][min,max,mem requests, mem limits, cpu req, cpu limits,env.counter, env.redisServerIp, env,redisServerPort,
# read,write,exec,handlerWaitDuration,linkerd,queue,profile
apps = []

usb_meter_involved = False
# Either battery_operated or battery_cfg should be True, if the second, usb meter needs enabling
battery_operated = False
# Battery simulation
# 1:max,2:initial #3current SoC,
# 4: renewable type, 5:poisson seed&lambda,6:dataset, 7:interval, 8 dead charge
battery_cfg = [True, 906, 906, 906, "poisson", [5, 5], [], 30, 90]
# NOTE: apps and battery_cfg values change during execution
down_time = 0
time_based_termination = [False, 3600]
snapshot_report = ['False', '200', '800']  # begin and end time
max_request_timeout = 30
min_request_generation_interval = 0
sensor_admission_timeout = 3
monitor_interval = 1
failure_handler_interval = 3
overlapped_allowed = True
max_cpu_capacity = 4000
boot_up_delay = 0
raspbian_upgrade_error = False  # True, if psutil io_disk error due to upgrade
# controllers
test_started = None
test_finished = None
under_test = False
lock = threading.Lock()
actuations = 0

sock = None  # bluetooth connection
sensor_log = {}
suspended_replies = []
# monitoring parameters
# in owl_actuator
response_time = []
# in monitor
response_time_accumulative = []
current_time = []
current_time_ts = []
battery_charge = []
cpuUtil = []
cpu_temp = []
cpu_freq_curr = []
cpu_freq_max = []
cpu_freq_min = []
cpu_ctx_swt = []
cpu_inter = []
cpu_soft_inter = []
memory = []
disk_usage = []
disk_io_usage = []
bw_usage = []

power_usage = []
throughput = []
throughput2 = []

if (utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4')) and battery_operated:
    relay_pin = 20
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    pijuice = PiJuice(1, 0x14)


def launcher(coordinator):
    global logger
    global node_name
    global node_IP
    logger.info('start')

    # set plan for coordinator itself.
    name = coordinator[1]
    ip = coordinator[2]
    plan = setup.plan[name]
    # config for multi-tests
    plan["test_name"] = setup.test_name[epoch]
    # set counter per app ???
    plan["apps"][0][8][6] = setup.counter[epoch]["ssd"]
    plan["apps"][1][8][6] = setup.counter[epoch]["yolo3"]
    plan["apps"][2][8][6] = setup.counter[epoch]["irrigation"]
    plan["apps"][3][8][6] = setup.counter[epoch]["crop-monitor"]
    plan["apps"][4][8][6] = setup.counter[epoch]["short"]
    # set battery size per test
    plan["battery_cfg"][1] = setup.max_battery_charge[epoch]
    # set cpu governor per test
    plan["cpu_freq_config"]["governors"] = setup.cpu_governor[epoch]
    # verify node_name
    if name != node_name:
        logger.error('MAIN: Mismatch node name: actual= ' + node_name + ' assigned= ' + name)
        return 'Mismatch node name: actual= ' + node_name + ' assigned= ' + name
    # verify assigned ip
    if ip != node_IP:
        logger.error('Mismatch node ip: actual= ' + node_IP + ' assigned= ' + ip)
        return ""

    sender = plan["node_role"]  # used in sending plan to peers
    logger.info(name + ' : ' + str(ip))
    # set local plan
    reply = main_handler('plan', 'INTERNAL', plan)

    if reply != "success":
        logger.error('INTERNAL interrupted and stopped')
        return "failed"

    reply_success = 0
    # set peers plan, sequentially, including USB Meter connection
    for node in setup.nodes:
        position = node[0]
        name = node[1]
        ip = node[2]
        plan = setup.plan[name]
        # config for multi-test
        plan["test_name"] = setup.test_name[epoch]
        # set counter per app ???
        plan["apps"][0][8][6] = setup.counter[epoch]["ssd"]
        plan["apps"][1][8][6] = setup.counter[epoch]["yolo3"]
        plan["apps"][2][8][6] = setup.counter[epoch]["irrigation"]
        plan["apps"][3][8][6] = setup.counter[epoch]["crop-monitor"]
        plan["apps"][4][8][6] = setup.counter[epoch]["short"]
        # set battery size per test
        plan["battery_cfg"][1] = setup.max_battery_charge[epoch]
        # set cpu governor per test
        plan["cpu_freq_config"]["governors"] = setup.cpu_governor[epoch]

        if position == "PEER":
            logger.info('peers:' + name + ': ' + str(ip))
            try:
                response = requests.post('http://' + ip + ':5000/main_handler/plan/' + sender, json=plan)
            except Exception as e:
                logger.error('peers: failed for ' + name + ":" + ip)
                logger.error('peers: exception:' + str(e))
                return
            if response.text == "success":
                logger.info(name + ' reply: ' + 'success')
                reply_success += 1
            else:
                logger.error('peers: request.text for ' + name + ' ' + str(response.text))

    # verify peers reply
    peers = len([node for node in setup.nodes if node[0] == "PEER"])
    if reply_success == peers:
        logger.info('all ' + str(peers) + ' nodes successful')

        # run local main_handler on
        logger.info('run all nodes main_handler')

        # internal
        thread_main_handler = threading.Thread(target=main_handler, args=('on', 'INTERNAL',))
        thread_main_handler.name = "main_handler"
        # it calls scheduler that initiates functions & workers and deploys functions also calls autoscaler
        thread_main_handler.start()
        # wait for initial function deployment roll-out
        logger.info('function roll out wait ' + str(setup.function_creation_roll_out) + 's')
        time.sleep(setup.function_creation_roll_out)

        # set peers on sequentially
        reply_success = 0
        for node in setup.nodes:
            position = node[0]
            name = node[1]
            ip = node[2]
            if position == "PEER":
                logger.info('main_handler on: peers:' + name + ': ' + str(ip))
                try:
                    response = requests.post('http://' + ip + ':5000/main_handler/on/' + sender)
                except Exception as e:
                    logger.error('main_handler on: peers: failed for ' + name + ":" + ip)
                    logger.error('main_handler on: peers: exception:' + str(e))
                if response.text == "success":
                    logger.info('main_handler on:' + name + ' reply: ' + 'success')
                    reply_success += 1
                else:
                    logger.info('main_handler on:' + name + ' reply: ' + str(response.text))
        # verify peers reply
        peers = len([node for node in setup.nodes if node[0] == "PEER"])
        if reply_success == peers:
            logger.info('main_handler on: all ' + str(peers) + ' nodes successful')
        else:
            logger.info('main_handler on: only ' + str(reply_success) + ' of ' + str(peers))

    else:
        logger.info('failed: only ' + str(reply_success) + ' of ' + str(len(setup.nodes)))
    logger.info('stop')

#load balancer
def load_balancer():
    global logger
    global under_test
    global debug
    global epoch
    global history
    #timing
    logger.info("started...")
    start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    
    #get config (as dict)
    load_balancing_config = setup.load_balancing[epoch]

    #history initializing
    history['load_balancer']= []
    #counter initializing
    load_balancing_round = 0
    
    #load balance
    while under_test:
        #[new round timing]
        now_ts = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        logger.info('Load balancing round #' + str(load_balancing_round) + ' started at ' + str(now_ts) + ' / ' + str(now))
        
        #[Add extra information to the config]

        #add round number and history to the config passed to algorithms
        load_balancing_config['load_balancing_round'] = load_balancing_round
        load_balancing_config['history'] = history['load_balancer']

        #and other data like energy SoC
        #?????


        #[plan]: run an algorithm and get updated plan for backends
        updated_backends_list, msg, error = pyloadbalancing.plan(**load_balancing_config)
            
        #add to history and update backends in config
        if not error:
            history['load_balancer'].append(updated_backends_list)
            load_balancing_config['backends'] = copy.deepcopy(updated_backends_list)
        else:
            logger.error('load_balancing plan failed \n' + str(error))
            time.sleep(3600)


        #build manifest, based on the especified 'Kind'
        manifest, msg, error = pymanifest.manifest_builder(**load_balancing_config)

        #include manifest into config and replace old one.
        if not error:
            load_balancing_config['manifest'] = copy.deepcopy(manifest)
        else:
            logger.error('load_balancing manifest builder failed \n' + str(error))
            time.sleep(3600)

        #execute
        kube_apply, msg, error = pykubectl.apply(**load_balancing_config)


    

        # sliced interval in 1 minutes
        logger.info('Load balancer done (round #' + str(load_balancing_round) + ') --- sleep for ' + str(
            load_balancing_config['interval']) + ' sec / ' + str(load_balancing_config['interval']/60) + ' min.')
        remained = load_balancing_config['interval']
        minute = 60
        while remained > 0:
            if remained >= minute:
                time.sleep(minute)
                remained -= minute
                if not under_test:
                    break
            else:
                time.sleep(remained)
                remained = 0


    # load balancer clean_up???
    logger.info('stop')


#autoscaler method
def autoscaler():
    global logger
    global under_test
    global debug
    global epoch
    global functions
    global history
    
    if setup.auto_scaling == "openfaas":
        logger.info("openfaas will handle the autoscaling by a request-per second policy")
        return None
    
    autoscaling_interval = 30
    
    #this thread is started after launcher method, so functions are already created.
    logger.info("started...")
    start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    #wait for the scheduler to initialize functions variable, then get functions name
    while functions == []:
        time.sleep(1)
    
    end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    logger.info("waited for functions variable to be set by scheduler for " + str(round(end-start,2)) + "s")
    #create HPA objects for functions and keep replacing them according to the load
    autoscaling_round = 0
    while under_test:
        autoscaling_round +=1
        logger.info("Started round #" + str(autoscaling_round))
        start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        
        for function in functions:
            # function = [identity, hosts[], func_info, profile]
            
            #identify function's name, i.e, from function[0]
            function_identity = function[0]
            
            function_node_name = function_identity[0] #e.g., "w1"
            function_app_name = function_identity[1] #e.g., "yolo3"
            function_name = function_node_name + "-" + function_app_name
            
            #get the following from function_info, i.e., from function[2]
            function_info = function[2]
            
            #set min replica
            min_replicas = function_info[0]
            #set max replicas
            max_replicas = function_info[1]
            
            #get the following from global values in setup.py file
            
            #set avg CPU utilization condition
            avg_cpu_utilization = setup.avg_cpu_utilization
            #set scale down stabilaztion window
            scale_down_stabilizationWindowSeconds = setup.scale_down_stabilizationWindowSeconds

            #create HPA
            pyhpa.auto_scaling_by_hpa(logger,
                                      function_name,
                                      min_replicas,
                                      max_replicas,
                                      avg_cpu_utilization,
                                      scale_down_stabilizationWindowSeconds)
        
        
        end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        
        #sleep
        # sliced interval in 1 minutes
        logger.info('End autoscaler round #' + str(autoscaling_round) + ' in ' + str(round(end-start,2)) + 's: sleep for ' + str(
            autoscaling_interval) + ' sec...')
        remained = autoscaling_interval
        minute = 60
        while remained > 0:
            sleep_duration = min(minute, remained)
            time.sleep(sleep_duration)
            remained -= sleep_duration
            if not under_test:
                break
    
    logger.info("stopped.")
    
    
# scheduler
def scheduler():
    global epoch
    global under_test
    global logger
    global debug
    global node_role
    global battery_cfg
    global workers
    global functions
    global max_cpu_capacity
    global log_path
    global history
    logger.info('start')

    # initialize workers and funcitons lists
    # default all functions' host are set to be placed locally
    workers, functions = initialize_workers_and_functions(setup.nodes, workers, functions,
                                                          battery_cfg, setup.plan, setup.zones)
    # history
    history["functions"] = {}
    history["workers"] = {}

    logger.info('after initialize_workers_and_functions:\n'
                + '\n'.join([str(worker) for worker in workers]))
    logger.info('after initialize_workers_and_functions:\n'
                + '\n'.join([str(function) for function in functions]))

    scheduling_round = 0
    while under_test:
        scheduling_round += 1
        logger.info('################################')
        logger.info('MAPE LOOP START: round #' + str(scheduling_round))
        # monitor: update Soc
        logger.info('monitor: call')
        workers = scheduler_monitor(workers, node_role)

        # ANALYZE (prepare for new placements)
        logger.info('analyzer: call')

        # definitions
        new_functions = copy.deepcopy(functions)

        # reset F's new location to null
        for new_function in new_functions:
            new_function[1] = []

        # reset nodes' capacity to max
        for worker in workers:
            worker[3] = setup.max_cpu_capacity

        # planner :workers set capacity, functions set hosts
        logger.info('planner: call: ' + str(setup.scheduler_name[epoch]))
        # Greedy
        if "greedy" in setup.scheduler_name[epoch]:
            workers, functions = scheduler_planner_greedy(workers, functions, new_functions,
                                                          setup.max_battery_charge[epoch], setup.zones,
                                                          setup.warm_scheduler,
                                                          setup.sticky, setup.stickiness[epoch], setup.scale_to_zero,
                                                          debug)
        # scoring
        elif "shortfaas" in setup.scheduler_name[epoch]:
            workers, functions = scheduler_planner_shortfaas(workers, functions, new_functions,
                                                             setup.max_battery_charge[epoch], setup.warm_scheduler,
                                                             setup.plugins[epoch], debug)
        # Local
        elif "local" in setup.scheduler_name[epoch]:
            workers, functions = scheduler_planner_local(workers, new_functions, debug)
        # Default-Kubernetes
        elif "default" in setup.scheduler_name[epoch]:
            workers, functions = scheduler_planner_default(workers, new_functions, debug)
        # Random
        elif "random" in setup.scheduler_name[epoch]:
            workers, functions = scheduler_planner_random(workers, new_functions, debug)
        # Bin-Packing
        elif "bin-packing" in setup.scheduler_name[epoch]:
            workers, functions = scheduler_planner_binpacking(workers, functions, new_functions, debug)
        # Optimal
        elif "optimal" in setup.scheduler_name[epoch]:
            pass
        else:
            logger.error('scheduler_name not found: ' + str(setup.scheduler_name[epoch]))
            return

        # EXECUTE
        logger.info('executor: call')
        # translate hosts to profile and then run helm command
        # return functions as it is modifying functions (i.e., profiles)
        functions = scheduler_executor(functions, setup.profile_chart,
                                       setup.profile_creation_roll_out,
                                       setup.function_chart, scheduling_round, log_path,
                                       setup.scheduler_name[epoch], workers, debug)

        # history
        history["functions"][scheduling_round] = copy.deepcopy(functions)
        history["workers"][scheduling_round] = copy.deepcopy(workers)

        # sliced interval in 1 minutes
        logger.info('MAPE LOOP (round #' + str(scheduling_round) + ') done: sleep for ' + str(
            setup.scheduling_interval[epoch]) + ' sec...')
        remained = setup.scheduling_interval[epoch]
        minute = 60
        while remained > 0:
            if remained >= minute:
                time.sleep(minute)
                remained -= minute
                if not under_test:
                    break
            else:
                time.sleep(remained)
                remained = 0

                # save history

    # scheduler clean_up???
    logger.info('stop')


# scoring
def scheduler_planner_shortfaas(workers, functions, new_functions,
                                max_battery_charge, warm_scheduler, plugins, debug):
    global logger
    # workers have full capacity available
    # new_functions have null as hosts

    logger.info("shortfaas:start")
    logger.info('shortfaas:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))

    # define and initialize scoring scheme
    scoring = {new_function[0][0] + '-' + new_function[0][1]:
                   {worker[0]:
                        {plugin: 0 for plugin in plugins}
                    for worker in workers} for new_function in new_functions}
    logger.info('shortfaas: set ' + '\n' + str(scoring))
    # add summations initialize
    for func, value in scoring.items():
        #
        for worker_name, value2 in scoring[func].items():
            scoring[func][worker_name]['sum_worker_scores'] = 0
        scoring[func]['sum_function_scores'] = 0
    # E.g.,
    # print(scoring['f1'])
    # print(scoring['f1']['w1'])
    # print(scoring['f1']['w1']['energy'])
    # print(scoring['f1']['sum_func_score'])
    # print(scoring['f1']['w1']['sum_worker_score'])

    logger.info('shortfaas: sum ' + '\n' + str(scoring))

    # calculate and set soc percent and normalize to -1-1 (index 4 of worker used for soc percent, instead of zone)
    for worker in workers:
        soc = worker[2]
        # assume all nodes have batteries of same size????
        # max_battery_charge = nodes_plan[worker[0]]["battery_cfg"][1]
        soc_percent = round(soc / max_battery_charge * 100)
        logger.info(worker[0] + ' soc : ' + str(soc_percent) + ' %')
        # normalize to 0-1
        worker[4] = round(soc_percent / 100, 2)

    logger.info('shortfaas:updated soc %:\n'
                + '\n'.join([str(worker) for worker in workers]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info('shortfaas: start setting scores per functions')
    for new_function in new_functions:
        # function_name
        function_name = new_function[0][0] + '-' + new_function[0][1]
        logger.info('shortfaas: functions **** ' + function_name + '  ****')
        logger.info('lworkers:\n'
                    + '\n'.join([str(worker) for worker in workers]))
        # function's old_hosts: last placement scheme
        old_hosts = copy.deepcopy([*(function[1] for function in functions if function[0] == new_function[0])][0])

        # old_hosts have soc value based on last epoch, so update them
        for index, old_host in enumerate(old_hosts):
            # update host's zone, capacity and Soc based on current status
            old_hosts[index] = [*(worker for worker in workers if worker[0] == old_host[0])][0]
        logger.info('old_hosts\n' + str(old_hosts))

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        owner_name = owner[0]
        # owner soc normalized
        owner_soc_normalized = copy.deepcopy(owner[4])

        logger.info('start scoring for ' + function_name)
        # score per node
        for worker in workers:
            worker_name = copy.deepcopy(worker[0])
            worker_soc_normalized = copy.deepcopy(worker[4])

            # per plugin
            # energy
            # deduct remote soc from owner
            scoring[function_name][worker_name]['energy'] = (round((
                                                                           worker_soc_normalized - owner_soc_normalized) *
                                                                   plugins['energy'], 2))

            # locally
            if owner_name == worker_name:
                # if itself, score locally
                scoring[function_name][worker_name]['locally'] = (round(
                    owner_soc_normalized * plugins['locally'], 2))
            else:
                # default 0
                pass

            # sticky
            # assume first replica (old_hosts[0]) location represents the whole replicas  ???
            if old_hosts[0][0] != owner_name:
                # has been offloaded in last round
                if old_hosts[0][0] == worker_name:
                    # if this worker was the last place
                    scoring[function_name][worker_name]['sticky'] = (
                        round(1 * plugins['sticky'], 2))
                else:
                    # default 0
                    pass
            else:
                # default 0
                pass
            # sum worker scores
            scoring[function_name][worker_name]['sum_worker_scores'] = (
                    scoring[function_name][worker_name]['energy']
                    + scoring[function_name][worker_name]['locally']
                    + scoring[function_name][worker_name]['sticky'])

        # sum function scores
        for key, value in scoring[function_name].items():
            worker_name = key
            # items, except the summation
            if worker_name != 'sum_function_scores':
                # add per worker
                scoring[function_name]['sum_function_scores'] += (
                    scoring[function_name][worker_name]['sum_worker_scores'])
        logger.info('shortfaas: end scoring for ' + function_name + '\n' +
                    str(scoring[function_name]))

    # end scoring
    logger.info('scoring done:' + '\n'.join(str(func) + str(info) for func, info in scoring.items()))

    # get a scores_tmp dict of function_name: sum_function_scores
    scores_tmp = {}  # function_name: sum_function_scores
    # create a dict
    for k, v in scoring.items():
        func_name = k
        sum_function_scores = v['sum_function_scores']
        scores_tmp[func_name] = sum_function_scores
    # sort dict (large to small)
    # scores_tmp={k: v for k,v in sorted(scores_tmp.items(), key=lambda item: item[],
    #                                                             reverse=True)}
    logger.info('scored functions in tmp \n' + str(scores_tmp))

    logger.info('*******    start placements    *******')
    # place by max score
    while len(scores_tmp):
        # get max scored functions
        function_name = max(scores_tmp.items(), key=lambda k: k[1])[0]  # key
        sum_function_scores = max(scores_tmp.items(), key=lambda k: k[1])[1]  # value
        logger.info('placement for ----- ' + function_name + '(sum scores=' + str(sum_function_scores) + ') -----')

        # get full function
        new_function = [*(new_function for new_function in new_functions if
                          new_function[0][0] == function_name.split('-')[0] and new_function[0][1] ==
                          function_name.split('-', 1)[1])][0]

        # function required capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_limits = int(new_function[2][5].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_limits * func_max_replica

        # placement
        # set new hosts
        new_hosts = []

        owner_name = function_name.split('-')[0]  # e.g. w1-irrigation
        owner = [*(worker for worker in workers if worker[0] == owner_name)][0]
        owner_soc = owner[2]
        logger.info('function owner \n' + str(owner))
        # if function not belong to a dead node
        if owner_soc >= battery_cfg[8]:
            # get max scored worker of this function
            max_score = float('-inf')  # minimum value, for max value remove '-' from inf
            selected_worker_name = ""

            nodes_score = scoring[function_name]
            for key, value in nodes_score.items():
                # keys: w1, w2, w3, sum_function_scores
                # e.g. {'w1': {'energy': 0, 'locally': 0, 'sticky': 0, 'sum_worker_score': 0}, 'w2': {'energy': 0, 'locally': 0, 'sticky': 0, 'sum_worker_score': 0}, 'sum_func_score': 1}
                # items, except 'sum_function_scores'
                if key != 'sum_function_scores':
                    if value['sum_worker_scores'] > max_score:
                        worker = [*(worker for worker in workers if worker[0] == key)][0]
                        # if capacity
                        if worker[3] >= func_required_cpu_capacity:
                            max_score = value['sum_worker_scores']
                            selected_worker_name = key

            # get the remote host
            worker = [*(worker for worker in workers if worker[0] == selected_worker_name)][0]

            # if offloading placement, first localize functions of remote host
            if worker[0] != owner_name:
                worker, new_functions, scores_tmp = localizer(worker, new_functions, scores_tmp)

            # set new_hosts
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(worker))
            logger.info('placement for  ' + function_name + '\n' + str(worker))
        else:
            # if owner is dead
            logger.info('(dead node) placement locally for ' + function_name)
            # how about functions belong to a dead node??? they are still scheduled locally
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        logger.info('deduct capacity for ' + function_name)
        # deduct function cpu requirement from worker's cpu capacity
        for new_host in new_hosts:
            # get selected worker index per replica
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_limits
            # update new_host, particulalrly its capacity
            new_host[3] = workers[index][3]

        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("shortfaas: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

        # delete
        del scores_tmp[function_name]

    # for loop: next new_function

    logger.info('shortfaas: done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


def getFunctionName(function):
    return function[0][0] + '-' + function[0][1]


def localizer(worker, new_functions, scores_tmp):
    global logger
    logger.info('localizer: start for worker ' + str(worker))
    logger.info('localizer: scores_tmp \n' + str(scores_tmp))
    worker_name = worker[0]

    # get functions of the worker
    for new_function in new_functions:
        # get function name
        function_name = getFunctionName(new_function)
        # get function owner
        function_owner = new_function[0][0]
        # if this function belongs to the worker, place locally
        if function_owner == worker[0]:
            logger.info('localizer: placement for ----- ' + function_name + ' -----')
            # if already placed, skip
            hosts = new_function[1]
            # if hosts not set yet
            if hosts != []:
                logger.info('localizer: already done, localizer skip for ' + function_name)
                continue
            # else place locally
            else:

                # function required capacity
                func_required_cpu_capacity = 0
                # exclude 'm'
                replica_cpu_limits = int(new_function[2][5].split('m')[0])
                func_max_replica = new_function[2][1]
                func_required_cpu_capacity = replica_cpu_limits * func_max_replica

                # placement
                # set new hosts
                new_hosts = []
                logger.info('localizer: placement locally for ' + function_name)
                for rep in range(func_max_replica):
                    new_hosts.append(copy.deepcopy(worker))

                # deduct capacity
                logger.info('localizer: deduct capacity for ' + function_name)
                # deduct function cpu requirement from worker's cpu capacity
                for new_host in new_hosts:
                    # deduct replica cpu requirement
                    worker[3] -= replica_cpu_limits
                    # update new_host, particulalrly its capacity
                    new_host[3] = worker[3]

                # set new_function new hosts
                new_function[1] = new_hosts
                if debug: logger.info("localizer: new_hosts for ("
                                      + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

                # delete
                del scores_tmp[function_name]
                logger.info('localizer: deleted scores_tmp: ' + str(scores_tmp))

    return worker, new_functions, scores_tmp


# -----------------
# ??? functions are received for only getting old_hosts. Only old_hosts can be sent to this planner
def scheduler_planner_greedy(workers, functions, new_functions, max_battery_charge, zones,
                             warm_scheduler, sticky, stickiness, scale_to_zero, debug):
    global logger
    logger.info("scheduler_planner_greedy:start")
    logger.info('scheduler_planner_greedy:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    zone_name = {1: 'rich', 2: 'poor', 3: 'vulnerable', 4: 'dead'}
    # update zones
    for worker in workers:
        soc = worker[2]
        # assume nodes have same size battery???
        # max_battery_charge = nodes_plan[worker[0]]["battery_cfg"][1]
        soc_percent = round(soc / max_battery_charge * 100)
        logger.info('soc percent: ' + str(soc_percent))
        new_zone = [*(zone[1] for zone in zones if soc_percent <= zone[2]
                      and soc_percent > zone[3])][0]
        worker[4] = new_zone

    logger.info('scheduler_planner_greedy:updated zones by Soc:\n'
                + '\n'.join([str(worker) for worker in workers]))

    # sort nodes by soc (large->small | descending)
    workers.sort(key=lambda x: x[2], reverse=True)
    logger.info('before showing : ' + str(workers))
    logger.info('scheduler_planner_greedy:sorted nodes by Soc (large->small):\n'
                + '\n'.join([str([worker, zone_name[worker[4]]]) for worker in workers]))
    logger.info('after showing : ' + str(workers))
    # sort functions: A: by priority of their owner's zone (small -> large | ascending)
    for i in range(len(new_functions)):
        lowest_value_index = i
        for j in range(i + 1, len(new_functions)):
            # find function's owner zone
            zone_j = [*(worker[4] for worker in workers if worker[0] == new_functions[j][0][0])][0]
            zone_lowest_value_index = \
            [*(worker[4] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
            # compare zone priorities
            if zone_j < zone_lowest_value_index:
                lowest_value_index = j
        # swap
        new_functions[i], new_functions[lowest_value_index] = new_functions[lowest_value_index], new_functions[i]
    # end sort
    logger.info('scheduler_planner_greedy:sorted functions by owner\'s zone priority (small->large):\n'
                + '\n'.join([str(new_function[0]) for new_function in new_functions]))

    # B: sort functions in each zone (small to large for poor and vulnerable) opposite dead, for rich does not matter
    for i in range(len(new_functions)):
        lowest_value_index = i
        largest_value_index = i
        lowest, largest = False, False
        zone_i = [*(worker[4] for worker in workers if worker[0] == new_functions[i][0][0])][0]
        # rich or dead
        if zone_i == 1 or zone_i == 4:
            # largest first
            largest = True
        # poor or vulnerable
        else:
            lowest = True

        for j in range(i + 1, len(new_functions)):
            # get function's owner zone
            zone_j = [*(worker[4] for worker in workers if worker[0] == new_functions[j][0][0])][0]
            zone_lowest_value_index = \
            [*(worker[4] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
            zone_largest_value_index = \
            [*(worker[4] for worker in workers if worker[0] == new_functions[largest_value_index][0][0])][0]
            if zone_j == zone_lowest_value_index:  # similar to say ==largest_value_index
                # get functions' owner soc
                soc_j = [*(worker[2] for worker in workers if worker[0] == new_functions[j][0][0])][0]
                soc_lowest_value_index = \
                [*(worker[2] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
                soc_largest_value_index = \
                [*(worker[2] for worker in workers if worker[0] == new_functions[largest_value_index][0][0])][0]
                # compare socs based on zones policy
                # if rich or dead , large to small
                if zone_largest_value_index == 1 or zone_largest_value_index == 4:
                    if soc_j > soc_largest_value_index:
                        largest_value_index = j
                # if poor or vulnerable, small to large
                elif zone_lowest_value_index == 2 or zone_lowest_value_index == 3:
                    if soc_j < soc_lowest_value_index:
                        lowest_value_index = j
        # swap
        if lowest:
            index = lowest_value_index
        else:
            index = largest_value_index
        new_functions[i], new_functions[index] = new_functions[index], new_functions[i]
    logger.info(
        'scheduler_planner_greedy:sorted functions by soc in zones (poor and vulnerable small to large. Rich and dead opposite):\n'
        + '\n'.join([str(new_function[0]) for new_function in new_functions]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info("scheduler_planner_greedy: start planning hosts for functions by priority")
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's old_hosts: last placement scheme
        old_hosts = copy.deepcopy([*(function[1] for function in functions if function[0] == new_function[0])][0])

        # old_hosts have zone numbers and Soc based on last epoch and the hosts zone may have changed now, so update their zones based on new status
        for index, old_host in enumerate(old_hosts):
            # update host's zone, capacity and Soc based on current status
            old_hosts[index] = [*(worker for worker in workers if worker[0] == old_host[0])][0]
        logger.info('greedy: old_hosts\n' + str(old_hosts))

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_limits = int(new_function[2][5].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_limits * func_max_replica
        owner_zone = owner[4]
        logger.info('greedy: planning for *** ' + str(new_function[0][0]) + '-'
                    + str(new_function[0][1]) + ' *** ')
        # try to fill new hosts for new_function
        new_hosts = []
        # if new_function belongs to a rich node
        if owner_zone == 1:
            # place locally
            logger.info('greedy: ' + owner[0] + '-' + new_function[0][1] + ' ---> locally')
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        # if poor, vulnerable or dead
        else:
            # if offloading
            # if setup.offloading == True:
            # if owners is dead, only offload if warm_scheduler is True; also if owner is poor or vulnerable, do the offloading
            if not (owner_zone == 4 and warm_scheduler == False):
                # Get rich and vulnerable (if the func is not vulnerable) workers
                volunteers = [*(worker for worker in workers if worker[4] == 1
                                or (worker[4] == 3 and owner_zone != 3))]

                logger.info('greedy: call offloader: volunteers \n'
                            + '\n'.join([str(volunteer) for volunteer in volunteers]))

                new_hosts = offloader(workers, functions, volunteers, new_function, sticky, stickiness,
                                      old_hosts, warm_scheduler, owner, func_max_replica,
                                      func_required_cpu_capacity, scale_to_zero, debug)

        # if not offloading was possible for fonctions owned by poor, vulnerable and dead nodes
        if new_hosts == []:
            # place locally
            logger.info('greedy: ' + owner[0] + '-' + new_function[0][1] + ' ---> locally')
            # how about functions belong to a dead node??? they are still scheduled locally
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        # deduct function cpu requirement from worker's cpu capacity
        for new_host in new_hosts:
            # get selected worker index per replica
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_limits
            # update new_host, particulalrly its capacity
            new_host[3] = workers[index][3]

        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_greedy: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

    # for loop: next new_function

    # replacad original functions with new_functions to apply new_hosts (placements)
    # functions = new_functions
    logger.info('scheduler_planner_greedy: done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# ??? functions are received for only getting old_hosts. Only old_hosts can be sent to this planner
def scheduler_planner_binpacking(workers, functions, new_functions, debug):
    global logger
    logger.info("scheduler_planner_binpacking:start")
    logger.info('scheduler_planner_binpacking:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))

    # sort nodes by soc (large->small | descending)
    workers.sort(key=lambda x: x[2], reverse=True)

    logger.info('scheduler_planner_binpacking:sorted nodes by Soc (large->small):\n'
                + str(workers))

    # sort functions: by owner's soc (small -> large | ascending)
    for i in range(len(new_functions)):
        lowest_value_index = i
        for j in range(i + 1, len(new_functions)):
            # find function's owner soc
            soc_j = [*(worker[2] for worker in workers if worker[0] == new_functions[j][0][0])][0]
            soc_lowest_value_index = \
            [*(worker[2] for worker in workers if worker[0] == new_functions[lowest_value_index][0][0])][0]
            # compare socs
            if soc_j < soc_lowest_value_index:
                lowest_value_index = j
        # swap
        new_functions[i], new_functions[lowest_value_index] = new_functions[lowest_value_index], new_functions[i]
    # end sort
    logger.info('scheduler_planner_binpacking:sorted functions by owner\'s soc(small->large):\n'
                + '\n'.join([str(new_function[0]) for new_function in new_functions]))

    # so far, new_functions have [] as hosts, workers have full as capacity and both workers and new_functions are sorted now
    logger.info("scheduler_planner_binpacking: start planning hosts for functions by soc")
    # PLAN
    # set hosts per function
    for new_function in new_functions:

        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_limits = int(new_function[2][5].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_limits * func_max_replica

        logger.info('binpacking: planning for *** ' + str(new_function[0][0]) + '-'
                    + str(new_function[0][1]) + ' *** \n Required_cpu_capacity: '
                    + str(func_required_cpu_capacity))
        # try to fill new hosts for new_function
        new_hosts = []
        # only functions belong to up nodes are scheduled. Those belong to dead nodes schedule locally
        min_battery_charge = battery_cfg[8]
        if owner[2] >= min_battery_charge:
            # pick the first possible option
            for index, worker in enumerate(workers):
                # if node is up
                if worker[2] >= min_battery_charge:
                    # if node has capacity
                    if worker[3] >= func_required_cpu_capacity:
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(worker))
                # if set
                if new_hosts != []:
                    break


        # dead node, schedule locally
        else:
            logger.info('bin_packing: locally')
            for rep in range(func_max_replica):
                new_hosts.append(copy.deepcopy(owner))

        # deduct function cpu requirement from worker's cpu capacity
        for new_host in new_hosts:
            # get selected worker index per replica
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_limits
            # update new_host, particulalrly its capacity
            new_host[3] = workers[index][3]
        logger.info('bin_packing: after deduction: new_hosts: ' + str(new_hosts))
        # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_binpacking: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

    # for loop: next new_function

    # replacad original functions with new_functions to apply new_hosts (placements)
    # functions = new_functions
    logger.info('scheduler_planner_binpacking: done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_planner_local
def scheduler_planner_local(workers, new_functions, debug):
    global logger
    logger.info("scheduler_planner_local:start")
    # set hosts for new_functions and update workers capacity
    logger.info('scheduler_planner_local:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        # func required cpu capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_limits = int(new_function[2][5].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_limits * func_max_replica

        # try to fill new hosts for new_function
        new_hosts = []

        # place locally
        # how about functions belong to a dead node??? they are still scheduled locally
        for rep in range(func_max_replica):
            new_hosts.append(copy.deepcopy(owner))

        # deduct function cpu requirement from worker's cpu capacity per replica
        for new_host in new_hosts:
            # get selected worker index
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_limits
            # apply worker's updated capacity to new_host as well
            new_host[3] = workers[index][3]

            # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_local: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))
    # for loop: next new_function

    logger.info('scheduler_planner_local: all done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_planner_default
# provide all nodes for each function scheduling. Kubenretes does it by nodes' performance, only once.
# If a node is under pressure, kubernetes is free to reschedule any time.
def scheduler_planner_default(workers, new_functions, debug):
    global logger
    logger.info("scheduler_planner_default:start")
    # set hosts for new_functions and update workers capacity
    logger.info('scheduler_planner_default:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        # func required cpu capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_limits = int(new_function[2][5].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_limits * func_max_replica

        # try to fill new hosts for new_function
        new_hosts = []

        # place anywhere you like Kubernetes
        # how about functions belong to a dead node??? they are still scheduled
        for worker in workers:
            new_hosts.append(copy.deepcopy(worker))

        # deduct function cpu requirement from worker's cpu capacity per replica
        for new_host in new_hosts:
            # get selected worker index
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_limits
            # apply worker's updated capacity to new_host as well
            new_host[3] = workers[index][3]

            # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_default: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))

    # for loop: next new_function

    logger.info('scheduler_planner_default: all done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_planner_random
def scheduler_planner_random(workers, new_functions, debug):
    global logger
    logger.info("scheduler_planner_random:start")
    # set hosts for new_functions and update workers capacity
    logger.info('scheduler_planner_random:\n available Workers \n'
                + '\n'.join([str(worker) for worker in workers]))
    # PLAN
    # set hosts per function
    for new_function in new_functions:
        # function's owner
        owner = [*(worker for worker in workers if worker[0] == new_function[0][0])][0]
        # func required cpu capacity
        func_required_cpu_capacity = 0
        # exclude 'm'
        replica_cpu_limits = int(new_function[2][5].split('m')[0])
        func_max_replica = new_function[2][1]
        func_required_cpu_capacity = replica_cpu_limits * func_max_replica

        # try to fill new hosts for new_function
        new_hosts = []

        # place on a random node that has capacity
        # how about functions belong to a dead node??? they are still scheduled
        random_places = []
        while random_places == []:
            random_index = random.randint(0, len(workers) - 1)  # 0 to 5
            # has enough capacity for all function replicas?
            if workers[random_index][3] >= func_required_cpu_capacity:
                # set place
                for rep in range(func_max_replica):
                    random_places.append(copy.deepcopy(workers[random_index]))

        new_hosts = random_places

        # deduct function cpu requirement from worker's cpu capacity per replica
        for new_host in new_hosts:
            # get selected worker index
            index = workers.index([*(worker for worker in workers if worker[0] == new_host[0])][0])
            # deduct replica cpu requirement
            workers[index][3] -= replica_cpu_limits
            # apply worker's updated capacity to new_host as well
            new_host[3] = workers[index][3]

            # set new_function new hosts
        new_function[1] = new_hosts
        if debug: logger.info("scheduler_planner_random: new_hosts for ("
                              + new_function[0][0] + "-" + new_function[0][1] + "):\n" + str(new_function[1]))
    # for loop: next new_function

    logger.info('scheduler_planner_random: all done: functions:\n'
                + '\n'.join([str(new_function) for new_function in new_functions]))

    return workers, new_functions


# scheduler_monitor
def scheduler_monitor(workers, node_role):
    global logger
    logger.info("scheduler_monitor: start")
    # MONITOR
    # Update SoC
    for worker in workers:
        ip = worker[1]
        success = False
        # retry
        while success == False:
            try:
                logger.info('scheduler_monitor: Soc req.: ' + worker[0])
                response = requests.get('http://' + ip + ':5000/main_handler/charge/'
                                        + node_role, timeout=10)
            except Exception as e:
                logger.error('scheduler_monitor:request failed for ' + worker[0] + ":" + str(e))
                time.sleep(1)
            else:
                soc = round(float(response.text), 2)
                index = workers.index(worker)
                workers[index][2] = soc
                logger.info('scheduler_monitor: Soc recv.: ' + worker[0] + ":" + str(soc) + "mWh")
                success = True

    logger.info('scheduler_monitor:\n' + '\n'.join([str(worker) for worker in workers]))
    logger.info("scheduler_monitor:done")
    return workers


# set initial workers and functions
def initialize_workers_and_functions(nodes, workers, functions, battery_cfg, nodes_plan, zones):
    global logger
    logger.info("initialize_workers_and_functions: start")
    # Set Workers & Functions
    for node in nodes:
        # worker = [name, ip, soc, capacity, zone]
        position = node[0]
        name = node[1]
        ip = node[2]
        soc = battery_cfg[3]  # set current SoC
        capacity = nodes_plan[name]["max_cpu_capacity"]  # set capacity as full
        # set zone
        max_battery_charge = battery_cfg[1]
        soc_percent = min(100, round(soc / max_battery_charge * 100))
        zone = [*(zone[1] for zone in zones if soc_percent <= zone[2] and soc_percent > zone[3])][0]
        # if node is involved in this tests
        if position == "PEER":
            # add worker
            worker = [name, ip, soc, capacity, zone]
            workers.append(worker)

            # add functions
            apps = nodes_plan[name]["apps"]
            for app in apps:
                if app[1] == True:
                    # function = [identity, hosts[], func_info, profile]
                    # set identity
                    worker_name = worker[0]
                    app_name = app[0]
                    identity = [worker_name, app_name]
                    # set hosts
                    hosts = []
                    # set function info
                    func_info = app[8]
                    # create and set profile name in function info
                    func_info[15] = worker_name + '-' + app_name
                    # set profile
                    profile = app[9]

                    function = []

                    # set local host per replicas and deduct cpu capacity from node
                    max_replica = func_info[1]
                    for rep in range(max_replica):
                        # update host capacity
                        replica_cpu_limits = func_info[5]
                        # exclude 'm'
                        replica_cpu_limits = int(replica_cpu_limits.split('m')[0])
                        index = workers.index(worker)
                        workers[index][3] -= replica_cpu_limits

                        # set host: default is local placement
                        hosts.append(worker)
                    # end for rep

                    # add function
                    function = [identity, hosts, func_info, profile]
                    functions.append(function)
                    f_name = function[0][0] + '-' + function[0][1]
            # end for app
    # end for node
    logger.info("initialize_workers_and_functions:stop")
    return workers, functions


# executor :set functions' profile using hosts, apply helm charts
def scheduler_executor(functions, profile_chart, profile_creation_roll_out,
                       function_chart, scheduling_round, log_path, scheduler_name, workers, debug):
    # 1 set profile based on hosts= set function[3] by new updates on function[1]
    logger.info('scheduler_executor:start')
    logger.info("scheduler_executor:set_profile per function")
    duration = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    for function in functions:
        # if debug: logger.info('scheduler_executor: set_profile:before:\n' + str(function[3]))
        # get old profile
        old_profile = copy.deepcopy(function[3])

        # translate hosts and map them to profile and set new profile scheme
        function[3] = scheduler_executor_set_profile(function, scheduler_name, workers, debug)
        # compare profiles, profile = function[3] looks like this ["w1", "nothing", "nothing",....]
        if old_profile != function[3]:
            # if profile is changed, set version to force re-schedule function based on new profile config
            function[2][16] += 1
            logger.info('scheduler_executor: ' + str(function[0][0]) + '-' + str(function[0][1])
                        + ': version = ' + str(function[2][16]))

        # if debug: logger.info('scheduler_executor: set_profile:after:\n' + str(function[3]))
    # all new profiles
    logger.info('scheduler_executor: All new profiles \n'
                + '\n'.join([str(str(function[0]) + '--->'
                                 + str(function[3])) for function in functions]))
    # 2 apply the new scheduling for functions by helm chart
    # if no change is profile happend, no re-scheduling is affected
    logger.info("scheduler_executor:apply all: call")
    scheduler_executor_apply(functions, profile_chart, profile_creation_roll_out,
                             function_chart, scheduling_round, log_path,
                             setup.auto_scaling, setup.auto_scaling_factor)

    duration = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp() - duration
    logger.info('scheduler_executor: done in ' + str(int(duration)) + 'sec')

    return functions


# offload
def offloader(workers, functions, volunteers, new_function, sticky, stickiness, old_hosts,
              warm_scheduler, owner, func_max_replica, func_required_cpu_capacity, scale_to_zero, debug):
    global logger
    logger.info("offloader: start: " + str(new_function[0][0] + '-' + new_function[0][1]))
    new_hosts = []
    # ??? assume that all replicas are always placed on 1 node
    # if sticky enabled and function was offloaded last time
    if owner[0] != old_hosts[0][0] and sticky:
        new_hosts = sticky_offloader(workers, functions, volunteers, stickiness, old_hosts,
                                     owner, func_max_replica, func_required_cpu_capacity,
                                     warm_scheduler, scale_to_zero)
    else:
        logger.info('offloader: skip sticky_offloader')
    # if sticky unsuccessful
    if new_hosts == []:
        # iterate over rich and vulnerables, already sorted by SoC (large -> small)
        for volunteer in volunteers:
            # if function belongs to a poor node
            if owner[4] == 2:
                if debug: logger.info('offloader: poor function')
                # if node is in rich zone
                volunteer_zone = volunteer[4]
                if volunteer_zone == 1:
                    if debug: logger.info('offloader: rich volunteer (' + volunteer[0] + ')')
                    # if enough capacity on volunteer node is available
                    if volunteer[3] >= func_required_cpu_capacity:
                        if debug: logger.info('offloader: rich volunteer has capacity')
                        # place this poor function on this rich volunteer per replica
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(volunteer))
                            # volunteer capacity is deducted later on in main algorithm
                        return new_hosts
                    else:
                        if debug: logger.info('offloader: rich volunteer has NOT capacity')
                # OR volunteer node is in vulnerable zone
                if volunteer_zone == 3:
                    if debug: logger.info('offloader: vulnerable volunteer (' + volunteer[0] + ')')
                    # evaluate cpu reservation for the vulnerable node own functions
                    reserved_capacity = 0
                    available_capacity = 0
                    for function in functions:
                        # if function belongs to this vulnerable volunteer node
                        if function[0][0] == volunteer[0]:
                            # caclulate reserved cpu capacity per replica for the function
                            reserved_capacity += function[2][1] * int(function[2][5].split('m')[0])
                    # if already one has offloaded on this, that one is also included here as volunteer[3] is the result of full capacity minus offloaded (end of each offloading this is deducted)
                    available_capacity = volunteer[3] - reserved_capacity

                    # if volunteer has enough cpu capacity, considering reservation
                    if available_capacity >= func_required_cpu_capacity:
                        if debug: logger.info('offloader: vulnerable volunteer has capacity + reservation')
                        # place functions belong to a poor node on volunteer per replica
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(volunteer))
                        return new_hosts
                    else:
                        if debug: logger.info('offloader: vulnerable volunteer has NOT capacity + reservation')
            # if function belongs to a vulnerable zone
            elif owner[4] == 3:
                if debug: logger.info('offloader: vulnerable function')
                # only if volunteer is in rich zone
                if volunteer[4] == 1:
                    if debug: logger.info('offloader: volunteer node\'s zone is rich (' + volunteer[0] + ')')
                    # and volunteer has cpu capacity for function
                    if volunteer[3] >= func_required_cpu_capacity:
                        logger.info('offloader: volunteer rich has capacity')
                        for rep in range(func_max_replica):
                            new_hosts.append(copy.deepcopy(volunteer))
                        return new_hosts
                    else:
                        if debug: logger.info('offloader: volunteer rich has NOT capacity')
                else:
                    if debug: logger.info('offloader: volunteer node\'s zone is NOT rich')
            # if function belongs to a dead node
            elif owner[4] == 4:
                if debug: logger.info('offloader: dead function')
                # if warm_scheduler on, otherwise functions belong to dead nodes are just placed locally
                if warm_scheduler == True:
                    if debug: logger.info('offloader: warm scheduler is True')
                    # if volunteer is in rich zone
                    if volunteer[4] == 1:
                        if debug: logger.info('offloader: rich volunteer (' + volunteer[0] + ')')
                        # if volunteer has cpu capacity
                        if volunteer[3] >= func_required_cpu_capacity:
                            if debug: logger.info('offloader: rich volunteer has capacity')
                            for rep in range(func_max_replica):
                                new_hosts.append(copy.deepcopy(volunteer))
                            return new_hosts
                        else:
                            if debug: logger.info('offloader: rich volunteer has NOT capacity')
                    else:
                        if debug: logger.info('offloader: volunteer is NOT rich (' + volunteer[0] + ')')

                    # or not exist any rich and all volunteers are just vulnerable
                    rich_nodes = [*(worker for worker in workers if worker[4] == 1)]
                    if len(rich_nodes) == 0:
                        if debug: logger.info('offloader: not exist any rich node and all volunteers are vulnerable')
                        # if volunteer has cpu capacity
                        if volunteer[3] >= func_required_cpu_capacity:
                            if debug: logger.info('offloader: vulnerable volunteer has capacity')
                            for rep in range(func_max_replica):
                                new_hosts.append(copy.deepcopy(volunteer))
                            return new_hosts
                        # if no cpu capacity, if scale to zero on, do it ????
                        elif setup.scale_to_zero == True:
                            pass
                        else:
                            if debug: logger.info('offloader: vulnerable volunteer has NOT capacity')
                    else:
                        if debug: logger.info('offloader: unlukily, exist rich volunteer')
                else:
                    if debug: logger.info('offloader: warm scheduler is False')
        # end for volunteer
        if len(volunteers) == 0:
            logger.info('offloader: skip offloading, no volunteer found')

    logger.info("offloader: done: " + str(new_function[0][0] + '-' + new_function[0][1])
                + ": new_hosts:\n" + str(new_hosts) if new_hosts != [] else ": [ ]")
    return new_hosts


# sticky offloader
def sticky_offloader(workers, functions, volunteers, stickiness, old_hosts, owner,
                     func_max_replica, func_required_cpu_capacity, warm_scheduler, scale_to_zero):
    global logger
    logger.info('sticky_offloader: start')
    new_hosts = []
    logger.info('sticky_offloader: old_hosts: ' + str(old_hosts))
    # apply sticky only if all replicas of the functions have been scheduled on only 1 zone???? how about per replica evaluation and letting each replica sticks to its last place
    old_hosts_zone = [host[4] for host in old_hosts]
    old_hosts_zone_set = list(set(old_hosts_zone))
    if len(old_hosts_zone_set) > 1:
        logger.error('sticky_offloader: all replicas are NOT on 1 node')
        logger.info('sticky_offloader: done' + str(new_hosts))
        return new_hosts

    logger.info('sticky_offloader: get best option')
    # Get best option for offloading, regardless of sticky
    # nodes (rich and vulnerable) already sorted by suitability
    best_option = []
    for volunteer in volunteers:
        # if function belongs to a poor node, and volunteer node is in vulnerable zone,
        # then because of undecided functions belonging to the node, consider node's own reservation
        available_capacity = 0
        if owner[4] == 2 and volunteer[4] == 3:
            # consider reservation to evaluate volunteer capacity
            # evaluate cpu reservation for the vulnerable node own functions
            reserved_capacity = 0

            for function in functions:
                # if function belongs to the volunteer node that is a vulnerable node
                if function[0][0] == volunteer[0]:
                    # caclulate reserved cpu capacity per replica for the function
                    reserved_capacity += function[2][1] * int(function[2][5].split('m')[0])
            # Note:if already one has offloaded on this, that one is also included here as volunteer[3] is the result of full capacity minus offloaded (end of each offloading this is deducted)
            available_capacity = volunteer[3] - reserved_capacity
        else:
            available_capacity = volunteer[3]
        # if node has capacity
        if available_capacity >= func_required_cpu_capacity:
            best_option = volunteer
            # the first answer, is the best option, do not continue
            break
    # end for
    logger.info('sticky_offloader: best option: ' + str(best_option))

    if best_option == []:
        logger.error('sticky_offloader: not a best option found, return null to offloader')
        logger.info('sticky_offloader: done' + str(new_hosts))
        return new_hosts

    # if old location of function (belonging to poor, vulnerable or (dead if warm is true)) is rich
    if old_hosts_zone[0] == 1:
        logger.info('sticky_offloader: old_host is rich')
        # if old node soc satisfies stickiness
        old_option_soc = old_hosts[0][2]
        best_option_soc = best_option[2]
        if old_option_soc >= (best_option_soc - (best_option_soc * stickiness)):
            logger.info('sticky_offloader: old_host_soc satisfy stickiness')
            # if old has capacity
            if old_hosts[0][3] >= func_required_cpu_capacity:
                logger.info('sticky_offloader: old_host has capacity')
                new_hosts = copy.deepcopy(old_hosts)
                # function requried cpu is later deducted from the node capacity in main algorithm
                logger.info('sticky_offloader: done' + str(new_hosts))
                return new_hosts
            # old has no capacity, but if f belongs to a dead node, place and scale to 0 even if no resource
            elif owner[4] == 4:
                # if scale to zero on ???
                if scale_to_zero == True:
                    logger.info('sticky_offloader: old_host NOT capacity, but func is dead and scale_to_zero is on')
                    # ??? it can be limited to only 1 zero function per node: if not exist any 0 already on this node
                    new_hosts = copy.deepcopy(old_hosts)
                    logger.info('sticky_offloader: done' + str(new_hosts))
                    return new_hosts
            else:
                logger.info('sticky_offloader: old_hosts has NOT capacity (or NOT a dead func + scale_to_zero=True)\n'
                            + 'func capacity = ' + str(func_required_cpu_capacity)
                            + ' old_host capacity= ' + str(old_hosts[0][3]))
        else:
            logger.info('sticky_offloader: old_host_soc NOT satisfy stickiness')
    # if old host is vulnerable and function belongs to a poor or dead node
    elif old_hosts_zone[0] == 3 and (owner[4] == 2 or owner[4] == 4):
        logger.info('sticky_offloader: old_host is vulnerable and func belongs to poor or dead node')
        # evaluate cpu reservation for the vulnerable node functions itself
        reserved_capacity = 0
        available_capacity = 0
        for function in functions:
            # if node name in function is equal to the old_host name, it is its local func
            if function[0][0] == old_hosts[0][0]:
                # caclulate reserved cpu capacity per replica for the function
                reserved_capacity += function[2][1] * int(function[2][5].split('m')[0])

        available_capacity = old_hosts[0][3] - reserved_capacity

        # if f belongs to a poor node and (no rich node exists || all are filled)
        # skip this part: and (best_option[4] != 1)
        if owner[4] == 2:
            logger.info('sticky_offloader: func belong to poor skipped(and (no rich or all riches are filled)')
            # if old host can satisfy stickiness, stick it
            # check stickiness
            old_option_soc = old_hosts[0][2]
            best_option_soc = best_option[2]
            if old_option_soc >= (best_option_soc - (best_option_soc * stickiness)):
                logger.info('sticky_offloader: satisfy stickiness')
                # if old has capacity
                if available_capacity >= func_required_cpu_capacity:
                    logger.info('sticky_offloader: has capacity')
                    new_hosts = copy.deepcopy(old_hosts)
                    logger.info('sticky_offloader: done' + str(new_hosts))
                    return new_hosts
                else:
                    logger.info('sticky_offloader: has NOT capacity')
            else:
                logger.info('sticky_offloader: NOT satisfy stickiness')
        # OR if f belongs to a dead node & warm & no rich node exists
        elif (owner[4] == 4 and warm_scheduler == True and
              (len([*(worker for worker in workers if worker[4] == 1)]) == 0)):
            logger.info('sticky_offloader: func belong to dead node and no rich node exist')
            # if enough capacity
            if available_capacity >= func_required_cpu_capacity:
                logger.info('sticky_offloader: has capacity')
                new_hosts = copy.deepcopy(old_hosts)
                logger.info('sticky_offloader: done' + str(new_hosts))
                return new_hosts
            else:
                logger.info('sticky_offloader: has NOT capacity')
            # if does not exist a dead already placed somewhere with scale to zero ???
            # else:
        else:
            logger.info('sticky: not happened: not being: \n'
                        + 'f belongs to a poor node and (no rich node exists || all are filled)\n'
                        + ' OR f belongs to a dead node & no rich node exists')
    logger.info('sticky_offloader: done' + str(new_hosts))

    return new_hosts


# set ptofile
# it only works for 5 nodes and 3 replica???
def scheduler_executor_set_profile(function, scheduler_name, workers, debug):
    global logger
    nodeAffinity_required_filter1 = "unknown"
    nodeAffinity_required_filter2 = "unknown"
    nodeAffinity_required_filter3 = "unknown"
    nodeAffinity_required_filter4 = "unknown"
    nodeAffinity_required_filter5 = "unknown"
    nodeAffinity_preferred_sort1 = "unknown"
    podAntiAffinity_preferred_functionName = "unknown"
    podAntiAffinity_required_functionName = "unknown"

    owner_name = function[0][0]
    app_name = function[0][1]
    function_name = owner_name + '-' + app_name
    hosts = function[1]
    # if debug: logger.info("scheduler_executor_set_profile:" + function_name + ":start")
    selected_nodes = []
    for host in hosts:
        selected_nodes.append(host[0])
    # if selected_nodes=[w1,w2,w2] then selected_nodes_set result is [w1, w2]
    selected_nodes_set = list(set(selected_nodes))

    if ("greedy" in scheduler_name or
            "shortfaas" in scheduler_name or
            "local" in scheduler_name or
            "random" in scheduler_name or
            "bin-packing" in scheduler_name):

        # place on 1 node #random is always 1
        if len(selected_nodes_set) == 1:
            nodeAffinity_required_filter1 = selected_nodes_set[0]
        # place on 2 nodes
        elif len(selected_nodes_set) == 2:
            nodeAffinity_required_filter1 = selected_nodes_set[0]
            nodeAffinity_required_filter2 = selected_nodes_set[1]
            preference = ""
            if selected_nodes.count(selected_nodes_set[0]) == 2:
                preference = selected_nodes_set[0]
            else:
                preference = selected_nodes_set[1]

            nodeAffinity_preferred_sort1 = preference
            podAntiAffinity_preferred_functionName = function_name
        # place on 3 nodes
        elif len(selected_nodes_set) == 3:
            nodeAffinity_required_filter1 = selected_nodes_set[0]
            nodeAffinity_required_filter2 = selected_nodes_set[1]
            nodeAffinity_required_filter3 = selected_nodes_set[2]
            podAntiAffinity_required_functionName = function_name
        else:
            logger.error('scheduler_set_profile:' + function_name + ': selected_nodes_set length = '
                         + str(len(selected_nodes_set)))
    # default-kubernetes scheduler
    elif "default" in scheduler_name:
        if len(selected_nodes_set) == len(workers):
            if len(selected_nodes_set) == 4:  # t????emporary code, both if else should be merged
                nodeAffinity_required_filter1 = selected_nodes_set[0]
                nodeAffinity_required_filter2 = selected_nodes_set[1]
                nodeAffinity_required_filter3 = selected_nodes_set[2]
                nodeAffinity_required_filter4 = selected_nodes_set[3]

            elif len(selected_nodes_set) == 5:  # ????temporary code
                nodeAffinity_required_filter1 = selected_nodes_set[0]
                nodeAffinity_required_filter2 = selected_nodes_set[1]
                nodeAffinity_required_filter3 = selected_nodes_set[2]
                nodeAffinity_required_filter4 = selected_nodes_set[3]
                nodeAffinity_required_filter5 = selected_nodes_set[4]
        else:
            logger.error('scheduler_set_profile: not all workers are selected: (len=='
                         + str(len(selected_nodes_set)) + ')')
    else:
        logger.error('scheduler_set_profile: scheduler_name not found:' + scheduler_name)

    # if debug: logger.info("scheduler_executor_set_profile:" + function_name + ":done")
    # return
    return [nodeAffinity_required_filter1,
            nodeAffinity_required_filter2,
            nodeAffinity_required_filter3,
            nodeAffinity_required_filter4,
            nodeAffinity_required_filter5,
            nodeAffinity_preferred_sort1,
            podAntiAffinity_preferred_functionName,
            podAntiAffinity_required_functionName]


last_version = [0]


# scheduler_executor_apply
def scheduler_executor_apply(functions, profile_chart, profile_creation_roll_out,
                             function_chart, scheduling_round, log_path,
                             auto_scaling, auto_scaling_factor):
    global logger
    global last_version
    logger.info('scheduler_executor_apply:start')
    logger.info('scheduler_executor_apply:profiles:start')
    prof_group = len(functions)

    # profile string
    prof_name = []
    nodeAffinity_required_filter1 = []
    nodeAffinity_required_filter2 = []
    nodeAffinity_required_filter3 = []
    nodeAffinity_required_filter4 = []
    nodeAffinity_required_filter5 = []
    nodeAffinity_preferred_sort1 = []
    podAntiAffinity_preferred_functionName = []
    podAntiAffinity_required_functionName = []
    # get profiles
    for i in range(len(functions)):
        function = functions[i]
        prof_name.append(function[0][0] + '-' + function[0][1])
        profile = function[3]

        nodeAffinity_required_filter1.append(profile[0])
        nodeAffinity_required_filter2.append(profile[1])
        nodeAffinity_required_filter3.append(profile[2])
        nodeAffinity_required_filter4.append(profile[3])
        nodeAffinity_required_filter5.append(profile[4])
        nodeAffinity_preferred_sort1.append(profile[5])
        podAntiAffinity_preferred_functionName.append(profile[6])
        podAntiAffinity_required_functionName.append(profile[7])
    # run command
    helm_chart_name = profile_chart[0]
    helm_chart_path = profile_chart[1]

    cmd = ("helm upgrade --install " + helm_chart_name + " " + helm_chart_path
           + " --wait --set-string \"profiles=" + str(prof_group) + ","
           + "profile.name={" + ','.join(prof_name) + "},"
           + "profile.nodeAffinity.required.filter1={" + ','.join(nodeAffinity_required_filter1) + "},"
           + "profile.nodeAffinity.required.filter2={" + ','.join(nodeAffinity_required_filter2) + "},"
           + "profile.nodeAffinity.required.filter3={" + ','.join(nodeAffinity_required_filter3) + "},"
           + "profile.nodeAffinity.required.filter4={" + ','.join(nodeAffinity_required_filter4) + "},"
           + "profile.nodeAffinity.required.filter5={" + ','.join(nodeAffinity_required_filter5) + "},"
           + "profile.nodeAffinity.preferred.sort1={" + ','.join(nodeAffinity_preferred_sort1) + "},"
           + "profile.podAntiAffinity.preferred.functionName={" + ','.join(
                podAntiAffinity_preferred_functionName) + "},"
           + "profile.podAntiAffinity.required.functionName={" + ','.join(podAntiAffinity_required_functionName) + "}\""
           + " --skip-crds --wait")

    logger.info('scheduler_executor_apply:profiles:run cmd')
    # log
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    path = log_path + "/helm-commands"
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = path + "/" + str(scheduling_round) + "_profiles.sim.cmd.log"
    log_cmd = cmd + " --dry-run > " + file_name
    logger.info('scheduler_executor_apply:log_cmd:profile:' + log_cmd)
    utils.shell(cmd)

    # actual cmd
    logger.info('scheduler_executor_apply:cmd:profile:' + cmd)
    out, error = utils.shell(cmd)
    logger.info('scheduler_executor_apply:cmd:profile:stdout:' + (str(out + error)))
    # wait to apply
    logger.info('scheduler_executor_apply:cmd:profile:rolling out (' + str(profile_creation_roll_out) + 's)')
    time.sleep(profile_creation_roll_out)
    logger.info('scheduler_executor_apply:profiles:done')

    # Functions Helm CHart
    # Get Functions String
    logger.info('scheduler_executor_apply:functions:start')
    func_group = len(functions)
    func_name = []
    func_image_name = []
    counter = []
    redisServerIp = []
    redisServerPort = []
    readTimeout = []
    writeTimeout = []
    execTimeout = []
    handlerWaitDuration = []
    scale_factor = []
    scale_min = []
    scale_max = []
    requests_memory = []
    limits_memory = []
    requests_cpu = []
    limits_cpu = []
    profile_names = []
    queue_names = []
    linkerd = []
    version = []
    # get func_info
    for i in range(len(functions)):
        function = functions[i]
        # function name
        name = function[0][0] + "-" + function[0][1]
        func_name.append(name)
        # image
        #func_image_name.append(function[0][1])

        # info
        func_info = function[2]
        #Note: if autoscaling is based on HPA, not openfaas, min and max replicas are set 1 to disable openfaas autoscaling. setting scaling factor to zero achiees the same.
        scale_min.append("1" if auto_scaling == "hpa" else str(func_info[0]))
        scale_max.append("1" if auto_scaling == "hpa" else str(func_info[1]))
        # factor is unused and not mentioned in setup for apps????
        scale_factor.append("0" if auto_scaling == "hpa" else str(auto_scaling_factor))
        requests_memory.append(func_info[2])
        limits_memory.append(func_info[3])
        requests_cpu.append(func_info[4])
        limits_cpu.append(func_info[5])
        counter.append(func_info[6])
        redisServerIp.append(func_info[7])
        redisServerPort.append(func_info[8])
        readTimeout.append(func_info[9])
        writeTimeout.append(func_info[10])
        execTimeout.append(func_info[11])
        handlerWaitDuration.append(func_info[12])
        linkerd.append(func_info[13])
        queue_names.append(func_info[14])
        profile_names.append(func_info[15])
        version.append(func_info[16])
        func_image_name.append(func_info[17])
        
    # run command
    logger.info('scheduler_executor_apply:functions:cmd')
    helm_chart_name = function_chart[0]
    helm_chart_path = function_chart[1]
    cmd = ("helm upgrade --install " + helm_chart_name + " " + helm_chart_path
           + " --set-string \"functions=" + str(func_group) + ","
           + "function.name={" + ','.join(func_name) + "},"
           + "function.imageName={" + ','.join(func_image_name) + "},"
           + "function.env.counter={" + ','.join(counter) + "},"
           + "function.env.redisServerIp={" + ','.join(redisServerIp) + "},"
           + "function.env.redisServerPort={" + ','.join(redisServerPort) + "},"
           + "function.env.execTimeout={" + ','.join(execTimeout) + "},"
           + "function.env.handlerWaitDuration={" + ','.join(handlerWaitDuration) + "},"
           + "function.env.readTimeout={" + ','.join(readTimeout) + "},"
           + "function.env.writeTimeout={" + ','.join(writeTimeout) + "},"
           + "function.scale.factor={" + ','.join(scale_factor) + "},"
           + "function.scale.min={" + ','.join(scale_min) + "},"
           + "function.scale.max={" + ','.join(scale_max) + "},"
           + "function.requests.memory={" + ','.join(requests_memory) + "},"
           + "function.limits.memory={" + ','.join(limits_memory) + "},"
           + "function.requests.cpu={" + ','.join(requests_cpu) + "},"
           + "function.limits.cpu={" + ','.join(limits_cpu) + "},"
           + "function.annotations.profile={" + ','.join(profile_names) + "},"
           + "function.annotations.queue={" + ','.join(queue_names) + "},"
           + "function.annotations.linkerd={" + ','.join(linkerd) + "},"
           + "function.env.version={" + ','.join([str(i) for i in version]) + "}\""
           + " --skip-crds --wait")

    # log
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    path = log_path + "/helm-commands"
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = path + "/" + str(scheduling_round) + "_functions.sim.cmd.log"
    # simulate
    log_cmd = cmd + " --dry-run > " + file_name
    logger.info('scheduler_executor_apply:log_cmd:functions:' + log_cmd)
    utils.shell(cmd)

    # actual cmd
    logger.info('scheduler_executor_apply:cmd:function:' + cmd)


    logger.info('run cmd: versions ' + str(version))
    cmd = ("helm upgrade --install " + helm_chart_name + " " + helm_chart_path
            + " --set-string \"functions=" + str(func_group) + ","
            + "function.name={" + ','.join(func_name) + "},"
            + "function.imageName={" + ','.join(func_image_name) + "},"
            + "function.env.counter={" + ','.join(counter) + "},"
            + "function.env.redisServerIp={" + ','.join(redisServerIp) + "},"
            + "function.env.redisServerPort={" + ','.join(redisServerPort) + "},"
            + "function.env.execTimeout={" + ','.join(execTimeout) + "},"
            + "function.env.handlerWaitDuration={" + ','.join(handlerWaitDuration) + "},"
            + "function.env.readTimeout={" + ','.join(readTimeout) + "},"
            + "function.env.writeTimeout={" + ','.join(writeTimeout) + "},"
            + "function.scale.factor={" + ','.join(scale_factor) + "},"
            + "function.scale.min={" + ','.join(scale_min) + "},"
            + "function.scale.max={" + ','.join(scale_max) + "},"
            + "function.requests.memory={" + ','.join(requests_memory) + "},"
            + "function.limits.memory={" + ','.join(limits_memory) + "},"
            + "function.requests.cpu={" + ','.join(requests_cpu) + "},"
            + "function.limits.cpu={" + ','.join(limits_cpu) + "},"
            + "function.annotations.profile={" + ','.join(profile_names) + "},"
            + "function.annotations.queue={" + ','.join(queue_names) + "},"
            + "function.annotations.linkerd={" + ','.join(linkerd) + "},"
            + "function.env.version={" + ','.join([str(i) for i in version]) + "}\""
            + " --skip-crds --wait")
    out, error = utils.shell(cmd)


    logger.info('scheduler_executor_apply:cmd:function:stdout:' + str(out + error))
    logger.info('scheduler_executor_apply:functions:done')

    logger.info('scheduler_executor_apply:stop')

#workload shape generator: reshape the concurrently based on the predefined stages
def workload_shape_generator(test_duration_time, test_elapsed_time, base_concurrently, stages, logger):
    #if no stage is defined, return the bas concurrently
    if stages == []: return base_concurrently

    # determine the concurrently based on the relevant stage specification

    # if no re-assignment occurs, the base_concurrently (original value) is used instead
    new_concurrently = base_concurrently

    # get test elapsed time in percent, as the stages start and end time are in percent format
    test_elapsed_percent = round(test_elapsed_time / test_duration_time * 100, 2)

    for stage in stages:
        # collect the stage information (pick default values if required)
        stageStartTimePercent = 0 if stage["stageStartTimePercent"] == None else stage["stageStartTimePercent"]
        stageEndTimePercent = 100 if stage["stageEndTimePercent"] == None else stage["stageEndTimePercent"]
        stageConcurrentlyStart = base_concurrently if stage["stageConcurrentlyStart"] == None else stage[
            "stageConcurrentlyStart"]
        stageConcurrentlyEnd = base_concurrently if stage["stageConcurrentlyEnd"] == None else stage[
            "stageConcurrentlyEnd"]
        stageSlope = "normal" if stage["stageSlope"] == None else stage["stageSlope"]
        stageStepLength = 1 if stage["stageStepLength"] == None else stage["stageStepLength"]

        # if test elapsed time is in the range of a specific stage, pick that stage
        if test_elapsed_percent >= stageStartTimePercent and test_elapsed_percent <= stageEndTimePercent:

            # step 1: Check the slope

            # if slope is set to default (45), do the usual, i.e., increment/decrement the concurrently towards the concurrentlyEnd gradually.
            if stageSlope == "normal":

                # normal slope

                # prepare some variables for calculations
                # measure stage duration time (max length) from percent values
                stage_duration_time = round(test_duration_time * ((stageEndTimePercent - stageStartTimePercent) / 100))
                # measure stage elapsed time
                # measure stage start time from its percent value
                stage_start_time = int(test_duration_time * (stageStartTimePercent / 100))
                stage_elapsed_time = test_elapsed_time - stage_start_time

                # main calculation
                # new_concurrently = base_concurrently
                new_concurrently = stageConcurrentlyStart
                new_concurrently += ((stageConcurrentlyEnd - stageConcurrentlyStart) / (
                            stage_duration_time / stageStepLength)) * \
                                    math.ceil((stage_elapsed_time / stageStepLength))
                # note that the steps are up then flat by "ceil". Otherwise, "floor" can be used. Now, partial steps are changed to full step.

            else:  # if the slope is flat, set the concurrently so it constantly remains equal to "stageConcurrentlyStart"; otherwise equal to base_concurrently
                if stageSlope == "flat":
                    # this simulates a flat rate in the button for the duration of the stage
                    new_concurrently = stageConcurrentlyStart if stageConcurrentlyStart != None else base_concurrently

                else:
                    logger.error("ERROR: The value for stageSlope is out of range")

            # only one stage applies at a time; hence stop searching at this interval.
            # Note: If some stages start and end time overlap, the one with the smallest index in stages is selected and the rest are ignored.
            break
        
    return round(new_concurrently)

#workload generator : a thread per application
@app.route('/workload', methods=['POST'])
def workload(my_app):
    time.sleep(1)  # Give enough time gap to create req to server to avoid connection error. or use sessions
    global logger
    global test_started
    global test_finished
    global apps
    global max_request_timeout
    global min_request_generation_interval
    global sessions
    global time_based_termination

    logger.info('workload: started')
    # [2] w type: "static" or "poisson" or "exponential-poisson"
    # [3] workload: [[0]iteration [1]interval/exponential lambda(10=avg 8s)
    # [2]concurrently/poisson lambda (15=avg 17reqs ) [3] random seed (def=5)]
    # [4] func_name [5] func_data [6] created [7] recv

    workload_type = my_app[2]  # "static" or "poisson" or "exponential-poisson"
    w_config = my_app[3]

    app_session = requests.session()
    # ???? 10 times concurrently is set by taste. pool_max_size can consider the max concurrently in workload_shape
    app_session.mount(
        'http://',
        requests.adapters.HTTPAdapter(pool_maxsize=w_config[2] * 10,
                                      max_retries=3,
                                      pool_block=True)
    )
    sessions[my_app[4]] = app_session

    iteration = 0
    interval = 0
    concurrently = 0
    seed = ""

    #static interarrival and concurrently
    if workload_type == 'static':
        iteration = w_config[0]
        # interval
        interval = w_config[1]
        # concurrently
        concurrently = w_config[2]

    #random concurrently
    elif workload_type == 'poisson':
        iteration = w_config[0]
        # interval
        interval = w_config[1]
        # determine concurrently list
        # set seed
        seed = w_config[3]
        np.random.seed(seed)

        lmd_rate = w_config[2]
        if lmd_rate != 0:
            concurrently = np.random.poisson(lam=lmd_rate, size=iteration)
        else:  # force 0, if lambda is 0
            concurrently = [0] * iteration

    #random interarrival and concurrently
    elif workload_type == 'exponential-poisson':
        iteration = w_config[0]
        # determine interval list
        # set seed
        seed = w_config[3]
        np.random.seed(seed)

        lmd_scale = w_config[1]
        if lmd_scale != 0:
            # random.exponential(scale=1.0, size=None)
            interval = np.random.exponential(scale=lmd_scale, size=iteration)
        else:  # force 0, if lambda is 0
            interval = [0] * iteration

        # determine concurrently list
        lmd_rate = w_config[2]
        if lmd_rate != 0:
            concurrently = np.random.poisson(lam=lmd_rate, size=iteration)
        else:  # force 0 if lambda is 0
            concurrently = [0] * iteration

    #random interarrival
    elif workload_type == 'exponential':
        iteration = w_config[0]
        # determine interval list
        # set seed
        seed = w_config[3]
        np.random.seed(seed)

        lmd_scale = w_config[1]
        if lmd_scale != 0:
            # random.exponential(scale=1.0, size=None)
            interval = np.random.exponential(scale=lmd_scale, size=iteration)
        else:  # force 0 if lambda is 0
            interval = [0] * iteration

        concurrently = w_config[2]

    #workload shape
    workload_shape = w_config[4]

    func_name = my_app[4]
    func_data = my_app[5]
    # my_app[6] sensor created counter
    # my_app[7] actuation recv counter

    logger.info("workload: App {0} \n workload: {1} \n Iteration: {2} \n "
                "Interval Avg. {3} ({4}-{5}) \n"
                "Concurrently Avg. {6} ({7}--{8})\n"
                " Seed {9} \n function {10} data {11}\n---------------------------".format(
        func_name, workload_type, iteration,
        round(sum(interval) / len(interval), 3) if "exponential" in workload_type else interval,
        round(min(interval), 3) if "exponential" in workload_type else "--",
        round(max(interval), 3) if "exponential" in workload_type else "--",
        round(sum(concurrently) / len(concurrently), 3) if "poisson" in workload_type else concurrently,
        round(min(concurrently), 3) if "poisson" in workload_type else "--",
        round(max(concurrently), 3) if "poisson" in workload_type else "--",
        seed, func_name, func_data))

    generator_st = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    # sensor counter
    created = 0
    # iterations
    for i in range(iteration):
        iter_started = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

        # interarrival
        interarrival = (interval[i] if "exponential" in workload_type else interval)
        if interarrival < min_request_generation_interval:
            interarrival = min_request_generation_interval

        # base concurrently (it may be manipulated by workload_shape_generator method)
        con = (round(concurrently[i]) if "poisson" in workload_type else round(concurrently))

            #shape to adjust concurrently
        test_duration_time = time_based_termination[1]
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        test_elapsed_time = now - test_started

        con = workload_shape_generator(test_duration_time, test_elapsed_time, con, workload_shape, logger)

        #start issuing requests

        # gevent or thread
        workload_worker = w_config[5]
        
        if workload_worker == "gevent":
            #gevents are created and started thank to monkey.
            pool = Pool(size=con)
            for i in range(con):
                pool.spawn(create_sensor, created, func_name, func_data, interarrival, )
            
            #this is synchronous (blocking) and waits for all gevents to finish, otherwise kills them after timeout.
            #pool = Pool(size=concurrently)
            #timeout = gevent.Timeout(2, gevent.Timeout)
            #timeout.start()

            #try:
            #    for i in range(concurrently):
            #        pool.spawn(sample, session,i,i,"i")
            #    pool.join()
            #except gevent.Timeout as e:
            #    print("rrrrr")
            #finally:
            #    timeout.close()
            
        # thread
        elif workload_worker == "thread":
            threads = []

            for c in range(con):
                created += 1
                thread_create_sensor = threading.Thread(target=create_sensor,
                                                        args=(created, func_name, func_data, interarrival,))
                thread_create_sensor.name = "create_sensor" + "-" + func_name + "#" + str(created)
                threads.append(thread_create_sensor)

            for t in threads:
                t.start()
        
        else:
            logger.error("workload: workload_worker not found")
        # check termination: do not sleep after the final iteration or test is forced to finish
        if i == iteration - 1 or under_test == False:
            break
        # Get iteration duration
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        iter_elapsed = now - iter_started
        # check duration
        if iter_elapsed < interarrival:
            if iter_elapsed > (interarrival / 2):
                logger.warning('Workload iteration #' + str(i) + ' rather long! (' + str(iter_elapsed) + ')')
            # wait untill next iteration -deduct elapsed time
            time.sleep(interarrival - iter_elapsed)

        else:
            logger.error('Workload: Iteration #' + str(i)
                         + ' overlapped! (' + str(iter_elapsed) + ' elapsed) - next interval= ' + str(interarrival))
            print('Workload Iteration #' + str(i) + ' overlapped!')
            # ???skip next intervals that are passed
    # break
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    logger.info('workload: All Generated: ' + func_name + ': in ' + str(round(now - test_started, 2)) + ' sec')

    # set created
    apps[apps.index(my_app)][6] = created
    # ????if some are dropped. they are not added to app[7], so this condition is always false
    # wait for all actuators of this app, or for timeout, then move
    if apps[apps.index(my_app)][7] < apps[apps.index(my_app)][6]:
        logger.info('workload: ' + my_app[4] + ' sleep 5 sec: '
                    + str(apps[apps.index(my_app)][6]) + ' > ' + str(apps[apps.index(my_app)][7]))
        time.sleep(5)
    if apps[apps.index(my_app)][7] < apps[apps.index(my_app)][6]:
        logger.info('workload: func: ' + my_app[4] + ' sleep 10sec: '
                    + str(apps[apps.index(my_app)][6]) + ' > ' + str(apps[apps.index(my_app)][7]))
        time.sleep(10)
    if apps[apps.index(my_app)][7] < apps[apps.index(my_app)][6]:
        logger.info('workload: func: ' + my_app[4] + ' sleep 15sec: '
                    + str(apps[apps.index(my_app)][6]) + ' > ' + str(apps[apps.index(my_app)][7]))
        time.sleep(15)
    if apps[apps.index(my_app)][7] < apps[apps.index(my_app)][6]:
        logger.info('workload: func: ' + my_app[4] + ' sleep ' + str(max_request_timeout - 30 + 1) + 'sec: '
                    + str(apps[apps.index(my_app)][6]) + ' > ' + str(apps[apps.index(my_app)][7]))
        time.sleep(max_request_timeout - 30 + 1)

    logger.info("Workload: done, func: " + my_app[4] + " created:" + str(my_app[6])
                + " recv:" + str(apps[apps.index(my_app)][7]))

    # App workload is finished, call main_handler if timer is not already stopped
    if under_test:
        main_handler('app_done', 'INTERNAL')
    logger.info('workload: func: ' + my_app[4] + ' stop')
    return 'workload: Generator done'


def all_apps_done():
    global logger
    global apps
    global sensor_log
    global time_based_termination
    global test_finished  # by the last app
    global node_role
    global peers
    global max_request_timeout
    global lock
    global sensor_log
    logger.info('all_apps_done: start')
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    # alternative, if exist any -1 in finished time list, wait for timeout and then finish

    # all apps termination
    all_apps_done = True
    for app in apps:
        # Among enabled apps
        if app[1] == True:
            # Have you finished creating?
            if app[6] != 0:
                # Have you finished receiving?
                if app[6] == app[7]:
                    # app is done
                    logger.info("all_apps_done: True: Func {0} done, recv {1} of {2}".format(
                        app[4], str(app[7]), str(app[6])))
                else:
                    # receiving in progress
                    logger.info(
                        'all_apps_done: False: func ' + app[4] + ' created < recv: ' + str(app[6]) + " < " + str(
                            app[7]))
                    all_apps_done = False
                    break
            else:  # creating in progres
                logger.info('all_apps_done:False: func ' + app[4] + ' not set created yet')
                all_apps_done = False
                break

    logger.info('all_apps_done: stop: ' + str(all_apps_done))
    return all_apps_done


def create_sensor(counter, func_name, func_data, admission_deadline):
    global sessions
    global session_enabled
    global pics_num
    global pics_folder
    global sensor_log
    global gateway_IP
    global node_IP
    global overlapped_allowed
    global debug
    global battery_cfg
    global sensor_admission_timeout
    global functions
    global boot_up_delay
    global lock

    # one-off sensor
    sample_started = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    try:
        # random image name, pic names must be like "pic_1.jpg"????
        n = random.randint(1, pics_num)
        #????Only pics image if yolo3 or ssd is in the function name. A parameter in the app config should tell if a function read images or not and it should be passed to the sensor_create.
        if 'yolo3' in func_name or 'ssd' in func_name:
            file_name = 'pic_' + str(n) + '.jpg'
            file = {'image_file': open(pics_folder + file_name, 'rb')}

        # create sensor id
        sensor_id = str(sample_started) + '#' + func_name + '-#' + str(counter)
        # [0] func_name [1]created, [2]submitted/admission-dur, [3]queue-dur, [4]exec-dur,
        # [5] finished, [6]rt, [7] status, [8] repeat
        sensor_log[sensor_id] = [func_name, sample_started, 0, 0, 0, 0, 0, -1, 0]

        # drop if no energy on node (in battery sim mode only)
        if battery_cfg[0] == True:
            soc = battery_cfg[3]
            min_battery_charge = battery_cfg[8]
            if soc < min_battery_charge:
                if debug: logger.info('dropped 451 -- dead node')
                # drop and set code to 451
                sensor_log[sensor_id][7] = 451
                # skip the rest of the thread
                return None
            # node come back to up, but not ready yet, drop it, except scheduler is warm
            elif (sample_started - battery_cfg[9]) < boot_up_delay:
                if debug: logger.info('dropped 452 -- booting up')
                # drop and set code to 452
                sensor_log[sensor_id][7] = 452
                # skip the rest of the thread
                return None

        # value: Send async req to yolo function along with image_file
        if func_data == 'value':
            # no response is received, just call back is received
            ##
            url = 'http://' + gateway_IP + ':31112/async-function/' + func_name
            header = {'X-Callback-Url': 'http://' + node_IP + ':5000/actuator',
                      'Sensor-ID': sensor_id}
            #??? only ssd and yolo is accepted for image load
            img = (file if 'yolo3' in func_name or 'ssd' in func_name else None)

            json_list = {}
            if 'crop-monitor' in func_name:
                json_list = {"user": sensor_id, "temperature": "10", "humidity": "5",
                             "moisture": "3", "luminosity": "1"}
            elif 'irrigation' in func_name:
                json_list = {"user": sensor_id, "temperature": "10", "humidity": "5",
                             "soil_temperature": "3", "water_level": "1", "spatial_location": "1"}
            # send
            if session_enabled:
                response = sessions[func_name].post(url, headers=header, files=img, json=json_list,
                                                    timeout=sensor_admission_timeout)
            else:
                response = requests.post(url, headers=header, files=img, json=json_list,
                                         timeout=sensor_admission_timeout)


        # Pioss: Send the image to Pioss. Then, it notifies the function.
        elif func_data == 'reference':
            url = 'http://' + node_IP + ':5000/pioss/api/write/' + func_name + '/' + file_name
            #???only ssd and yolo is accepted
            img = (file if 'yolo3' in func_name or 'ssd' in func_name else None)
            header = {'Sensor-ID': sensor_id}
            if session_enabled:
                response = sessions[func_name].post(url, headers=header, timeout=sensor_admission_timeout, files=img)
            else:
                response = requests.post(url, headers=header, timeout=sensor_admission_timeout, files=img)
            # no response is received
            # finished when next operation (sending actual requst to function) is done.
        else:  # Minio
            pass

        # handle 404 error ?????
        if response.status_code == 202 or response.status_code == 200:

            now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            sample_elapsed = now - sample_started
            if debug: logger.info('submitted (' + str(round(sample_elapsed, 2)) + 's)')
            # Set admission duration
            sensor_log[sensor_id][2] = round(sample_elapsed, 2)
            if (sample_elapsed) >= admission_deadline:
                logger.warning('admission overlapped (' + str(sample_elapsed) + 's)')
                if not overlapped_allowed:
                    logger.error('admission overlapped (' + str(sample_elapsed) + 's)')

        else:
            logger.error(func_name + '#' + str(counter) + '\n' + str(response.status_code))
    except requests.exceptions.ReadTimeout as ee:
        logger.error('ReadTimeout:' + func_name + '#' + str(counter) + '\n' + str(ee))
    except requests.exceptions.RequestException as e:
        logger.error('RequestException:' + func_name + '#' + str(counter) + '\n' + str(e))
    except Exception as eee:
        logger.error('Exception:' + func_name + '#' + str(counter) + '\n' + str(eee))


# Pi Object Storage System (Pioss)
# API-level and Method-level route decoration
@app.route('/pioss/api/write/<func_name>/<file_name>', methods=['POST'], endpoint='write_filename')
@app.route('/pioss/api/read/<func_name>/<file_name>', methods=['GET'], endpoint='read_filename')
def pioss(func_name, file_name):
    global file_storage_folder
    global logger
    global lock
    global gateway_IP
    global sensor_admission_timeout
    global debug
    global sessions
    global session_enabled
    # write operations
    if request.method == 'POST':
        if debug: logger.info('Pioss Write')
        try:
            with lock:
                try:
                    # get image
                    file = request.files['image_file']
                except:
                    logger.error('pioss: ' + func_name + ': ' + file_Name + ': unable to get')
                try:
                    # download
                    file.save(file_storage_folder + file_name)
                    if debug: logger.info('Pioss: write done - func:' + func_name + ' - ' + file_name)
                except:
                    logger.error('pioss: ' + func_name + ': ' + file_Name + ': unable to download')

                # notification: trigger the object detection function
                # curl -X POST -H "X-Callback-Url: http://10.0.0.91:5000/actuator" -H "Image-URL:http://10.0.0.91:5000/pioss/api/read/pic_41.jpg" http://10.0.0.91:31112/async-function/yolo3
                # Example: curl -X POST -F image_file=@./storage/pic_121.jpg  http://10.0.0.90:31112/function/yolo3
                # add sensor-id to -H

                # Trigger the function and pass Image_URL
                url = 'http://' + gateway_IP + ':31112/async-function/' + func_name
                image_URL = 'http://' + node_IP + ':5000/pioss/api/read/' + func_name + '/' + file_name
                callback_url = 'http://' + node_IP + ':5000/actuator'
                header = {'X-Callback-Url': callback_url,
                          'Image-URL': image_URL,
                          'Sensor-ID': str(request.headers.get('Sensor-ID'))}
                try:
                    if session_enabled:
                        response = sessions[func_name].post(url, headers=header, timeout=sensor_admission_timeout)
                    else:
                        response = requests.post(url, headers=header, timeout=sensor_admission_timeout)
                except:
                    logger.error('pioss: ' + func_name + ': ' + file_Name + ': sending failed')
                # no response is received
                if response.status_code == 200 or response.status_code == 202:
                    if debug: logger.info('Pioss: Notification Sent: ' + url)
                else:
                    logger.error('Pioss: Failed')
                return "write&notification done"
        except:
            logger.error('Pioss: write failed (make sure openfaas components are up and deployed on master only)')


    # read operation
    elif request.method == 'GET':
        if debug: logger.info('Pioss Read')
        # get file
        img = open(file_storage_folder + file_name, 'rb').read()
        # preapare response (either make_response or send_file)
        response = make_response(img)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename=file_name)

        return response
        # return send_file(io.BytesIO(img), attachment_filename=file_name)
    else:
        logger.error('Pioss: operation not found')
        return "Failed"


@app.route('/actuator', methods=['POST'])
def owl_actuator():
    global logger
    global actuations
    global response_time
    global test_started
    global sensor_log
    global time_based_termination
    global apps
    global peers
    global suspended_replies
    global debug

    with lock:
        if debug: logger.info('actuator: '
                              + str(request.headers.get('Sensor-Id')) + ' - code: '
                              + str(request.headers.get("X-Function-Status")) + ' - '
                              + str(round(float(request.headers.get('X-Duration-Seconds')), 2)
                                    if request.headers.get('X-Duration-Seconds') is not None
                                       and request.headers.get('X-Duration-Seconds') != "" else "-0.0") + ' s')
        data = request.get_data(as_text=True)


        actuations += 1

        # get sensor id
        # X-Function-Status: 500
        # X-Function-Name: yolo3
        get_id = str(request.headers.get('Sensor-Id'))
        # print('get_id: ' + str(get_id))

        # if failed
        if get_id == 'None':
            # if debug: logger.warning('Actuator - Sensor-ID=None| app: ' +request.headers.get("X-Function-Name") + '| code: ' + request.headers.get("X-Function-Status") +' for #' + str(actuations))
            if debug: logger.warning("Actuator: " + str(request.headers))
            func_name = str(request.headers.get("X-Function-Name"))
            status = int(request.headers.get("X-Function-Status"))
            # IGNORED
            # NOTE: X-start-Time in headers is based on a different timeslot and format than my timestamp
            # sometimes X-Start-Time header is missed in replies with code 500, so set start_time=now
            if str(request.headers.get("X-Start-Time")) != 'None':
                start_time = float(request.headers.get("X-Start-Time"))
            else:
                start_time = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            # END IGNORED

            stop_time = start_time = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            exec_dur = float(request.headers.get("X-Duration-Seconds"))

            # add to suspended replies
            suspended_replies.append([func_name, status, stop_time, exec_dur])
        else:  # code=200
            print('Actuator: Duration: ', str(request.headers.get('X-Duration-Seconds')))

            response_time.append(float(request.headers.get('X-Duration-Seconds')))

            # [0] function_name already set
            # [1]created time already set
            # [2]admission duration already set
            # [3] set NATstream queuing duration
            # NOTE: Openfaas X-Start-Time value is in 19 digits, not simillar to my timestamp
            # sensor_log[get_id][2]= float(request.headers.get('X-Start-Time')) - sensor_log[get_id][0] - sensor_log[get_id][1]
            sensor_log[get_id][3] = None
            # [4] set execution duration=given by openfaas
            sensor_log[get_id][4] = round(float(request.headers.get('X-Duration-Seconds')), 3)
            # [5] finished time=now
            now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            sensor_log[get_id][5] = now
            # [6]set response time (round trip)=finished time- created time
            sensor_log[get_id][6] = round(sensor_log[get_id][5] - sensor_log[get_id][1], 3)
            # [3] queuing=response time - admission dur. and execution dur.
            sensor_log[get_id][3] = round(sensor_log[get_id][6] - sensor_log[get_id][2] - sensor_log[get_id][4], 3)
            if sensor_log[get_id][3] < 0: sensor_log[get_id][3] = 0
            # [7] status code
            sensor_log[get_id][7] = int(request.headers.get('X-Function-Status'))
            # [8] replies
            sensor_log[get_id][8] = sensor_log[get_id][8] + 1
            # increment received
            c = [index for index, app in enumerate(apps) if app[4] == sensor_log[get_id][0]]
            apps[c[0]][7] += 1

            # if repetitious
            if sensor_log[get_id][8] > 1:
                logger.error('Actuator: a repetitious reply received: ' + str(sensor_log[get_id]))

    return 'Actuator Sample Done'


# ---------------------------------------
def failure_handler():
    global logger
    global sensor_log
    global max_request_timeout
    global failure_handler_interval
    global suspended_replies
    global apps
    global under_test
    logger.info('failure_handler: start')
    # status codes:
    # 404: happens in create_sensor: not submitted to gateway as function does not exist (already removed)
    # 500: happens after submission: submitted but while executing, function started rescheduling to going down. Partial execution of task can happen here
    # 502: happens after submission: submitted but function is in scheduling process and is not up yet
    # 502: function timeout (especified in function yaml file)
    # 503: gateway timeout (especified in gateway yaml by kubectl edit deploy/gateway -n openfaas
    # note: queue-worker timeout seems ineffective
    # function and gateway have timeout settings.
    wrap_up = max_request_timeout + (failure_handler_interval * 2)

    while under_test or wrap_up > 0:
        # missed sensors
        missed_sensor_log = {}

        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        # exist suspended replies, set on failed replies in owl_actuator
        if len(suspended_replies) > 0:
            # set missed sensors
            for key, sensor in sensor_log.items():
                # among those with no reply received by code
                if sensor[7] == -1:
                    # make sure it will not receive any reply
                    # and outdated (must have received a timeout reply at least, so it's missed)
                    if sensor[1] + max_request_timeout < now:
                        # add to missed sensors
                        missed_sensor_log[key] = sensor
            # sort missed sensors ascendingly by creation time
            # NOTE: sort, remove, etc. return None and should not be assigned to anything
            sorted(missed_sensor_log.items(), key=lambda e: e[1][1])

            # sort suspended replies ascendingly by stop_time
            suspended_replies.sort(key=lambda x: x[2])

            # assign suspended_replies to outdated missed_sensors
            for key, missed_sensor in missed_sensor_log.items():
                for reply in suspended_replies:
                    # As sorted, get the first match and break
                    # same application
                    # reply=[func_name, status, stop_time, exec_dur] #start_time is not used???? It is sometimes missed in replies 500 by OpenFaaS
                    if missed_sensor[0] == reply[0]:
                        # set exec_duration
                        missed_sensor[4] = reply[3]
                        # set status
                        missed_sensor[7] = reply[1]
                        # set reply counter
                        missed_sensor[8] = missed_sensor[8] + 1

                        # update sensor_log
                        sensor_log[key] = missed_sensor

                        # increment received
                        c = [index for index, app in enumerate(apps) if app[4] == missed_sensor[0]]
                        apps[c[0]][7] += 1

                        # removal of the suspended reply
                        suspended_replies.remove(reply)
                        break
        time.sleep(failure_handler_interval)

        if not under_test:
            # only first time run
            if wrap_up == max_request_timeout + (failure_handler_interval * 2):
                logger.info("failure_handler: wrapping up: " + str(wrap_up) + "sec...")
            if not all_apps_done():  # is all_apps_done, no need to wait for failure handler
                wrap_up -= failure_handler_interval
            else:
                break
            # only last time run
            if wrap_up <= 0:
                logger.info('failure_handler:missed' + str(missed_sensor_log))
                logger.info('failure_handler:suspended' + str(suspended_replies))
    logger.info('failure_handler: stop')


# monitoring
def monitor():
    logger.info('start')
    global monitor_interval
    global down_time
    global current_time
    global current_time_ts
    global response_time_accumulative
    global battery_charge
    if utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4'): global pijuice
    global cpuUtil
    global cpu_temp
    global cpu_freq_curr
    global cpu_freq_max
    global cpu_freq_min
    global cpu_ctx_swt
    global cpu_inter
    global cpu_soft_inter
    global memory
    global disk_usage
    global disk_io_usage
    global bw_usage
    global power_usage
    global under_test
    global raspbian_upgrade_error
    global battery_cfg

    while under_test:
        # time
        # ct = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
        ct = datetime.datetime.now(datetime.timezone.utc).astimezone()  # local
        ct_ts = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()  # local ts

        current_time.append(ct)
        current_time_ts.append(ct_ts)

        # response time
        if not response_time:
            response_time_accumulative.append(0)
        else:
            response_time_accumulative.append(round(sum(response_time) / len(response_time), 3))
        # read Pijuice battery
        if (utils.what_device_is_it('raspberry pi 3') or utils.what_device_is_it('raspberry pi 4')) and battery_operated:
            charge = pijuice.status.GetChargeLevel()
            battery_charge.append(int(charge['data']))
        # battery sim
        elif battery_cfg[0] == True:
            max_battery_charge = battery_cfg[1]
            soc = battery_cfg[3]
            soc_percent = round(soc / max_battery_charge * 100)
            battery_charge.append(soc_percent)

        else:
            battery_charge.append(-1)

        # read cpu
        cpu = psutil.cpu_percent()
        #read GPU???for Jetson Nano
        cpuUtil.append(cpu)
        # cpu frequency
        freq = re.split(', |=', str(psutil.cpu_freq()).split(')')[0])
        cpu_freq_curr.append(int(freq[1].split('.')[0]))
        cpu_freq_min.append(int(freq[3].split('.')[0]))
        cpu_freq_max.append(int(freq[5].split('.')[0]))

        swt = re.split(', |=', str(psutil.cpu_stats()).split(')')[0])
        cpu_ctx_swt.append(int(swt[1]))
        cpu_inter.append(int(swt[3]))
        cpu_soft_inter.append(int(swt[5]))

        # read memory
        memory_tmp = psutil.virtual_memory().percent
        memory.append(memory_tmp)
        # read disk
        disk_usage_tmp = psutil.disk_usage("/").percent
        disk_usage.append(disk_usage_tmp)
        # read disk I/O: read_count, write_count, read_bytes, write_bytes
        if raspbian_upgrade_error:
            tmp = ['-1', '-1', '-1', '-1', '-1', '-1', '-1', '-1', ]
        else:
            tmp = str(psutil.disk_io_counters()).split("(")[1].split(")")[0]
            tmp = re.split(', |=', tmp)
        tmp_list = [int(tmp[1]), int(tmp[3]), int(tmp[5]), int(tmp[7])]
        disk_io_usage.append(tmp_list)
        # read cpu temperature
        sensors_temp = psutil.sensors_temperatures()
        if utils.what_device_is_it('raspberry pi'):
            cpu_temp_curr = sensors_temp['cpu_thermal'][0]
            cpu_temp_curr = re.split(', |=', str(cpu_temp_curr))[3]
        elif utils.what_device_is_it('nvidia jetson nano'):
            cpu_temp_curr = sensors_temp['thermal-fan-est'][0]
            cpu_temp_curr = re.split(', |=', str(cpu_temp_curr))[3]
        else:
            #??? cpu temperature for some devices like Intel NUC are not found in this way.
            cpu_temp_curr = "0"
        cpu_temp.append(cpu_temp_curr)
        # read bandwidth: packets_sent, packets_rec, bytes_sent, bytes_rec, bytes_dropin, bytes_dropout
        bw_tmp = [psutil.net_io_counters().packets_sent, psutil.net_io_counters().packets_recv,
                  psutil.net_io_counters().bytes_sent, psutil.net_io_counters().bytes_recv,
                  psutil.net_io_counters().dropin, psutil.net_io_counters().dropout]
        bw_usage.append(bw_tmp)

        # read usb power meter
        if usb_meter_involved:
            power_usage.append(read_power_meter())
        else:
            power_usage.append([-1, -1, -1, -1, -1, -1])

        time.sleep(monitor_interval)

    # close bluetooth connection
    if usb_meter_involved:
        sock.close()

    logger.info('done')


def read_power_meter():
    global lock
    global sock
    global logger
    output = []
    # Send request to USB meter
    d = b""
    with lock:
        while True:
            sock.send((0xF0).to_bytes(1, byteorder="big"))
            d += sock.recv(130)
            if len(d) != 130:
                continue
            else:
                break

    # read data
    data = {}
    data["Volts"] = struct.unpack(">h", d[2: 3 + 1])[0] / 1000.0  # volts
    data["Amps"] = struct.unpack(">h", d[4: 5 + 1])[0] / 10000.0  # amps
    data["Watts"] = struct.unpack(">I", d[6: 9 + 1])[0] / 1000.0  # watts
    data["temp_C"] = struct.unpack(">h", d[10: 11 + 1])[0]  # temp in C

    g = 0
    for i in range(16, 95, 8):
        ma, mw = struct.unpack(">II", d[i: i + 8])  # mAh,mWh respectively
        gs = str(g)

        data[gs + "_mAh"] = ma
        data[gs + "_mWh"] = mw
        g += 1

    temp = [data["0_mWh"], data["0_mAh"],
            data["Watts"], data["Amps"], data["Volts"],
            data["temp_C"]]

    output = temp

    return output


# connect to USB power meter
def usb_meter_connection():
    # python usbmeter --addr 00:15:A5:00:03:E7 --timeout 10 --interval 1 --out /home/pi/logsusb
    global sock
    global logger
    global bluetooth_addr
    sock = None
    addr = bluetooth_addr

    # Disconnect previous Bluetooth connection???
    # instead, do not reconnect after each test. Keep using previous connection
    # or shotdown() and then close() socket after each test
    # or use hcitool in python https://www.programcreek.com/python/example/14725/bluetooth.BluetoothSocket
    stoutdata = sp.getoutput("sudo hcitool dc " + bluetooth_addr)
    logger.info("Bluetooth disconnected")
    connected = False

    while True:
        try:
            sock = BluetoothSocket(RFCOMM)
        except Exception as e:
            logger.error(str(e))
            logger.error('Bluetooth driver might not be installed, or python is used instead of ***python3***')
        # sock.settimeout(10)
        try:
            logger.info("usb_meter_connection: Attempting connection...")
            res = sock.connect((addr, 1))
        except btcommon.BluetoothError as e:
            logger.warning("usb_meter_connection: attempt failed: " + str(e))
            connected = False
        except:
            logger.warning("usb_meter_connection: attempt failed2:" + addr)
            connected = False
        else:
            print("Connected OK")
            logger.info('usb_meter_connection: USB Meter Connected Ok (' + addr + ')')
            connected = True
            break
        time.sleep(3)

    # time.sleep(60)
    if connected == False:
        # wifi on
        cmd = "rfkill unblock all"
        print(cmd)
        logger.info(cmd)
        utils.shell(cmd)
        print('usb_meter_connection: ERROR-USB Meter Failed to connect!!!!!')
        logger.error('ERROR-USB Meter Failed to connect!!!!!')
        if battery_operated: battery_power('ON')
        # logger.error('usb_meter_connection: Node in Sleep...')
        # time.sleep(86400)

    return connected


# ---------------------------------

def save_reports():
    global metrics
    global node_name
    global apps
    global test_name
    global log_path
    global test_started
    global test_finished
    global sensor_log
    global node_role
    global snapshot_report
    global throughput
    global throughput2
    global down_time
    global functions
    global workers

    test_finished = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    test_duration = round((test_finished - test_started) / 60, 0)

    metrics["info"] = {"test_name": test_name,
                       "test_duration": test_duration,
                       "test_started": test_started,
                       "test_finished": test_finished}
    # print logs
    logger.critical('save_reports: Test ' + test_name + ' lasted: '
                    + str(test_duration) + ' min')

    if node_role == "LOAD_GENERATOR" or node_role == "STANDALONE":
        # OVERALL

        # calculate response times
        app_name = []
        creation_time = []
        admission_duration = []
        queuing_duration = []
        execution_duration = []
        useless_execution_duration = []
        finished_time = []
        response_time_suc = []
        response_time_suc_fail = []
        # sensors
        created = 0
        sent = 0
        recv = 0
        for app in apps:  # ???index based on apps order, in future if apps change, it changes
            if app[1] == True:
                created += copy.deepcopy(app[6])
                recv += copy.deepcopy(app[7])

        logger.critical('created {} recv {}'.format(created, recv))

        # replies
        # actuator/reply counter
        replies_counter = [0] * len(apps)
        # reply status
        replies_status = [[0] * 6 for _ in range(len(apps))]  # *len(apps) #status code of 200, 500, 502, 503, others
        # dropped sensors per app
        dropped_sensors = [0] * len(apps)
        # dropped due to boot up per app
        dropped_sensors_in_boot_up = [0] * len(apps)
        # [0] func_name [1]created, [2]submitted/admission-dur, [3]queue-dur, [4]exec-dur. [5] finished, [6]rt
        sensor_data = []

        labels = ['func_name', 'created_at', 'admission', 'queue', 'exec', 'finished_at',
                  'round_trip', 'status', 'replies']
        sensor_data.append(labels)

        for sensor in sensor_log.values():  # consider failed ones ?????
            # Get app index
            c = [index for index, app in enumerate(apps) if app[4] == sensor[0]]
            app_index = apps.index(apps[c[0]])

            if sensor[7] != 451 and sensor[
                7] != 452:  # dropped (not sent) sensors are not involved in response time and replies
                # time and durations
                admission_duration.append(sensor[2])
                if sensor[7] == 200:  # only success sensors contribute in response time????? weight of failed ones???
                    creation_time.append(sensor[1])
                    finished_time.append(sensor[5])

                    queuing_duration.append(sensor[3])
                    execution_duration.append(sensor[4])

                    response_time_suc.append(sensor[6])
                    response_time_suc_fail.append(sensor[6])

                else:
                    useless_execution_duration.append(sensor[4])
                    # app timeout = max exec time
                    func_info = apps[app_index][8]
                    func_timeout = int(func_info[12].split('s')[0])
                    response_time_suc_fail.append(func_timeout)
                # reply counter
                replies_counter[app_index] += sensor[8]

                # reply status
                if sensor[7] == 200:
                    replies_status[app_index][0] += 1
                elif sensor[7] == 500:
                    replies_status[app_index][1] += 1
                elif sensor[7] == 502:
                    replies_status[app_index][2] += 1
                elif sensor[7] == 503:
                    replies_status[app_index][3] += 1
                elif sensor[7] == -1:
                    replies_status[app_index][4] += 1
                else:  # others
                    replies_status[app_index][5] += 1

                # sent
                sent += 1

            # dropped sensor
            else:
                if sensor[7] == 451:
                    dropped_sensors[app_index] += 1
                elif sensor[7] == 452:
                    dropped_sensors_in_boot_up[app_index] += 1
                else:
                    logger.error('unknown dropped_sensor')

            # data list
            sensor_data.append([str(sensor[0]), str(sensor[1]), str(sensor[2]),
                                str(sensor[3]), str(sensor[4]), str(sensor[5]),
                                str(sensor[6]), str(sensor[7]), str(sensor[8])])

        # save sensor data
        log_index = log_path + "/" + node_name + "-sensors.csv"
        logger.critical('save_reports: ' + log_index)
        np.savetxt(log_index, sensor_data, delimiter=",", fmt="%s")

        # PRINT LOGS of METRICS
        logger.critical('METRICS: OVERALL****************************')

        # OVERALL created recv by replies (actuators)
        logger.critical('OVERALL: REQ. CREATED: ' + str(created)
                        + '     RECV (by apps): ' + str(recv) + '     RECV (by sensor[8] counter): ' + str(
            sum(replies_counter)))
        sent_percent = round(sent / created * 100, 2) if created > 0 else 0
        logger.critical('OVERALL: REQ. SENT: ' + str(sent) + ' (' + str(sent_percent) + ' %)')

        # OVERALL status codes
        code200 = 0
        code500 = 0
        code502 = 0
        code503 = 0
        code_1 = 0
        others = 0
        for row in replies_status:
            code200 += row[0]
            code500 += row[1]
            code502 += row[2]
            code503 += row[3]
            code_1 += row[4]
            others += row[5]
        success_rate = (round((code200 / sum([code200, code500, code502, code503, code_1, others])) * 100, 2)
                        if sum([code200, code500, code502, code503, code_1, others]) > 0 else 0)

        logger.critical("OVERALL: Success Rate (200/sent): {}%".format(success_rate))
        logger.critical(
            "OVERALL: Success Rate (200/sent) new: {}%".format(round(code200 / sent * 100, 2) if sent > 0 else 0))
        logger.critical("OVERALL: {0}{1}{2}{3}{4}{5}".format(
            'CODE200=' + str(code200) if code200 > 0 else ' ',
            ', CODE500=' + str(code500) if code500 > 0 else ' ',
            ', CODE502=' + str(code502) if code502 > 0 else ' ',
            ', CODE503=' + str(code503) if code503 > 0 else ' ',
            ', CODE-1=' + str(code_1) if code_1 > 0 else ' ',
            ', OTHERS=' + str(others) if others > 0 else ' '))

        dropped_sensors_sum = sum(dropped_sensors)
        dropped_sensors_percent = round((sum(dropped_sensors) / created) * 100, 2) if created > 0 else 0
        logger.critical("OVERALL: Dropped Sensors (created, not sent): sum "
                        + str(dropped_sensors_sum) + " --- percent " + str(dropped_sensors_percent) + " %")
        dropped_sensors_in_boot_up_sum = sum(dropped_sensors_in_boot_up)
        dropped_sensors_in_boot_percent = round((sum(dropped_sensors_in_boot_up) / created) * 100,
                                                2) if created > 0 else 0
        logger.critical("OVERALL: Dropped Sensors in boot up (created, not sent): "
                        + "sum(" + str(dropped_sensors_in_boot_up_sum) + ") "
                        + " --- percent " + str(dropped_sensors_in_boot_percent) + " %")

        # OVERALL response time
        admission_duration_avg = round(statistics.mean(admission_duration), 2) if len(admission_duration) else 0
        admission_duration_max = round(max(admission_duration), 2) if len(admission_duration) else 0
        queuing_duration_avg = round(statistics.mean(queuing_duration), 2) if len(queuing_duration) else 0
        queuing_duration_max = round(max(queuing_duration), 2) if len(queuing_duration) else 0

        execution_duration_avg = round(statistics.mean(execution_duration), 2) if len(execution_duration) else 0
        execution_duration_max = round(max(execution_duration), 2) if len(execution_duration) else 0

        response_time_suc_avg = round(statistics.mean(response_time_suc), 2) if len(response_time_suc) else 0
        response_time_suc_max = round(max(response_time_suc), 2) if len(response_time_suc) else 0

        response_time_suc_fail_avg = round(statistics.mean(response_time_suc_fail), 2) if len(
            response_time_suc_fail) else 0
        response_time_suc_fail_max = round(max(response_time_suc_fail), 2) if len(response_time_suc_fail) else 0

        useless_execution_duration_sum = round(sum(useless_execution_duration)) if len(
            useless_execution_duration) else 0

        logger.critical('OVERALL: avg. Adm. Dur. (sent only)---> ' + str(admission_duration_avg)
                        + '  (max= ' + str(admission_duration_max) + ')')
        logger.critical('OVERALL: avg. Q. Dur. (success only) ---> ' + str(queuing_duration_avg)
                        + '  (max= ' + str(queuing_duration_max) + ')')
        logger.critical('OVERALL: avg. Exec. +(scheduling) Dur. (success only) ---> '
                        + str(execution_duration_avg)
                        + '  (max= ' + str(execution_duration_max) + ')')
        logger.critical('OVERALL: avg. RT (success only) ---> ' + str(response_time_suc_avg)
                        + '  (max= ' + str(response_time_suc_max) + ')')
        logger.critical('OVERALL: avg. RT (success + fail) ---> ' + str(response_time_suc_fail_avg)
                        + '  (max= ' + str(response_time_suc_fail_max) + ')')
        logger.critical('OVERALL: sum Useless Exec. Dur. ---> ' + str(useless_execution_duration_sum))

        # Percentile
        percentiles_suc = (
            np.percentile(response_time_suc, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(response_time_suc) else [0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0])
        percentiles_suc = ([round(num, 3) for num in percentiles_suc])

        percentiles_suc_fail = (np.percentile(response_time_suc_fail, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(
            response_time_suc_fail) else [0, 0, 0, 0, 0, 0, 0, 0, 0])
        percentiles_suc_fail = ([round(num, 3) for num in percentiles_suc_fail])
        logger.critical('OVERALL: Percentiles (success only): ' + str(percentiles_suc))
        logger.critical('OVERALL: Percentiles (success success + fail): ' + str(percentiles_suc_fail))
        # Throughput (every 30sec)
        throughput = []
        throughput2 = []
        timer = test_started + 30

        while True:
            created_tmp = 0
            for time in creation_time:
                if time < timer and time > timer - 30:
                    created_tmp += 1

            finished = 0
            for time in finished_time:
                if time < timer and time > timer - 30:
                    finished += 1

            # avoid divided by zero
            if created_tmp == 0:
                throughput.append(0)
            else:
                throughput.append((finished / created_tmp) * 100)
            throughput2.append(finished / 30)

            if timer >= (test_finished):
                break
            else:
                timer += 30

        throughput_avg = round(statistics.mean(throughput), 2) if len(throughput) else 0
        throughput_max = round(max(throughput), 2) if len(throughput) else 0
        throughput2_avg = round(statistics.mean(throughput2), 2) if len(throughput2) else 0
        throughput2_max = round(max(throughput2), 2) if len(throughput2) else 0

        logger.critical('OVERALL:throughput (success only)---> ' + str(throughput_avg)
                        + '  (max= ' + str(throughput_max) + ')')
        logger.critical('OVERALL:throughput2 (success only)---> ' + str(throughput2_avg)
                        + '  (max= ' + str(throughput2_max) + ')')

        metrics["app_overall"] = {"created": created, "sent": {"sum": sent, "percent": sent_percent},
                                  "code200": {"sum": code200, "percent": success_rate},
                                  "code500": code500, "code502": code502, "code503": code503, "code-1": code_1,
                                  "others": others,
                                  "dropped": {"sum": dropped_sensors_sum, "percent": dropped_sensors_percent},
                                  "dropped_in_bootup": {"sum": dropped_sensors_in_boot_up_sum,
                                                        "percent": dropped_sensors_in_boot_percent},
                                  "admission_dur": {"avg": admission_duration_avg, "max": admission_duration_max},
                                  "queue_dur": {"avg": queuing_duration_avg, "max": queuing_duration_max},
                                  "exec_dur": {"avg": execution_duration_avg, "max": execution_duration_max},
                                  "round_trip_suc": {"avg": response_time_suc_avg, "max": response_time_suc_max},
                                  "round_trip_suc_fail": {"avg": response_time_suc_fail_avg,
                                                          "max": response_time_suc_fail_max},
                                  "useless_exec_dur": useless_execution_duration_sum,
                                  "percentiles_suc": {"p0": percentiles_suc[0], "p25": percentiles_suc[1],
                                                      "p50": percentiles_suc[2], "p75": percentiles_suc[3],
                                                      "p90": percentiles_suc[4], "p95": percentiles_suc[5],
                                                      "p99": percentiles_suc[6],
                                                      "p99.9": percentiles_suc[7], "p100": percentiles_suc[8]},
                                  "percentiles_suc_fail": {"p0": percentiles_suc_fail[0],
                                                           "p25": percentiles_suc_fail[1],
                                                           "p50": percentiles_suc_fail[2],
                                                           "p75": percentiles_suc_fail[3],
                                                           "p90": percentiles_suc_fail[4],
                                                           "p95": percentiles_suc_fail[5],
                                                           "p99": percentiles_suc_fail[6],
                                                           "p99.9": percentiles_suc_fail[7],
                                                           "p100": percentiles_suc_fail[8]},
                                  "throughput2": {"avg": throughput2_avg, "max": throughput2_avg}}

        logger.critical('METRICS PER APP  ****************************')
        app_order = []

        # per app rt
        # how many apps?
        for app in apps:
            creation_time = []
            admission_duration = []
            queuing_duration = []
            execution_duration = []
            useless_execution_duration = []
            finished_time = []
            response_time_suc = []
            response_time_suc_fail = []
            reply = 0
            status = [0] * 6
            dropped_sensor = 0
            dropped_sensor_in_boot_up = 0
            if app[1] == True:
                logger.critical('**************     ' + app[0] + '     **************')

                sent = 0

                for sensor in sensor_log.values():
                    # check function name
                    if sensor[0] == app[4]:
                        # dropped sensors are not considered in response time and replies
                        if sensor[7] != 451 and sensor[7] != 452:

                            sent += 1

                            admission_duration.append(sensor[2])
                            reply += sensor[8]
                            if sensor[7] == 200:  # respoonse time only based on success tasks????weight of failed????
                                creation_time.append(sensor[1])
                                queuing_duration.append(sensor[3])
                                execution_duration.append(sensor[4])
                                finished_time.append(sensor[5])
                                response_time_suc.append(sensor[6])
                                response_time_suc_fail.append(sensor[6])
                            else:
                                useless_execution_duration.append(sensor[4])
                                # app timeout = max exec time
                                func_info = app[8]
                                func_timeout = int(func_info[12].split('s')[0])
                                response_time_suc_fail.append(func_timeout)
                            # get status
                            if sensor[7] == 200:
                                status[0] += 1
                            elif sensor[7] == 500:
                                status[1] += 1
                            elif sensor[7] == 502:
                                status[2] += 1
                            elif sensor[7] == 503:
                                status[3] += 1
                            elif sensor[7] == -1:
                                status[4] += 1
                            else:  # others
                                status[5] += 1
                        # if dropped sensor
                        else:
                            if sensor[7] == 451:
                                dropped_sensor += 1
                            elif sensor[7] == 452:
                                dropped_sensor_in_boot_up += 1
                            else:
                                logger.error('dropped sensor unknown')

                # calculate metrics of this app

                # OVERALL created recv by replies (actuators)
                created = app[6]
                recv = app[7]

                app_name = app[0]
                app_order.append(app_name)

                logger.critical('APP(' + app[4] + '): REQ. CREATED: ' + str(created)
                                + ' RECV (by apps): ' + str(recv) + ' RECV (by counter): ' + str(reply))
                sent_percent = round(sent / created * 100, ) if created > 0 else 0
                logger.critical('APP(' + app[4] + '): REQ. SENT: ' + str(sent) + ' (' + str(sent_percent) + ')')
                # status
                sum_s = sum([status[0], status[1], status[2], status[3], status[4], status[5]])
                success_rate = round(status[0] / sum_s * 100, 2) if sum_s > 0 else 0
                logger.critical("APP(" + app[4] + "): Success Rate (200/sent): {}%".format(success_rate))
                logger.critical("APP(" + app[4] + "): Success Rate (200/sent) new: {}%".format(
                    round(status[0] / sent * 100, 2) if sent > 0 else 0))
                logger.critical('APP(' + app[4] + '): {0}{1}{2}{3}{4}{5}'.format(
                    'CODE200=' + str(status[0]) if status[0] > 0 else ' ',
                    'CODE500=' + str(status[1]) if status[1] > 0 else ' ',
                    'CODE502=' + str(status[2]) if status[2] > 0 else ' ',
                    'CODE503=' + str(status[3]) if status[3] > 0 else ' ',
                    'CODE-1=' + str(status[4]) if status[4] > 0 else ' ',
                    'OTHERS=' + str(status[5]) if status[5] > 0 else ' '))

                dropped_sensor_sum = dropped_sensor
                dropped_sensor_percent = round((dropped_sensor / created) * 100, 2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): Dropped (created, not sent): {} - percent {}%".format(
                    dropped_sensor_sum, dropped_sensor_percent))

                dropped_sensor_in_boot_up_sum = dropped_sensor_in_boot_up
                dropped_sensor_in_boot_up_percent = round((dropped_sensor_in_boot_up_sum / created) * 100,
                                                          2) if created > 0 else 0
                logger.critical("APP(" + app[4] + "): Dropped inboot up(created, not sent): {} - percent {}%".
                                format(dropped_sensor_in_boot_up_sum, dropped_sensor_in_boot_up_percent))

                # print per app: ???admission dur should only consider sent sensors, not createds
                admission_duration_avg = round(statistics.mean(admission_duration), 2) if len(admission_duration) else 0
                admission_duration_max = round(max(admission_duration), 2) if len(admission_duration) else 0
                queuing_duration_avg = round(statistics.mean(queuing_duration), 2) if len(queuing_duration) else 0
                queuing_duration_max = round(max(queuing_duration), 2) if len(queuing_duration) else 0
                execution_duration_avg = round(statistics.mean(execution_duration), 2) if len(execution_duration) else 0
                execution_duration_max = round(max(execution_duration), 2) if len(execution_duration) else 0
                response_time_suc_avg = round(statistics.mean(response_time_suc), 2) if len(response_time_suc) else 0
                response_time_suc_max = round(max(response_time_suc), 2) if len(response_time_suc) else 0
                response_time_suc_fail_avg = round(statistics.mean(response_time_suc_fail), 2) if len(
                    response_time_suc_fail) else 0
                response_time_suc_fail_max = round(max(response_time_suc_fail), 2) if len(response_time_suc_fail) else 0
                useless_execution_duration_avg = round(statistics.mean(useless_execution_duration), 2) if len(
                    useless_execution_duration) else 0

                logger.critical('APP(' + app[4] + '): Adm. Dur. (sent only): avg '
                                + str(admission_duration_avg) + ' --- max ' + str(admission_duration_max))

                logger.critical('APP(' + app[4] + '): Q. Dur. (success only): avg '
                                + str(queuing_duration_avg) + ' --- max ' + str(queuing_duration_max))
                logger.critical('APP(' + app[4] + '): Exec. +(scheduling) Dur. (success only): avg '
                                + str(execution_duration_avg) + ' --- max ' + str(execution_duration_max))
                logger.critical('APP(' + app[4] + '): RT (success only): avg '
                                + str(response_time_suc_avg) + ' --- max ' + str(response_time_suc_max))
                logger.critical('APP(' + app[4] + '): RT (success + fail): avg '
                                + str(response_time_suc_fail_avg) + ' --- max ' + str(response_time_suc_fail_max))
                logger.critical('APP(' + app[4] + '): Useless Exec. Dur.: sum '
                                + str(useless_execution_duration_avg))

                # Percentile
                percentiles_suc = (np.percentile(response_time_suc, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(
                    response_time_suc) else [0, 0, 0, 0, 0, 0, 0, 0, 0])
                percentiles_suc = ([round(num, 3) for num in percentiles_suc])
                percentiles_suc_fail = (
                    np.percentile(response_time_suc_fail, [0, 25, 50, 75, 90, 95, 99, 99.9, 100]) if len(
                        response_time_suc_fail) else [0, 0, 0, 0, 0, 0, 0, 0, 0])
                percentiles_suc_fail = ([round(num, 3) for num in percentiles_suc_fail])
                logger.critical('APP(' + app[4] + '): Percentiles (success + fail): '
                                + str(percentiles_suc_fail))

                # System Throughput (every 30sec)
                throughput = []
                throughput2 = []
                timer = test_started + 30

                while True:
                    created_tmp = 0
                    for time in creation_time:
                        if time < timer and time > timer - 30:
                            created_tmp += 1

                    finished = 0
                    for time in finished_time:
                        if time < timer and time > timer - 30:
                            finished += 1

                    # avoid divided by zero
                    if created_tmp == 0:
                        throughput.append(0)
                    else:
                        throughput.append((finished / created_tmp) * 100)
                    throughput2.append(finished / 30)

                    if timer >= (test_finished):
                        break
                    else:
                        timer += 30

                throughput_avg = round(statistics.mean(throughput), 2) if len(throughput) else 0
                throughput_max = round(max(throughput), 2) if len(throughput) else 0
                throughput2_avg = round(statistics.mean(throughput2), 2) if len(throughput2) else 0
                throughput2_max = round(max(throughput2), 2) if len(throughput2) else 0

                logger.critical('APP(' + app[4] + '):throughput (success only) avg '
                                + str(throughput_avg) + ' --- max ' + str(throughput_max))

                logger.critical('APP(' + app[4] + '): throughput2 (success only) avg '
                                + str(throughput2_avg) + ' --- max' + str(throughput2_max))

                metrics[app_name] = {"created": created, "sent": {"sum": sent, "percent": sent_percent},
                                     "code200": {"sum": status[0], "percent": success_rate},
                                     "code500": status[1], "code502": status[2], "code503": status[3],
                                     "code-1": status[4], "others": status[5],
                                     "dropped": {"sum": dropped_sensor_sum, "percent": dropped_sensor_percent},
                                     "dropped_in_bootup": {"sum": dropped_sensor_in_boot_up_sum,
                                                           "percent": dropped_sensor_in_boot_up_percent},
                                     "admission_dur": {"avg": admission_duration_avg, "max": admission_duration_max},
                                     "queue_dur": {"avg": queuing_duration_avg, "max": queuing_duration_max},
                                     "exec_dur": {"avg": execution_duration_avg, "max": execution_duration_max},
                                     "round_trip_suc": {"avg": response_time_suc_avg, "max": response_time_suc_max},
                                     "round_trip_suc_fail": {"avg": response_time_suc_fail_avg,
                                                             "max": response_time_suc_fail_max},
                                     "useless_exec_dur": useless_execution_duration_avg,
                                     "percentiles_suc": {"p0": percentiles_suc[0], "p25": percentiles_suc[1],
                                                         "p50": percentiles_suc[2], "p75": percentiles_suc[3],
                                                         "p90": percentiles_suc[4], "p95": percentiles_suc[5],
                                                         "p99": percentiles_suc[6],
                                                         "p99.9": percentiles_suc[7], "p100": percentiles_suc[8]},
                                     "percentiles_suc_fail": {"p0": percentiles_suc_fail[0],
                                                              "p25": percentiles_suc_fail[1],
                                                              "p50": percentiles_suc_fail[2],
                                                              "p75": percentiles_suc_fail[3],
                                                              "p90": percentiles_suc_fail[4],
                                                              "p95": percentiles_suc_fail[5],
                                                              "p99": percentiles_suc_fail[6],
                                                              "p99.9": percentiles_suc_fail[7],
                                                              "p100": percentiles_suc_fail[8]},
                                     "throughput2": {"avg": throughput2_avg, "max": throughput2_max}}

        # end per app
        if len(app_order):
            app_order.insert(0, 'app_overall')
        metrics["app_order"] = app_order

    # scheduler logs
    if node_role == "MASTER":
        # scheduler logs
        rescheduled_sum = 0
        rescheduled_per_worker = [0] * len(workers)
        rescheduled_per_func = [0] * len(functions)

        for function in functions:
            versions = int(function[2][16])
            # sum
            rescheduled_sum += versions
            # per worker
            index = 0
            for worker in workers:
                if worker[0] == function[0][0]:
                    index = workers.index(worker)
                    break
            rescheduled_per_worker[index] += versions
            # per functions
            rescheduled_per_func[functions.index(function)] += versions
        # print
        logger.critical('Scheduler Logs:\n rescheduling: \n '
                        + 'Sum: ' + str(rescheduled_sum)
                        + '\nPer Worker: ' + ' -- '.join([str(str(workers[index][0]) + ': '
                                                              + str(rescheduled_per_worker[index])) for index in
                                                          range(len(rescheduled_per_worker))])
                        + '\nPer Function: ' + '\n'.join([str(str(functions[index][0][0]) + '-'
                                                              + str(functions[index][0][1]) + ': '
                                                              + str(rescheduled_per_func[index])) for index in
                                                          range(len(rescheduled_per_func))]))

        per_worker = {workers[index][0]: rescheduled_per_worker[index] for index in
                      range(len(rescheduled_per_worker))}
        logger.info(per_worker)

        per_function = {functions[index][0][0] + '-' + functions[index][0][1]:
                            rescheduled_per_func[index] for index in range(len(rescheduled_per_func))}
        # down per scheduling iterations
        down_counter = {worker[0]: 0 for worker in workers}
        # per scheduling_round
        for key, value in history["workers"].items():
            scheudling_round = key
            nodes = value
            # evaluate all nodes SoC one at a time
            for node in nodes:
                soc = node[2]
                min_battery_charge = battery_cfg[8]
                # if node is down, increment its down_counter
                if soc < min_battery_charge:
                    name = node[0]
                    down_counter[name] += 1

        metrics["scheduler"] = {"placements": {"sum": rescheduled_sum,
                                               "workers": per_worker,
                                               "functions": per_function},
                                "down_counter": down_counter}

        logger.info(metrics["scheduler"])

        # save scheduler history to file
        # as numpy array
        # np.save(log_path + "/functions", history["functions"])
        # np.save(log_path + "/workers", history["workers"])
        # as json?????????
        with open(log_path + "/functions.txt", "w") as f:
            json.dump(history["functions"], f, indent=2)
        with open(log_path + "/workers.txt", "w") as w:
            json.dump(history["workers"], w, indent=2)
        # to read
        # functions = json.load(open(log_path + "/functions.txt", "r"))
        # workers = json.load(open(log_path + "/workers.txt", "r"))
    # else any role

    log_index = log_path + "/" + node_name + "-monitor.csv"
    labels = ['time1', 'time2', 'rt_acc', 'battery', 'cpu_util', 'memory', 'disk',
              'cpu_temp', 'cpu_freq_curr', 'cpu_freq_min', 'cpu_freq_max', 'cpu_ctx_swt', 'cpu_inter', 'cpu_soft_inter',
              'io_read_count', 'io_write_count', 'io_read_bytes', 'io_write_bytes',
              'bw_pack_sent', 'bw_pack_rec', 'bw_bytes_sent', 'bw_bytes_rec', 'bw_bytes_dropin', 'bw_bytes_dropout']
    if usb_meter_involved:
        labels.extend(['mwh_new', 'mwh', 'mah', 'watts', 'amps', 'volts', 'temp'])

    monitor_data = []
    monitor_data.append(labels)
    # mwh
    mwh_sum = 0
    mwh_first = power_usage[0][0]
    mwh_second = 0

    # bw
    bw_usage_sum = [0] * len(bw_usage[0])
    bw_usage_first = bw_usage[0]
    bw_usage_second = [0] * len(bw_usage[0])
    if len(cpuUtil) != len(power_usage):
        logger.error('len (cpuUtil)= ' + str(len(cpuUtil)) + ' len (power_usage)= ' + str(len(power_usage)))

    for i in range(len(cpuUtil)):
        curr_list = []
        curr_list.append(str(current_time[i]))
        curr_list.append(str(current_time_ts[i]))
        curr_list.append(str(response_time_accumulative[i]))
        # ???Throughput accumulative
        curr_list.append(str(battery_charge[i]))
        curr_list.append(str(cpuUtil[i]))
        curr_list.append(str(memory[i]))
        curr_list.append(str(disk_usage[i]))
        curr_list.append(str(cpu_temp[i]))
        curr_list.append(str(cpu_freq_curr[i]))
        curr_list.append(str(cpu_freq_min[i]))
        curr_list.append(str(cpu_freq_max[i]))
        curr_list.append(str(cpu_ctx_swt[i]))
        curr_list.append(str(cpu_inter[i]))
        curr_list.append(str(cpu_soft_inter[i]))
        curr_list.append(str(disk_io_usage[i][0]))
        curr_list.append(str(disk_io_usage[i][1]))
        curr_list.append(str(disk_io_usage[i][2]))
        curr_list.append(str(disk_io_usage[i][3]))
        # bw usage new
        if i > 0:
            bw_usage_second = bw_usage[i]
            usage = [bw_usage_second[index] - bw_usage_first[index] for index in range(len(bw_usage[0]))]

            bw_usage_sum = [bw_usage_sum[index] + usage[index] for index in range(len(bw_usage[0]))]
            # exchange
            bw_usage_first = bw_usage_second

        curr_list.append(str(bw_usage_sum[0]))
        curr_list.append(str(bw_usage_sum[1]))
        curr_list.append(str(bw_usage_sum[2]))
        curr_list.append(str(bw_usage_sum[3]))
        curr_list.append(str(bw_usage_sum[4]))
        curr_list.append(str(bw_usage_sum[5]))

        if usb_meter_involved:
            # sometimes len power_usage is 1 index shorter than others ???
            if i < len(power_usage):
                # power usage new
                if i > 0:
                    # mwh
                    mwh_second = power_usage[i][0]
                    usage = mwh_second - mwh_first
                    if usage < 0:  # loop point
                        usage = (99999 - mwh_first) + (mwh_second - 97222)

                    mwh_sum += usage
                    # exchange
                    mwh_first = mwh_second

                curr_list.append(str(mwh_sum))

                curr_list.append(str(power_usage[i][0]))
                curr_list.append(str(power_usage[i][1]))
                curr_list.append(str(power_usage[i][2]))
                curr_list.append(str(power_usage[i][3]))
                curr_list.append(str(power_usage[i][4]))
                curr_list.append(str(power_usage[i][5]))
            else:
                logger.warning('save_reports: power_usage shorter than cpu_usage')
                curr_list.append(str(mwh_sum))

                curr_list.append(str(power_usage[i - 1][0]))
                curr_list.append(str(power_usage[i - 1][1]))
                curr_list.append(str(power_usage[i - 1][2]))
                curr_list.append(str(power_usage[i - 1][3]))
                curr_list.append(str(power_usage[i - 1][4]))
                curr_list.append(str(power_usage[i - 1][5]))

        monitor_data.append(curr_list)
    # save monitor.csv
    np.savetxt(log_index, monitor_data, delimiter=",", fmt="%s")

    logger.critical('Save_Reports: ' + log_index)
    if len(response_time) == 0: response_time.append(1)
    logger.critical('METRICS********************')
    logger.critical('######Exec. time (only success) avg='
                    + str(round(sum(response_time) / len(response_time), 2)))
    logger.critical('######Exec. time (only success) accumulative= '
                    + str(sum(response_time_accumulative) / len(response_time_accumulative)))
    cpuUtil_avg = round(statistics.mean(cpuUtil), 2)
    cpuUtil_max = round(max(cpuUtil), 2)
    logger.critical('######cpu= '
                    + str(round(sum(cpuUtil) / len(cpuUtil), 2)) + ' max=' + str(max(cpuUtil)))
    cpuFreq_avg = round(statistics.mean(cpu_freq_curr), 2)

    cpuFreq_min = min(cpu_freq_curr)
    cpuFreq_max = max(cpu_freq_curr)
    logger.critical('######cpuFreq= '
                    + str(cpuFreq_avg)
                    + '  min=' + str(cpuFreq_min)
                    + '  max=' + str(cpuFreq_max))
    min_battery_charge_percent = (battery_cfg[8] / battery_cfg[1]) * 100
    cpuUtil_up = [cpuUtil[i] for i in range(len(cpuUtil)) if battery_charge[i] >= min_battery_charge_percent]
    cpuUtil_up_avg = round(statistics.mean(cpuUtil_up), 2) if len(cpuUtil_up) else 0
    cpuUtil_up_max = round(max(cpuUtil_up), 2) if len(cpuUtil_up) else 0
    logger.critical('######cpu (up)= '
                    + str(round(sum(cpuUtil_up) / len(cpuUtil_up), 2) if cpuUtil_up != [] else 0)
                    + ' max=' + str(max(cpuUtil_up) if cpuUtil_up != [] else 0))

    memory_avg = round(statistics.mean(memory), 2) if len(memory) else 0
    memory_max = round(max(memory), 2) if len(memory) else 0
    logger.critical('######memory=' + str(round(sum(memory) / len(memory), 2))
                    + ' max=' + str(max(memory)))

    logger.critical('######disk_io_usage_Kbyte_read= '
                    + str(round((disk_io_usage[-1][2] - disk_io_usage[0][2]) / 1024, 2)))
    logger.critical('######disk_io_usage_Kbyte_write= '
                    + str(round((disk_io_usage[-1][3] - disk_io_usage[0][3]) / 1024, 2)))
    # logger.critical('######bw_packet_sent=' + str(round(bw_usage[-1][0] - bw_usage[0][0],2)))
    # logger.critical('######bw_packet_recv=' + str(round(bw_usage[-1][1]- bw_usage[0][1],2)))
    logger.critical('######bw_Kbytes_sent= '
                    + str(round((bw_usage[-1][2] - bw_usage[0][2]) / 1024, 2)))
    logger.critical('######bw_Kbytes_recv= '
                    + str(round((bw_usage[-1][3] - bw_usage[0][3]) / 1024, 2)))
    # power usage
    power_usage_incremental = mwh_sum
    # remover?
    mwh_sum = 0
    mwh_first = power_usage[0][0]
    mwh_second = 0
    usage = 0
    for row in power_usage[1:]:
        mwh_second = row[0]
        usage = mwh_second - mwh_first
        if usage < 0:  # loop point
            usage = (99999 - mwh_first) + (mwh_second - 97222)

        mwh_sum += usage
        # exchange
        mwh_first = mwh_second

    logger.critical('######power_usage= '
                    + str(mwh_sum) + ' mWh --- inc. (' + str(power_usage_incremental) + ')')

    # down_time
    down_time_minute = 0
    down_time_percent = 0
    if battery_cfg[0] == True:
        test_duration = test_finished - test_started
        logger.info('test_duration= ' + str(round(test_duration)) + ' sec ('
                    + str(round(test_duration / 60)) + ' min)')
        down_time_minute = round((down_time) / 60, 2)
        down_time_percent = round(down_time / test_duration * 100, 0)
        logger.critical('######down_time= ' + str(down_time_minute)
                        + ' min  (=' + str(down_time_percent) + ' %)')

    # metrics
    metrics["node"] = {"role": node_role, "name": node_name, "ip": node_IP,
                       "power_usage": power_usage_incremental,
                       "down_time": {"minute": down_time_minute, "percent": down_time_percent},
                       "cpu_usage": {"avg": cpuUtil_avg, "max": cpuUtil_max},
                       "cpu_usage_up": {"avg": cpuUtil_up_avg, "max": cpuUtil_up_max},
                       "cpuFreq": {"avg": cpuFreq_avg, "min": cpuFreq_min, "max": cpuFreq_max},
                       "memory_usage": {"avg": memory_avg, "max": memory_max},
                       "bw_usage": {"sent_mb": round(bw_usage_sum[2] / 1024 / 1024),
                                    "recv_mb": round(bw_usage_sum[3] / 1024 / 1024)}}

    # writing metrics to excel
    if node_role == 'LOAD_GENERATOR':
        # send to master
        metrics_sender(metrics)
    elif node_role == 'MASTER':
        # write locally using metrics_writer()
        cmd = 'metrics'
        sender = 'internal'
        main_handler(cmd, sender)
    else:
        logger.warning('skip metrics_sender()')

    # save metrics
    with open(log_path + "/metrics.txt", "w") as m:
        json.dump(metrics, m, indent=8)

    if snapshot_report[0] == 'True':
        begin = int(snapshot_report[1])
        end = int(snapshot_report[2])
        logger.critical('Snapshot: ' + str(begin) + ' to ' + str(end))

        logger.critical('######Exec. time avg=' + str(round(sum(response_time) / len(response_time), 2)))
        logger.critical('######Exec. time accumulative=' + str(
            round(sum(response_time_accumulative) / len(response_time_accumulative)), 2))
        logger.critical('######cpu=' + str(round(sum(cpuUtil[begin:end]) / len(cpuUtil[begin:end]), 2)))
        logger.critical('######memory=' + str(round(sum(memory[begin:end]) / len(memory[begin:end]), 2)))
        logger.critical('######bw_packet_sent=' + str(round(bw_usage[end][0] - bw_usage[begin][0])))
        logger.critical('######bw_packet_recv=' + str(round(bw_usage[end][1] - bw_usage[begin][1])))
        logger.critical('######bw_Kbytes_sent=' + str(round((bw_usage[end][2] - bw_usage[begin][2]) / 1024)))
        logger.critical('######bw_Kbytes_recv=' + str(round((bw_usage[end][3] - bw_usage[begin][3]) / 1024)))
        if usb_meter_involved:
            logger.critical('######power_usage=' + str(power_usage[end][0] - power_usage[begin][0]))


def metrics_sender(metrics):
    global logger
    global gateway_IP
    global node_name
    logger.info('metrics_sender: start')
    while True:
        try:
            # to avoid multiple write operations on a single file
            # time.sleep(random.randint(1,3))
            # specific to node name w1 w2 .... ????
            time.sleep(int(node_name.split('w')[1]) * 3)
            sender = node_name
            response = requests.post('http://' + gateway_IP + ':5000/main_handler/metrics/' + sender, json=metrics)
        except Exception as e:
            logger.error('metrics_sender: exception:' + str(e))
        # if no exception
        else:
            if response.text == "success":
                logger.info('metrics_sender: success')
                break
            else:
                logger.error('metrics_sender: failed')
                time.sleep(random.randint(1, 3))
                logger.info('metrics_sender: retry')


@app.route('/main_handler/<cmd>/<sender>', methods=['POST', 'GET'])
def main_handler(cmd, sender, plan={}):
    global epoch
    global test_name
    global under_test
    global monitor_interval
    global logger
    global node_role
    global test_started
    global test_finished
    global battery_cfg
    global apps
    global time_based_termination
    global sensor_log
    global max_request_timeout
    global monitor_interval
    global battery_charge
    global lock
    logger.info('main_handler: cmd = ' + cmd + ', sender = ' + sender)

    if cmd == 'plan':
        # ACTIONS BASED ON SENDER role or location
        # wait
        if under_test == True:
            under_test = False
            cooldown()

        # reset times, battery_cfg(current SoC), apps (created/recv), monitor, free up resources,
        reset()

        if node_role == "MASTER":
            openfaas_clean_up()

        # plan
        # set plan for LOAD_GENERATOR, MONITOR, STANDALONE by master node
        if sender == 'MASTER':
            plan = request.json

            # verify plan
            if plan == None:
                logger.warning('main_handler:plan:master:no plan received, so default values are used')
            else:
                verified = apply_plan(plan)
                if verified == False:
                    return "failed to set plan"
        # set plan for coordinator (master or standalone) by itself
        elif sender == "INTERNAL":
            if len(plan) > 0:
                verified = apply_plan(plan)
                if verified == False:
                    return "failed to set plan"
            else:
                logger.error('main_handler:plan:INTERNAL: no plan received for coordinator')
                return "main_handler: plan: no plan received for master"
        # set plan for MONITOR only in standalone tests by STANDALONE node
        elif sender == "STANDALONE":
            plan = request.json
            if plan == None:
                logger.warning('main_handler:plan:standalone: no plan received, so default values are used')
            else:
                apply_plan(plan)

            if node_role != "MONITOR":
                logger.error('main_handler:plan:standalone: no monitor role for monitor')
                return "main_handler:plan:standalone: no monitor role for monitor"
        else:
            logger.error("main_handler:plan:unknown sender")
            return "main_handler:plan:unknown sender"

            # show_plan()

        # verify usb meter connection
        if usb_meter_involved == True:
            if usb_meter_connection() == False:
                logger.error('main_handler:plan:usb_meter_connection:failed')
                return "main_handler:plan:usb_meter_connection:failed"

        return "success"

    # cmd=on
    elif cmd == 'on':
        # ACTIONS BASED ON assigned node_role
        # wait
        if under_test == True:
            under_test = False
            cooldown()

        # get plan
        show_plan()

        # under test
        under_test = True

        # set start time
        test_started = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

        # run monitor
        thread_monitor = threading.Thread(target=monitor, args=())
        thread_monitor.name = "monitor"
        thread_monitor.start()

        # run battery_sim
        if battery_cfg[0] == True:
            if usb_meter_involved == False:
                logger.error('main_handler:on: USB Meter is needed for Battery Sim')
                return "main_handler:on: USB Meter is needed for Battery Sim"

            thread_battery_sim = threading.Thread(target=battery_sim, args=())
            thread_battery_sim.name = "battery_sim"
            thread_battery_sim.start()

        # run timer
        if time_based_termination[0] == True:
            thread_timer = threading.Thread(target=timer, args=())
            thread_timer.name = "timer"
            thread_timer.start()

        # run failuer handler
        if node_role == 'LOAD_GENERATOR' or node_role == 'STANDALONE':
            thread_failure_handler = threading.Thread(target=failure_handler, args=())
            thread_failure_handler.name = "failure_handler"
            thread_failure_handler.start()

        # run workload
        if node_role == "LOAD_GENERATOR" or node_role == 'STANDALONE':
            # per apps
            for my_app in apps:
                if my_app[1] == True:
                    thread_app = threading.Thread(target=workload, args=(my_app,))
                    thread_app.name = "workload-" + my_app[0]
                    thread_app.start()

        # run scheduler and autoscaler
        if node_role == "MASTER":
            #scheduler
            thread_scheduler = threading.Thread(target=scheduler, args=())
            thread_scheduler.name = "scheduler"
            thread_scheduler.start()
            #autoscaler
            thread_autoscaler = threading.Thread(target=autoscaler, args=())
            thread_autoscaler.name = "autoscaler"
            thread_autoscaler.start()
        
        return 'success'

    # called if an app workload finishes
    elif cmd == 'app_done':
        if all_apps_done() == True:
            # avoid double stop at the same time
            if under_test == False:
                logger.info('main_handler:app_done: all apps done already or timer trigerred')
                return 'success'

            logger.info('main_handler:app_done: all apps done')

            if time_based_termination[0] == True:
                pass  # refer to timer
            # not time based
            else:
                if node_role == "STANDALONE":
                    peers_stop()
                # stop monitor and battery_sim
                under_test = False

                time.sleep(monitor_interval)
                logger.info('main_handler:app_done: call save reports')
                save_reports()
        else:
            logger.info('main_handler:app_done: a workload done, but not all apps yet')

    # metrics write
    elif cmd == 'metrics':
        with lock:
            if 'internal' in sender:
                data = metrics
            else:
                data = request.json

            # write

            logger.info('call excel_writer.write')
            logger.info('data')
            logger.info(data)
            logger.info('excel_file_path')
            logger.info(setup.excel_file_path)
            result, row = excel_writer.write(data, setup.excel_file_path)
            logger.info('call excel_writer.write done in row #' + str(row))

            # write avg of results if this is the last worker sending metrics
            #Assumption, nodes involved in experiments have mode on 'PEER' and name in the format of 'w#' where # is a number. Otherwise, writing to excel fails.
            #which node is the latest one?
            get_latest_node_to_wrapup = ""
            rows_count = 0
            for node in setup.nodes:
                #if node is PEER, which means involved in the test
                if node[0] == "PEER":
                    rows_count +=1
                    #if first identified one
                    if get_latest_node_to_wrapup == "":
                        #pick it
                        get_latest_node_to_wrapup = node[1]
                    #if its number part is larger thanthe picked one
                    elif int(node[1].split('w')[1]) > int(get_latest_node_to_wrapup.split('w')[1]):
                        #pick it
                        get_latest_node_to_wrapup = node[1]

            #if current metrics belong to the latest (by node number) expected node, wrap it up
            if data["node"]["name"] == get_latest_node_to_wrapup:
                logger.info('call excel_writer.avg')
                row = excel_writer.write_avg(rows_count, setup.excel_file_path)
                logger.info('call excel_writer.avg done in row #' + str(row))
            logger.info('write is done')
            return result

    elif cmd == 'stop':
        # stop monitor and battery_sim
        logger.info('main_handler:stop: under_test=False')
        under_test = False
        # stop workload in background, workload waits for req timeout
        cooldown()

        if node_role == "STANDALONE":
            peers_stop()

        if node_role == "MONITOR":
            test_finished = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

        logger.info('main_handler:stop: call save_reports')
        save_reports()
        logger.info('Test ' + test_name + ' is done!')

        # thread to start a new test
        if node_role == "MASTER":
            # epoch
            epoch += 1

            if epoch < len(setup.test_name):
                logger.info('Try another test ...')
                # clean up
                openfaas_clean_up()

                # cooldown
                cooldown(setup.intra_test_cooldown)

                node = [node for node in setup.nodes if
                        node[0] == "COORDINATOR" and node[1] == socket.gethostname() and node[2] == node_IP][0]
                logger.info('node: ' + str(node))

                thread_launcher = threading.Thread(target=launcher, args=(node,))
                thread_launcher.name = "launcher"
                thread_launcher.start()

    # 'charge'
    elif cmd == "charge":
        logger.info("main_handler:charge: req. from " + str(sender) + ": start")
        logger.info("main_handler:charge: return to "
                    + str(sender) + ": " + str(round(battery_cfg[3], 2)) + " mwh")
        return str(battery_cfg[3])
        logger.info("main_handler:charge: sender:" + str(sender) + ": stop")
    else:
        logger.error('main_handler: unknown cmd')
        return 'failed'

    logger.info('main_handler: stop')


# clean up is used at the start and end of experiments
def openfaas_clean_up():
    # clean up
    global logger
    logger.info('clean_up: start')
    try:
        
        #delete hpa objects
        cmd = "kubectl delete hpa --all -n openfaas-fn"
        logger.info('clean up hpa objects: ' + cmd)
        out, error = utils.shell(cmd)
        print(out + error)
        
        #delete profile objects. profiles are created in openfaas namespace, not openfaas-fn
        cmd = "kubectl delete profile --all -n openfaas"
        logger.info('clean up profile objects: ' + cmd)
        out, error = utils.shell(cmd)
        print(out + error)
        
        #delete functions or set their replicas to 1????? to avoid leftover functions with extra replicas for the next test
        
        #delete helm chart
        cmd = "helm delete " + setup.function_chart[0]
        logger.info('clean up function chart: ' + cmd)
        out, error = utils.shell(cmd)
        print(out + error)

        #restart nats
        cmd = "kubectl rollout restart -n openfaas deployment/nats"
        logger.info('clean up nats chart: ' + cmd)
        out, error = utils.shell(cmd)
        print(out + error)

        #restart queue-worker ????? should get name of queues from a reliable variable
        if setup.multiple_queue:
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-ssd"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-yolo3"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-irrigation"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-crop-monitor"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker-short"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
        else:
            cmd = "kubectl rollout restart -n openfaas deployment/queue-worker"
            logger.info('clean up queue-worker: ' + cmd)
            out, error = utils.shell(cmd)
            if error:
                logger.error(out + error)
            else:
                logger.info(out + error)
    except Exception as e:
        logger.error('clean_up:\n' + str(e))

    logger.info('clean_up: done')


# cooldown
def cooldown(intra_test_cooldown=0):
    global node_role
    global battery_cfg
    global monitor_interval
    global max_request_timeout
    global failure_handler_interval
    global apps
    global cpuFreq
    global logger
    logger.info('cooldown:start')
    wait = 0

    if node_role == "MONITOR" or node_role == "MASTER":
        if battery_cfg[0] == True:
            wait = sum([monitor_interval, battery_cfg[7]])
        else:
            wait = monitor_interval

    else:  # node_role == "STANDALONE or LOAD_GENERATOR"
        if battery_cfg[0] == True:
            wait = sum([monitor_interval, battery_cfg[7], failure_handler_interval,
                        max_request_timeout])  # sum get no more than 2 args
        else:
            wait = sum([monitor_interval, failure_handler_interval, max_request_timeout])
        # while any([True if app[1]==True and app[6]!=app[7] else False for app in apps ])==True:
        #    wait=3
        #    logger.info('cooldown: wait for ' + str(wait) + ' sec')
        #    time.sleep(wait)

        # reset cpu frequency settings
        stdout = sp.getoutput("sudo chown -R $USER /sys/devices/system/cpu/*")
        logger.info('output of sudo chown -R $USER /sys/devices/system/cpu/*: \n' + str(stdout))
        try:
            cpuFreq.reset()
        except:
            logger.error('cpuFreq.reset() ')

    if wait < intra_test_cooldown:
        wait = intra_test_cooldown

    logger.info('cooldown: wait for ' + str(wait) + ' sec...')
    time.sleep(wait)

    logger.info('cooldown: stop')


def show_plan():
    #
    global epoch
    global test_name
    global node_name
    global debug
    global gateway_IP
    global bluetooth_addr
    global apps
    global battery_cfg
    global time_based_termination
    global max_request_timeout
    global min_request_generation_interval
    global sensor_admission_timeout
    global node_role
    global peers
    global monitor_interval
    global failure_handler_interval
    global usb_meter_involved
    global battery_operated
    global node_IP
    global socket
    global max_cpu_capacity
    global raspbian_upgrade_error
    global boot_up_delay
    global log_path
    # counters/variables
    global under_test
    global test_started
    global test_finished
    global sensor_log
    global workers
    global functions
    global history
    global suspended_replies
    global down_time

    logger.info('show_plan: start')
    show_plan = ("test_name: " + test_name
                 + " node_name: " + str(socket.gethostname()) + " / " + str(node_name)
                 + "\n IP: " + node_IP
                 + "\n node_role: " + node_role
                 + "\n gateway_IP: " + gateway_IP
                 + "\n Debug: " + str(debug)
                 + "\n bluetooth_addr: " + bluetooth_addr
                 + "\n apps: " + '\n'.join([str(app) for app in apps])
                 + "\n peers: " + str(peers)
                 + "\n usb_meter_involved: " + str(usb_meter_involved)
                 + "\n battery_operated: " + str(battery_operated)
                 + "\n battery_cfg: " + str(battery_cfg)
                 + "\n time_based_termination: " + str(time_based_termination)
                 + "\n monitor_interval: " + str(monitor_interval)
                 + "\n failure_handler_interval: " + str(failure_handler_interval)
                 + "\n scheduling_interval: " + str(
                [setup.scheduling_interval[epoch] if node_role == 'MASTER' or node_role == 'STANDALONE' else 'null'][0])
                 + "\n max_request_timeout: " + str(max_request_timeout)
                 + "\n min_request_generation_interval: " + str(min_request_generation_interval)
                 + "\n sensor_admission_timeout: " + str(sensor_admission_timeout)
                 + "\n max_cpu_capacity: " + str(max_cpu_capacity)
                 + "\n boot_up_delay: " + str(boot_up_delay)
                 + "\n log_path: " + str(log_path)
                 + "\n under_test: " + str(str(under_test))
                 + "\n test_started: " + str(str(test_started))
                 + "\n test_finished: " + str(str(test_finished))
                 + "\n sensor_log: " + str(str(sensor_log))
                 + "\n functions: " + str(str(functions))
                 + "\n workers: " + str(str(workers))
                 + "\n history: " + str(str(history))
                 + "\n suspended_replies: " + str(str(suspended_replies))
                 + "\n down_time: " + str(str(down_time))
                 + "\n raspbian_upgrade_error: " + str(raspbian_upgrade_error))
    logger.info("show_plan: " + show_plan)

    logger.info('show_plan: stop')


def apply_plan(plan):
    global test_name
    global debug
    global gateway_IP
    global bluetooth_addr
    global apps
    global battery_cfg
    global time_based_termination
    global max_request_timeout
    global min_request_generation_interval
    global session_enabled
    global sensor_admission_timeout
    global node_role
    global peers
    global waitress_threads
    global monitor_interval
    global failure_handler_interval
    global usb_meter_involved
    global battery_operated
    global max_cpu_capacity
    global log_path
    global pics_folder
    global file_storage_folder
    global boot_up_delay
    global raspbian_upgrade_error
    logger.info('apply_plan: start')
    # create test_name
    test_name = socket.gethostname() + "_" + plan["test_name"]

    node_role = plan["node_role"]
    gateway_IP = plan["gateway_IP"]
    debug = plan["debug"]
    bluetooth_addr = plan["bluetooth_addr"]
    apps = plan["apps"]
    peers = plan["peers"]
    usb_meter_involved = plan["usb_meter_involved"]
    # Either battery_operated or battery_cfg should be True, if the second, usb meter needs enabling
    battery_operated = plan["battery_operated"]
    # Battery simulation
    battery_cfg = plan["battery_cfg"]  # 1:max,2:initial (and current) SoC, 3:renewable seed&lambda, 4:interval
    # NOTE: apps and battery_cfg values change during execution
    time_based_termination = plan["time_based_termination"]  # end time-must be longer than actual test duration
    monitor_interval = plan["monitor_interval"]
    failure_handler_interval = plan["failure_handler_interval"]
    max_request_timeout = plan["max_request_timeout"]
    min_request_generation_interval = plan["min_request_generation_interval"]
    session_enabled = plan["session_enabled"]
    sensor_admission_timeout = plan["sensor_admission_timeout"]
    max_cpu_capacity = plan["max_cpu_capacity"]

    # get home directory
    home = expanduser("~")

    log_path = plan["log_path"]
    log_path = home + log_path + test_name
    # empty test_name folder (if not exist, ignore_errors)
    shutil.rmtree(log_path, ignore_errors=True)
    # create test_name folder
    if not os.path.exists(log_path): os.makedirs(log_path)

    # update logger fileHandler
    # default mode is append 'a' to existing log file. But, 'w' is write from scratch
    # change fileHandler file on the fly
    # another option: [%(funcName)s] ???
    formatter = logging.Formatter('%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s')
    fileHandler = logging.FileHandler(log_path + '/' + os.path.basename(__file__).split('.')[0] + '.log', mode='w')
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.DEBUG)
    log = logging.getLogger()  # root logger
    for hndlr in log.handlers[:]:  # remove the existing file handlers
        log.removeHandler(hndlr)
    log.addHandler(fileHandler)  # set the new handler

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(logging.DEBUG)

    logger.addHandler(consoleHandler)

    if debug: log.setLevel(logging.DEBUG)

    pics_folder = home + plan["pics_folder"]
    if not os.path.exists(pics_folder):
        logger.error('apply_plan: no pics_folder directory found at ' + pics_folder)
        return False
    file_storage_folder = home + plan["file_storage_folder"]
    if not os.path.exists(file_storage_folder): os.makedirs(file_storage_folder)

    waitress_threads = plan["waitress_threads"]
    boot_up_delay = plan["boot_up_delay"]
    raspbian_upgrade_error = plan["raspbian_upgrade_error"]

    # set cpu frequency config, if the node_role is requested to affect
    if node_role in plan["cpu_freq_config"]["effect"]:
        apply_cpu_freq_config(plan["cpu_freq_config"])

    logger.info('apply_plan: stop')
    return True


# cpu frequency config
def apply_cpu_freq_config(config):
    global cpuFreq
    global logger
    stdout = sp.getoutput("sudo chown -R $USER /sys/devices/system/cpu/*")
    logger.info('output of sudo chown -R $USER /sys/devices/system/cpu/*: \n' + str(stdout))

    #run Jetson Nano on MAX power (10W)
    if utils.what_device_is_it('nvidia jetson nano'):
        #-m 0 = MAXN mode and it needs proper powering while -m 1 = 5V mode where 2 CPU cores will be off
        cmd = 'sudo /usr/sbin/nvpmodel -m 0'
        output, error = utils.shell(cmd)
        if error:
            logger.error('NANO power mode:' + error)
        else:
            logger.info(output + '\nNano power mode is now MAXN')
    
    #apply CPU config
    try:
        cpuFreq.reset()
        #CPU informations are in files located in 'cd /sys/devices/system/cpu/cpu0/cpufreq'
        #You may manually Collect informations by 'paste <(ls *) <(cat *) | column -s $'\t' -t'
        available_govs = cpuFreq.available_governors
        logger.info('available governors: ' + str(available_govs))
        govs = cpuFreq.get_governors()
        logger.info('default governors per core: ' + str(govs))
        #set governors
        cpuFreq.set_governors(config['governors'])
        govs = cpuFreq.get_governors()
        logger.info('used governors per core: ' + str(govs))
        mismatch_governor = True if True in [True if config['governors'] != governor else False for core, governor in govs.items()] else False
        if mismatch_governor:
            logger.error('suggested governors (' + config['governors'] + ') != running governors (' + str(govs) + ')')

        available_freqs = cpuFreq.available_frequencies
        logger.info('available frequencies: ' + str(available_freqs))

        # set min and max frequencies. If min value is less than actual min, the actual min is set, and vise versa.
        #if set as 0, default min max are used.
        if config['set_min_frequencies'] != 0:
            cpuFreq.set_min_frequencies(config['set_min_frequencies'])
        if config['set_max_frequencies'] != 0:
            cpuFreq.set_max_frequencies(config['set_max_frequencies'])

        # only if governor is 'userspace' we can set fixed frequencies. It affects scaling_setspeed file
        if config['governors'] == 'userspace':
            cpuFreq.set_frequencies(config['set_frequencies'])
#disable Jetson Nano 
    sudo jetson_clocks --store
    sudo jetson_clocks --restore
        # output
        govs = cpuFreq.get_governors()
        freq = re.split(', |=', str(psutil.cpu_freq()).split(')')[0])
        freq_curr = freq[1]
        freq_min = freq[3]
        freq_max = freq[5]
        logger.info('cpu config: ' + 'governors: ' + str(govs)
                    + 'curr= ' + str(freq_curr)
                    + '  min= ' + str(freq_min)
                    + '  max= ' + str(freq_max))
        if freq_min == freq_curr and freq_curr == freq_max:
            logger.error('freq_min, freq_curr and freq_max are all equal!\n'
                        + 'If this is not planned and the device is Jetson Nano, perhaps the jetson_clocks is running\n'
                        + 'You may disable that by sudo jetson_clocks --restore or restart the device')
            # if utils.what_device_is_it('nvidia jetson nano'):
            #     cmd = 'sudo jetson_clocks --restore'
            #     output, error = utils.shell(cmd)
            #     if error:
            #         logger.error('Failed to restor jetson_clock\n' + error)
            #     else:
            #         #verify if CPU frequencies:min, max and curr are correct now.

    except Exception as e:
        logger.error(str(e))

# timer
def timer():
    global monitor_interval
    global max_request_timeout
    global failure_handler_interval
    global time_based_termination
    global test_started
    global under_test
    logger.info('start')

    while under_test:
        now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        elapsed = now - test_started
        if elapsed >= time_based_termination[1]:
            break
        else:
            time.sleep(min(failure_handler_interval, monitor_interval, max_request_timeout))

    if under_test == True:
        # alarm main_handler
        thread_terminator = threading.Thread(target=main_handler, args=('stop', 'INTERNAL',))
        thread_terminator.name = "terminator"
        thread_terminator.start()
    logger.info('stop')


# terminate who is "me" or "others" or "all"
@app.route('/terminate/<who>', methods=['GET', 'POST'])
def terminate(who):
    if who == "me":
        main_handler('stop', 'INTERNAL')
    elif who == "others":
        for node in setup.nodes:
            if node[0] == "PEER":
                ip = node[2]
                try:
                    response = requests.post('http://' + ip + ':5000/main_handler/stop')
                except:
                    logger.error('terminator: failed for ' + ip)
    elif who == "all":
        main_handler('stop', 'INTERNAL')

        for node in setup.nodes:
            if node[0] == "PEER":
                ip = node[2]
                try:
                    response = requests.post('http://' + ip + ':5000/main_handler/stop')
                except:
                    logger.error('terminator: failed for ' + ip)
    else:
        logger.info('terminator: who is unknown')
        return 'failed'

    return "stopped"


def peers_stop():
    global logger
    global peers

    logger.info('peers_stop: all_apps_done or time ended')
    # remote monitors stop
    reply = []
    try:
        for i in range(len(peers)):
            response = requests.get('http://10.0.0.' + peers[i] + ':5000/main_handler/stop/STANDALONE')
            reply.append(response.text)
    except Exception as e:
        logger.error('peers_stop:error:' + peers[i] + ':' + str(s))

    if len([r for r in reply if "success" in r]) == len(peers):
        if len(peers) == 0:
            logger.info('peers_stop: No Peers')
        else:
            logger.info('peers_stop: Remote Peer Monitor Inactive')

    else:
        logger.error('peers_stop: Failed - remote peers monitors')


def battery_sim():
    global logger
    global under_test
    global battery_cfg
    global down_time
    logger.info('Start')
    max_battery_charge = battery_cfg[1]  # theta: maximum battery capacity in mWh

    renewable_type = battery_cfg[4]

    renewable_inputs = []
    start_time = 0

    # get poisson
    if renewable_type == "poisson":

        # Generate renewable energy traces
        np.random.seed(battery_cfg[5][0])
        renewable_inputs = np.random.poisson(lam=battery_cfg[5][1], size=10000)
        # get real dataset
    elif renewable_type == "real":

        renewable_inputs = battery_cfg[6]

        start_time = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()

    else:
        logger.error('renewable_type not found:' + str(renewable_type))

    previous_usb_meter = read_power_meter()[0]

    renewable_index = 0
    renewable_input = 0
    interval = battery_cfg[7]

    while under_test:
        # GET
        soc = battery_cfg[3]  # soc: previous observed SoC in Mwh
        last_soc = soc
        # renewable
        if renewable_type == "poisson":
            renewable_index += 1
            renewable_input = renewable_inputs[renewable_index]
        elif renewable_type == "real":
            # index and effect
            # index
            # hourly dataset, and scale 6 to 1, means each index is for 10 min
            now = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            dur = now - start_time
            renewable_index = math.floor(dur / 600)  # if 601 sec, index = 1, if 200sec, index=0
            # if dataset finishs, it starts from the begining
            renewable_index = int(math.fmod(renewable_index, len(renewable_inputs))) if len(renewable_inputs) else 0
            # effect
            raw_input = renewable_inputs[renewable_index] if len(renewable_inputs) else 0
            # calculate the share for this interval

            renewable_input = (raw_input / (600 / interval)) 
        else:
            logger.error('unknown renewable_type  --> ' + str(renewable_type))

        usb_meter = read_power_meter()[0]

        energy_usage = usb_meter - previous_usb_meter
        #a fix for mAh may be required also to avoid loops???
        # fix USB meter loop in 99999 to 97223. NOTE: INTERVALS SHOULD NOT BE TOO LONG: > 2500mWH
        if usb_meter - previous_usb_meter < 0:
            energy_usage = (99999 - previous_usb_meter) + (usb_meter - 97222)
        # UPDATE
        # min to avoid overcharge. max to avoid undercharge
        soc = min(max_battery_charge, max(0, soc + renewable_input - energy_usage))
        # check overcharging
        if (soc + renewable_input - energy_usage) > max_battery_charge:
            logger.warning("battery_sim: battery charge higher than max (" + str(max_battery_charge) + ") at " + str(
                soc) + ", but capped at max")

        battery_cfg[3] = soc

        # down_time
        # calculate down_time
        min_battery_charge = battery_cfg[8]
        if soc < min_battery_charge:
            down_time += interval
            if last_soc > min_battery_charge:
                logger.info('node went to dead mode!')

        # when it went to up
        if last_soc < min_battery_charge and soc > min_battery_charge:
            turned_up_at = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            battery_cfg[9] = turned_up_at
            logger.info('node is up back')

        previous_usb_meter = usb_meter

        time.sleep(interval)

    logger.info('Stop')


# ---------------------------------

@app.route('/reset', methods=['POST'])
def reset():
    logger.info('reset:start')
    global test_name
    global metrics
    global under_test
    global gateway_IP
    global test_started
    global test_finished
    global sensor_log
    global battery_cfg
    global workers
    global functions
    global history
    global apps
    global cpuFreq
    global failure_handler_interval
    global suspended_replies
    global down_time
    global boot_up_delay
    global log_path
    global min_request_generation_interval
    global max_request_timeout
    global sensor_admission_timeout
    # monitoring parameters
    global response_time
    # in monitor
    global response_time_accumulative

    global current_time
    global current_time_ts
    global battery_charge
    global cpuUtil
    global cpu_temp
    global cpu_freq_curr
    global cpu_freq_max
    global cpu_freq_min
    global cpu_ctx_swt
    global cpu_inter
    global cpu_soft_inter
    global memory
    global disk_usage
    global disk_io_usage
    global bw_usage

    global power_usage
    global throughput
    global throughput2

    # preparation
    logger.info('reset: Turn off USB and free up memory --HDMI is not disabled!')
    # Turn OFF HDMI output. ????tvservice is not enabled on devices always. An alternative solution is required.
    # cmd = "sudo /opt/vc/bin/tvservice -o"
    # out, error = utils.shell(cmd)
    # print(out + error)

    # USB chip control
    #Pi 3B+: https://learn.pi-supply.com/make/how-to-save-power-on-your-raspberry-pi/#disable-wi-fi-bluetooth
    if utils.what_device_is_it('raspberry pi 3'):
        #turn on USBs if an attached device like TPU is detected.
        if utils.attached_tpu_detected():
            #or sudo uhubctl -l 1-1 -p 2 -a on
            cmd = "echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/bind"    
        else:
            #tunr off USBs
            #or sudo uhubctl -l 1-1 -p 2 -a off
            cmd = "echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/unbind"
        out, error = utils.shell(cmd)
        print(out + error)
    #Pi 4B
    elif utils.what_device_is_it('raspberry pi 4'):
        #turn on USBs if an attached device like TPU is detected.
        if utils.attached_tpu_detected():
            #turn on
            cmd = "sudo uhubctl -l 1-1 -a on"
        else:
            #turn off
            cmd = "sudo uhubctl -l 1-1 -a on"
        out, error = utils.shell(cmd)
        print(out + error)
    #Jetson Nano
    elif utils.what_device_is_it('nvidia jetson nano'):
        #Jetson Nano: bus 2-1 is the usb3.0 bus corresponding to the 4 ports on the dev kit. https://github.com/mvp/uhubctl/issues/258#issue-669452920
        #turn on USBs if an attached device like TPU is detected.
        if utils.attached_tpu_detected():
            #turn on
            cmd = "echo '2-1' |sudo tee /sys/bus/usb/drivers/usb/bind"
        else:
            #turn off
            cmd = "echo '2-1' |sudo tee /sys/bus/usb/drivers/usb/unbind"
        out, error = utils.shell(cmd)
        print(out + error)
    else:
        logger.warning('Device is not pi 3, 4 or jetson nano, so no USB is turned off')
    
    
    # free up memory
    # cache (e.g., PageCache, dentries and inodes) and swap
    cmd = "sudo echo 3 > sudo /proc/sys/vm/drop_caches && sudo swapoff -a && sudo swapon -a && printf '\n%s\n' 'Ram-cache and Swap Cleared'"
    out, error = utils.shell(cmd)
    print(out + error)

    # reset cpu frequency settings
    stdout = sp.getoutput("sudo chown -R $USER /sys/devices/system/cpu/*")
    logger.info('output of sudo chown -R $USER /sys/devices/system/cpu/*: \n' + str(stdout))
    try:
        cpuFreq.reset()
    except:
        logger.error('cpuFreq.reset() ')
    # variables
    test_name = "no_name"
    metrics = {}
    under_test = False
    gateway_IP = ""
    test_started = None
    test_finished = None
    down_time = 0
    sensor_log = {}
    home = expanduser("~")
    log_path = home + "/" + test_name

    apps = []
    battery_cfg[3] = battery_cfg[2]  # current =initial

    # scheudler
    workers = []
    functions = []
    history = {'functions': {}, 'workers': {}}
    suspended_replies = []
    boot_up_delay = 0
    # monitoring parameters
    # in owl_actuator
    response_time = []
    min_request_generation_interval = 0
    max_request_timeout = 30
    sensor_admission_timeout = 3
    # in monitor
    response_time_accumulative = []
    current_time = []
    current_time_ts = []
    battery_charge = []
    cpuUtil = []
    cpu_temp = []
    cpu_freq_curr = []
    cpu_freq_max = []
    cpu_freq_min = []
    cpu_ctx_swt = []
    cpu_inter = []
    cpu_soft_inter = []
    memory = []
    disk_usage = []
    disk_io_usage = []
    bw_usage = []

    power_usage = []
    throughput = []
    throughput2 = []

    logger.info('reset:stop')





if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s')
    # default mode is append 'a' to existing log file. But, 'w' is write from scratch
    if not os.path.exists(log_path): os.makedirs(log_path)
    fileHandler = logging.FileHandler(log_path + '/' + os.path.basename(__file__).split('.')[0] + '.log', mode='w')
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(logging.DEBUG)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

    # setup file exists?
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(dir_path + "/setup.py"):

        # run launcher if coordinator
        for node in setup.nodes:
            # find this node in nodes
            position = node[0]
            name = node[1]
            if name == socket.gethostname():
                # verify if this node's position is COORDINATOR
                if position == "COORDINATOR":
                    # just MASTER and STANDALONE are eligible to be a COORDINATOR
                    if setup.plan[name]["node_role"] == "MASTER" or setup.plan[name]["node_role"] == "STANDALONE":
                        logger.info('MAIN: Node position is coordinator')
                        thread_launcher = threading.Thread(target=launcher, args=(node,))
                        thread_launcher.name = "launcher"
                        thread_launcher.start()
                        break
                    else:
                        logger.error('MAIN: Node role in its plan must be MASTER or STANDALONE')
                else:
                    logger.info('MAIN: Node position is ' + position)
    else:
        logger.info('MAIN: No setup found, so wait for a coordinator')

    try:
        # threads=number of requests can work concurrently in waitress; exceeded requests wait for a free thread
        serve(app, host='0.0.0.0', port='5000', threads=waitress_threads)
    except OSError as e:
        print(str(e) + '\nMake sure this port is not already given to someone else, e.g., docker ps -a.')

