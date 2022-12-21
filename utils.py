
def what_device_is_it(name):
    import io
    name = name.lower()
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if name in m.read().lower(): return True
    except Exception: pass
    return False

def attached_tpu_detected():
    usb_devices, error = shell('lsusb')
    if error: 
        print('ERROR:' + error, flush=True)
        return False
    else:
        #or by vendor:product through lsusb -d 0x1a6e:0x089a
        return True if 'Google Inc.' in usb_devices or 'Global Unichip Corp.' in usb_devices else False

#password= "", "any_password", "prompt"
def shell(cmd, password="", timeout=30):
    import subprocess
    output = ""
    error = ""
    popen = False
    if password:
        popen= True
    #else: check_output

    #run cmd
    try:
        #without password
        if not popen:
            #run
            output= subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout).decode("utf-8") 
        #with password
        else:
            #prompt password if required
            if password == "prompt":
                import getpass
                password = getpass.getpass(prompt='sudo password: ')
            #run
            cmd = cmd.split()
            p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE,  stdin=subprocess.PIPE)
            output, error = p.communicate(input=(password+'\n').encode(),timeout=timeout)
            output = output.decode('utf-8')
            error = error.decode('utf-8')
    except subprocess.CalledProcessError as e:
        if not popen:
            error += 'ERROR: ' + e.output.decode("utf-8")
        else:
            error += 'ERROR: ' + str(e)
            p.kill()
    except subprocess.TimeoutExpired as e:
        if not popen:
            error += 'ERROR: ' + e.output.decode("utf-8")
        else:
            error += 'ERROR: ' + str(e)
            p.kill()
    except Exception as e:
        if not popen:
            error += 'ERROR: ' + e.output.decode("utf-8")
        else:
            error += 'ERROR: ' + str(e)
            p.kill()

    return output, error


######
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(dir_path + "/pykubectl.py"): import pykubectl

#patch a function
def openfaas_function_customizations(function_name, function_worker_name, accelerators, namespace='openfaas-fn', operation='get-json', patch_type='application/merge-patch+json'):
    results = None; msg = ""; error=""

    #get Deployment of the function as json
    manifest = {}

    patch_info = {
        "api_version": "apps/v1",
        "kind": "Deployment",
        "object_name": function_name,
        "manifest": manifest,
        "namespace": namespace,
        "operation": operation,
    }

    #get
    try:
        deployment_dict, msg, error = pykubectl.apply(**patch_info)
        if error:
            print(error)
            
    except Exception as e:
        print('utils pykubectl,.apply\n' + str(e))
        error += '\n' + str(e)
    #get main container (in case multi-container is enables using like service mesh side car)
    index=-1
    for container in deployment_dict['spec']['template']['spec']['containers']:
        if container['name'] == function_name:
            index = deployment_dict['spec']['template']['spec']['containers'].index(container)
            break
    if index ==-1:
        error += '\nA container with the name of function was not found in the deployment'
        return results, msg, error

    
    #customize fields

    #imagepullPolicy = Never. Do this carefully???
    deployment_dict['spec']['template']['spec']['containers'][index]['imagePullPolicy'] = 'Never'
    # deployment.spec.template.spec.containers[container_id].image_pull_policy = 'Never'
   
    #allowPrivilegeEscalation = True
    #privileged = True
    #runAsUser = 0
    #readOnlyRootFilesystem = False (openfaas adds this to functions, so include this to avoid loosing it upon patching securityContext)
    deployment_dict['spec']['template']['spec']['containers'][index]['securityContext'] = {"allowPrivilegeEscalation": True,
                                                                                           "privileged": True,
                                                                                            "runAsUser": 0,
                                                                                            "readOnlyRootFilesystem": False,
                                                                                            }

    #volumes hostPath
    deployment_dict['spec']['template']['spec']['volumes'] = [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]
    # deployment.spec.template.spec.volumes = [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]
    #'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'

    #volumeMounts mountPath
    deployment_dict['spec']['template']['spec']['containers'][index]['volumeMounts'] = [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]
    # deployment.spec.template.spec.containers[container_id].volumeMounts = [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]
    #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu", "volumeMounts":[{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}]}}}}'
    
    #env??????????????
    '''- name: REDIS_SERVER_PORT
          value: "3679"
        - name: read_timeout
          value: 15s
        - name: write_debug
          value: "true"
        - name: COUNTER
          value: "0"
        - name: REDIS_SERVER_IP
          value: 10.43.189.161
        - name: exec_timeout
          value: 15s
        - name: handler_wait_duration
          value: 15s
        - name: version
          value: "1"
        - name: write_timeout
          value: 15s'''

    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'MODEL_PRE_LOAD', 'value': 'yes', 'value_from': None})
    #???these are not configurable from setup.py
    model_run_on = 'cpu'
    model_cpu_workers = 4
    flask_waitress_threads = 4
    if function_worker_name in accelerators: 
        if 'tpu' in accelerators[function_worker_name]:
            model_run_on = 'tpu'
            model_cpu_workers = 1
            flask_waitress_threads = 1
        elif 'gpu' in accelerators[function_worker_name]:
            model_run_on = 'gpu'
            model_cpu_workers = 1
            flask_waitress_threads = 4
    else:
        print('ERROR: ' + function_worker_name + ' not found in accelerator= ' + str(accelerators))
        
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'MODEL_RUN_ON', 'value': model_run_on, 'value_from': None})
    #???
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'MODEL_CPU_WORKERS', 'value': str(model_cpu_workers), 'value_from': None})
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'WAITRESS_THREADS', 'value': str(flask_waitress_threads), 'value_from': None})

    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'NODE_NAME', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'spec.nodeName'}}})
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_NAME', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'metadata.name'}}})
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_NAMESPACE', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'metadata.namespace'}}})
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_IP', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'status.podIP'}}})
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_IPS', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'status.podIPs'}}})
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_HOST_IP', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'status.hostIP'}}})
    deployment_dict['spec']['template']['spec']['containers'][index]['env'].append({'name': 'POD_UID', 'value': None, 'valueFrom': {'fieldRef': {'apiVersion': 'v1', 'fieldPath': 'metadata.uid'}}})
    a='''
        - name: POD_HOST_IP
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
    '''

    #prepare
    patch_info = {
        "api_version": "apps/v1",
        "kind": "Deployment",
        "object_name": function_name,
        "manifest": deployment_dict,
        "namespace": namespace,
        "operation": 'patch',
        "patch_type": patch_type,
    }
    
    #patch
    patched_deployment, msg_child, error = pykubectl.apply(**patch_info)
    msg += msg_child
    # print('RRRRRRRRRRRRRRRRRRRRRR')
    # if not error:
    #     print( results)

    # print(msg)
    # print('ERROR:' +error)
    results = patched_deployment
    return results, msg, error

    
    


# openfaas_function_customizations('w5-ssd')
