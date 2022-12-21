import getpass
#first run main.py on PEERs

#epoch driver
#'throughput-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10'
#'ai-cnfidence-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10'
#'qos-rt-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10'
#'energy-total-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10'
#'even-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10'
#'energy-processing-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10'
#'local-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10',
#'cost-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10',
#'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10',
#'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10',
#'data-remote-local-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner4',
#'data-locality-qos-rt-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner4',

# test_name = ['cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner4',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner4','cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner4',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner5',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner5', 'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner5',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner5','cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner5',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner6',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner6', 'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner6',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner6','cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner6',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner7',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner7', 'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner7',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner7','cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner7',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner8',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner8', 'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner8',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner8','cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner8',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner9',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner9', 'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner9',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner9','cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner9',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner10',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner10', 'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner10',
#     'cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner10','cpu-freq-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10',]

test_name = ['ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner1',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner1', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner1',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner1','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner1',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner2',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner2', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner2',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner2','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner2',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner3',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner3', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner3',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner3','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner3',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner4',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner4', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner4',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner4','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner4',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner5',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner5', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner5',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner5','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner5',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner6',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner6', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner6',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner6','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner6',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner7',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner7', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner7',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner7','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner7',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner8',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner8', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner8',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner8','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner8',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner9',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner9', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner9',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner9','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner9',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round1-spawner10',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round2-spawner10', 'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round3-spawner10',
    'ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round4-spawner10','ai-precision-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round5-spawner10',]

test_name = ['even-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round6-spawner8',
'even-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round7-spawner8',
'even-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round8-spawner8',
'even-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round9-spawner8',
'even-10min-minio-gen-40mbits-pics-83num-resized-half-6mb-max130kb-round10-spawner8',]



variable_parameters=['workload_cfg']
test_duration= 10 * 60 #####
#[0] position (e.g.,COORDINATOR, PEER, or -) [1] node (host) name [2] node ip
#for scheduling, max 5 nodes are considered.
nodes=[["COORDINATOR","master","10.0.0.90"],
       ["www", "w1","10.0.0.91"],
       ["PEER", "w2","10.0.0.92"],
       ["PEER", "w3","10.0.0.93"],
       ["PEER", "w4","10.0.0.94"],
       ["PEER", "w5","10.0.0.95"],
       ["www", "w6","10.0.0.96"],
       ["PEER", "w7","10.0.0.97"],]

accelerators = {'w1': [], 'w2': [], 'w3': [], 'w4': ['tpu'], 'w5': ['gpu'], 'w6': [], 'w7': []}

#load balancing

#if linkerd
# backends = [{'service': node[1] + '-' + 'ssd', 'weight': 1000} for node in nodes if node[0] == 'PEER']
#if envoy
#even
backends = [{'service':'w2-ssd','weight': 200, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 200, 'ip': '', 'port': ''},
             {'service':'w4-ssd','weight': 200, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 200, 'ip': '', 'port': ''}, 
             {'service':'w7-ssd','weight': 200, 'ip': '', 'port': ''}]
# #static energy-totall
# backends = [{'service':'w2-ssd','weight': 192, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 186, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 130, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 219, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 273, 'ip': '', 'port': ''}]
#static cpu * frequency
# backends = [{'service':'w2-ssd','weight': 206, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 200, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 375, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 102, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 118, 'ip': '', 'port': ''}]
#static AI confidence
# backends = [{'service':'w2-ssd','weight': 193, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 193, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 188, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 233, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 193, 'ip': '', 'port': ''}]
#static QoS response time (exec time or tail latency?)
# backends = [{'service':'w2-ssd','weight': 170, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 213, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 378, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 128, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 111, 'ip': '', 'port': ''}]
#static throughput
# backends = [{'service':'w2-ssd','weight': 245, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 273, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 265, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 100, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 117, 'ip': '', 'port': ''}]
#static energy-processing
# backends = [{'service':'w2-ssd','weight': 200, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 124, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 499, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 93, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 85, 'ip': '', 'port': ''}]

#cost
# backends = [{'service':'w2-ssd','weight': 200, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 212, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 355, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 82, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 151, 'ip': '', 'port': ''}]

#ai-precision
# backends = [{'service':'w2-ssd','weight': 202, 'ip': '', 'port': ''}, {'service':'w3-ssd','weight': 202, 'ip': '', 'port': ''},
#              {'service':'w4-ssd','weight': 136, 'ip': '', 'port': ''},  {'service':'w5-ssd','weight': 258, 'ip': '', 'port': ''}, 
#              {'service':'w7-ssd','weight': 202, 'ip': '', 'port': ''}]

#For type, 'handler' = openfaas-gateway, linkerd or envoy.
#For type, if 'handler'=linkerd, service_mesh paramter must be True.
#For type['control-plane], vlue can be centralized, distributed or decentralized.
#For algorithm, if ['type']['handler'] == 'linkerd, then algorithm = even or static
#For algorithm, if ['type']['handler'] == 'envoy, algorithm = local or (even or static). If local, postfix = 'func_name' else postfix = ''
#For frontend if envoy, if 'static' , 'frontends': [{'type': 'static', 'listeners': {'name': 'envoy', 'ip': '10.43.10.10', 'address': '0.0.0.0', 'port': 9000, 'route_by': 'path', 'match': {'prefix': '/'}, 'path': '/', 'postfix': '', 'cluster': 'cluster1', 'redis_server_ip': '10.43.189.161'}}],
#For frontends, if openfaas-gateway, 'frontends': [{'type': 'static', 'listeners': {'name': 'openfaas-gateway', 'ip': '10.0.0.90', 'port': '31112', 'path': '/async-function/', 'postfix': 'func_name', 'redis_server_ip': '10.43.189.161'},},],
#For frontends, if name == openfaas-gateway, path can be '/function/' or  '/async-function/' for sync and async
#For frontends, if type 'dynamic', listeners['ip'] must be measured on runtime to be given to workload_generator
#For object_storage 1,  default --> {'read':{'decoupled': False, 'type':'anything', 'ip': 'anything', 'port': 5000}},
#For object_storage 2,  decoupled local-generator --> {'read':{'decoupled': True, 'type':'decentralized-tinyobj', 'ip': 'local-generator', 'port': 5500}},
#For object_storage 2,  decoupled local-executor --> {'read':{'decoupled': True, 'type':'decentralized-tinyobj', 'ip': 'local-executor', 'port': 5500}},
#For object_storage 3, decoupled centralized --> {'read':{'decoupled': True, 'type':'centralized-tinyobj', 'ip': '10.0.0.91', 'port': 5500}},
#For object_storage, minio centralized --> {'read': {'decoupled': True, 'type':'centralized-minio', 'ip': '10.0.0.96', 'port': 9000, 'resource': '/', 'bucket': 'mybucket', 's3_key': 'minioadmin', 's3_secret': 'minioadmin', 'content_type': 'application/octet-stream',}},
#For object_storage, minio decentralized -->  'object_storage': {'read': {'decoupled': True, 'type':'decentralized-minio', 'ip': 'local-generator', 'port': 9000, 'resource': '/', 'bucket': 'mybucket130k', 's3_key': 'minioadmin', 's3_secret': 'minioadmin', 'content_type': 'application/octet-stream',}},
#For object_storage, minio --> wget https://dl.minio.io/server/minio/release/linux-arm/minio
#wget https://dl.minio.io/client/mc/release/linux-arm/mc
#sudo ln -s /home/ubuntu/minio /usr/bin/minio
#sudo ln -s /home/ubuntu/mc /usr/bin/mc
#wget https://dl.min.io/server/minio/release/linux-arm64/minio & chmod +x minio & mkdir -p /data & minio server /home/ubuntu/data &
#open dashboard 10.0.0.91:9000, create bucket 'mybucket', set public access to bucket
#populate mybucket using minio-put.py
#For object_storage, if port different than main flask, a tineobj.py my be ran on hosts listening on the port.
#For add_headers, {'Use-Local-Image': '0-170'}, or {'Internal-Connection': 'close'}, or {'Internal-Session': 'anything'},
#Do not use object_storage read with add_headers['Use-Local-Image'] 
#For backend_discovery, value = static (use 'backends') or dynamic.
#For backend_discovery, if type['handler'] == linkerd, then 'type' = 'static' and deployments['backends']['TrafficSplit'] and ['Function'] name must be equal.
#For 'deploy', if ['type']['handler'] == envoy and ['type']['deployment'] == kubernetes, then 'deploy'= ['Deployment-envoy', 'Service-envoy',] and Requires envoy.yaml file address. 
#For 'deployments'['Deployment-envoy'] if 'nodeName' != master and ARM, envoy image will fail and isntead use image: thegrandpkizzle/envoy:1.24.0 but for AMD value of 'host_user_ip' is like 'ubuntu@10.0.0.91'
#For 'deploy', if ['type']['handler'] == linkerd  and ['type']['deployment'] == kubernetes, then 'deploy'= ['Function-function']. 

load_balancing ={
        'type': {'adaptive': False, 'control-plane': 'centralized', 'handler': 'envoy', 'deployment': 'kubernetes'}, 
        'interval': 800,
        'algorithm': 'static',
        'accelerators': accelerators,
        'admin':{'name': 'admin', 'ip': '10.0.0.90', 'port': 8000,},
        'frontends': [{'type': 'static', 'listeners': {'name': 'envoy', 'ip': '10.43.10.10', 'address': '0.0.0.0', 'port': 9000, 
                                                    'route_by': 'path', 'match': {'prefix': '/'}, 'path': '/', 'postfix': '', 'cluster': 'cluster1', 'redis_server_ip': '10.43.189.161'}}],
        'object_storage': {'read': {'decoupled': True, 'type':'decentralized-minio', 'ip': 'local-generator', 'port': 9000, 'resource': '/', 'bucket': 'mybucket130k', 's3_key': 'minioadmin', 's3_secret': 'minioadmin', 'content_type': 'application/octet-stream',}},
        'add_headers':{},
        'backend_discovery': {'type': 'static', 'backends': backends},
        'deploy': ['Deployment'],
        'deployments': {
            'Deployment-envoy': 
                {'api_version': 'apps/v1', 'kind': 'Deployment', 'object_name': 'envoy', 'namespace': 'openfaas-fn', 
                'image': 'envoyproxy/envoy:v1.24.0', 'nodeName': 'master', 'host_user_ip': 'ubuntu@10.0.0.91', 'annotations': {'version': '1'}, 'ports': [{'containerPort': 9000}], 
                'volumeMounts': [{'name': 'envoy-config', 'mountPath': '/etc/envoy/envoy.yaml'},],
                'volumes': [{'name': 'envoy-config', 'hostPath': {'path': '/home/ubuntu/envoy.yaml'}},], 'manifest': {}, 'envoy-config': {}},
            'Service-envoy':
                {'api_version': 'v1', 'kind': 'Service', 'object_name': 'envoy', 'namespace': 'openfaas-fn', 'clusterIP': '10.43.10.10',
                'ports': [{'protocol': 'TCP', 'port': 9000, 'targetPort': 9000}], 'manifest': {},},
            'Function-linkerd':
                {'api_version': 'openfaas.com/v1', 'kind': 'Function', 'object_name': 'gw-func', 'namespace': 'openfaas-fn', 'image': 'aslanpour/ssd:cpu-tpu-amd64',
                'labels': {'com.openfaas.scale.min': '1','com.openfaas.scale.max': '1'}, 'annotations': {'linkerd.io/inject': 'enabled'},
                'constraints': ['kubernetes.io/hostname=master'], 'manifest': {},},
            'TrafficSplit':
                {'api_version': 'split.smi-spec.io/v1alpha2', 'kind': 'TrafficSplit', 'object_name': 'my-traffic-split','namespace': 'openfaas-fn',
                'service': 'gw-func', 'operation': 'safe-patch','manifest': {}, 'backends': [],},
        }
    
    } #variable

#NOTE if True, queues must be already created! and follows the name pattern as queue-worker-functionName. Only works in async.
multiple_queue=False
#if true, Linkerd is required for OpenFaaS
service_mesh=True

redis_server_ip= "10.43.189.161" #assume default port is selected as 3679

#local #default-kubernetes #random #bin-packing #greedy #shortfaas
scheduler_name = ["local"] #variable
#zonal categorization by Soc %
#[0] zone [1] priority [2] max Soc threshold [3] min Soc threshold
zones = [["rich", 1, 100, 60],
        ["vulnerable", 3, 60, 30],
        ["poor", 2, 30, 10],
        ["dead", 4, 10, -1]] #-1 means 0
#if 1250=100%, then 937.5=75%, 312.5=25% and 125=10%

#plugins and weights for shortfaas scoring
plugins = [{'energy':100, 'locally':100, 'sticky':30}] #variable

#==0 only if scheduler_name=="greedy" and warm_scheduler=True
#and should be limited just in case function is not locally placed. (not implemented yet this part), so it is applied all the time if used
#this time takes for newly up node to be ready to send_sensors
boot_up_delay = 0   ####
#scheduler_greedy_config
sticky = True # it requires offloading=True to be effective
stickiness = [0.2] #variable #20% # it requires offloading=True to be effective #####
warm_scheduler = False # it requires offloading=True to be effective -- if true, workload will be generated and sent once the node is down.


#cpu frequency: governors: ondemand, powersave, performance, conservative
#set_frequencies for setting static frequencies is used only if governors is 'userspace'.
#key "governors" tells which governor must be used.
#sample min frequency: 600000
cpu_freq_config={"effect": ["LOAD_GENERATOR", "STANDALONE"],"governors": "ondemand",
    "set_min_frequencies": 0, "set_max_frequencies": 0, "set_frequencies": 600000}

cpu_governor = ['ondemand'] #variable
#??????????????????image name has gpu
apps = {"ssd": True, "yolo3": False, "irrigation":False, "crop-monitor": False, "short": False}
#w5-ssd is just for Nano to pull gpu-based image.??
apps_image = {"ssd": "aslanpour/ssd:cpu-tpu", "w5-ssd": "aslanpour/ssd:cpu-tpu-gpu", "yolo3": "aslanpour/yolo3-quick", "irrigation":"aslanpour/irrigation", "crop-monitor": "aslanpour/crop-monitor", "short": "aslanpour/short"}

#[WORKLOAD]
#"sync" or "static" or "poisson" (concurrently) or "exponential" (interval) or "exponential-poisson"
workload_type ="sync"

#No workload test: set workload_type ="sync" and concurrency=0
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
#[x][2]concurrently/poisson lambda (lambda~=avg) [x][3] random seed (def=5)]. In async means x requests (in x threads) per y sec. In sync means x spawners (in threads) sending 1 req each back to back.
# [x][4] shape, [x][5] worker "thread" or "gevent"
#in the main.py is w_config = my_app[3] --> w_config[0-3]
#if static, only set int values ????? otherwise, workload() gives error.

#1,1,1,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4,4,4,5,5,5,5,5,6,6,6,6,6,7,7,7,7,7,8,8,8,8,8,9,9,9,9,9,10,10,10,10,10,
workload_cfg ={
"w1":[[10000, 1, [000],seed, shapes["w1"],worker], [10000, 6, 1.9,seed, shapes["w1"],worker], [10000, 10, 1,seed, shapes["w1"],worker], [10000, 1, 1,seed, shapes["w1"],worker], [10000, 1, 1,seed, shapes["w1"],worker]],
"w2":[[10000, 1, [8,8,8,8,8],seed, shapes["w2"],worker], [10000, 20, 1.9,seed, shapes["w2"],worker], [10000, 15, 1.0,seed, shapes["w2"],worker], [10000, 1, 1,seed, shapes["w2"],worker], [10000, 1, 1,seed, shapes["w2"],worker]],
"w3":[[10000, 1, [8,8,8,8,8],seed, shapes["w3"],worker], [10000, 10, 1.9,seed, shapes["w3"],worker], [10000, 8, 1.0,seed, shapes["w3"],worker], [10000, 10, 1,seed, shapes["w3"],worker], [10000, 10, 1,seed, shapes["w3"],worker]],
"w4":[[10000, 1, [8,8,8,8,8],seed, shapes["w4"],worker], [10000, 10, 1.9,seed, shapes["w4"],worker], [10000, 8, 1.0,seed, shapes["w4"],worker], [10000, 10, 1,seed, shapes["w4"],worker], [10000, 10, 1,seed, shapes["w4"],worker]],
"w5":[[10000, 1, [8,8,8,8,8],seed, shapes["w5"],worker], [10000, 6, 1.9,seed, shapes["w5"],worker], [10000, 5, 1.0,seed, shapes["w5"],worker], [10000, 10, 1,seed, shapes["w5"],worker], [10000, 10, 1,seed, shapes["w5"],worker]],
"w6":[[10000, 1, [000],seed, shapes["w6"],worker], [10000, 6, 1.9,seed, shapes["w6"],worker], [10000, 5, 1.0,seed, shapes["w6"],worker], [10000, 10, 1,seed, shapes["w6"],worker], [10000, 10, 1,seed, shapes["w6"],worker]],
"w7":[[10000, 1, [8,8,8,8,8],seed, shapes["w7"],worker], [10000, 6, 1.9,seed, shapes["w7"],worker], [10000, 5, 1.0,seed, shapes["w7"],worker], [10000, 10, 1,seed, shapes["w7"],worker],[10000, 10, 1,seed, shapes["w7"],worker]],}

#copy chart-latest and chart-profile folders to home directory of master
profile_chart = ["chart-profile", "~/charts/chart-profile"]
function_chart = ["chart-latest", "~/charts/chart-latest"]
excel_file_path = "/home/" + getpass.getuser() + "/logs/metrics.xlsx" # this file should already be there with a sheet named nodes

clean_up = True #####
profile_creation_roll_out = 15  #### 30
function_creation_roll_out = 60  # 120


#CPU intensity of applications request per nodes per app
counter=[{"ssd": "0", "yolo3":"20", "irrigation":"75", "crop-monitor":"10", "short":"5"}] #variable

monitor_interval=10 #second
scheduling_interval= [800] #variable  ### second -- default 5 *  60 equivalent to 30 min
failure_handler_interval=10
battery_sim_update_interval=10
min_request_generation_interval = 1
sensor_admission_timeout = 3
max_request_timeout = 15 #max timeout was 30 set for apps, used for timers, failure_handler, etc.

intra_test_cooldown = 6 * 60 # 10 between each epoch to wait for workers
debug=True #master always True
max_cpu_capacity = 3600  #### #actual capacity is 4000m millicpu (or millicores), but 10% is deducted for safety net. Jetson nano and Pi 3 and 4 have 4 cores.
#initial charge value must be turn in to max_battery_charge if > max_battery_charge???
initial_battery_charge = 5000
min_battery_charge = 125 #mwh equals battery charge 10%
max_battery_charge = [5000]#variable #mwh full battery, 9376 - 20% and scale in 1/6: 1250mwh
#home dir will be attached before this path by pi-agent
#pics folder must be already filled with pics
pics_folder = "/pics-83num-resized-half-6mb-max130kb/" # /pics/
pics_num= 83
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w1"][0], 'master-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w1"][0], 'master-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w1"][1], 'master-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w1"][2], 'master-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w1"][3], 'master-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w1"][0], 'w1-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w1"][0], 'w1-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w1"][1], 'w1-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w1"][2], 'w1-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w1"][3], 'w1-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w2"][0], 'w2-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0,  apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w2"][0], 'w2-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0,  apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w2"][1], 'w2-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w2"][2], 'w2-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w2"][3], 'w2-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w3"][0], 'w3-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w3"][0], 'w3-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w3"][1], 'w3-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w3"][2], 'w3-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w3"][3], 'w3-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w4"][0], 'w4-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w4"][0], 'w4-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w4"][1], 'w4-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w4"][2], 'w4-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w4"][3], 'w4-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w5"][0], 'w5-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w5"][0], 'w5-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w5"][1], 'w5-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w5"][2], 'w5-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w5"][3], 'w5-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w6"][0], 'w6-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w6"][0], 'w6-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w6"][1], 'w6-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w6"][2], 'w6-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w6"][3], 'w6-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
    "load_balancing": load_balancing,
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
        ['ssd', apps["ssd"], workload_type, workload_cfg["w7"][0], 'w7-ssd', 'reference', 0, 0,
           [min_replicas["ssd"], max_replicas["ssd"], app_memory_quote["ssd"][0],app_memory_quote["ssd"][1],app_cpu_quote["ssd"][0], app_cpu_quote["ssd"][1], counter[0]["ssd"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-ssd" if multiple_queue else ""), "",0, apps_image["ssd"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['yolo3', apps["yolo3"], workload_type, workload_cfg["w7"][0], 'w7-yolo3', 'reference', 0, 0,
           [min_replicas["yolo3"], max_replicas["yolo3"], app_memory_quote["yolo3"][0],app_memory_quote["yolo3"][1],app_cpu_quote["yolo3"][0], app_cpu_quote["yolo3"][1], counter[0]["yolo3"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled") , ("queue-worker-yolo3" if multiple_queue else ""), "",0, apps_image["yolo3"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['irrigation', apps["irrigation"], workload_type, workload_cfg["w7"][1], 'w7-irrigation', 'reference', 0, 0,
           [min_replicas["irrigation"], max_replicas["irrigation"], app_memory_quote["irrigation"][0],app_memory_quote["irrigation"][1],app_cpu_quote["irrigation"][0], app_cpu_quote["irrigation"][1], counter[0]["irrigation"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-irrigation" if multiple_queue else ""), "",0, apps_image["irrigation"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['crop-monitor', apps["crop-monitor"], workload_type, workload_cfg["w7"][2], 'w7-crop-monitor', 'reference', 0, 0,
           [min_replicas["crop-monitor"], max_replicas["crop-monitor"], app_memory_quote["crop-monitor"][0],app_memory_quote["crop-monitor"][1],app_cpu_quote["crop-monitor"][0], app_cpu_quote["crop-monitor"][1], counter[0]["crop-monitor"], redis_server_ip, "3679","15s","15s","15s","15s",
            ("enabled" if service_mesh else "disabled"), ("queue-worker-crop-monitor" if multiple_queue else ""), "",0, apps_image["crop-monitor"]],
             ["unknown", "unknown","unknown", "unknown", "unknown", "unknown", "unknown", "unknown"]],
        ['short', apps["short"], workload_type, workload_cfg["w7"][3], 'w7-short', 'reference', 0, 0,
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
    "pics_num": pics_num,
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
