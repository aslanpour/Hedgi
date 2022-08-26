from kubernetes import client,config, dynamic
from kubernetes.client import api_client
import datetime

#[input]
#api_version, e.g., autoscaling/v2, split.smi-spec.io/v1alpha1, openfaas.com/v1, apps/v1
#kind, e.g., Deployment, Function, Pod, HorizontalPodAutoscaler, TrafficSplit
#object_name, e.g., sample_deployment
#namespace, e.g., openfaas-fn
#manifest, e.g., a json object
#operation, e.g., replace, safe_replace (if object not exists, first create it), create, patch, safe_patch (if object not exists, first create it), delete
#patch_type, e.g., application/merge-patch+json, application/json-patch+json, application/apply-patch+yaml


#required input:
#api_version, kind, object_name, manifest, namespace="default", operation= "safe_replace", patch_type= "application/merge-patch+json",
def apply(**kwargs):
    #start
    error = ""; msg = ""; results = None

    #check input requirements
    if 'api_version' not in kwargs or 'kind' not in kwargs or 'object_name' not in kwargs or 'manifest' not in kwargs:
        error += '\nBasig input is not given, i.e., api_version, kind, object_name, or manifest'
        return results, msg, error

    #set defaults, if not given by kwargs
    namespace = kwargs['namespace'] if 'namespace' in kwargs else "default"
    operation = kwargs['operation'] if 'operation' in kwargs else "safe_replace"
    patch_type = kwargs['patch_type'] if 'patch_type' in kwargs else "application/merge-patch+json"

    
    #print the input
    msg +=("Kube apply started:"
        + "\napi_version= " + kwargs['api_version']
        + "\nkind= " + kwargs['kind']
        + "\nobject_name= " + kwargs['object_name']
        + "\nnamespace= " + namespace
        + "\noperation= " +  operation
        + "\npatch_type= " + patch_type
        + ("\n**kwargs= " + str({k:v for k,v in kwargs.items()}) if len(kwargs)>0 else ""))

    
    #client
    try:
        # setup the kubernetes API
        client = dynamic.DynamicClient(api_client.ApiClient(configuration=config.load_kube_config()))
        api_resources = client.resources.get(api_version=kwargs['api_version'], kind=kind)
    except:
        error += "\nFailed to create a client using the kubeconfig file"
        return results, msg, error

    
    #operation
    #If the operation is 'replace/patch', verify if the object exists; otherwise a 'create' will be requested automatically if a safe operation is requested.
    object_already_exists = False
    if 'replace' in operation or 'patch' in operation:
        #get all objects
        for item in api_resources.get(namespace=namespace).items:
            #Check each by name
            #either as dictionery/json
            object_under_check = api_resources.get(name=item.metadata.name, namespace=namespace)
            
            object_under_check_name = object_under_check["metadata"]["name"]
            #or as Yaml
            object_under_check_name = item.metadata.name

            if object_under_check_name == kwargs['object_name']:
                object_already_exists = True
                msg += "\nObject " + kwargs['object_name'] + " exists."
                break
        #check done
        if not object_already_exists:
            msg += "\nObject " + kwargs['object_name'] + " does NOT exists."


    #apply

    #replace or patch
    if 'replace' in operation or 'patch' in operation:
        #object exists
        if object_already_exists:
            #replace
            if 'replace' in operation:
                msg += "\nA replace operation is taken."
                try:
                    results = api_resources.replace(body=kwargs['manifest'], namespace=namespace)
                except Exception as e:
                    error += '\n' + str(e)
            #patch
            elif 'patch' in operation:
                msg += "\nA patch operation is taken."
                try:
                    results = api_resources.patch(body=kwargs['manifest'], namespace=namespace, name=kwargs['object_name'], content_type=patch_type)
                except Exception as e:
                    error += '\n' + str(e)
        #object NOT exists
        else:
            #if safe, 
            #create one for a requested replace 
            if 'safe' in operation and 'replace' in operation:
                msg += "\nA create operation is taken."
                try:
                    results = api_resources.create(body=kwargs['manifest'], namespace=namespace)
                except Exception as e:
                    error += '\n' + str(e)
            #create one for a requested patch
            elif 'safe' in operation and 'patch' in operation:
                msg += "\nA create operation is taken."
                try:
                    results = api_resources.create(body=kwargs['manifest'], namespace=namespace)
                except Exception as e:
                    error += '\n' + str(e)
            #no operation
            else:
                error += "\nThe action is dismissed since the object does not exist and operation is not a safe one."
                
    #create
    elif 'create' in operation:
        msg += "\nA create operation is taken."
        try:
            results = api_resources.create(body=kwargs['manifest'], namespace=namespace)
        except Exception as e:
            error += '\n' + str(e)
    #delete
    elif 'delete' in operation:
        msg += "\nA delete operation is taken."
        try:
            results = api_resources.delete(name=kwargs['object_name'], body={}, namespace=namespace)
        except Exception as e:
            error += '\n' + str(e)
    #unknown
    else:
        error += "\nOperation =" + operation + " is not known"

    #return
    return results, msg, error







#sample trafficsplit
#create
'''
object_name= "function-split"
api_version= "split.smi-spec.io/v1alpha2"
kind= "TrafficSplit"
namespace="openfaas-fn"
operation= "safe_patch"
patch_type= "application/merge-patch+json"

#extra
service= "ssd-tpu"

manifest = {
    "apiVersion": api_version,
    "kind": kind,
    "metadata": {
        "name": object_name,
        "namespace": namespace
    },
    "spec": {
        "backends": [],
        "service": service
    }
}
'''
#patch
'''
manifest = {"spec": {
        "backends": [
            {
                "service": "ssd-tpu-blue",
                "weight": 1000
            }
        ],
        "service": "ssd-tpu"
    }
}
'''