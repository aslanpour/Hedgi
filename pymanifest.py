#build manifest 
#always required: api_version, kind, object_name, namespace
def manifest_builder(**kwargs):
    results = None
    msg =""
    error = ""

    msg += '\nmanifest_builder started.'

    #check basic requirements to build a manifest
    if 'api_version' not in kwargs or 'kind' not in kwargs or 'object_name' not in kwargs or 'namespace' not in kwargs:
        error += '\n required fields are not given, i.e., api_version, kind, object_name, or namespace.'
        return results, msg, error

    #pick a builder

    #TrafficSplit
    if kwargs['kind'] == 'TrafficSplit':
        manifest, msg_child, error = trafficSplit(**kwargs)
    else:
        error +='\nKind: ' + kwargs['kind'] + ' not implemented'
    
    return manifest, msg, error



# manifest builder for trafficSplit
def trafficSplit(**kwargs):
    results= None; msg=""; error=""
    msg +="manifest builder for trafficSplit started."

    #verify especial fileds for a TrafficSplit, e.g., backend and service
    if not 'backends' in kwargs or not 'service' in kwargs:
        error += '\nNo backends and/or service are not given in kwargs'
        return results, msg, error


    #manifest
    manifest = {
        "apiVersion": kwargs['api_version'],
        "kind": kwargs['kind'],
        "metadata": {
            "name": kwargs['object_name'],
            "namespace": kwargs['namespace']
        },
        "spec": {
            "backends": kwargs['backends'],
            "service": kwargs['service']
        }
    }


    return manifest, msg, error
