import datetime
import pymanifest

#pick and run an algorithm
def plan(**kwargs):
    results = None
    msg =""
    error= ""
    msg += '\nplan: started'
    if kwargs['type']:
        if kwargs['type'] == 'trafficsplit':
            results, msg_child, error = traffic_split_approach(**kwargs)
            msg += msg_child
        else:
            error += 'The load balancing approach type is not defined'
    else:
        error += 'Load balancing type must be given as key type'

    msg += '\nplan: stopped'
    return results, msg, error

    


def traffic_split_approach(**kwargs):
    results=None; msg=""; error=""
    msg += '\ntraffic_split_approach: started'
    #get algorithm name
    if not 'algorithm' in kwargs: 
        error += '\nNo item as algorithm found in kwargs given to plan'
        return results, msg, error
    else:
        algorithm_name = kwargs['algorithm']

    #at first round, 
    if kwargs['load_balancing_round'] == 0:
        #deploy a gateway deployment and service (or openfaas function)
        msg +='\nDeploy gateway function...'
        gateway_function = kwargs['gateway_function']

        results, msg_child, error = deploy_gateway_function(**gateway_function)
        msg += msg_child
        if error:
            error +='deploy_gateway_function:\n' + error
            return results, msg, error

    #pick an algorithm
    if algorithm_name == "even":
        updated_backend_list, msg_child, error = plan_even(**kwargs)
        msg += msg_child
    else:
        error += "\nalgorithm_name=" + algorithm_name + "NOT found"
        return None, msg, error

    msg += '\ntraffic_split_approach: stopped'
    #return an updated list of backends
    return updated_backend_list, msg, error

    

#run even algorithm
#Sample --> 'backends':[{'service':'w5-ssd','weight': 1000}, {'service':'w6-ssd','weight': 0}]
def plan_even(**kwargs):
    start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    results = None
    msg =""
    error= ""

    msg += 'event_plan: algorithm even started.'
    #get backends list
    backends_list = []
    if 'backends' in kwargs:
        backends_list = kwargs['backends']
    else:
        error += '\nNo backends found in kwargs'
        return results, msg, error

    msg += '\nplan_even:backends_before_plan: ' + str(backends_list)

    #plan
    #give all backends equal weights
    for i in range(len(backends_list)):
        #e.g., {'service':'w5-ssd','weight': 1000}
        backend = backends_list[i]

        #e.g., key="v1" and value=100. Note: this removes the item from backend and subsequently from backends
        # key, value = backend.popitem()

        #calculate the weight
        backend['weight'] = int(1000 / len(backends_list))
        # if backend['service'] == 'w5-ssd':
        #     backend['weight'] = 1000
        # else:
        #     backend['weight'] = 0

        backends_list[i]=backend

    end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    elapsed = end - start
    msg += "\nelapsed= " + str(round(elapsed,2))
    msg += '\nplan_even:backends_after_plan: ' + str(backends_list)

    results = backends_list
    #return an updated list of backends
    return results, msg, error


#deploy gateway function
def deploy_gateway_function(**kwargs):
    import pykubectl

    results=None; msg=""; error=""
    msg += 'deploy_gateway_function: started'

    #build function manifest
    gateway_function = kwargs
    manifest, msg_child, error = pymanifest.manifest_builder(**gateway_function)
    msg += msg_child
    if error:
        return manifest, msg, error

    gateway_function['manifest'] = manifest

    #deploy function
    gateway_function['operation'] = 'safe-patch'     
    results, msg_child, error = pykubectl.apply(**gateway_function)
    msg += msg_child
    msg += '\ndeploy_gateway_function: stopped'
    return results, msg, error

#by disabling USB on a device where a function is running and has loaded TPU model, the container (not Pod) will fail and restart.
#get acceleerators on a node
def has_accelerators(node_name, **kwargs):
    results=None; msg=""; error = ""
    results = []

    #verify if accelerators key exists
    if not 'accelerators' in kwargs:
        error += 'An accelerators key is missing from **kwargs'
        return results, msg, error

    #search
    #e.g., accelerators = {'w5': ['gpu', 'tpu']} is set by setup.py
    accelerators = kwargs['accelerators']
    if 'tpu' in accelerators[node_name]:
        results.append('tpu')
    elif 'gpu' in accelerators[node_name]:
        results.append('gpu')
    else:
        error += 'accelerators[node_name] found a value as ' + str(accelerators[node_name]) + ' that is not defined here.'

    return results, msg, error

    #by sending config read request
    # res = requests.get('http://10.0.0.90:31112/function/w5-ssd/config/read', json={})
    # if res.ok:
    #     config = res.json()