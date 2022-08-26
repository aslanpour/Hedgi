10.42.5.53

#runs by default on cpu --- otherwise preload TPU and/or GPU models and set their interpreter by setting env variables for the container (e.g., e.g., MODEL_SUPPORTED_RESOURCES_TPU=yes) and/or setting them as the model in use (e.g., MODEL_RUN_ON=tpu)
curl -X POST -i -F  image_file=@./images/image1.jpg  http://localhost:5000/

#on Jetson Nano (test for GPU use)
#this node has GPU (but just merely this setting, nothing will happen -- this is a prerequisitic for using another resource)
curl -X POST -i http://localhost:5000/config/write  -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{"config":{"Model": {"supported_resources_gpu": "yes"}}}'
#now on, run on GPU
curl -X POST -i http://localhost:5000/config/write  -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{"config":{"Model": {"run_on": "gpu"}}}'
#test GPU
curl -X POST -i -F  image_file=@./images/image1.jpg  http://localhost:5000/
#Note: convert curl commands in python: https://curlconverter.com/

#in Kuberneets deployment do the following:
#Grant --privileged
kubectl patch deployment ssd-tpu --patch '{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"privileged": true}}]}}}}'
#run as root
kubectl patch deployment ssd-tpu --patch '{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"runAsUser": 0}}]}}}}'
#Mount -v /dev/bus/usb:    of the host
kubectl patch deployment ssd-tpu --patch '{"spec": {"template": {"spec": {"volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'
# to /dev/bus/usb of the container
kubectl patch deployment ssd-tpu --patch '{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu", "volumeMounts":[{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}]}}}}'

#all together at once
kubectl patch deployment ssd-tpu --patch '{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"privileged": true, "runAsUser": 0}, "volumeMounts": [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}], "volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'

#in OpenFaaS function (add -n openfaas-fn), as well as the above, you have to enable allowPrivilegeEscalation which is flase for function by OpenFaaS; otherwise, it conflicts with privilged.
kubectl patch deployment ssd-tpu --patch '{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"allowPrivilegeEscalation": true}}]}}}}'
#all together becomes:
kubectl patch deployment ssd-tpu -n openfaas-fn --patch '{"spec": {"template": {"spec": {"containers": [{"name": "ssd-tpu","image": "aslanpour/ssd:cpu-tpu", "securityContext": {"privileged": true, "runAsUser": 0, "allowPrivilegeEscalation": true}, "volumeMounts": [{"mountPath": "/dev/bus/usb", "name": "usb-devices"}]}], "volumes": [{"name": "usb-devices", "hostPath": {"path": "/dev/bus/usb"}}]}}}}'
