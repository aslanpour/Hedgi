
def what_device_is_it(name):
    import io
    name = name.lower()
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if name in m.read().lower(): return True
    except Exception: pass
    return False

def attached_tpu_detected():
    usb_devices = shell('lsusb')
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



####################
def patch_kubernetes_deployment(name, namespace = "default", enabling_tpu_gpu_access = False):
    from kubernetes import config, dynamic
    from kubernetes.client import api_client
    import datetime
    import pytz
    error = ""

    # Creating a dynamic client
    try:
        dynamic_api_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )
    except Exception as e:
        error += '\n' + str(e)
        error= 'Unable to get kubeconfig'
        return error, 400

    #Does the requested deployment exist?
    exists = False
    from kubernetes import client
    apps_v1 = client.AppsV1Api()
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
    for i in deployments.items:
            #print(f'{i.status.available_replicas}\t\t{i.spec.replicas}\t\t{i.metadata.namespace}\t{i.metadata.name}')
            if i.metadata.name == name:
                exists = True
    if exists == False:
        error += '\n The requested deployment name=' + name + ' is not found in namespace=' + namespace
        return error, 400

    # fetching the deployment api
    dynamic_api = dynamic_api_client.resources.get(api_version="apps/v1", kind="Deployment")

    #get the deployment by name
    try:
        deployment = dynamic_api.get(name=name, namespace=namespace)
    except Exception as e:
        error += '\n' + str(e)
        error += '\nFailed to get the requested deployment -- name=' + name + ' namespace=' + namespace
        return error, 400
    
    if enabling_tpu_gpu_access:
        #update the fileds
        #allowPrivilegeEscalation = True
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"allowPrivilegeEscalation": true}}]}}}}'
        deployment.spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation = True
        #privileged = True
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"privileged": true}}]}}}}'
        deployment.spec.template.spec.containers[0].securityContext.privileged = True
        #runAsUser = 0
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"runAsUser": 0}}]}}}}'
        deployment.spec.template.spec.containers[0].securityContext.runAsUser = 0
        #volumes hostPath
        #'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'
        deployment.spec.template.spec.volumes = [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]
        #volumeMounts mountPath
        #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu", "volumeMounts":[{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}]}}}}'
        deployment.spec.template.spec.containers[0].volumeMounts = [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]

        #get Pod info as env into the container
        deployment.spec.template.spec.containers[0].env = [{"name": "GREETING", "value": "WARM_GREETING"},
                                                            {"name": "NODE_NAME", "valueFrom": {"fieldRef":{"fieldPath": "spec.nodeName"}}},
                                                            {"name": "POD_NAME", "valueFrom": {"fieldRef":{"fieldPath": "metadata.name"}}},
                                                            {"name": "POD_NAMESPACE", "valueFrom": {"fieldRef":{"fieldPath": "metadata.namespace"}}},
                                                            {"name": "POD_IP", "valueFrom": {"fieldRef":{"fieldPath": "status.podIP"}}},
                                                            {"name": "POD_IPS", "valueFrom": {"fieldRef":{"fieldPath": "status.podIPs"}}},
                                                            {"name": "POD_HOST_IP", "valueFrom": {"fieldRef":{"fieldPath": "status.hostIP"}}},
                                                            {"name": "DEPLOYMENT_NAME", "valueFrom": {"fieldRef":{"fieldPath": "metadata.labels['app']"}}},
                                                            {"name": "POD_UID", "valueFrom": {"fieldRef":{"fieldPath": "metadata.uid"}}}]

    else:
        error += '\nPatching this field is not implemented yet.'
        return error, 400

    #patch
    try:
        result = dynamic_api.patch(body=deployment, name=name, namespace=namespace)
    except Exception as e:
        error += '\n' + str(e)
        error += '\nPatch failed -- name=' + name + ' namespace=' + namespace + ' body=' + deployment
        return error, 400
    return error, 200

    #alternative way of patching a deployment by Kubectl. ref: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#patch-deployment-v1-apps
    '''
    kubectl patch deployment deployment-example -p \
	'{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.16"}]}}}}'
    '''
    
    #alternative way of patching a deployment by Curl. Ref: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#patch-deployment-v1-apps
    '''
    kubectl proxy

    $ curl -X PATCH -H 'Content-Type: application/strategic-merge-patch+json' --data '
        {"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.16"}]}}}}' \
	    'http://127.0.0.1:8001/apis/apps/v1/namespaces/default/deployments/deployment-example'

    '''

    #alternative way of patching a deployment in Python
    '''
    from kubernetes import client, config

    DEPLOYMENT_NAME = "ssd-tpu"
    client.configuration.debug = True
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()


    #'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"allowPrivilegeEscalation": true}}]}}}}'
    # patch = [{"op": "replace", "value": True, "path": "/spec/template/spec/containers/0/securityContext/allowPrivilegeEscalation"}]
    #'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'

    patch = [{"op": "replace", "value": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}], "path": "/spec/template/spec/volumes"}]
    # patch the deployment
    resp = apps_v1.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="saas-fn", body=patch
    )
    '''

#######################
# patch_kubernetes_deployment('ssd-tpu', namespace = "openfaas-fn", enabling_tpu_gpu_access = True)