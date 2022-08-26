import datetime

#pick and run an algorithm
def plan(**kwargs):
    results = None
    msg =""
    error= ""

    #get algorithm name
    if not 'algorithm' in kwargs: 
        error += '\nNo item as algorithm found in kwargs given to plan'
        return results, msg, error
    else:
        algorithm_name = kwargs['algorithm']

    
    #pick an algorithm
    if algorithm_name == "even":
        updated_backend_list, msg_child, error = plan_even(**kwargs)
        msg += msg_child
    else:
        error += "\nalgorithm_name=" + algorithm_name + "NOT found"
        return None, msg, error

    #return an updated list of backends
    return updated_backend_list, msg, error


#run even algorithm
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

    #plan
    for i in range(len(backends_list)):
        #e.g., {"v1": 100}
        backend = backends_list[i]
        #e.g., key="v1" and value=100. Note: this removes the item from backend and subsequently from backends
        key, value = backend.popitem()

        #calculate the weight
        weight = 1000 / len(backends_list)
        value = weight
        backend= {key, value}
        backends_list[i]=backend

    end = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
    elapsed = end - start
    msg += "\nelapsed= " + str(round(elapsed,2))

    results = backends_list
    #return an updated list of backends
    return results, msg, error



