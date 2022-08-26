from kubernetes import config, dynamic
from kubernetes.client import api_client
import datetime
import pytz

# Creating a dynamic client
client = dynamic.DynamicClient(
    api_client.ApiClient(configuration=config.load_kube_config())
)

# fetching the deployment api
#api = client.resources.get(api_version="apps/v1", kind="Deployment")
api = client.resources.get(api_version="split.smi-spec.io/v1alpha1", kind="TrafficSplit")

#get the deployment by name
# name = "ssd-tpu"
name = "function-split"
from kubernetes import client
apps_v1 = client.AppsV1Api()
deployments = apps_v1.list_namespaced_deployment(namespace="default")
for i in deployments.items:
        print(f'{i.status.available_replicas}\t\t{i.spec.replicas}\t\t{i.metadata.namespace}\t{i.metadata.name}')
        if i.metadata.name == name:
            print('exists')
#deployment = api.get(name=name, namespace="default")
trafficsplit = api.get(name=name, namespace="openfaas-fn")
print(trafficsplit)
trafficsplit.spec.backends = [{"service": "ssd-tpu-green", "weight": "500m"}]
#update the fileds
#allowPrivilegeEscalation = True
#'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"allowPrivilegeEscalation": true}}]}}}}'
# deployment.spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation = True

#privileged = True
#'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"privileged": true}}]}}}}'
# deployment.spec.template.spec.containers[0].securityContext.privileged = True

#runAsUser = 0
#'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"runAsUser": 0}}]}}}}'
# deployment.spec.template.spec.containers[0].securityContext.runAsUser = 0

#volumes hostPath
#'{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'
# deployment.spec.template.spec.volumes = [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]

#volumeMounts mountPath
#'{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu", "volumeMounts":[{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}]}}}}'
# deployment.spec.template.spec.containers[0].volumeMounts = [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]

#patch
# result = api.patch(body=deployment, name=name, namespace="default")
result = api.patch(body=trafficsplit, name=name, namespace="openfaas-fn",content_type="application/merge-patch+json")




#alternative way of patching a deployment
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
    name=DEPLOYMENT_NAME, namespace="openfaas-fn", body=patch
)
'''